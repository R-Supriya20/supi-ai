from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from bson import ObjectId

from config.settings import settings
from repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


user_repository = UserRepository()


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(token,
                             settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm]
                             )

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception


    try:
        user = user_repository.find_by_id(ObjectId(user_id))
    except Exception:
        raise credentials_exception

    if not user:
        raise credentials_exception

    return user


def require_admin(current_user=Depends(get_current_user)):

    if current_user["role"] != "admin":
        raise HTTPException(status_code=403,detail="Admin access required")
    return current_user