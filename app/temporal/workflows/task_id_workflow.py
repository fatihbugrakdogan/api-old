from datetime import timedelta, time, datetime
from temporalio import workflow, exceptions
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import *
    from app.models.temporal_models import TaskIDWorkflowInput
    from app.utils.task_id_workflow_formatter import format_task_id_workflow
    from app.repositories.user_repository import UserRepository
    from app.repositories.base import BaseRepository


@workflow.defn
class TaskIDWorkflow:
    @workflow.run
    async def run(self, input: TaskIDWorkflowInput) -> None:
        user = await workflow.execute_activity(
            get_user_by_id,
            input.user_id,
            start_to_close_timeout=timedelta(60),
        )
        print(user, "user")

        tasks = await workflow.execute_activity(
            get_asana_tasks,
            input,
            start_to_close_timeout=timedelta(60),
        )

        for id, task in enumerate(tasks):
            task_name: str = task.get("name")

            formatted_task_name = f"{input.prefix}-{id} | {task_name}"

            await workflow.execute_activity(
                add_id_to_task,
                {
                    "task_gid": task.get("gid"),
                    "name": formatted_task_name,
                    "user_id": input.user_id,
                    "webhook_key": input.webhook_key,
                },
                start_to_close_timeout=timedelta(60),
            )

        increment_id = len(list(tasks))
        formatted_workflow_data = format_task_id_workflow(
            increment_id=increment_id,
            user_id=input.user_id,
            project_gid=input.project_gid,
            prefix=input.prefix,
            email=user.get("email"),
            key=input.webhook_key,
            create_date=input.create_date,
        )
        await workflow.execute_activity(
            create_webhook,
            formatted_workflow_data,
            start_to_close_timeout=timedelta(60),
        )

        await workflow.execute_activity(
            create_workflow,
            formatted_workflow_data,
            start_to_close_timeout=timedelta(60),
        )


@workflow.defn
class TaskIDWebhookHandler:
    @workflow.run
    async def run(self, input):
        if not input["webhook_payload"]:
            print("no events")

            return "no events"

        for i, event in enumerate(input["webhook_payload"]):
            await workflow.execute_activity(
                handle_task_id_webhook,
                {"user_id": input["user_id"], "event": event, "key": input["key"]},
                start_to_close_timeout=timedelta(60),
            )

        return "success"
