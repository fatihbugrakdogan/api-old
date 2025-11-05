from .base import BaseRepository


class ListenerRepository(BaseRepository):
    collection_name = "listeners"

    @classmethod
    async def create_listener(cls, listener):
        created_listener = await cls.create(item=listener)
        return created_listener

    @classmethod
    async def get_listener_by_key(cls, key):
        collection = cls.db[cls.collection_name]
        return await collection.find_one({"key": key})
