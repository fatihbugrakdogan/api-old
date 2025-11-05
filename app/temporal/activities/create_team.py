from temporalio import activity
from app.integrations.workino_client.workino_client import WorkinoClient
from app.integrations.asana import AsanaWithAccessToken as Asana
from app.core.config import settings
import secrets


@activity.defn(name="Asana Team is Creating...")
async def create_team(input):
    target_asana = Asana(input["target_workspace_token"])

    team = target_asana.create_team(
        {"name": secrets.token_hex(), "organization": input["organization_gid"]}
    )
    return team
