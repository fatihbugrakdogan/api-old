from app.integrations.asana import Asana
from app.repositories.credentials_repository import CredentialsRepository


async def get_asana_client_from_listener(user_id):
    token = await CredentialsRepository().get_token_from_platform(
        user_id=user_id, platform="asana"
    )
    asana = Asana(token=token)
    asana = await asana.initialize()
    return asana
