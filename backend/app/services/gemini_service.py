import json
import logging

from google import genai
from google.genai.errors import APIError
from pydantic import ValidationError

from app.config import Settings
from app.models.candidate import CandidateProfile


logger = logging.getLogger(__name__)


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini is not configured."""


class GeminiResponseError(RuntimeError):
    """Raised when Gemini does not return valid candidate data."""


class GeminiService:
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY is not configured.")
        try:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        except Exception as exc:
            logger.exception("Gemini client initialization failed")
            raise GeminiResponseError(
                "Gemini could not be initialized. Please try again later."
            ) from exc
        self._model = settings.gemini_model

    def generate_profile(
        self,
        resume_text: str,
        joining_document_text: str,
        basic_information: dict[str, str],
    ) -> CandidateProfile:
        prompt = f"""
Return only a factual candidate profile matching CandidateProfile.
Return JSON only; do not generate HTML or any explanation.
Use only information supported by the uploaded resume, joining document/job
description, and basic candidate information. Never invent companies, dates,
skills, achievements, metrics, education, certifications, or responsibilities.
Distinguish candidate evidence from job requirements: a requirement is not proof
that the candidate has that capability. Empty strings and empty lists are
acceptable whenever evidence is absent. Include short supporting evidence only
when the schema provides an evidence field.

Basic information:
{json.dumps(basic_information, ensure_ascii=True)}

Resume:
{resume_text}

Joining document / job description:
{joining_document_text}
""".strip()

        logger.info(
            "Calling Gemini for candidate profile",
            extra={"gemini_called": True, "model": self._model},
        )
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": CandidateProfile.model_json_schema(),
                },
            )
        except APIError as exc:
            # log safe API error details (type and short message) but never log documents/keys
            safe_msg = getattr(exc, "message", None) or getattr(exc, "status", None) or str(exc)
            logger.error(
                "Gemini APIError",
                extra={
                    "gemini_called": True,
                    "error_type": exc.__class__.__name__,
                    "error_message": safe_msg,
                },
            )
            raise GeminiResponseError(f"Gemini request failed: {exc.__class__.__name__}: {safe_msg}") from exc
        except Exception as exc:
            logger.exception(
                "Gemini API call failed",
                extra={"gemini_called": True, "response_success": False},
            )
            raise GeminiResponseError(
                "Gemini could not generate a candidate profile. Please try again."
            ) from exc

        # Safe metadata about the response (do not log contents)
        try:
            parsed = getattr(response, "parsed", None)
        except Exception as exc:
            logger.warning(
                "Gemini parsed attribute access failed; will use text fallback",
                extra={"parsed_available": False, "error_type": exc.__class__.__name__},
                exc_info=exc,
            )
            parsed = None

        response_status = getattr(response, "status", None)
        response_text = getattr(response, "text", None)
        text_present = bool(isinstance(response_text, str) and response_text.strip())

        logger.info(
            "Gemini response received",
            extra={
                "gemini_called": True,
                "response_success": True,
                "response_status": response_status,
                "parsed_available": parsed is not None,
                "text_present": text_present,
            },
        )

        if parsed is not None:
            try:
                profile = (
                    parsed
                    if isinstance(parsed, CandidateProfile)
                    else CandidateProfile.model_validate(parsed)
                )
            except ValidationError as exc:
                logger.warning(
                    "Gemini parsed response failed CandidateProfile validation",
                    extra={"validation_success": False},
                    exc_info=exc,
                )
                raise GeminiResponseError(
                    "Gemini returned data that does not match the candidate profile schema."
                ) from exc
            logger.info(
                "Gemini parsed response validated",
                extra={"validation_success": True},
            )
            return profile

        try:
            response_text = getattr(response, "text", None)
        except Exception as exc:
            logger.warning(
                "Gemini response text was unavailable",
                extra={"validation_success": False},
                exc_info=exc,
            )
            raise GeminiResponseError(
                "Gemini returned an unreadable response."
            ) from exc

        if not isinstance(response_text, str) or not response_text.strip():
            logger.warning(
                "Gemini returned an empty response",
                extra={"validation_success": False},
            )
            raise GeminiResponseError("Gemini returned an empty candidate profile.")

        try:
            profile = CandidateProfile.model_validate_json(response_text)
        except (ValidationError, ValueError) as exc:
            logger.warning(
                "Gemini text fallback failed CandidateProfile validation",
                extra={"validation_success": False},
                exc_info=exc,
            )
            raise GeminiResponseError(
                "Gemini returned malformed or invalid candidate profile JSON."
            ) from exc

        logger.info(
            "Gemini text fallback validated",
            extra={"validation_success": True},
        )
        return profile
