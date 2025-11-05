from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.utils.objectid import PydanticObjectId
from bson import ObjectId


class UserBase(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class UserInDB(UserBase):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(UserBase):
    pass


class UserCreateWithoutPassword(BaseModel):
    email: EmailStr


class UserWithoutPasswordInDB(UserCreateWithoutPassword):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
