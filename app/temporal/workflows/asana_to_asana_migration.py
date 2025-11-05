from datetime import timedelta, time, datetime
from temporalio import workflow, exceptions
from temporalio.common import RetryPolicy


# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import *
    from app.utils.task_id_workflow_formatter import format_task_id_workflow
    from app.repositories.user_repository import UserRepository
    from app.repositories.base import BaseRepository


@workflow.defn(name="Asana to Asana Migration Workflow")
class AsanaToAsanaMigrationWorkflow:
    @workflow.run
    async def run(self, input) -> None:
        target_team = await workflow.execute_activity(
            create_team,
            {
                "target_workspace_token": input["target_personal_access_token"],
                "organization_gid": input["target_workspace_id"],
            },
            start_to_close_timeout=timedelta(60),
        )
        for source_project_gid in input["selected_projects"]:
            created_project = await workflow.execute_activity(
                create_project,
                {
                    "source_workspace_token": input["source_personal_access_token"],
                    "target_workspace_token": input["target_personal_access_token"],
                    "project_gid": source_project_gid["id"],
                    "target_workspace_gid": input["target_workspace_id"],
                    "team_gid": target_team["gid"],
                },
                start_to_close_timeout=timedelta(60),
            )

            create_section_and_tasks = await workflow.execute_activity(
                create_section_and_task,
                {
                    "source_workspace_token": input["source_personal_access_token"],
                    "target_workspace_token": input["target_personal_access_token"],
                    "source_project_gid": source_project_gid["id"],
                    "target_workspace_gid": input["target_workspace_id"],
                    "team_gid": target_team["gid"],
                    "target_project_gid": created_project,
                    "configurations": input["configurations"],
                },
                start_to_close_timeout=timedelta(600),
            )
