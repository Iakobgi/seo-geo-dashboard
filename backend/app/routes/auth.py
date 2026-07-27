from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas, auth
from app.dependencies import get_current_user
from app.services.email_service import send_report_email
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(email=user.email, hashed_password=auth.get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/password-reset-request")
def request_password_reset(req: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset. Sends a reset link via email if the account exists."""
    user = db.query(models.User).filter(models.User.email == req.email).first()

    # Always return the same response, whether or not the user exists (avoid leaking account info)
    generic_response = {"message": "If an account exists for that email, a reset link has been sent."}

    if not user:
        return generic_response

    reset_token = auth.create_reset_token()
    user.password_reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    email_body = (
        f"Hi,\n\n"
        f"We received a request to reset your password for the SEO/GEO AI Dashboard.\n\n"
        f"Click the link below to set a new password (valid for 1 hour):\n"
        f"{reset_link}\n\n"
        f"If you didn't request this, you can safely ignore this email.\n"
    )
    sent = send_report_email(user.email, email_body, subject="Reset your password")

    if not sent:
        # SMTP not configured or failed — fall back to returning the token for dev/testing
        generic_response["token"] = reset_token
        generic_response["note"] = "SMTP not configured — returning token for dev/testing only."

    return generic_response


@router.post("/password-reset")
def reset_password(reset: schemas.PasswordReset, db: Session = Depends(get_db)):
    """Reset password using reset token."""
    user = db.query(models.User).filter(models.User.password_reset_token == reset.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if not user.reset_token_expires or auth.is_reset_token_expired(user.reset_token_expires):
        raise HTTPException(status_code=400, detail="Reset token expired")

    user.hashed_password = auth.get_password_hash(reset.new_password)
    user.password_reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successful"}


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
