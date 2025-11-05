from .base import BaseRepository


class RulesRepository(BaseRepository):
    collection_name = "rules"

    async def create_rule(self, rule):
        created_rule = await self.create(item=rule)
        return created_rule

    async def get_rule_by_action_id(self, action_id):
        rule = await self.db[self.collection_name].find_one({"action": action_id})
        return rule
