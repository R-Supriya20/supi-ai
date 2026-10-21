from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from jose import jwt
from bson import ObjectId

from config.settings import settings
from repositories.user_repository import UserRepository


password_hasher = PasswordHasher()

user_repository = UserRepository()


class AuthService:

    def register_user(
        self,
        email: str,
        password: str,
        email_verified: bool = False
    ):
        email = email.strip().lower()

        existing_user = user_repository.find_by_email(email)

        if existing_user:
            raise ValueError("User already exists")

        hashed_password = password_hasher.hash(password)

        user_data = {
            "email": email,
            "password": hashed_password,
            "role": "user",
            "email_verified": email_verified,
            "created_at": datetime.now(timezone.utc),
        }

        user_id = user_repository.create_user(user_data)

        return {
            "id": str(user_id),
            "email": email,
            "role": "user",
        }



    def authenticate_user(
        self,
        email: str,
        password: str
    ):
        user = user_repository.find_by_email(email)

        if not user:
            return None

        try:
            password_hasher.verify(
                user["password"],
                password
            )
        except Exception:
            return None

        # Check email verification
        if not user.get("email_verified", False):
            raise ValueError(
                "Please verify your email before logging in."
            )

        return user



    def create_access_token(
        self,
        user_id: str
    ):

        expire = (
            datetime.now(timezone.utc)
            + (
                timedelta(hours=settings.access_token_expire_hours)
                if settings.access_token_expire_hours is not None
                else timedelta(minutes=settings.access_token_expire_minutes)
            )
        )


        payload = {
            "sub": user_id,
            "exp": expire
        }


        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )


        return token