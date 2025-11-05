from temporalio import activity
from app.integrations.workino_client.workino_client import WorkinoClient
from app.integrations.asana import AsanaWithAccessToken as Asana
from app.core.config import settings


@activity.defn(name="Asana Project is Creating...")
async def create_project_old_v(input):
    ### Create Project With Custom Fields ###

    source_asana = Asana(input["source_workspace_token"])

    target_asana = Asana(input["target_workspace_token"])

    source_project = source_asana.get_a_project(input["project_gid"])

    target_project = target_asana.create_project(
        {
            "name": source_project["name"],
            "workspace": input["target_workspace_gid"],
            "team": input["team_gid"],
            "notes": source_project["notes"],
        }
    )

    for custom_field in source_project["custom_fields"]:
        if custom_field["resource_subtype"] == "enum":
            custom_field_ = {
                "name": custom_field["name"],
                "type": "enum",
                "enum_options": custom_field["enum_options"],
            }

        elif custom_field["resource_subtype"] == "multi_enum":
            custom_field_ = {
                "name": custom_field["name"],
                "type": "multi_enum",
                "enum_options": custom_field["enum_options"],
            }

        elif custom_field["resource_subtype"] == "text":
            custom_field_ = {"name": custom_field["name"], "type": "text"}

        elif custom_field["resource_subtype"] == "number":
            custom_field_ = {
                "name": custom_field["name"],
                "type": "number",
                "precision": custom_field["precision"],
            }

        elif custom_field["resource_subtype"] == "date":
            custom_field_ = {"name": custom_field["name"], "type": "date"}

        elif custom_field["resource_subtype"] == "people":
            custom_field_ = {"name": custom_field["name"], "type": "people"}
        try:
            for remove_enabled in custom_field_["enum_options"]:
                remove_enabled.pop("enabled", None)
                remove_enabled.pop("gid", None)
        except:
            pass

        try:
            target_asana.add_custom_field_to_project(
                target_project["gid"], custom_field_
            )

        except:
            pass
    try:
        for custom_field in source_project["custom_field_settings"]:
            if custom_field["custom_field"]["resource_subtype"] == "enum":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "enum",
                    "enum_options": custom_field["custom_field"]["enum_options"],
                }

            elif custom_field["custom_field"]["resource_subtype"] == "multi_enum":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "multi_enum",
                    "enum_options": custom_field["custom_field"]["enum_options"],
                }

            elif custom_field["custom_field"]["resource_subtype"] == "text":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "text",
                }

            elif custom_field["custom_field"]["resource_subtype"] == "number":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "number",
                    "precision": custom_field["custom_field"]["precision"],
                }

            elif custom_field["custom_field"]["resource_subtype"] == "date":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "date",
                }

            elif custom_field["custom_field"]["resource_subtype"] == "people":
                custom_field_ = {
                    "name": custom_field["custom_field"]["name"],
                    "type": "people",
                }
            try:
                for remove_enabled in custom_field_["enum_options"]:
                    remove_enabled.pop("enabled", None)
                    remove_enabled.pop("gid", None)
            except:
                pass

            try:
                target_asana.add_custom_field_to_project(
                    target_project["gid"], custom_field_
                )
            except:
                pass
    except:
        pass

    return target_project
