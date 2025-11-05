from pydantic import BaseModel, Field, EmailStr
from app.utils.objectid import PydanticObjectId
from bson import ObjectId
from typing import Optional


class AsanaAuthIn(BaseModel):
    code: str


class AsanaUser(BaseModel):
    email: EmailStr
    name: str
    gid: str


class AsanaTokenExchangeOut(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float
    data: AsanaUser


class RefreshToken(BaseModel):
    refresh_token: str


class GoogleTokenExchange(BaseModel):
    redirect_uri: str
    scopes: str
    auth_in: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    scope: Optional[str] = None


class Logout(BaseModel):
    refresh_token: str
    user_id: str
