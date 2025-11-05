### Create repository for project

from .base import BaseRepository


class ProjectRepository(BaseRepository):
    collection_name = "projects"

    async def get_projects_by_migration_id(self, migration_id: str):
        collection = self.db[self.collection_name]
        return await collection.find({"migration_id": migration_id}).to_list(
            length=1000
        )
