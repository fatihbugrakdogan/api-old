from .base import BaseRepository


class RuleLogsRepository(BaseRepository):
    collection_name = "rule_logs"

    async def create_rule_log(self, rule):
        created_rule = await self.create(item=rule)
        return created_rule

    async def get_rule_log_by_a_idempotency_key(self, idempotency_key):
        rule = await self.db[self.collection_name].find_one(
            {"data.idempotency_key": idempotency_key}
        )
        return rule
