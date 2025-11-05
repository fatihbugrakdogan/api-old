# from app.repositories.credentials_repository import CredentialsRepository
# from app.repositories.user_repository import UserRepository
# from app.repositories.base import BaseRepository
# from app.repositories.workflow_repository import WorkflowRepository
# from app.repositories.rule_logs import RuleLogsRepository
# from app.repositories.rules import RulesRepository
# from app.repositories.listener_repository import ListenerRepository
# from app.repositories.template_repository import TemplateRepository
# from app.models.api_models import CredentialsBase, UserCreateWithoutPassword, UserCreate
# import pytest
# from app.core.config import settings


# @pytest.mark.asyncio
# async def test_repostories():

#     start_db = BaseRepository.connect(
#         database_name=settings.MONGO_DB_NAME, url=settings.MONGO_URL
#     )

#     ### User Repository ###

#     user_without_password = await UserRepository().create_user_without_password(
#         user=UserCreateWithoutPassword(
#             email="fatih@omter.com",
#         )
#     )

#     assert user_without_password.email, "failed"

#     user_with_password = await UserRepository().create_user(
#         user=UserCreate(
#             email="fatih@omter.com",
#             password="password",
#         )
#     )

#     assert user_with_password.email, "failed"

#     user_info = await UserRepository().get_by_email("fatih@omter.com")

#     assert user_info.email, "failed"

#     user_id = await UserRepository().get_user_by_id(user_info.id)

#     assert user_id, "failed"

#     ### Delete Crete User ###

#     await UserRepository().delete(user_with_password.id)

#     assert "Silindi", "failed"

#     await UserRepository().delete(user_without_password.id)

#     assert "Silindi", "failed"

#     ### Credential Repository ###

#     credential = await CredentialsRepository().create_or_update_credential(
#         {
#             "access_token": "access_token",
#             "refresh_token": "refresh_token",
#             "platform": "platform",
#             "user_id": "user_id",
#             "expires_at": 1212,
#             "extra_info": {
#                 "gid": "asana_user_id",
#                 "email": "fatih@omter.com",
#                 "name": "name",
#             },
#         }
#     )

#     assert credential["access_token"], "failed"

#     credential_info = await CredentialsRepository().get_credential_by_user_id("user_id")

#     assert credential_info["access_token"], "failed"

#     token_info = await CredentialsRepository().get_token_from_platform(
#         "platform", "user_id"
#     )

#     assert token_info["access_token"], "failed"

#     # asana_user = await CredentialsRepository().get_credential_by_asana_user_id(
#     #     "asana_user_id"
#     # )

#     # assert asana_user["access_token"], "failed"

#     ### Delete Credential ###

#     await CredentialsRepository().delete(credential["_id"])

#     assert "Silindi", "failed"

#     ### Rules Repository ###

#     rule = await RulesRepository().create_rule(
#         {
#             "data": {
#                 "action": "action",
#                 "rule": "rule",
#                 "user_id": "user_id",
#                 "status": "status",
#             }
#         }
#     )

#     assert rule, "failed"

#     rule_info = await RulesRepository().get_rule_by_action_id("action")

#     assert rule_info, "failed"

#     ### Delete Rule ###

#     await RulesRepository().delete(rule["_id"])

#     ### Rule Logs Repository ###

#     rule_log = await RuleLogsRepository().create_rule_log(
#         {
#             "data": {
#                 "action": "action",
#                 "rule": "rule",
#                 "user_id": "user_id",
#                 "status": "status",
#                 "idempotency_key": "idempotency_key",
#             }
#         }
#     )

#     assert rule_log, "failed"

#     rule_log_info = await RuleLogsRepository().get_rule_log_by_a_idempotency_key(
#         "idempotency_key"
#     )

#     assert rule_log_info, "failed"

#     ### Delete Rule Log ###

#     await RuleLogsRepository().delete(rule_log["_id"])

#     ### Listener Repository ###

#     ### Şimdilik Eklenmedi ###

#     ### Template Repository ###

#     ## Şimdilik Eklenmedi ##

#     # template = await TemplateRepository().get_all_templates()

#     # assert template, "failed"

#     ### Workflow Repository ###

#     workflow = await WorkflowRepository().create_workflow(
#         {
#             "name": "name",
#             "user_id": "user_id",
#             "status": "status",
#             "webhook": {
#                 "key": "key",
#             },
#             "last_increment": 0,
#         }
#     )

#     assert workflow["name"], "failed"

#     workflow_info = await WorkflowRepository().get_workflow_by_user_id("user_id")

#     assert workflow_info["name"], "failed"

#     workflow_key = await WorkflowRepository().get_workflow_by_webhook_key("key")

#     assert workflow_key["name"], "failed"

#     workflow_increment = await WorkflowRepository().update_workflow_increment_id(
#         "key", 1
#     )

#     assert workflow_increment, "failed"

#     ### Delete Workflow ###

#     await WorkflowRepository().delete(workflow["_id"])

#     assert "Silindi", "failed"
