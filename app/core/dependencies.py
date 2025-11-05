from fastapi import Depends, HTTPException, status, Request
from app.repositories.user_repository import UserRepository
from app.models import UserCreate, TokenPayload
from app.models.api_models.users import UserInDB
from fastapi.security import OAuth2PasswordBearer
from app.core import security
from app.core.config import settings
from jose import jwt
from app.repositories.credentials_repository import CredentialsRepository
from app.integrations.asana import Asana
from app.repositories.base import BaseRepository
from app.models.api_models.rules.discord import DiscordRuleOnSubmit
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_repository(repo_class):
    async def _get_repo():
        repo = repo_class()
        async with repo:
            yield repo

    return _get_repo


def get_token_from_cookie(request: Request) -> str:

    print("request", request.cookies)
    token = request.cookies.get("auth-token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No auth token found in cookies.",
        )
    return token


async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)  # parse token sub, exp, etc.
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired."
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    user = await user_repository.get_by_id(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserInDB(**user)


async def get_asana_client_in_password_flow(user=Depends(get_current_user)):
    token = await CredentialsRepository().get_token_from_platform(
        user_id=str(user.id), platform="asana"
    )

    return Asana(
        token={
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_at": token["expires_at"],
        }
    )
