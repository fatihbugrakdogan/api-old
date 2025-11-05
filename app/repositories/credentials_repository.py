from typing import Optional
from .base import BaseRepository
from app.models import CredentialInDB, CredentialsBase, CredentialByUserID
from app.core import security
from fastapi import HTTPException


class CredentialsRepository(BaseRepository):
    collection_name = "credentials"

    async def create_or_update_credential(self, credential: CredentialsBase):
        user_id = credential.user_id

        has_credential = await self.get_credential_by_user_id(user_id)

        if has_credential:
            collection = self.db[self.collection_name]

            credential_update = await collection.update_one(
                {"user_id": user_id},
                {"$set": credential.model_dump(mode="python")},
                upsert=True,
            )
            return credential_update

        return await self.create(item=credential.model_dump(mode="python"))

    async def get_credential_by_user_id(self, user_id: str):
        collection = self.db[self.collection_name]
        return await collection.find_one({"user_id": user_id})

    async def get_token_from_platform(self, platform, user_id: str):
        collection = self.db[self.collection_name]
        return await collection.find_one(
            {"user_id": user_id, "platform": platform}, {"_id": 0}
        )

    async def get_credential_by_asana_user_id(self, asana_user_gid: str):
        collection = self.db[self.collection_name]
        return await collection.find_one({"extra_info.gid": asana_user_gid})
