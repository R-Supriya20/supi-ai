from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    app_name: str = "AI Customer Support Backend"
    debug: bool = True

    mongo_uri: str
    database_name: str = "customer_support"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    access_token_expire_hours: int | None = None

    gemini_api_key: str

    gmail_address: str
    gmail_app_password: str
    otp_secret: str

    class Config:
        env_file = ".env"


settings = Settings()