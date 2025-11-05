from fastapi import APIRouter, Depends
from app.core.dependencies import get_repository
from app.repositories.user_repository import UserRepository
from app.models import UserInDB, UserCreate
from typing import Any
from app.core import security


router = APIRouter()


@router.get("/get-user", response_model=UserInDB)
async def get_user_by_name(id: str):
    user = await UserRepository.get_by_id(id)
    return user


@router.post("/", response_model=UserInDB)
async def create_user(
    user: UserCreate,
):
    user_dict = user.dict()
    # düzelteceğim
    user_dict["password"] = security.get_password_hash(user_dict["password"])
    return await UserRepository.create(user_dict)
