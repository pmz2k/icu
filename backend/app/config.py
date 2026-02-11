from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Security
    SECRET_SALT: str

    # Database
    DATABASE_URL: str = "sqlite:///./epr.db"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
