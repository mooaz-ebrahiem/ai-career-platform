from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume, User
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/career",
    tags=["Career & AI"]  # ده الاسم اللي هيظهر كقسم مستقل في الـ Swagger
)

@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": "أهلاً بك! لقد وصلت لهذا المسار المحمي بنجاح.",
        "user_email": current_user.email
    }


@router.get("/dashboard")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "status": "success",
        "user_email": current_user.email,
        "user_name": current_user.email.split("@")[0],
        "total_resumes": db.query(Resume).filter(Resume.user_id == current_user.id).count(),
        "career_matches": None,
        "resume_score": None,
        "ai_insights": [],
    }