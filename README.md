# Career Platform

FastAPI backend with a static HTML/CSS/vanilla-JavaScript frontend. User accounts and extracted resume text are stored in SQLite; ChromaDB is used for optional resume retrieval. Hugging Face provides structured resume analysis, question answering, and user-supplied job-description comparison when configured.

## Setup

Use Python 3.11 or newer. From the project directory in PowerShell:

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `SECRET_KEY` in `.env` to a random value of at least 32 characters. Generate one locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Set `HUGGINGFACE_TOKEN` to enable analysis, RAG answers, and job matching. The service starts without the AI token, but those operations report that the provider is not configured.

Run the API from the project directory:

```powershell
uvicorn app.main:app --reload
```

Serve `frontend/html` with a static server such as VS Code Live Server on port 5500. The default CORS allowlist covers `localhost:5500` and `127.0.0.1:5500`; set `CORS_ORIGINS` in `.env` for another origin. Set `window.CAREER_API_BASE_URL` before `frontend/js/api.js` if the API is hosted somewhere other than `http://127.0.0.1:8000`.

## API

- `POST /auth/register` and `POST /auth/login`
- `GET /career/me` and `GET /career/dashboard`
- `GET /resumes`, `POST /resumes/upload`, and `POST /resumes/{resume_id}/query`
- `POST /matching/compare`

Protected endpoints require `Authorization: Bearer <access_token>`. Resume upload accepts PDF and DOCX files up to 10 MB. Resume content is extracted and stored in SQLite before optional vector indexing and analysis. The matching endpoint compares a saved resume with a job description supplied by the user; the current database has no job catalogue for automatic recommendations.

## Data and security notes

The existing `career_platform.db` is retained. SQLAlchemy `create_all` creates missing tables but does not migrate existing tables. Chroma data remains under `chroma_db/`. Uploaded document contents are not written as files; extracted text and the original filename are stored in the `resumes` table. Configure a strong JWT secret before using authentication. Do not commit `.env` or local database/vector data.

## Tests

Run the standard-library test suite with:

```powershell
python -m unittest discover -s tests -v
```
