from typing import Any
from WrikePy import *
import json


class WrikeHandler:

    def __init__(self, token: str):
        self.token = token
        self.url = "https://www.wrike.com/api/v4/"
        self.client = Wrike(self.url, self.token)

    def __call__(self) -> Any:
        return self.client

    def check_token(self):

        try:
            Spaces(self.client).query__spaces()
            return True

        except:
            return False

    def get_workspaces(self):
        workspaces = Spaces(self.client).query__spaces()

        ## Make response JSON

        workspaces = json.loads(workspaces.text)
        workspace_list = []

        for workspace in workspaces["data"]:
            workspace_list.append({"id": workspace["id"], "name": workspace["title"]})

        return workspace_list

    def get_projects(self, workspace_id: str):
        projects = FoldersProjects(self.client).query_folders_folderIds()

        ## Make response JSON

        projects = json.loads(projects.text)
        project_list = []

        for project in projects["data"]:
            project_list.append({"id": project["id"], "name": project["title"]})

        return project_list

    def get_project(self, project_id: str):
        project = FoldersProjects(self.client).get_folders_folderId(project_id)

        ## Make response JSON

        project = json.loads(project.text)

        return project

    def get_current_user(self):
        """Get the current user's information"""
        try:
            # Get current user from Wrike API
            from WrikePy import Contacts
            user_response = Contacts(self.client).query_contacts_me()
            user_data = json.loads(user_response.text)
            if user_data.get("data"):
                profiles = user_data["data"][0].get("profiles", [])
                if profiles:
                    return {"email": profiles[0].get("email")}
            return {"email": None}
        except Exception as e:
            return {"email": None}
