from fastapi import APIRouter, Query, Depends
from app.core.dependencies import get_current_user
from app.integrations.asana import AsanaWithAccessToken as Asana
from hashi.workflows.migrate_asana_to_asana import AsanaToAsanaMigration
from app.core.config import settings
from temporalio.client import Client
import secrets
import time

router = APIRouter()


@router.post("/confirm-pat-and-workspace")
async def check_pat_and_workspace(
    payload: dict,
):
    try:
        type = payload["type"] + "_"
        asana = Asana(payload[type + "personal_access_token"])

        projects = asana.get_multiple_projects(
            {"workspace": payload[type + "workspace_id"]}
        )

        projects_list = []

        for project in projects:
            projects_list.append(
                {
                    "name": project["name"],
                    "gid": project["gid"],
                    "resource_type": project["resource_type"],
                }
            )

        return True
    except:
        return False

    #### Create Project ####


@router.post("/migrate-asana-to-asana")
async def migrate_asana_to_asana(
    payload: dict,
):
    client = await Client.connect(settings.TEMPORAL_URL)

    key = secrets.token_hex(16)

    migration_workflow = await client.start_workflow(
        AsanaToAsanaMigration.run,
        payload,
        id=key,
        task_queue="tasks-queue",
    )

    return key


@router.post("/get-asana-projects")
async def get_projects(
    payload: dict,
):
    asana = Asana(payload["personal_access_token"])

    projects = asana.get_multiple_projects({"workspace": payload["workspace_id"]})

    projects_list = []

    for project in projects:
        projects_list.append(
            {
                "name": project["name"],
                "id": project["gid"],
            }
        )

    return projects_list
