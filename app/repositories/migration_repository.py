## Write Migration Repository


from .base import BaseRepository


class MigrationRepository(BaseRepository):
    collection_name = "migrations"

    async def create_migration_info(self, migration_info):
        created_rule = await self.create(item=migration_info)
        return created_rule

    async def get_migration_info_by_migration_id(self, migration_id: str):
        collection = self.db[self.collection_name]
        return await collection.find_one({"migration_id": migration_id})

    async def create_user_mapping(self, user_mappings,migration_id):
        user_mapping_collection = self.db["user_mappings"]
        user_mapping_dict = {}
        for user_mapping in user_mappings:
            user_mapping_dict[user_mapping.get("source_email")] = user_mapping.get("target_email")
        await user_mapping_collection.insert_one(user_mapping_dict)
        return user_mapping_dict

