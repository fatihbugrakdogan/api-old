from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, TypeVar, Generic, List
from bson import ObjectId
from app.core.config import settings

T = TypeVar("T", bound=dict)  # Assuming you'll be dealing primarily with dictionaries.


class BaseRepository(Generic[T]):
    collection_name = None

    def __init__(self):
        self.client = None
        self.db = None

    async def __aenter__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.MONGO_DB_NAME]
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.client.close()

    async def get_all(self) -> List[T]:
        collection = self.db[self.collection_name]
        return await collection.find().to_list(length=100)

    async def get_by_id(self, item_id: str) -> Optional[T]:
        collection = self.db[self.collection_name]
        return await collection.find_one({"_id": ObjectId(item_id)})

    async def create(self, item: dict) -> T:
        collection = self.db[self.collection_name]
        result = await collection.insert_one(item)
        item["_id"] = result.inserted_id
        return item

    async def delete(self, item_id: str) -> bool:
        collection = self.db[self.collection_name]
        result = await collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0
