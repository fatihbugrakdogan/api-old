from temporalio.client import Client
from hashi.workflows.migrate_asana_to_asana import AsanaToAsanaMigration
from hashi.models.workflow.models import MigrationInput, Platform
import asyncio
import json

### Get test_dicts_json file ###

data = {
    "source": {
        "access_token": "2/1201999580693479/1207640855638587:e4409b0cabf7d482f34c90ed2eb50a4",
        "workspace_id": "1199881345422090",
        "platform_id": "asana",
    },
    "target": {
        "access_token": "2/1201999580693479/1207640855638587:e4409b0cabf7d482f34c90ed2eb50a4",
        "workspace_id": "1199881345422090",
        "platform_id": "asana",
    },
    "projects": ["1201999580693479"],
    "tenant": "test-tenant",
    "migration_id": "test-migration-123",
    "run_id": "test-run-123",
}


async def test():
    temporal_client = await Client.connect(
        target_host="http://viaduct.proxy.rlwy.net:56564",
        namespace="default",
        tls=False,
    )

    await temporal_client.start_workflow(
        AsanaToAsanaMigration.run,
        MigrationInput(
            tenant=data["tenant"],
            migration_id=data["migration_id"],
            run_id=data["run_id"],
            source=Platform(**data["source"]),
            target=Platform(**data["target"]),
            projects=data["projects"],
        ),
        id="test-asana-to-asana-migration",
        task_queue="main",
    )


### start with asyncio
asyncio.run(test())
