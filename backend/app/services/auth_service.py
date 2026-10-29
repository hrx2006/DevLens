from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import UserModel
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest
from app.core.security import hash_password, verify_password, validate_password_strength

class AuthService:
    @staticmethod
    def register_user(db: Session, reg_data: RegisterRequest) -> UserModel:
        if reg_data.password != reg_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match."
            )

        valid_pwd, msg = validate_password_strength(reg_data.password)
        if not valid_pwd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        # Check existing email
        normalized_email = reg_data.email.strip().lower()
        existing = db.query(UserModel).filter(UserModel.email == normalized_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists."
            )

        hashed = hash_password(reg_data.password)
        new_user = UserModel(
            email=normalized_email,
            full_name=reg_data.full_name.strip(),
            password_hash=hashed,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> UserModel:
        normalized_email = login_data.email.strip().lower()
        user = db.query(UserModel).filter(UserModel.email == normalized_email).first()
        
        # Generic authentication failure message prevents email enumeration
        invalid_credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

        if not user:
            # Perform dummy verification to mitigate timing attacks
            verify_password("dummy_password", "$argon2id$v=19$m=65536,t=2,p=1$dummy$dummy")
            raise invalid_credentials_exc

        if not verify_password(login_data.password, user.password_hash):
            raise invalid_credentials_exc

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is currently deactivated."
            )

        return user

    @staticmethod
    def change_password(db: Session, user: UserModel, pwd_data: ChangePasswordRequest) -> None:
        if not verify_password(pwd_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password entered is incorrect."
            )

        if pwd_data.new_password != pwd_data.confirm_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match."
            )

        valid_pwd, msg = validate_password_strength(pwd_data.new_password)
        if not valid_pwd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        user.password_hash = hash_password(pwd_data.new_password)
        db.commit()

auth_service = AuthService()
