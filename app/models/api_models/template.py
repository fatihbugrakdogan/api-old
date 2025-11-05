from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from app.utils.objectid import PydanticObjectId
from bson import ObjectId


class Template(BaseModel):
    name: str
    id: int
    description: str
    template_id: int
    type: str
    status: bool


class TemplateInDB(Template):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
