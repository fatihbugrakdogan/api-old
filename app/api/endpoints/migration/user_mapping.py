from fastapi import APIRouter, Depends
from app.utils.get_provider_class import create_provider_client
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.models import UserInDB

router = APIRouter()


@router.get("/user-mapping")
async def get_user_mapping(
    source_provider: str,
    target_provider: str,
    source_token: str,
    target_token: str,
    source_workspace_id: str,
    target_workspace_id: str,
    user: UserInDB = Depends(get_current_user),
):

    source_provider = create_provider_client(source_provider, source_token)
    target_provider = create_provider_client(target_provider, target_token)

    source_users = source_provider.get_all_users(source_workspace_id)
    target_users = target_provider.get_all_users(target_workspace_id)

    for source_user in source_users:
        source_user["is_available"] = False
        for target_user in target_users:
            if source_user["email"] == target_user["email"]:
                source_user["is_available"] = True
                source_user["target_email"] = target_user["email"]

    user_mapping = [
        {
            "source_email": user["email"],
            "is_available": user["is_available"],
            "target_email": user.get("target_email", None),
        }
        for user in source_users
    ]

    return user_mapping


@router.get("/check-availability")
async def check_availability(
    target_provider: str,
    target_token: str,
    target_workspace_id: str,
    source_email: str,
):
    target_provider = create_provider_client(target_provider, target_token)

    is_available = target_provider.check_user_exists(target_workspace_id, source_email)

    return {
        "is_available": is_available,
        "source_email": source_email,
        "target_email": source_email,
    }
