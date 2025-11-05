from datetime import timedelta
from temporalio import workflow
from app.models.api_models.workflows import MigrationInfos

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import *


@workflow.defn
class MigrationWorkflow:
    @workflow.run
    async def run(self, param: MigrationInfos) -> str:
        # Activity çağırma
        result = await workflow.execute_activity(
            create_project, param, start_to_close_timeout=timedelta(seconds=30)
        )

        print(f"Activity result: {result}")

        # Sleep ekleme (bekleme işlemi)
        print("Migration workflow slept for 10 seconds")

        return f"Workflow completed: {result}"
