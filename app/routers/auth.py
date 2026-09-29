from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, register_user as create_user
from app.utils.security import SecurityConfigurationError, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_data.email, user_data.password)


@router.post("/login", response_model=TokenResponse)
def login_user(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    try:
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
    except SecurityConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }