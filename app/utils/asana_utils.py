from app.integrations.asana import Asana
from app.models import AsanaAuthIn
from app.repositories.user_repository import UserRepository, UserCreateWithoutPassword
from app.repositories.credentials_repository import (
    CredentialsRepository,
    CredentialsBase,
)
from app.repositories.base import BaseRepository
from app.core.config import settings
from app.core import security
from fastapi import Depends, Header, Request, HTTPException
import hashlib
import hmac
import json
from typing import Optional


async def handle_asana_auth(payload: AsanaAuthIn, marketplace: bool):

    asana = Asana(marketplace=marketplace)

    BaseRepository.connect(database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL)

    get_token_from_asana = asana.token_exchange(code=payload.code)

    email = get_token_from_asana.data.email

    user = await UserRepository().get_by_email(email=email)

    if not user:
        user = UserRepository().create_user_without_password(
            user=UserCreateWithoutPassword(email=email)
        )

    await CredentialsRepository.create_or_update_credential(
        CredentialsBase(
            access_token=get_token_from_asana.access_token,
            refresh_token=get_token_from_asana.refresh_token,
            platform="asana",
            user_id=str(user.id),
            expires_at=get_token_from_asana.expires_at,
            extra_info=get_token_from_asana.data,
        )
    )
    return {"user": user, "jwt": security.create_access_refresh_tokens(user_id=user.id)}


def verify_app_request(
    request: Request,
    x_asana_request_signature: Optional[str] = Header(None),
):
    print(request.query_params)
    if request.method == "GET":
        signature = hmac.new(
            key=settings.ASANA_CLIENT_SECRET.encode("ascii", "ignore"),
            msg=str(request.query_params).encode("ascii", "ignore"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    elif request.method == "POST":
        body = request.body()
        body = json.loads(body)
        body = body["data"]
        signature = hmac.new(
            key=settings.ASANA_CLIENT_SECRET.encode("ascii", "ignore"),
            msg=str(body).encode("ascii", "ignore"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    if not hmac.compare_digest(
        signature.encode("ascii", "ignore"),
        x_asana_request_signature.encode("ascii", "ignore"),
    ):
        raise HTTPException(status_code=403, detail="Could not verify your request")
