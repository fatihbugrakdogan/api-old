from temporalio import activity
from app.integrations.workino_client.workino_client import WorkinoClient
from app.integrations.asana import AsanaWithAccessToken as Asana
from app.core.config import settings


@activity.defn(name="Asana Section and Task are Creating...")
async def create_section_and_task(input):
    source_asana = Asana(input["source_workspace_token"])

    target_asana = Asana(input["target_workspace_token"])

    #### Check Configurations ####

    attachemts = False

    subtasks = False

    comments = False

    for configuration in input["configurations"]:
        if configuration == "attachments":
            attachemts = True
        elif configuration == "subtasks":
            subtasks = True
        elif configuration == "comments":
            comments = True

    source_sections = source_asana.get_sections_in_project(input["source_project_gid"])

    for source_section in source_sections:
        target_section = target_asana.create_section_in_project(
            input["target_project_gid"]["gid"], {"name": source_section["name"]}
        )

        source_tasks = source_asana.get_tasks_from_section(source_section["gid"])

        for source_task in source_tasks:
            source_task = source_asana.get_detail_of_task(source_task["gid"])

            try:
                target_task = target_asana.create_task(
                    {
                        "name": source_task["name"],
                        "projects": [input["target_project_gid"]["gid"]],
                        "notes": source_task["notes"],
                        "due_on": source_task["due_on"],
                        "completed": source_task["completed"],
                    }
                )

                target_asana.add_task_to_section(
                    target_section["gid"], target_task["gid"]
                )

            except:
                continue

            #### Check Subtask On
            if subtasks:
                try:
                    source_subtasks = source_asana.get_subtasks_of_a_task(
                        source_task["gid"]
                    )

                    for source_subtask in source_subtasks:
                        target_asana.create_subtask(
                            {
                                "name": source_subtask["name"],
                                "projects": [input["target_project_gid"]["gid"]],
                                "parent": target_task["gid"],
                            }
                        )
                except:
                    pass

            #### Check Attachments On
            if attachemts:
                try:
                    source_attachments = source_asana.get_attachments_from_task(
                        source_task["gid"]
                    )
                    for source_attachment in source_attachments:
                        detail_of_attachment = source_asana.get_an_attachment(
                            source_attachment["gid"]
                        )
                        if (
                            detail_of_attachment["resource_subtype"] == "asana"
                            or detail_of_attachment["resource_subtype"] == "external"
                        ):
                            target_asana.create_attachment(
                                target_task["gid"],
                                source_attachment["name"],
                                source_attachment["url"],
                            )
                except:
                    pass

            #### Check Comments On
            if comments:
                try:
                    source_stories = source_asana.get_stories_from_task(
                        source_task["gid"]
                    )
                    for source_story in source_stories:
                        if source_story["type"] == "comment":
                            formatted_text = f"{source_story['created_by']['name']} added a comment: \n\n {source_story['text']}"
                            target_asana.create_story(
                                target_task["gid"], {"text": formatted_text}
                            )
                except:
                    pass

    return "success"
