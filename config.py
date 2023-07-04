from pydantic import BaseSettings

class Settings(BaseSettings):
    jwt_secret_key: str
    user_email: str
    user_password: str

    class Config:
        env_file = ".env"

settings = Settings()
