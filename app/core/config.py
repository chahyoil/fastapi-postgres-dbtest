from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    API_V1_STR: str
    DEBUG: bool
    DATABASE_URL: str = None

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / '.env'
        env_file_encoding = 'utf-8'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()