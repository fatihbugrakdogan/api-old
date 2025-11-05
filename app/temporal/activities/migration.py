from temporalio import activity
import time
from app.models.api_models.workflows import MigrationInfos
from app.utils.get_provider_class import create_provider_client


@activity.defn
async def migration_activity(param: str) -> str:
    print(f"Migration activity triggered with param: {param}")
    time.sleep(30)
    return f"Activity completed with param: {param}"


@activity.defn
async def create_project(migration_infos: MigrationInfos):

    source_provider = create_provider_client(
        migration_infos.source.platform_id, migration_infos.source.access_token
    )

    target_provider = create_provider_client(
        migration_infos.target.platform_id, migration_infos.target.access_token
    )

    for project_id in migration_infos.project_ids:
        project = source_provider.get_project(project_id)
        print(f"Project {project_id} fetched from source provider")

    return "Projects created successfully"
