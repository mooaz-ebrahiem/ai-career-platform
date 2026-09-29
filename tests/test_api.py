import io
import unittest
from unittest.mock import patch

from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services.resume_parser import extract_resume_text
from app.utils import security


class CareerPlatformApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        security.JWT_SECRET_KEY = "unit-test-key-that-is-long-enough-for-hmac"
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.session_factory = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        def override_get_db():
            with self.session_factory() as db:
                yield db

        self.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.email = "candidate@example.test"
        self.token = self._register_and_login(self.email)
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides = self.original_overrides

    def _register_and_login(self, email):
        response = self.client.post(
            "/auth/register",
            json={"email": email, "password": "correct-horse-123", "role": "admin"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["role"], "user")
        login = self.client.post(
            "/auth/login",
            json={"email": email, "password": "correct-horse-123"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        return login.json()["access_token"]

    @staticmethod
    def _docx_bytes(text):
        document = Document()
        document.add_paragraph(text)
        content = io.BytesIO()
        document.save(content)
        return content.getvalue()

    def test_auth_and_dashboard_use_current_database_state(self):
        response = self.client.get("/career/dashboard", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total_resumes"], 0)
        self.assertIsNone(response.json()["career_matches"])
        self.assertEqual(self.client.get("/resumes").status_code, 401)

    def test_docx_upload_persists_resume_without_external_ai(self):
        content = self._docx_bytes("Python engineer with database and API experience.")
        with (
            patch("app.routers.resumes.index_resume_record", return_value={"status": "indexed"}),
            patch(
                "app.routers.resumes.analyze_resume_text",
                return_value={"status": "not_configured", "analysis": None},
            ),
        ):
            response = self.client.post(
                "/resumes/upload",
                headers=self.auth_headers,
                files={
                    "file": (
                        "resume.docx",
                        content,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
            )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["analysis_result"]["status"], "not_configured")
        resumes = self.client.get("/resumes", headers=self.auth_headers)
        self.assertEqual(resumes.status_code, 200, resumes.text)
        self.assertEqual(resumes.json()[0]["filename"], "resume.docx")

    def test_matching_uses_only_owned_resume(self):
        content = self._docx_bytes("Python engineer with database and API experience.")
        with (
            patch("app.routers.resumes.index_resume_record", return_value={"status": "indexed"}),
            patch(
                "app.routers.resumes.analyze_resume_text",
                return_value={"status": "not_configured", "analysis": None},
            ),
        ):
            uploaded = self.client.post(
                "/resumes/upload",
                headers=self.auth_headers,
                files={"file": ("resume.docx", content, "application/octet-stream")},
            )
        resume_id = uploaded.json()["resume_id"]
        result = {
            "match_score": 80,
            "strengths": ["Python"],
            "skill_gaps": [],
            "recommendation": "strong_match",
            "explanation": "Relevant experience is present.",
        }
        with patch("app.routers.matching.supervisor.route_task", return_value={"status": "complete", "result": result}):
            matched = self.client.post(
                "/matching/compare",
                headers=self.auth_headers,
                json={"resume_id": resume_id, "job_description": "A" * 60},
            )
        self.assertEqual(matched.status_code, 200, matched.text)
        self.assertEqual(matched.json()["match_score"], 80)

        other_token = self._register_and_login("other@example.test")
        hidden = self.client.post(
            "/matching/compare",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"resume_id": resume_id, "job_description": "A" * 60},
        )
        self.assertEqual(hidden.status_code, 404)

    def test_document_parser_rejects_corrupted_and_unsupported_files(self):
        with self.assertRaises(ValueError):
            extract_resume_text(b"not a document", "resume.pdf")
        with self.assertRaises(ValueError):
            extract_resume_text(b"content", "resume.txt")

    def test_cors_preflight_allows_default_frontend(self):
        response = self.client.options(
            "/auth/login",
            headers={
                "Origin": "http://localhost:5500",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:5500",
        )


if __name__ == "__main__":
    unittest.main()
