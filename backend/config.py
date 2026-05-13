from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    BACKEND_URL: str = "http://localhost:8000"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
