from pydantic import BaseModel
from typing import Optional, List, Dict


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
    tenant: str
    run_id: Optional[str] = None
