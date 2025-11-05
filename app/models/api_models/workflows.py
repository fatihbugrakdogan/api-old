from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List,Dict
from app.utils.objectid import PydanticObjectId
from bson import ObjectId


class TaskIDIn(BaseModel):
    prefix: str
    project_gid: str


class PlatformMigrationData(BaseModel):
    access_token: str
    workspace_id: str
    platform_id: str


class MigrationInfos(BaseModel):
    source: PlatformMigrationData
    target: PlatformMigrationData
    entities: List[str]
    project_ids: List[str]
    user_mappings: List[Dict]
