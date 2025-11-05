from temporalio import activity
from app.repositories.user_repository import UserRepository


@activity.defn
async def get_user_by_id(user_id: str):
    user = await UserRepository().get_user_by_id(user_id)
    return user
