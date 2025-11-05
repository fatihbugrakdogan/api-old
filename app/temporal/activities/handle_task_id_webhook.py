from temporalio import activity
from app.repositories.credentials_repository import CredentialsRepository
from app.repositories.base import BaseRepository
from app.core.config import settings
from app.integrations.asana import Asana
from app.repositories.workflow_repository import WorkflowRepository


@activity.defn
async def handle_task_id_webhook(input):
    print(input)

    if (
        input["event"]["action"] == "added"
        and input["event"]["resource"]["resource_type"] == "task"
        and input["event"]["parent"]["resource_type"] == "project"
    ):
        print("Task added")

        ### Get Asana Credentials
        BaseRepository.connect(
            url=settings.MONGO_URL, database_name=settings.MONGO_DB_NAME
        )

        credential = await CredentialsRepository().get_token_from_platform(
            user_id=input["user_id"], platform="asana"
        )

        asana = Asana(credential)

        ### Get Task
        print(input["key"])
        workflow = await WorkflowRepository().get_workflow_by_webhook_key(input["key"])

        task = asana.get_task(input["event"]["resource"]["gid"])

        print(workflow, "workflow")

        ### Update Task

        new_task_name = (
            workflow["prefix"]
            + "-"
            + str(workflow["last_increment"])
            + " "
            + "|"
            + " "
            + task["name"]
        )

        asana.update_task(task["gid"], {"name": new_task_name})

        await WorkflowRepository().update_workflow_increment_id(
            input["key"], workflow["last_increment"] + 1
        )

    return "success"
