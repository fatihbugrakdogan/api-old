from typing import Optional
from app.models import Template
from .base import BaseRepository
from fastapi import HTTPException


class TemplateRepository(BaseRepository):
    collection_name = "templates"

    @classmethod
    async def get_all_templates(cls):
        collection = cls.db[cls.collection_name]
        return await collection.find({"_id": 0})
