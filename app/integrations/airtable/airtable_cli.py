from pyairtable import Api


class AirtableClient:
    def __init__(self, api_key):
        self.api = Api(api_key)

    def check_token(self):
        """Check if the token is valid"""
        try:
            self.api.bases()
            return True
        except:
            return False

    def get_workspaces(self):
        """Get all workspaces from the base"""

        bases = self.api.bases()

        return [{"id": base.id, "name": base.name} for base in bases]

    def get_projects(self, workspace_id):
        """Get all projects from the base"""

        tables = self.api.base(workspace_id).tables()

        return [{"id": table.id, "name": table.name} for table in tables]

    def get_project_name(self, workspace_id, project_id):
        """Get the name of the project"""
        return self.api.table(workspace_id, project_id).name

    def get_project_url(self, workspace_id, project_id):
        """Get the url of the project"""
        return f"https://airtable.com/{workspace_id}/{project_id}"

    def get_workspace_name(self, workspace_id):
        """Get the name of the workspace"""
        return self.api.base(workspace_id).name
