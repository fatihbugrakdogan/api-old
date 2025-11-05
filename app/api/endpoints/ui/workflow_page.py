from fastapi import APIRouter, Query, Depends
from app.repositories.template_repository import TemplateRepository
from app.models.api_models import Template
from typing import List
from app.core.dependencies import get_asana_client_in_password_flow
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.base import BaseRepository
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.integrations.sentry.sentry_config import sentry_config

router = APIRouter()


@router.get("/workspaces")
def get_workspaces_from_asana(
    asana=Depends(get_asana_client_in_password_flow),
):
    data = []
    try:
        workspaces = asana.get_workspaces()
        sentry_config.send_info_to_sentry("Workspaces fetched", {"workspaces": workspaces})
    except Exception as e:
        sentry_config.send_error_to_sentry("Error fetching workspaces", {"error": e})

    for workspace in workspaces:
        data.append(workspace)

    return data


@router.get("/projects")
def get_projects_from_asana(
    workspace_gid: str,
    asana=Depends(get_asana_client_in_password_flow),
):
    try:
        data = []
        projects = asana.get_projects(workspace_gid=workspace_gid)
        sentry_config.send_info_to_sentry("Projects fetched", {"workspace_gid": workspace_gid, "projects_count": len(projects)})
    except Exception as e:
        sentry_config.send_error_to_sentry("Error fetching projects", {"error": e, "workspace_gid": workspace_gid})

    for project in projects:
        data.append(
            {
                "name": project["name"],
                "gid": project["gid"],
                "resource_type": project["resource_type"],
            }
        )

    return data


@router.get("/workflows")
async def get_created_workflows(user=Depends(get_current_user)):
    BaseRepository.connect(settings.MONGO_URL, settings.MONGO_DB_NAME)
    print(user.id, "user")
    try:
        workflow = await WorkflowRepository().get_workflow_by_user_id(str(user.id))
        sentry_config.send_info_to_sentry("Workflows fetched", {"user_id": user.id, "workflow": workflow})
    except Exception as e:
        sentry_config.send_error_to_sentry("Error fetching workflows", {"error": e, "user_id": user.id})
    print(workflow)
    if workflow:
        workflow.pop("_id")
        return [workflow]
    return []


@router.post("/check-credit")
def get_credit(template: dict):
    return False
