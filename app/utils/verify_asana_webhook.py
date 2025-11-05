from fastapi import Header, HTTPException, Query, Request
from typing import Optional
from app.repositories.listener_repository import ListenerRepository
from app.repositories.user_repository import UserRepository
import hashlib
import hmac

hook_secret = None


async def verify_webhook_request(
    request: Request,
    x_hook_secret: Optional[str] = Header(None),
    x_hook_signature: Optional[str] = Header(None),
    key: str = Query(default=None),
    email: str = Query(default=None),
):
    global hook_secret

    if x_hook_signature:
        body = await request.body()

        listener = await ListenerRepository().get_listener_by_key(key=key)

        signature = hmac.new(
            listener.get("secret").encode("ascii", "ignore"),
            msg=body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            signature.encode("ascii", "ignore"),
            x_hook_signature.encode("ascii", "ignore"),
        ):
            raise HTTPException(status_code=401)

        return await UserRepository().get_by_email(email=email)

    if x_hook_secret:
        """First contact with webhook target URL"""
        user = await UserRepository().get_by_email(email=email)
        listener = {"key": key, "secret": x_hook_secret, "user": str(user.id)}
        await ListenerRepository().create_listener(listener=listener)

        raise HTTPException(status_code=201, headers={"X-Hook-Secret": x_hook_secret})
