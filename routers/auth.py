from fastapi import APIRouter, HTTPException, Depends

from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)

from services.auth_service import AuthService

from dependencies.auth import get_current_user

from services.otp_service import issue_otp, verify_otp
from schemas.auth import VerifyEmailRequest, ResendOTPRequest


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


auth_service = AuthService()


@router.post("/register", response_model=UserResponse)
def register(data: RegisterRequest):

    try:
        user = auth_service.register_user(
            data.email,
            data.password,
        )

        issue_otp(data.email)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "message": "Registration successful. Please check your email for the OTP.",
        "user": user,
    }



@router.post("/login",response_model=TokenResponse)
def login(data: LoginRequest):

    try:
        user = auth_service.authenticate_user(
            data.email,
            data.password
        )

    except ValueError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error)
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = auth_service.create_access_token(
        str(user["_id"])
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }



@router.get("/me",response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):

    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "role": current_user["role"]
    }


@router.post("/verify-email")
def verify_email(request: VerifyEmailRequest):
    verify_otp(request.email, request.otp)

    return {
        "message": "Email verified successfully. You can now log in."
    }


@router.post("/resend-otp")
def resend_otp(request: ResendOTPRequest):
    issue_otp(request.email)

    return {
        "message": "A new verification code has been sent."
    }