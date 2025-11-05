from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.utils.objectid import PydanticObjectId
from bson import ObjectId


### Workflow Models ###
class TaskIDWorkflowInput(BaseModel):
    user_id: str
    project_gid: str
    prefix: str
    webhook_key: str
    create_date: str
