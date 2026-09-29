from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.utils.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str) -> User:
	existing_user = db.query(User).filter(User.email == email).first()
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email is already registered",
		)

	user = User(email=email, password_hash=hash_password(password), role="user")
	db.add(user)
	try:
		db.commit()
	except IntegrityError as error:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email is already registered",
		) from error

	db.refresh(user)
	return user


def authenticate_user(db: Session, email: str, password: str) -> User:
	user = db.query(User).filter(User.email == email).first()
	if not user or not verify_password(password, user.password_hash):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return user
