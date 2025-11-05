import json
import requests


class Monday:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def make_request(self, query, variables=None):
        """
        Make a request to the Monday.com GraphQL API.
        """
        payload = {"query": query, "variables": variables or {}}
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        if "errors" in data:
            raise Exception(f"API Error: {data['errors']}")
        return data["data"]

    def __call__(self):
        return self

    def get_project_name(self, workspace_id, board_id):
        print(workspace_id, board_id)
        return self.make_request(f"query {{boards(ids: [{board_id}]) {{name}}}}")[
            "boards"
        ][0]["name"]

    def check_token(self):
        try:
            # Make a simple test query to verify token works
            query = """
            query {
                me {
                    id
                }
            }
            """
            self.make_request(query)
            return True
        except requests.exceptions.RequestException:
            return False

    def get_workspaces(self):
        try:
            query = """
            query {
                workspaces {
                    id
                    name
                }
            }
            """
            response = self.make_request(query)

            return response["workspaces"]
        except Exception as e:
            print(f"Error getting workspaces: {str(e)}")
            return []

    def __get_boards(self, workspace_id):
        """
        Retrieve a list of boards for a specific workspace.
        """
        query = f"""
        query {{
            boards(workspace_ids: [{workspace_id}]) {{
                id
                name
            }}
        }}
        """

        response = self.make_request(query)

        return response["boards"]

    def get_projects(self, workspace_id):
        return self.__get_boards(workspace_id)

    def get_workspace_name(self, workspace_id):
        query = f"""
        query {{
            workspaces(ids: [{workspace_id}]) {{
                name
            }}
        }}
        """
        response = self.make_request(query)
        return response["workspaces"][0]["name"]

    def get_project_url(self, workspace_id, board_id):
        """
        Retrieve a specific board by ID with detailed information including permissions,
        tags, groups, and columns.
        """
        query = (
            """
        query {
            boards(ids: [%s]) {
                id
                name
                url
                groups {
                    id
                    title
                }
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
            % board_id
        )
        print(workspace_id, board_id)
        response = self.make_request(query)

        return response["boards"][0]["url"]

    def get_all_users(self, workspace_id):
        """
        Retrieve all users using page-based pagination
        without relying on a separate variables dictionary.
        """
        all_users = []
        page = 1
        limit = 100  # Adjust as needed

        while True:
            # Embed page and limit directly in the query string
            query = f"""
            query {{
            users(page: {page}, limit: {limit}) {{
                id
                name
                email
                # Add any other user fields you need here
            }}
            }}
            """

            # Make the request without passing a 'variables' argument
            response_data = self.make_request(query)
            print(response_data, type(response_data))
            users = response_data.get("users", [])

            # If no users are returned, we've reached the end
            if not users:
                break

            # Collect the retrieved users
            all_users.extend(users)

            # If we received fewer than 'limit' results, no more pages exist
            if len(users) < limit:
                break

            # Move to the next page
            page += 1

        return all_users

    def get_current_user(self):
        """Get the current user's information"""
        try:
            query = """
            query {
                me {
                    id
                    name
                    email
                }
            }
            """
            response = self.make_request(query)
            return {"email": response["me"].get("email")}
        except Exception as e:
            return {"email": None}
