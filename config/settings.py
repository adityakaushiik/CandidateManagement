from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # For Render
    PYTHON_VERSION: str = "3.12.10"

    # For Supabase
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""

    # For Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_AUTH_URL: str = ""
    GOOGLE_TOKEN_URL: str = ""
    GOOGLE_USER_INFO_URL: str = ""
    GOOGLE_REDIRECT_URL: str = ""

    # JWT
    JWT_SECRET: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"

    # For MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_NAME: str = "CandidateManagement"

    # Ignore extra env keys (e.g., legacy DATABASE_NAME) to avoid validation errors
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
