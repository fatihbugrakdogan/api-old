from temporalio import activity
from app.integrations.workino_client.workino_client import WorkinoClient
from app.integrations.asana import Asana
import secrets
from app.core.config import settings


@activity.defn
async def create_webhook(workflow) -> list:
    token = await WorkinoClient(
        user_id=workflow.get("user_id"), api_key=settings.SECRET_KEY
    ).get_asana_tokens(user_id=workflow.get("user_id"))

    asana = Asana(token)

    webhook = asana.create_webhook(
        action=workflow["webhook"].get("action"),
        resource=workflow["webhook"].get("resource"),
        resource_type=workflow["webhook"].get("resource_type"),
        target_path=workflow["webhook"].get("target_path"),
        email=workflow["webhook"].get("email"),
        resource_subtype=workflow["webhook"].get("resource_subtype"),
        key=workflow["webhook"].get("key"),
    )

    return "success"
