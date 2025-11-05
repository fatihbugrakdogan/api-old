import logging
from app.core.config import settings
import asana
from app.models import AsanaTokenExchangeOut, CredentialInDB
from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import (
    CredentialsBase,
    CredentialsRepository,
)
import asyncio
from app.repositories.base import BaseRepository

logging.getLogger("requests_oauthlib.oauth2_session").setLevel(logging.DEBUG)


def token_saver(response):
    # Parse the response to match AsanaTokenExchangeOut structure
    token_data = AsanaTokenExchangeOut(**response)
    BaseRepository().connect(
        database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL
    )

    async def fetch_user_and_save_token():
        # Fetch the user asynchronously
        user = await UserRepository.get_by_email(email=token_data.data.email)

        # Handle the case where the user is not found
        if not user:
            raise ValueError(f"User with email {token_data.data.email} not found")

        # Create or update the user's credentials
        await CredentialsRepository.create_or_update_credential(
            CredentialsBase(
                access_token=token_data.access_token,
                refresh_token=token_data.refresh_token,
                platform="asana",
                user_id=str(user.id),
                expires_at=token_data.expires_at,
                extra_info=token_data.data,
            )
        )

    # Check if there's an existing running loop in the current context
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # If there is a running loop, create a task in it
            loop.create_task(fetch_user_and_save_token())
        else:
            # If there's a loop but it's not running, run the coroutine
            loop.run_until_complete(fetch_user_and_save_token())
    except RuntimeError:
        # If no running loop, create a new event loop and run the coroutine
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(fetch_user_and_save_token())
        new_loop.close()


class Asana:
    def __init__(self, token=None) -> None:
        self.token = token
        self.client = self.get_client()

    def get_client(self):
        return asana.Client.oauth(
            token=self.token,
            client_id=settings.ASANA_CLIENT_ID,
            client_secret=settings.ASANA_CLIENT_SECRET,
            redirect_uri=settings.ASANA_REDIRECT_URL,
            auto_refresh_url="https://app.asana.com/-/oauth_token",
            auto_refresh_kwargs={
                "client_id": settings.ASANA_CLIENT_ID,
                "client_secret": settings.ASANA_CLIENT_SECRET,
            },
            token_updater=token_saver,
        )

    def token_exchange(self, code: str) -> AsanaTokenExchangeOut:
        response = self.client.session.fetch_token(code=code)
        return AsanaTokenExchangeOut(**response)

    def create_webhook(
        self,
        action,
        resource: str,
        resource_type,
        target_path: str,
        email: str,
        key: str,
        resource_subtype: str = None,
    ):
        print(f"{settings.ASANA_WEBHOOK_URI}/{target_path}?key={key}&email={email}")
        webhook = self.client.webhooks.create_webhook(
            {
                "filters": [
                    {"action": action, "resource_type": resource_type},
                ],
                "resource": resource,
                "target": f"{settings.ASANA_WEBHOOK_URI}/{target_path}?key={key}&email={email}",
            },
            opt_pretty=True,
        )

        return webhook

    def get_tasks_in_project(self, project_gid: str):
        return self.client.tasks.get_tasks_for_project(project_gid, opt_pretty=True)

    def get_task(self, task_gid: str):
        return self.client.tasks.get_task(task_gid, opt_pretty=True)

    def update_task(self, task_gid: str, data: dict):
        return self.client.tasks.update_task(task_gid, data, opt_pretty=True)

    def get_workspaces(self):
        return self.client.workspaces.get_workspaces(opt_pretty=True)

    def get_projects(self, workspace_gid: str):
        return self.client.projects.get_projects(
            {"workspace": workspace_gid}, opt_pretty=True
        )

    def get_webhooks(self, workspace):
        return self.client.webhooks.get_webhooks(
            {"workspace": workspace}, opt_pretty=True
        )

    def delete_webhook(self, webhook_gid):
        return self.client.webhooks.delete_webhook(webhook_gid, opt_pretty=True)

    def get_workspace_name(self, workspace_gid):
        return self.client.workspaces.get_workspace(workspace_gid).get("name")

    def get_project_url(self, project_gid):
        return self.client.projects.get_project(project_gid).get("permalink_url")
