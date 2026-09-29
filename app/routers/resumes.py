from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume, User
from app.utils.security import get_current_user
from app.services.resume_parser import MAX_RESUME_SIZE_BYTES, extract_resume_text
from app.schemas import ResumeListItem, ResumeQuestionRequest
from app.services.resume_service import (
    create_resume_record,
    index_resume_record,
    query_resume_record,
)
from app.agents.resume_analyzer import analyze_resume_text

router = APIRouter(
    prefix="/resumes",
    tags=["Resume Analyzer & AI"]
)


@router.get("", response_model=list[ResumeListItem])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.id.desc())
        .all()
    )

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = (file.filename or "").replace("\\", "/").rsplit("/", maxsplit=1)[-1]
    if not filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    content = await file.read(MAX_RESUME_SIZE_BYTES + 1)
    try:
        resume_text = extract_resume_text(content, filename)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    try:
        resume = create_resume_record(db, current_user.id, filename, resume_text)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume could not be saved.",
        ) from error

    indexing = index_resume_record(resume)
    analysis = analyze_resume_text(resume_text)
    
    return {
        "status": "success",
        "message": "Resume uploaded and processed.",
        "resume_id": resume.id,
        "filename": resume.filename,
        "uploaded_by": current_user.email,
        "analysis_result": analysis,
        "indexing": indexing,
    }


@router.post("/{resume_id}/query")
def query_resume(
    resume_id: int,
    request: ResumeQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    result = query_resume_record(resume.id, request.question)
    return {"resume_id": resume.id, **result}