from fastapi import APIRouter, Depends
from app.models.api_models.workflows import MigrationInfos
from app.core.config import settings
from temporalio.client import Client
from bento.workflows import (
    SmartsheetToAsanaMigrationWorkflow,
    MondayToAsanaMigrationWorkflow,
    AsanaToAsanaMigrationWorkflow,
    WrikeToAsanaMigrationWorkflow,
    AirtableToAsanaMigrationWorkflow,
)
from temporalio.client import Client
from uuid import uuid4
from app.repositories.migration_repository import MigrationRepository
from app.core.dependencies import get_repository
from datetime import datetime
import os

router = APIRouter()


def select_migration_type(migration_input: MigrationInfos):
    if migration_input.source.platform_id == "monday":
        return MondayToAsanaMigrationWorkflow
    elif migration_input.source.platform_id == "asana":
        return AsanaToAsanaMigrationWorkflow
    elif migration_input.source.platform_id == "smartsheet":
        return SmartsheetToAsanaMigrationWorkflow
    elif migration_input.source.platform_id == "wrike":
        return WrikeToAsanaMigrationWorkflow
    elif migration_input.source.platform_id == "airtable":
        return AirtableToAsanaMigrationWorkflow


@router.post("/create-migration")
async def create_migration(
    migration_input: MigrationInfos,
    migration_repository: MigrationRepository = Depends(
        get_repository(MigrationRepository)
    ),
):

    ### Control Entities ###

    migration_id = str(uuid4())

    temporal_client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        api_key=os.getenv("TEMPORAL_API_KEY"),
        tls=True,  # Simple TLS for Temporal Cloud
    )

    migration_type = select_migration_type(migration_input)

    formatted_migration_input = {
        **migration_input.model_dump(by_alias=True),
        "migration_id": migration_id,
    }

    await temporal_client.start_workflow(
        migration_type.run,
        formatted_migration_input,
        id=migration_id,
        task_queue="main",
    )

    ### Save to DB ###

    await migration_repository.create_migration_info(
        {
            **migration_input.model_dump(by_alias=True),
            "migration_id": migration_id,
            "status": "pending",
            "created_at": datetime.now(),
            "source_platform_id": migration_input.source.platform_id,
            "target_platform_id": migration_input.target.platform_id,
        }
    )

    return migration_id
