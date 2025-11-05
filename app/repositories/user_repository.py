from typing import Optional
from app.models import (
    UserInDB,
    UserBase,
    UserCreate,
    UserWithoutPasswordInDB,
    UserCreateWithoutPassword,
)
from .base import BaseRepository
from app.core import security
from bson import ObjectId
from fastapi import HTTPException


class UserRepository(BaseRepository):
    collection_name = "users"

    async def get_user_by_id(self, id: str):
        collection = self.db[self.collection_name]
        user = await collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
        return user

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        collection = self.db[self.collection_name]
        user = await collection.find_one({"email": email})
        if not user:
            return None
        return UserInDB(**user)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.get_by_email(email=email)
        if not user or not security.verify_password(
            plain_password=password, hashed_password=user.password
        ):
            return None
        return user

    async def create_user(self, user: UserCreate):
        user_in = user.dict()
        user_in["password"] = security.get_password_hash(user_in["password"])
        created_user = await self.create(item=user_in)
        return UserInDB(**created_user)

    async def check_user_previously_sign_up(self, email: str):
        is_user_already_sign_up = await self.get_by_email(email=email)
        if is_user_already_sign_up:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    async def create_user_without_password(self, user: UserCreateWithoutPassword):
        user_in = user.dict()
        created_user = await self.create(item=user_in)
        return UserWithoutPasswordInDB(**created_user)

    async def get_by_external_id(self, external_id: str) -> Optional[UserInDB]:
        """Get user by external ID (like Vercel user ID)"""
        collection = self.db[self.collection_name]
        user = await collection.find_one({"external_id": external_id})
        if not user:
            return None
        return UserInDB(**user)
