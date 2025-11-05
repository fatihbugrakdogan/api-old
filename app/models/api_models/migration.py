from pydantic import BaseModel
from enum import Enum
from typing import List, Dict


class SourceProvider(str, Enum):
    wrike = "wrike"
    asana = "asana"
    monday = "monday"
    smartsheet = "smartsheet"
    airtable = "airtable"


class MigrationTokenControl(BaseModel):
    token: str
    source_provider: SourceProvider


class MigrationWorkspace(BaseModel):
    token: str
    source_provider: SourceProvider


class SourceInput(BaseModel):
    access_token: str
    provider: SourceProvider
    workspace_id: str


class TargetInput(BaseModel):
    access_token: str
    provider: SourceProvider
    workspace_id: str


class MigrationInput(BaseModel):
    source: SourceInput
    target: TargetInput
    entities: List[str]
    project_ids: List[str]


class MigrationItem(BaseModel):
    source_provider: SourceProvider


class MigrationProjects(BaseModel):
    token: str
    source_provider: SourceProvider


class MigrationUserMappingRequest(BaseModel):
    source_token: str
    source_provider: str
    source_workspace_id: str
    target_token: str
    target_provider: str
    target_workspace_id: str
    rule: Dict
