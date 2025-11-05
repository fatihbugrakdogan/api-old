import smartsheet


class SmartsheetClient:
    def __init__(self, access_token):
        self.client = smartsheet.Smartsheet(access_token)
        self.client.errors_as_exceptions(True)

    def check_token(self):
        """Check if the token is valid"""
        try:
            self.client.Sheets.list_sheets()
            return True
        except:
            return False

    def get_project_name(self, workspace_id, sheet_id):
        """Get the name of the project"""
        print(workspace_id, sheet_id)
        return self.client.Sheets.get_sheet(sheet_id).name

    def get_project_url(self, workspace_id, sheet_id):
        """Get the url of the project"""
        print(workspace_id, sheet_id)
        return self.client.Sheets.get_sheet(sheet_id).url

    def get_sheets(self):
        """Get all sheets accessible to the authenticated user"""
        response = self.client.Sheets.list_sheets()
        return response.data

    def get_sheet_by_id(self, sheet_id):
        """Get a specific sheet by its ID"""
        return self.client.Sheets.get_sheet(sheet_id)

    def get_sheet_by_name(self, sheet_name):
        """Get a specific sheet by its name"""
        sheets = self.get_sheets()
        for sheet in sheets:
            if sheet.name == sheet_name:
                return self.get_sheet_by_id(sheet.id)
        return None

    def get_tasks(self, sheet_id):
        """Get all rows (tasks) from a specific sheet"""
        sheet = self.get_sheet_by_id(sheet_id)
        return sheet.rows

    def get_projects(self, workspace_id):
        """Get all projects from a specific sheet"""

        workspace = self.client.Workspaces.get_workspace(workspace_id, load_all=True)
        print(workspace, "smartsheet workspace")
        projects = []
        if hasattr(workspace, "folders"):
            for folder in workspace.folders:
                if hasattr(folder, "sheets"):
                    for sheet in folder.sheets:
                        projects.append({"id": str(sheet.id), "name": sheet.name})

        print(projects)

        return projects

    def get_columns(self, sheet_id):
        """Get all columns from a specific sheet"""
        sheet = self.get_sheet_by_id(sheet_id)
        return sheet.columns

    def get_workspaces(self):
        """Get all workspaces"""
        response = self.client.Workspaces.list_workspaces()
        workspaces = []
        for workspace in response.data:
            print(workspace)
            workspaces.append({"id": str(workspace.id), "name": workspace.name})
        return workspaces

    def get_folder_list(self):
        """Get all folders"""
        response = self.client.Folders.list_folders()
        return response.data

    def get_attachments(self, sheet_id, row_number):
        """Get all attachments for a task"""
        response = self.client.Attachments.list_row_attachments(sheet_id, row_number)
        return response.data

    def get_a_attachment(self, sheet_id, attachment_id):
        """Get a specific attachment for a task"""
        response = self.client.Attachments.get_attachment(sheet_id, attachment_id)
        return response

    def get_comments(self, sheet_id, row_number):
        """Get all comments for a task"""
        response = self.client.Discussions.get_row_discussions(sheet_id, row_number)
        return response.data

    def get_a_task(self, sheet_id, row_number):
        """Get a specific task by its row number"""
        response = self.client.Sheets.get_row(sheet_id, row_number)
        return response

    def get_workspace_name(self, workspace_id):
        """Get the name of the workspace"""
        response = self.client.Workspaces.get_workspace(workspace_id)
        return response.name

    def get_current_user(self):
        """Get the current user's information"""
        try:
            # Get current user info from Smartsheet
            current_user = self.client.Users.get_current_user()
            return {"email": current_user.email}
        except Exception as e:
            return {"email": None}
