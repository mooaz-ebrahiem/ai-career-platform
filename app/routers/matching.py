from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resume, User
from app.schemas import JobMatchRequest, JobMatchResponse
from app.services.supervisor_agent import supervisor
from app.utils.security import get_current_user


router = APIRouter(prefix="/matching", tags=["Job Matching"])


@router.post("/compare", response_model=JobMatchResponse)
def compare_resume_to_job(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == request.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    outcome = supervisor.route_task(
        "match_job",
        {
            "resume_text": resume.extracted_text,
            "job_description": request.job_description,
        },
    )
    if outcome["status"] == "not_configured":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job matching is not configured. Set HUGGINGFACE_TOKEN.",
        )
    if outcome["status"] != "complete":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job matching is temporarily unavailable.",
        )
    return outcome["result"]
