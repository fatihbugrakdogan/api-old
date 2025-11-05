from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from app.models.api_models.migration import (
    MigrationTokenControl,
    MigrationItem,
    MigrationUserMappingRequest,
)
from app.utils.get_provider_class import create_provider_client
from app.repositories.migration_repository import MigrationRepository
from app.core.dependencies import get_repository
import json
from app.repositories.project_repository import ProjectRepository
from app.models.api_models.workflows import MigrationInfos
from hashi.workflows.migrate_asana_to_asana import AsanaToAsanaMigration
from hashi.models.workflow.models import MigrationInput, Platform
from uuid import uuid4
from datetime import datetime
from temporalio.client import Client
from app.integrations.sentry.sentry_config import sentry_config

router = APIRouter()


def get_platform_mappings():
    """Load and return platform mappings from JSON file"""
    with open("app/api/endpoints/ui/platform_mapping.json") as f:
        return json.load(f)


@router.options("/migration-sources")
async def options_migration_sources():
    """Handle preflight requests for migration-sources"""
    return {"message": "OK"}


@router.get("/migration-sources")
def get_migration_sources():
    """Get list of available migration source platforms"""
    mappings = get_platform_mappings()
    return list(mappings.get("platforms", {}).values())


@router.post("/migration-token-check")
async def migration_token_check(
    payload: MigrationTokenControl,
):
    try:
        """Validate migration platform access token"""
        provider = create_provider_client(payload.source_provider, payload.token)

        if provider.check_token():
            sentry_config.send_info_to_sentry("Token is valid", {"payload": payload})
            return {
                "status": "success",
                "message": "Token is valid",
                "data": {},
            }

        sentry_config.send_error_to_sentry("Token is not valid", {"payload": payload})
        print("Token is not valid")
        raise HTTPException(status_code=403, detail="Token is not valid")
    except Exception as e:
        sentry_config.send_error_to_sentry(
            "Error in migration token check", {"error": e}
        )
        print("Error in migration token check")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/migration-projects-csv")
def get_migration_projects_csv(
    token: str,
    source_provider: str,
    workspace_id: str,
):
    """Get projects for given workspace in CSV format"""
    provider = create_provider_client(source_provider, token)

    try:
        projects = provider.get_projects(workspace_id)
        sentry_config.send_info_to_sentry(
            "Projects fetched",
            {"workspace_id": workspace_id, "projects_count": len(projects)},
        )
    except Exception as e:
        sentry_config.send_error_to_sentry(
            "Error fetching projects", {"error": e, "workspace_id": workspace_id}
        )
    projects_for_csv = []
    for project in projects:

        projects_for_csv.append(
            {
                "name": project.get("name"),
                "gid": project.get("id"),
                "owner": project.get("owner"),
                "permalink_url": project.get("permalink_url"),
                "migrating": "no",
            }
        )
    return {
        "csv_data": projects_for_csv,
        "columns": ["name", "id", "owner", "permalink_url", "migrating"],
    }


@router.get("/get-current-user")
def get_current_user(
    token: str,
    source_provider: str,
):
    """Get current user"""
    provider = create_provider_client(source_provider, token)
    current_user = provider.get_current_user()

    return current_user.get("email")


@router.post("/migration-projects-csv-upload")
def migration_projects_csv_upload(csv_data: list[dict], columns: list[str]):
    ## Validate csv data has correct columns
    if columns != ["name", "id", "migrating"]:
        raise HTTPException(status_code=400, detail="Invalid columns")

    ## Validate csv data has correct data
    migrating_projects = []
    for row in csv_data:
        if row.get("migrating") == "yes" or row.get("migrating") == "Yes":
            migrating_projects.append(
                {"id": row.get("id"), "name": row.get("name"), "migrating": "yes"}
            )

    ## Validate csv data has unique ids
    return {
        "csv_data": migrating_projects,
        "columns": ["name", "id", "owner", "permalink_url", "migrating"],
    }


