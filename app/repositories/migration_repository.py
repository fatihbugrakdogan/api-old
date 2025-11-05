## Write Migration Repository


from .base import BaseRepository
from datetime import datetime
from app.utils.get_provider_class import create_provider_client


class MigrationRepository(BaseRepository):
    collection_name = "migrations"

    async def create_migration_info(self, migration_info):
        created_rule = await self.create(item=migration_info)
        return created_rule

    async def get_migration_info_by_migration_id(self, migration_id: str):
        collection = self.db[self.collection_name]
        return await collection.find_one({"migration_id": migration_id})

    async def create_user_mapping(self, user_mappings, migration_id):
        user_mapping_collection = self.db["user_mappings"]
        user_mapping_dict = {"migration_id": migration_id}
        for user_mapping in user_mappings:
            user_mapping_dict[user_mapping.get("source_email")] = user_mapping.get(
                "target_email"
            )
        await user_mapping_collection.insert_one(user_mapping_dict)
        return user_mapping_dict

    ## Status Page
    async def migration_status_page(self, migration_id: str):
        ledger_collection = self.db["ledger_records"]
        migration_collection = self.db["migrations"]
        portfolios = await ledger_collection.find(
            {"migration_id": migration_id, "source.kind": "portfolio"}
        ).to_list(length=1000)
        teams = await ledger_collection.find(
            {"migration_id": migration_id, "source.kind": "team"}
        ).to_list(length=1000)
        projects = await ledger_collection.find(
            {"migration_id": migration_id, "source.kind": "project"}
        ).to_list(length=1000)

        migration_info = await migration_collection.find_one(
            {"migration_id": migration_id}
        )
        source_provider = create_provider_client(
            migration_info.get("source", {}).get("platform_id"),
            migration_info.get("source", {}).get("access_token"),
        )
        target_provider = create_provider_client(
            migration_info.get("target", {}).get("platform_id"),
            migration_info.get("target", {}).get("access_token"),
        )

        ## Structure data to display on status page
        portfolio_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }
        for portfolio in portfolios:
            if portfolio.get("status") == "created":
                portfolio_metrics["created"] += 1
            elif portfolio.get("status") == "skipped":
                portfolio_metrics["skipped"] += 1
            elif portfolio.get("status") == "failed":
                portfolio_metrics["failed"] += 1
            elif portfolio.get("status") == "pending":
                portfolio_metrics["pending"] += 1

        team_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }
        for team in teams:
            if team.get("status") == "created":
                team_metrics["created"] += 1
            elif team.get("status") == "skipped":
                team_metrics["skipped"] += 1
            elif team.get("status") == "failed":
                team_metrics["failed"] += 1
            elif team.get("status") == "pending":
                team_metrics["pending"] += 1

        project_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }
        for project in projects:
            if project.get("status") == "created":
                project_metrics["created"] += 1
            elif project.get("status") == "skipped":
                project_metrics["skipped"] += 1
            elif project.get("status") == "failed":
                project_metrics["failed"] += 1
            elif project.get("status") == "pending":
                project_metrics["pending"] += 1

        task_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }
        comment_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }
        attachment_metrics = {
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "pending": 0,
            "status": "pending",
            "progress": 0,
        }

        for project in projects:
            task_metrics_dict = (
                project.get("rollup", {}).get("entities", {}).get("task", {})
            )
            task_metrics["pending"] += task_metrics_dict.get("pending", 0)
            task_metrics["created"] += task_metrics_dict.get("created", 0)
            task_metrics["skipped"] += task_metrics_dict.get("skipped", 0)
            task_metrics["failed"] += task_metrics_dict.get("failed", 0)
            task_metrics["progress"] += task_metrics_dict.get("success_rate", 0)

            comment_metrics_dict = (
                project.get("rollup", {}).get("entities", {}).get("comment", {})
            )
            comment_metrics["pending"] += comment_metrics_dict.get("pending", 0)
            comment_metrics["created"] += comment_metrics_dict.get("created", 0)
            comment_metrics["skipped"] += comment_metrics_dict.get("skipped", 0)
            comment_metrics["failed"] += comment_metrics_dict.get("failed", 0)
            comment_metrics["progress"] += comment_metrics_dict.get("success_rate", 0)

            attachment_metrics_dict = (
                project.get("rollup", {}).get("entities", {}).get("attachment", {})
            )
            attachment_metrics["pending"] += attachment_metrics_dict.get("pending", 0)
            attachment_metrics["created"] += attachment_metrics_dict.get("created", 0)
            attachment_metrics["skipped"] += attachment_metrics_dict.get("skipped", 0)
            attachment_metrics["failed"] += attachment_metrics_dict.get("failed", 0)
            attachment_metrics["progress"] += attachment_metrics_dict.get(
                "success_rate", 0
            )

        # Calculate totals and progress percentages
        def calculate_progress(created, total):
            return (created / max(total, 1)) * 100 if total > 0 else 0

        return {
            "migration_id": migration_id,
            "migration_name": f"{source_provider.get_workspace_name(migration_info.get('source', {}).get('workspace_id'))} → {target_provider.get_workspace_name(migration_info.get('target', {}).get('workspace_id'))} migration",
            "overall_status": "In Progress",
            "source_platform": migration_info.get("source", {}).get(
                "platform_id", "unknown"
            ),
            "destination_platform": migration_info.get("target", {}).get(
                "platform_id", "unknown"
            ),
            "migration_start_datetime": migration_info.get("created_at"),
            "time_ago": (
                int(
                    (datetime.now() - migration_info.get("created_at")).total_seconds()
                    / 60
                )
                if migration_info.get("created_at")
                else 0
            ),
            "migration_id_display": migration_info.get("migration_id"),
            "metrics": [
                {
                    "title": "Portfolios",
                    "total": len(portfolios),
                    "status": (
                        "completed"
                        if portfolio_metrics["created"] == len(portfolios)
                        and len(portfolios) > 0
                        else "pending"
                    ),
                    "pending": portfolio_metrics["pending"],
                    "created": portfolio_metrics["created"],
                    "skipped": portfolio_metrics["skipped"],
                    "failed": portfolio_metrics["failed"],
                    "progress": calculate_progress(
                        portfolio_metrics["created"], len(portfolios)
                    ),
                },
                {
                    "title": "Teams",
                    "total": len(teams),
                    "status": (
                        "completed"
                        if team_metrics["created"] == len(teams) and len(teams) > 0
                        else "pending"
                    ),
                    "pending": team_metrics["pending"],
                    "created": team_metrics["created"],
                    "skipped": team_metrics["skipped"],
                    "failed": team_metrics["failed"],
                    "progress": calculate_progress(team_metrics["created"], len(teams)),
                },
                {
                    "title": "Projects",
                    "total": len(projects),
                    "status": (
                        "completed"
                        if project_metrics["created"] == len(projects)
                        and len(projects) > 0
                        else "pending"
                    ),
                    "pending": project_metrics["pending"],
                    "created": project_metrics["created"],
                    "skipped": project_metrics["skipped"],
                    "failed": project_metrics["failed"],
                    "progress": calculate_progress(
                        project_metrics["created"], len(projects)
                    ),
                },
                {
                    "title": "Tasks",
                    "total": task_metrics["created"]
                    + task_metrics["pending"]
                    + task_metrics["skipped"]
                    + task_metrics["failed"],
                    "status": (
                        "completed"
                        if task_metrics["pending"] == 0
                        and (
                            task_metrics["created"]
                            + task_metrics["skipped"]
                            + task_metrics["failed"]
                        )
                        > 0
                        else "pending"
                    ),
                    "pending": task_metrics["pending"],
                    "created": task_metrics["created"],
                    "skipped": task_metrics["skipped"],
                    "failed": task_metrics["failed"],
                    "progress": task_metrics["progress"] / max(len(projects), 1),
                },
                {
                    "title": "Attachments",
                    "total": attachment_metrics["created"]
                    + attachment_metrics["pending"]
                    + attachment_metrics["skipped"]
                    + attachment_metrics["failed"],
                    "status": (
                        "reconciliating"
                        if attachment_metrics["pending"] > 0
                        else "completed"
                    ),
                    "pending": attachment_metrics["pending"],
                    "created": attachment_metrics["created"],
                    "skipped": attachment_metrics["skipped"],
                    "failed": attachment_metrics["failed"],
                    "progress": attachment_metrics["progress"] / max(len(projects), 1),
                },
                {
                    "title": "Comments",
                    "total": comment_metrics["created"]
                    + comment_metrics["pending"]
                    + comment_metrics["skipped"]
                    + comment_metrics["failed"],
                    "status": (
                        "completed"
                        if comment_metrics["pending"] == 0
                        and (
                            comment_metrics["created"]
                            + comment_metrics["skipped"]
                            + comment_metrics["failed"]
                        )
                        > 0
                        else "pending"
                    ),
                    "pending": comment_metrics["pending"],
                    "created": comment_metrics["created"],
                    "skipped": comment_metrics["skipped"],
                    "failed": comment_metrics["failed"],
                    "progress": comment_metrics["progress"] / max(len(projects), 1),
                },
            ],
        }

    # async def get_migration_runs(self, migration_id: str):

    async def get_migration_project_details(self, migration_id: str):
        migration_info = await self.get_migration_info_by_migration_id(migration_id)

        collection = self.db["ledger_records"]

        projects = await collection.find(
            {"migration_id": migration_id, "source.kind": "project"}
        ).to_list(length=1000)

        projects_list = []

        source_client = create_provider_client(
            migration_info.get("source", {}).get("platform_id"),
            migration_info.get("source", {}).get("access_token"),
        )
        target_client = create_provider_client(
            migration_info.get("target", {}).get("platform_id"),
            migration_info.get("target", {}).get("access_token"),
        )
        for project in projects:
            try:
                projects_list.append(
                    {
                        "project_id": project.get("source", {})
                        .get("data", {})
                        .get("id"),
                        "name": source_client.get_project_name(
                            migration_info.get("source", {}).get("workspace_id"),
                            project.get("source", {}).get("data", {}).get("id"),
                        ),
                        "status": project.get("status"),
                        "progress": project.get("status"),
                        "source_url": source_client.get_project_url(
                            migration_info.get("source", {}).get("workspace_id"),
                            project.get("source", {}).get("data", {}).get("id"),
                        ),
                        "destination_url": target_client.get_project_url(
                            migration_info.get("target", {}).get("workspace_id"),
                            project.get("target", {}).get("data", {}).get("id"),
                        ),
                    }
                )
            except Exception as e:
                print(e)

        return {"projects": projects_list, "total_projects": len(projects_list)}
