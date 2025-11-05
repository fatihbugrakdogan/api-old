from temporalio import activity
from app.integrations.workino_client.workino_client import WorkinoClient
from app.integrations.asana import Asana
from app.core.config import settings


@activity.defn
async def add_id_to_task(input) -> list:
    token = await WorkinoClient(
        user_id=input.get("user_id"), api_key=settings.SECRET_KEY
    ).get_asana_tokens(user_id=input.get("user_id"))

    asana = Asana(token)

    print(input)

    asana.update_task(input.get("task_gid"), {"name": input.get("name")})
