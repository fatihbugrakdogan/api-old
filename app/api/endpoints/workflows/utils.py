# from fastapi import APIRouter
# from app.repositories.base import BaseRepository
# from app.repositories.workflow_repository import WorkflowRepository
# from tests.asana_test_infos import *
# from app.integrations.asana import AsanaWithAccessToken as Asana

# from app.core.config import settings


# router = APIRouter()


# ### Delete Workflow From DB and Delete Webhook ###


# @router.post("/delete-workflow-and-webhook")
# async def delete_workflow_and_webhook(key: str):
#     await BaseRepository().connect(
#         database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL
#     )
#     workflow_info = await WorkflowRepository().get_workflow_by_webhook_key()
#     await WorkflowRepository().delete(workflow_info["_id"])
#     asana = Asana(access_token=access_token_1)
#     asana.delete_webhook(webhook_id=workflow_info.get("webhook_id"))