@router.post("/migration-user-mapping-csv")
def get_migration_user_mapping_csv(
    request: MigrationUserMappingRequest,
):
    """Get user mapping for given workspace in CSV format"""
    source_provider = create_provider_client(
        request.source_provider, request.source_token
    )
    target_provider = create_provider_client(
        request.target_provider, request.target_token
    )
    source_users = source_provider.get_all_users(request.source_workspace_id)
    # target_users = target_provider.get_all_users(request.target_workspace_id)
    user_mapping = []

    if request.rule.get("type") == "domain_changed":
        for source_user in source_users:
            if request.rule.get("source_domain") not in source_user.get("email"):
                continue
            target_user = source_user.get("email").split(
                request.rule.get("source_domain")
            )[0]
            target_user = target_user + request.rule.get("target_domain")
            check_user_exists = target_provider.check_user_exists(
                request.target_workspace_id, target_user
            )
            if check_user_exists and source_user.get("email"):
                user_mapping.append(
                    {
                        "source_email": source_user.get("email"),
                        "target_email": target_user,
                        "exists in target": "yes",
                        "migrating": "yes",
                    }
                )
            else:
                if source_user.get("email"):
                    user_mapping.append(
                        {
                            "source_email": source_user.get("email"),
                            "target_email": target_user,
                            "exists in target": "no",
                            "migrating": "no",
                        }
                    )

    elif request.rule.get("type") == "domain_same":
        for source_user in source_users:
            user_mail = source_user.get("email")
            check_user_exists = target_provider.check_user_exists(
                request.target_workspace_id, user_mail
            )
            if check_user_exists and source_user.get("email"):
                user_mapping.append(
                    {
                        "source_email": user_mail,
                        "target_email": user_mail,
                        "exists in target": "yes",
                        "migrating": "yes",
                    }
                )
            else:
                if source_user.get("email"):
                    user_mapping.append(
                        {
                            "source_email": user_mail,
                            "target_email": user_mail,
                            "exists in target": "no",
                            "migrating": "no",
                        }
                    )

    return {
        "csv_data": user_mapping,
        "columns": ["source_email", "target_email", "exists in target", "migrating"],
    }


@router.post("/migration-user-mapping-csv-upload")
def migration_user_mapping_csv_upload(csv_data: list[dict], columns: list[str]):
    # 1. Kolon sırası kontrolü
    expected_columns = ["source_email", "target_email", "exists in target", "migrating"]
    if columns != expected_columns:
        raise HTTPException(
            status_code=400, detail=f"Invalid columns. Expected: {expected_columns}"
        )

    # 3. "exists in target" ve "migrating" alanları sadece "yes" veya "no" olmalı
    for idx, row in enumerate(csv_data):
        for col in ["exists in target", "migrating"]:
            val = row.get(col, "").lower()
            if val not in ["yes", "no"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx+1}: '{col}' must be 'yes' or 'no', got '{row.get(col)}'",
                )

    # 4. Duplicate (tekrar eden) source_email kontrolü
    seen = set()
    for idx, row in enumerate(csv_data):
        email = row.get("source_email")
        if email in seen:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate source_email found: {email} (Row {idx+1})",
            )
        seen.add(email)

    # 5. (Opsiyonel) Tüm satırlar valid ise, mapping güncellemesi yapılabilir (örnek olarak sadece valid datayı döndürüyoruz)
    # Burada gerçek DB update işlemi eklenebilir.
    return {
        "csv_data": csv_data,
        "columns": expected_columns,
        "message": "CSV mapping uploaded and validated successfully.",
    }


@router.get("/migration-workspaces")
def get_migration_workspaces(
    token: str,
    source_provider: str,
):
    """Get workspaces for given platform and token"""
    try:
        provider = create_provider_client(source_provider, token)
        workspaces = provider.get_workspaces()
        sentry_config.send_info_to_sentry(
            "Workspaces fetched", {"source_provider": source_provider}
        )
        return workspaces
    except Exception as e:
        sentry_config.send_error_to_sentry(
            "Error fetching workspaces",
            {"error": e, "source_provider": source_provider},
        )
        raise HTTPException(status_code=500, detail="Could not fetch workspaces")


def migration_provider_class(migration_input: MigrationInfos):
    """Select appropriate migration workflow based on source platform - only supports Asana to Asana"""
    if (
        migration_input.source.platform_id == "asana"
        and migration_input.target.platform_id == "asana"
    ):
        return AsanaToAsanaMigration
    else:
        raise HTTPException(
            status_code=400, detail="Only Asana to Asana migration is supported"
        )


