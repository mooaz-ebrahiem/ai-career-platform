from typing import List, Literal

from pydantic import BaseModel, EmailStr, Field


# القالب اللي المستخدم هيبعته لما يسجل
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResumeQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class ResumeListItem(BaseModel):
    id: int
    filename: str


class JobMatchRequest(BaseModel):
    resume_id: int = Field(gt=0)
    job_description: str = Field(min_length=50, max_length=12000)


class JobMatchResponse(BaseModel):
    match_score: int = Field(ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    recommendation: Literal["strong_match", "potential_match", "weak_match"]
    explanation: str

class ResumeAnalysisResponse(BaseModel):
    full_name: str | None = None
    main_skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience_years: str = "Not specified"
    summary: str = ""
# القالب اللي هنرجعه للفرونت اند (بدون كلمة المرور لأسباب أمنية)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True