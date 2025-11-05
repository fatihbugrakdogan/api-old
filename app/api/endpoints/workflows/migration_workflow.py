from fastapi import APIRouter, Depends, HTTPException
from app.models.api_models.workflows import MigrationInfos
from app.core.config import settings
from temporalio.client import Client
from hashi.workflows.migrate_asana_to_asana import AsanaToAsanaMigration
from temporalio.client import Client
from uuid import uuid4
from app.repositories.migration_repository import MigrationRepository
from app.core.dependencies import get_repository
from datetime import datetime
import os

router = APIRouter()


def select_migration_type(migration_input: MigrationInfos):
    # Only support Asana to Asana migration with hashi
    if (
        migration_input.source.platform_id == "asana"
        and migration_input.target.platform_id == "asana"
    ):
        return AsanaToAsanaMigration
    else:
        raise HTTPException(
            status_code=400, detail="Only Asana to Asana migration is supported"
        )


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

    # Generate run_id if not provided
    run_id = migration_input.run_id or str(uuid4())

    # Format input for hashi MigrationInput
    from hashi.models.workflow.models import MigrationInput, Platform

    formatted_migration_input = MigrationInput(
        tenant=migration_input.tenant,
        migration_id=migration_id,
        run_id=run_id,
        source=Platform(
            access_token=migration_input.source.access_token,
            platform_id=migration_input.source.platform_id,
            workspace_id=migration_input.source.workspace_id,
        ),
        target=Platform(
            access_token=migration_input.target.access_token,
            platform_id=migration_input.target.platform_id,
            workspace_id=migration_input.target.workspace_id,
        ),
        projects=migration_input.project_ids,
    )

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
