from fastapi import APIRouter, Depends, HTTPException, Body
from app.models.api_models.rules.discord import (
    DiscordRuleConfig,
    DiscordRuleOnSubmit,
    DiscordRuleTrigger,
)
from app.repositories.base import BaseRepository
from app.repositories.credentials_repository import CredentialsRepository
from app.repositories.rules import RulesRepository
from app.repositories.rule_logs import RuleLogsRepository
from app.core.config import settings
from app.utils.asana_utils import verify_app_request
from discord import Webhook
import aiohttp
from app.core.dependencies import get_current_user, get_repository
import json

router = APIRouter()


@router.get("/discord/send-message/metadata")
async def get_discord_config(
    action_type: str,
    expires_at: str,
    project: str,
    user: str,
    workspace: str,
    verify_app_request=Depends(verify_app_request),
    credentials_repository: CredentialsRepository = Depends(
        get_repository(CredentialsRepository)
    ),
):

    credential = await credentials_repository.get_credential_by_asana_user_id(
        asana_user_gid=user
    )

    if credential is None:

        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "template": "form_metadata_v0",
        "metadata": {
            "on_submit_callback": f"{settings.ASANA_WEBHOOK_URI}/rules/discord/send-message/on_submit",
            "on_change_callback": f"{settings.ASANA_WEBHOOK_URI}/rules/discord/send-message/on_change",
            "fields": [
                {
                    "type": "single_line_text",
                    "id": "discord_link",
                    "name": "Discord Webhook URL.",
                    "value": "",
                    "is_required": True,
                    "placeholder": "Webhook URL",
                    "width": "full",
                },
                {
                    "type": "multi_line_text",
                    "id": "content",
                    "name": "Content you want to send to discord.",
                    "value": "",
                    "is_required": True,
                    "placeholder": "Content",
                    "width": "full",
                },
            ],
        },
    }


@router.post("/discord/send-message/on_submit")
async def discord_on_submit(
    payload: dict = Body(...),
    rules_repository: RulesRepository = Depends(get_repository(RulesRepository)),
):

    ### Reshape Dict ###
    payload = json.loads(payload.get("data"))

    ### Check Discord URL is Valid ###

    if not "https://discord.com/api/webhooks" in payload["values"]["discord_link"]:

        raise HTTPException(status_code=400, detail="Invalid Discord Webhook URL")

    ### Check Exist with same Action ID ###

    rule = await rules_repository.get_rule_by_action_id(action_id=payload["action"])

    if rule is not None:

        await rules_repository.delete(rule["_id"])

    await rules_repository.create_rule(payload)

    return {
        "action_result": "ok",
        "error": "That resource no longer exists",
        "resources_created": [
            {
                "error": "No resource matched that input",
                "resource_name": "Build the Thing",
                "resource_url": "",
            }
        ],
    }


@router.post("/discord/send-message/action")
async def discord_trigger(
    payload: dict = Body(...),
    rules_repository: RulesRepository = Depends(get_repository(RulesRepository)),
    rule_logs_repository: RuleLogsRepository = Depends(
        get_repository(RuleLogsRepository)
    ),
):

    ### Check Trigger Handled Before ###
    payload = json.loads(payload.get("data"))
    rule_log_check = await rule_logs_repository.get_rule_log_by_a_idempotency_key(
        payload["idempotency_key"]
    )

    if rule_log_check is not None:

        return {
            "action_result": "ok",
            "error": "That resource no longer exists",
            "resources_created": [
                {
                    "error": "No resource matched that input",
                    "resource_name": "Build the Thing",
                    "resource_url": "",
                }
            ],
        }
    ### Get Rule Info ###

    rule = await rules_repository.get_rule_by_action_id(action_id=payload["action"])

    payload_dict = payload
    print(rule)

    if rule is None:

        raise HTTPException(status_code=404, detail="Rule Not Found")

    try:
        async with aiohttp.ClientSession() as session:

            webhook = Webhook.from_url(rule["values"]["discord_link"], session=session)

            await webhook.send(
                rule["values"]["content"],
                username="Asana Bot",
                avatar_url="https://avatars.slack-edge.com/2021-11-01/2672890963171_7010e3c61fd59a0e601c_512.png",
            )
            payload_dict["status"] = "Success"
            await rule_logs_repository.create_rule_log(payload_dict)
    except:

        payload_dict["status"] = "Failed"

        await rule_logs_repository.create_rule_log(payload_dict)

    return {
        "action_result": "ok",
        "error": "That resource no longer exists",
        "resources_created": [
            {
                "error": "No resource matched that input",
                "resource_name": "Build the Thing",
                "resource_url": "",
            }
        ],
    }