@router.post("/migration")
async def create_migration(
    migration_input: MigrationInfos,
    migration_repository: MigrationRepository = Depends(
        get_repository(MigrationRepository)
    ),
):
    """Create and start a new migration workflow"""
    migration_id = str(uuid4())

    ## upload user mapping to database
    await migration_repository.create_user_mapping(
        migration_input.user_mappings, migration_id
    )

    # Initialize temporal client and start workflow
    try:
        temporal_client = await Client.connect(
            namespace=settings.TEMPORAL_NAMESPACE,
            api_key=settings.TEMPORAL_API_KEY,
            tls=True,  # Simple TLS for Temporal Cloud
            target_host=settings.TEMPORAL_ADDRESS,
        )
        sentry_config.send_info_to_sentry(
            "Temporal client connected", {"temporal_client": temporal_client}
        )
    except Exception as e:
        sentry_config.send_error_to_sentry(
            "Error connecting to temporal client", {"error": e}
        )

    migration_type = migration_provider_class(migration_input)

    # Format input for hashi MigrationInput
    formatted_migration_input = MigrationInput(
        tenant=migration_input.tenant,
        migration_id=migration_id,
        run_id=migration_input.run_id or str(uuid4()),
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

    try:
        await temporal_client.start_workflow(
            migration_type.run,
            formatted_migration_input,
            id=migration_id,
            task_queue="hashi-task-queue",
        )
        sentry_config.send_info_to_sentry(
            "Migration started", {"migration_id": migration_id}
        )

        # Save migration info to database
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
        return {"id": migration_id}
    except Exception as e:
        sentry_config.send_error_to_sentry(
            "Error in migration creation",
            {
                "error": e,
                "migration_id": migration_id,
                "migration_input": migration_input,
            },
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/migration-items")
def get_migration_items(payload: MigrationItem):
    """Get available migration items"""
    try:
        mappings = get_platform_mappings()
        # sentry_config.send_info_to_sentry(
        #     "Migration items fetched", {"user_id": user.id}
        # )
        return list(mappings.get("platforms", {}).values())
    except Exception:
        # sentry_config.send_error_to_sentry(
        #     "Error fetching migration items", {"error": e, "user_id": user.id}
        # )
        raise HTTPException(status_code=500, detail="Could not fetch migration items")


# @router.get("/migration-projects")
# def get_migration_item_fields(
#     token: str,
#     source_provider: str,
#     workspace_id: str,
#     user: UserInDB = Depends(get_current_user),
# ):
#     """Get projects for given workspace"""
#     try:
#         provider = create_provider_client(source_provider, token)
#         projects = provider.get_projects(workspace_id)
#         sentry_config.send_info_to_sentry(
#             "Projects fetched",
#             {
#                 "source_provider": source_provider,
#                 "workspace_id": workspace_id,
#                 "user_id": user.id,
#                 "projects_count": len(projects),
#             },
#         )
#         return projects
#     except Exception as e:
#         sentry_config.send_error_to_sentry(
#             "Error fetching projects",
#             {
#                 "error": e,
#                 "source_provider": source_provider,
#                 "workspace_id": workspace_id,
#                 "user_id": user.id,
#             },
#         )
#         raise HTTPException(status_code=500, detail="Could not fetch projects")


@router.get("/migration-status")
async def get_migration_status(
    migration_id: str,
    project_repository: ProjectRepository = Depends(get_repository(ProjectRepository)),
    migration_repository: MigrationRepository = Depends(
        get_repository(MigrationRepository)
    ),
):
    """Get detailed migration status including all projects"""
    return await migration_repository.migration_status_page(migration_id)


# @router.get("/migration-runs")
# async def get_migration_runs(
#     migration_id: str,
#     migration_repository: MigrationRepository = Depends(
#         get_repository(MigrationRepository)
#     ),
#     user: UserInDB = Depends(get_current_user),
# ):
#     """Get migration runs"""
#     return await migration_repository.get_migration_runs(migration_id)


@router.get("/migration-projects")
async def get_migration_projects(
    migration_id: str,
    migration_repository: MigrationRepository = Depends(
        get_repository(MigrationRepository)
    ),
):
    """Get migration projects"""
    return await migration_repository.get_migration_project_details(migration_id)
