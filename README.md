# Antbox AI Portfolio Generator

Foundation MVP for extracting factual candidate data from a resume and joining document, validating it with Pydantic, and rendering it through the manager-approved HTML template.

## Run locally

From `portfolio-generator`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The API health check is available at `http://localhost:8000/health`. The frontend is available at the Vite URL, normally `http://localhost:5173`.

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. The backend also reads the existing workspace-level `.env` for local development; the key is never sent to the frontend.

## Deploy to Vercel

Use the repository root as the Vercel project root. `vercel.json` runs
`npm --prefix frontend run build` and publishes `frontend/dist`. The FastAPI
entrypoint is `api/index.py`, so production API requests use the same-origin
pattern `/api/health` and `/api/generate-portfolio`. Set `GEMINI_API_KEY` as a
Vercel server-side environment variable; do not add it to frontend variables.

## Current scope

- `/health` is implemented.
- `/generate-portfolio` extracts PDF/DOCX text, sends evidence to Gemini, and validates a `CandidateProfile`.
- The approved template is served at `/template.html` for preview.
- Dynamic injection, persisted portfolios, downloads, and sharing are intentionally not implemented yet.
