from fastapi import APIRouter, Query, Depends, Body, Request, Response
from temporalio.client import Client
from app.utils.verify_asana_webhook import verify_webhook_request
from app.utils.get_asana_client_from_listener import get_asana_client_from_listener
from app.core.dependencies import get_current_user
from app.repositories.workflow_repository import WorkflowRepository
from app.temporal.workflows.task_id_workflow import TaskIDWorkflow, TaskIDWebhookHandler
from app.models.temporal_models import TaskIDWorkflowInput
from app.models.api_models import TaskIDIn
import secrets
from app.core.security import settings
from app.integrations.asana import Asana
from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import CredentialsRepository
from app.repositories.base import BaseRepository
from datetime import datetime

router = APIRouter()


@router.post("/webhook")
async def task_id_webhook_reciever(
    request: Request,
):
    BaseRepository.connect(database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL)

    x_hook_secret = request.headers.get("X-Hook-Secret")

    if x_hook_secret:
        # Handshake isteği için 'X-Hook-Secret' ile yanıt ver
        return Response(status_code=200, headers={"X-Hook-Secret": x_hook_secret})

    key = request.query_params.get("key")

    email = request.query_params.get("email")

    if key is None or email is None:
        return "FAILED"

    user = await UserRepository.get_by_email(email)

    payload = await request.json()

    events = payload.get("events")

    client = await Client.connect(settings.TEMPORAL_URL)

    input = {"webhook_payload": events, "user_id": str(user.id), "key": key}

    webhook_handler = await client.start_workflow(
        TaskIDWebhookHandler.run, input, id=key, task_queue="tasks-queue"
    )

    return "SUCCESS"


@router.post("/create")
async def create_task_id_workflow(
    input: TaskIDIn,
    user=Depends(get_current_user),
):
    client = await Client.connect(settings.TEMPORAL_URL)

    key = secrets.token_hex(16)

    print(key)

    input = TaskIDWorkflowInput(
        project_gid=input.project_gid,
        prefix=input.prefix,
        user_id=str(user.id),
        webhook_key=key,
        create_date=str(datetime.now()),
    )

    task_id_workflow = await client.start_workflow(
        TaskIDWorkflow.run,
        input,
        id=key,
        task_queue="tasks-queue",
    )

    return key






















#### Test Purpose ####


@router.get("/delete-webhooks")
async def delete_webhooks(access_token):
    BaseRepository().connect(
        database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL
    )
    user = await UserRepository().get_by_email("fatih@omtera.com")
    credential = await CredentialsRepository().get_token_from_platform(
        platform="asana", user_id=str(user.id)
    )
    print(credential)
    asana = Asana(token=credential)
    webhooks = asana.get_webhooks(workspace="1199881345422090")
    for webhook in webhooks:
        print(webhook)
        asana.delete_webhook(webhook.get("gid"))
        print("deleted")
