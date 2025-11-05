# Need and endpoint getting code and exhange token with asana and save it to the database

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from fastapi import Response

from app.integrations.asana.asana import Asana
from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import CredentialsRepository
from app.models import UserCreateWithoutPassword, CredentialsBase
from app.core.dependencies import get_repository


router = APIRouter()


class AsanaAuthIn(BaseModel):
    code: str


@router.post("/auth/asana")
async def asana_auth(
    input: AsanaAuthIn,
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
    credential_repository: CredentialsRepository = Depends(
        get_repository(CredentialsRepository)
    ),
):

    asana = Asana()

    token = asana.token_exchange(code=input.code)

    user = await user_repository.get_by_email(email=token.data.email)

    if not user:
        user = await user_repository.create_user_without_password(
            user=UserCreateWithoutPassword(email=token.data.email)
        )

    await credential_repository.create_or_update_credential(
        CredentialsBase(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            platform="asana",
            user_id=str(user.id),
            expires_at=token.expires_at,
            extra_info=token.data,
        )
    )

    return Response(
        status_code=status.HTTP_200_OK, content="Asana authentication successful"
    )
