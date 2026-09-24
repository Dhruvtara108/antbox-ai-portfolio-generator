from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.services.document_service import DocumentExtractionError, extract_text
from app.services.gemini_service import (
    GeminiConfigurationError,
    GeminiResponseError,
    GeminiService,
)
from app.services.template_service import render_template


router = APIRouter()


@router.post("/generate-portfolio")
async def generate_portfolio(
    resume: UploadFile = File(...),
    joining_document: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    location: str = Form(""),
    role: str = Form(""),
):
    try:
        resume_text, joining_text = await _extract_documents(resume, joining_document)
        service = GeminiService(get_settings())
        profile = service.generate_profile(
            resume_text,
            joining_text,
            {"name": name, "email": email, "phone": phone, "location": location, "role": role},
        )
        html = render_template(profile)
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiResponseError as exc:
        # Return a sanitized development-friendly error message, never exposing documents or keys
        safe_detail = f"Gemini request failed: {str(exc)}"
        raise HTTPException(status_code=502, detail=safe_detail) from exc

    return {"profile": profile.model_dump(), "html": html, "status": "generated"}


async def _extract_documents(
    resume: UploadFile, joining_document: UploadFile
) -> tuple[str, str]:
    return await extract_text(resume), await extract_text(joining_document)
