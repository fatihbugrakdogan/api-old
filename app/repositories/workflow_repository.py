from .base import BaseRepository


class WorkflowRepository(BaseRepository):
    collection_name = "workflows"

    @classmethod
    async def create_workflow(cls, workflow):
        created_workflow = await cls.create(item=workflow)
        return created_workflow

    @classmethod
    async def get_workflow_by_user_id(cls, user_id):
        collection = cls.db[cls.collection_name]
        return await collection.find_one({"user_id": user_id})

    @classmethod
    async def get_workflow_by_webhook_key(cls, key):
        collection = cls.db[cls.collection_name]
        return await collection.find_one({"webhook.key": key})

    @classmethod
    async def update_workflow_increment_id(cls, key, increment):
        collection = cls.db[cls.collection_name]
        return await collection.update_one(
            {"webhook.key": key}, {"$set": {"last_increment": increment}}
        )
