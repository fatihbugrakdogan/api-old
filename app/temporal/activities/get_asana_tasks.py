from temporalio import activity
import sys

from app.integrations.asana import Asana
from app.integrations.workino_client import WorkinoClient
from app.core.config import settings
from json import loads


@activity.defn
async def get_asana_tasks(input) -> list:
    tasks = []
    token = await WorkinoClient(
        user_id=input.get("user_id"), api_key=settings.SECRET_KEY
    ).get_asana_tokens(user_id=input.get("user_id"))
    asana = Asana(token)
    tasks_generator = asana.get_tasks_in_project(input.get("project_gid"))
    for task in tasks_generator:
        tasks.append(task)
    return tasks
