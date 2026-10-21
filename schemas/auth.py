from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class UserResponse(BaseModel):

    id: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):

    access_token: str
    token_type: str

class VerifyEmailRequest(BaseModel):
    email: str
    otp: str = Field(pattern=r"^\d{6}$")


class ResendOTPRequest(BaseModel):
    email: str