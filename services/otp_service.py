import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException

from config.settings import settings
from database.mongodb import get_database
from services.email_service import send_otp_email


OTP_LIFETIME_SECONDS = 600  # 10 minutes
RESEND_COOLDOWN_SECONDS = 60  # 1 minute
MAX_ATTEMPTS = 5


def get_users_collection():
    return get_database()["users"]


def hash_otp(email: str, otp: str) -> str:
    message = f"{email.lower()}:{otp}".encode()

    return hmac.new(
        settings.otp_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def issue_otp(email: str) -> None:
    email = email.strip().lower()
    users = get_users_collection()

    user = users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    if user.get("email_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified.",
        )

    now = time.time()

    if now - user.get("otp_sent_at", 0) < RESEND_COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=429,
            detail="Please wait before requesting another OTP.",
        )

    otp = f"{secrets.randbelow(1_000_000):06d}"

    # Send email before storing its OTP hash.
    send_otp_email(email, otp)

    users.update_one(
        {"_id": user["_id"], "email_verified": {"$ne": True}},
        {
            "$set": {
                "otp_hash": hash_otp(email, otp),
                "otp_expires_at": now + OTP_LIFETIME_SECONDS,
                "otp_sent_at": now,
                "otp_attempts": 0,
            }
        },
    )


def verify_otp(email: str, otp: str) -> None:
    email = email.strip().lower()
    users = get_users_collection()

    user = users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or OTP.",
        )

    if user.get("email_verified", False):
        return

    if user.get("otp_attempts", 0) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Request a new OTP.",
        )

    expected_hash = user.get("otp_hash")
    expires_at = user.get("otp_expires_at", 0)

    if not expected_hash or time.time() >= expires_at:
        raise HTTPException(
            status_code=400,
            detail="OTP expired. Request a new one.",
        )

    supplied_hash = hash_otp(email, otp)

    if not hmac.compare_digest(expected_hash, supplied_hash):
        users.update_one(
            {"_id": user["_id"]},
            {"$inc": {"otp_attempts": 1}},
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid email or OTP.",
        )

    users.update_one(
        {"_id": user["_id"], "otp_hash": expected_hash},
        {
            "$set": {"email_verified": True},
            "$unset": {
                "otp_hash": "",
                "otp_expires_at": "",
                "otp_sent_at": "",
                "otp_attempts": "",
            },
        },
    )