from bento import TemporalClient
from bento.workflows import AutoIncrementerWorkflowInitializer, MigrationWorkflow
from bento.dataclasses import MigrationInput, Platform
import asyncio
import json

### Get test_dicts_json file ###

data = {
    "source": {
        "access_token": "eyJ0dCI6InAiLCJhbGciOiJIUzI1NiIsInR2IjoiMSJ9.eyJkIjoie1wiYVwiOjE2MzgxODIsXCJpXCI6OTE2MzQ1NyxcImNcIjo0Njg3ODc1LFwidVwiOjIwMTE2MTIxLFwiclwiOlwiVVNcIixcInNcIjpbXCJXXCIsXCJGXCIsXCJJXCIsXCJVXCIsXCJLXCIsXCJDXCIsXCJEXCIsXCJNXCIsXCJBXCIsXCJMXCIsXCJQXCJdLFwielwiOltdLFwidFwiOjB9IiwiaWF0IjoxNzI0NjY3MjU1fQ.kpFRiFjjHva4O7w4jVQNvTaTtCuidwzwHGqQ2M5PTV4",
        "workspace_id": "IEABR7ZGI4PN7WMO",
        "platform_id": "wrike",
    },
    "target": {
        "access_token": "2/1201999580693479/1207640855638587:e4409b0cabf7d482f34c90ed2eb50a4",
        "workspace_id": "1199881345422090",
        "platform_id": "asana",
    },
    "entities": ["project"],
    "project_ids": ["IEABR7ZGI7777777"],
}


async def test():

    temporal_client = await TemporalClient(
        host="http://viaduct.proxy.rlwy.net:56564"
    ).get_client()

    await temporal_client.execute_workflow(
        MigrationWorkflow.run,
        MigrationInput(
            source=Platform(**data["source"]),
            target=Platform(**data["target"]),
            entities=["project"],
            project_ids=["IEABR7ZGI7777777"],
        ),
        id=str("AUTO_INCREMENTER_WORKFLOW2"),
        task_queue="test-queue",
    )


### start with asnycio
asyncio.run(test())
