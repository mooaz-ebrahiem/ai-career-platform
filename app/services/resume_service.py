import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Resume
from app.services.supervisor_agent import supervisor


logger = logging.getLogger(__name__)


def create_resume_record(
    db: Session,
    user_id: int,
    filename: str,
    extracted_text: str,
) -> Resume:
    resume = Resume(
        user_id=user_id,
        filename=filename,
        extracted_text=extracted_text,
    )
    db.add(resume)
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise RuntimeError("Resume could not be saved.") from error

    db.refresh(resume)
    return resume


def index_resume_record(resume: Resume) -> dict:
    try:
        result = supervisor.route_task(
            "index_resume",
            {"resume_id": str(resume.id), "resume_text": resume.extracted_text},
        )
        return result
    except Exception:
        logger.exception("Resume %s could not be indexed", resume.id)
        return {"status": "unavailable"}


def query_resume_record(resume_id: int, question: str) -> dict:
    return supervisor.route_task(
        "query_resume",
        {"resume_id": str(resume_id), "query": question},
    )
