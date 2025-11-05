from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from app.utils.objectid import PydanticObjectId
from bson import ObjectId
from app.models.api_models.auth import AsanaUser


class CredentialsBase(BaseModel):
    platform: str
    access_token: str
    refresh_token: str
    scopes: Optional[str] = None
    expires_at: float
    user_id: str
    extra_info: Optional[AsanaUser] = None


class CredentialInDB(CredentialsBase):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CredentialByUserID(BaseModel):
    user_id: PydanticObjectId
