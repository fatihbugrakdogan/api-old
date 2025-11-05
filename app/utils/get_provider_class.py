from app.integrations.asana.asana_class_with_access_token import (
    AsanaWithAccessToken as Asana,
)
from app.integrations.wrike.wrike import WrikeHandler
from app.integrations.monday.monday_client import Monday
from app.models.api_models.migration import SourceProvider
from app.integrations.smartsheet.smartsheet_cli import SmartsheetClient
from app.integrations.airtable.airtable_cli import AirtableClient


PROVIDER_MAP = {
    SourceProvider.asana: Asana,
    SourceProvider.wrike: WrikeHandler,
    SourceProvider.monday: Monday,
    SourceProvider.smartsheet: SmartsheetClient,
    SourceProvider.airtable: AirtableClient,
}


class UnsupportedProviderError(Exception):
    pass


def create_provider_client(provider, token):
    provider_class = PROVIDER_MAP.get(provider)
    if provider_class:
        return provider_class(token)
    raise UnsupportedProviderError(f"Provider {provider} is not supported.")
