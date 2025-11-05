import ast
import secrets
from typing import List, Optional, Union
import os
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ASANA_REDIRECT_URL: AnyHttpUrl
    ASANA_CLIENT_ID: str
    ASANA_CLIENT_SECRET: str
    ASANA_WEBHOOK_URI: str
    ASANA_APP_REDIRECT_URL: str
    MONGO_URL: str
    MONGO_DB_NAME: str
    TEMPORAL_URL: str
    SENTRY_DSN: str
    TEMPORAL_API_KEY: str
    TEMPORAL_NAMESPACE: str
    TEMPORAL_ADDRESS: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:  # noqa
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (str)):
            return ast.literal_eval(v)
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        # env_file = ".env.local"

settings = Settings()