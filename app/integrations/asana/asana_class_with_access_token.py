import asana


class AsanaWithAccessToken:
    def __init__(self, token) -> None:
        self.client = asana.Client.access_token(token)

    def __call__(self):
        return self.client

    def check_token(self):
        try:
            self.client.users.me(opt_pretty=True)
            return True
        except:
            return False

    def get_project_name(self, workspace_id, project_id):
        print(workspace_id, project_id)
        project = self.client.projects.get_project(
            project_id, {"workspace": workspace_id}
        )
        return project.get("name")

    def get_project_url(self, workspace_id, project_id):
        print(workspace_id, project_id)
        project = self.client.projects.get_project(project_id, opt_pretty=True)
        return project.get("permalink_url")

    def get_workspaces(self):
        workspaces = []
        for workspace in self.client.workspaces.get_workspaces(opt_pretty=True):
            workspaces.append(
                {
                    "name": workspace["name"],
                    "id": workspace["gid"],
                }
            )
        return workspaces

    def get_all_users_from_workspace(self, workspace_gid):
        users=self.client.workspace_memberships.get_workspace_memberships_for_workspace(
                workspace_gid,
            )
        users_list=[]
        for user in users:
            if user["user"]["is_guest"]:
                continue
            users_list.append(
                user
            )
        return users_list

    def get_workspace_name(self, workspace_gid):
        workspace = self.client.workspaces.get_workspace(workspace_gid)
        return workspace.get("name")

    def get_projects(self, workspace_gid):
        projects = self.client.projects.get_projects({"workspace": workspace_gid}, opt_fields="name,permalink_url,owner.name,gid")
        projects_list = []
        for project in projects:
            projects_list.append(
                {
                    "name": project["name"],
                    "id": project["gid"],
                    "owner": project.get("owner").get("name") if project.get("owner") else "No owner",
                    "permalink_url": project["permalink_url"],
                }
            )
        return projects_list

    def _get_users(self, workspace_gid, offset=None):
        params = {"workspace": workspace_gid}
        if offset:
            params["offset"] = offset

        return self.client.users.get_users(params, opt_fields=["email","is_guest"])
    
    def get_current_user(self):
        return self.client.users.me(opt_pretty=True)

    def get_all_users(self, workspace_gid):
        all_users = []
        response = self._get_users(workspace_gid)

        # Since response is a generator, iterate through it directly
        for user in response:
            if user["is_guest"]:
                continue
            all_users.append({"id": user["gid"], "email": user["email"]})

        return all_users

    def check_user_exists(self, workspace_gid, email):
        response = self.client.workspace_memberships.get_workspace_memberships_for_user(
            email, {"workspace": workspace_gid}
        )

        # Convert generator to list to get actual response
        try:
            users = list(response)
            return True
        except Exception as e:
            print(e)
            return False

    def get_detail_of_user(self, user_gid):
        return self.client.users.get_user(user_gid)

    def get_custom_fields_from_workspace(self, workspace_gid):
        return self.client.custom_fields.get_custom_fields_for_workspace(workspace_gid)

    def create_custom_field(self, data):
        return self.client.custom_fields.create_custom_field_in_workspace(data)

    def get_a_project(self, project_gid):
        return self.client.projects.get_project(project_gid)

    def create_project(self, data):
        return self.client.projects.create_project(data)

    def add_custom_field_to_project(self, project_gid, custom_field_data):
        return self.client.projects.add_custom_field_setting_for_project(
            project_gid, {"custom_field": custom_field_data}
        )

    def get_sections_in_project(self, project_gid):
        return self.client.sections.get_sections_for_project(project_gid)

    def create_section_in_project(self, project_gid, data):
        return self.client.sections.create_section_for_project(project_gid, data)

    def get_tasks_from_section(self, section_gid):
        return self.client.tasks.get_tasks_for_section(section_gid)

    def get_detail_of_task(self, task_gid):
        return self.client.tasks.get_task(task_gid)

    def get_subtasks_of_a_task(self, task_gid):
        return self.client.tasks.get_subtasks_for_task(task_gid)

    def get_a_project(self, project_gid):
        return self.client.projects.get_project(project_gid)

    def update_task_custom_field(self, custom_field_gid, task_gid, value):
        return self.client.tasks.update_task(
            task_gid, {"custom_fields": {custom_field_gid: value}}
        )

    def create_task(self, data):
        return self.client.tasks.create_task(data)

    def add_task_to_section(self, section_gid, task_gid):
        return self.client.sections.add_task_for_section(
            section_gid, {"task": task_gid}
        )

    def create_subtask(self, task_gid, data):
        return self.client.tasks.create_subtask_for_task(task_gid, data)

    def get_stories_from_task(self, task_gid):
        return self.client.stories.get_stories_for_task(task_gid)

    def create_story(self, task_gid, data):
        return self.client.stories.create_story_for_task(task_gid, data)

    def get_attachments_from_task(self, task_gid):
        return self.client.attachments.get_attachments_for_object({"parent": task_gid})

    def create_attachment(self, task_gid, name, url=None, file_content=None):
        return self.client.attachments.create_attachment_for_task(
            task_id=task_gid,
            file_name=name,
            file_content=url,
            file_content_type=file_content,
        )

    def get_an_attachment(self, attachment_gid):
        return self.client.attachments.get_attachment(attachment_gid)

    def get_dependencies_from_task(self, task_gid):
        return self.client.tasks.get_dependencies_for_task(task_gid)

    def get_projects_from_team(self, team_gid):
        return self.client.projects.get_projects({"team": team_gid})

    def add_dependencies_to_task(self, task_gid, data):
        return self.client.tasks.add_dependencies_for_task(
            task_gid, {"dependencies": data}
        )

    def get_a_project_only_html_notes(self, project_gid):
        return self.client.projects.get_project(
            project_gid, {"opt_fields": "html_notes"}
        )

    def get_a_task_only_html_notes(self, task_gid):
        return self.client.tasks.get_task(task_gid, {"opt_fields": "html_notes"})

    def get_multiple_projects(self, data):
        return self.client.projects.get_projects(data)

    def get_multiple_projects_with_names(self, workspace):
        return self.client.projects.get_projects(
            {"workspace": workspace}, opt_fields="name"
        )

    def update_project(self, project_gid, data):
        return self.client.projects.update_project(project_gid, data)

    def get_tasks_from_project(self, project_gid):
        return self.client.tasks.get_tasks_for_project(project_gid)

    def get_multiple_tasks(self, data):
        return self.client.tasks.get_tasks(data)

    def delete_project(self, project_gid):
        return self.client.projects.delete_project(project_gid)

    def get_sections_in_project(self, project_gid):
        return self.client.sections.get_sections_for_project(project_gid)

    def delete_task(self, task_gid):
        return self.client.tasks.delete_task(task_gid)

    def update_task(self, task_gid, data):
        return self.client.tasks.update_task(task_gid, data)

    def delete_section(self, section_gid):
        return self.client.sections.delete_section(section_gid)

    def get_a_portfolio(self, portfolio_gid):
        return self.client.portfolios.get_portfolio(portfolio_gid)

    def get_portfolio_items(self, portfolio_gid):
        return self.client.portfolios.get_items_for_portfolio(portfolio_gid)

    def update_portfolio(self, portfolio_gid, data):
        return self.client.portfolios.update_portfolio(portfolio_gid, data)

    def add_custom_fields_to_portfolio(self, portfolio_gid, data):
        return self.client.portfolios.add_custom_field_setting_for_portfolio(
            portfolio_gid, {"custom_field": data}
        )

    def update_project_custom_field(self, custom_field_gid, project_gid, value):
        return self.client.projects.update_project(
            project_gid, {"custom_fields": {custom_field_gid: value}}
        )

    def add_item_to_portfolio(self, portfolio_gid, data):
        return self.client.portfolios.add_item_for_portfolio(portfolio_gid, data)

    def remove_task_from_project(self, task_gid, project_gid):
        return self.client.tasks.remove_project_for_task(
            task_gid, {"project": project_gid}
        )

    def get_multiple_project(self, data):
        return self.client.projects.get_projects(data)

    def get_project_statuses(self, project_gid):
        return self.client.project_statuses.get_project_statuses_for_project(
            project_gid
        )

    def get_a_status(self, status_gid):
        return self.client.project_statuses.get_project_status(status_gid)

    def create_a_project_status(self, data, project_gid):
        return self.client.project_statuses.create_project_status_for_project(
            project_gid, data
        )

    def delete_status(self, status_gid):
        return self.client.project_statuses.delete_project_status(status_gid)

    def get_goals(self, data):
        return self.client.goals.get_goals(data)

    def get_a_goal(self, goal_gid):
        return self.client.goals.get_goal(goal_gid)

    def create_a_goal(self, data):
        return self.client.goals.create_goal(data)

    def get_time_periods(self, data):
        return self.client.time_periods.get_time_periods(data)

    def create_goal_metric(self, goal_gid, data):
        return self.client.goals.create_goal_metric(goal_gid, data)

    def delete_a_goal(self, goal_gid):
        return self.client.goals.delete_goal(goal_gid)

    def get_status_update_from_object(self, object_gid):
        return self.client.status_updates.get_statuses_for_object(
            {"parent": object_gid}
        )

    def get_a_status_update(self, status_update_gid):
        return self.client.status_updates.get_status(status_update_gid)

    def create_a_status_update(self, data):
        return self.client.status_updates.create_status_for_object(data)

    def delete_story(self, story_gid):
        return self.client.stories.delete_story(story_gid)

    def delete_attachment(self, attachment_gid):
        return self.client.attachments.delete_attachment(attachment_gid)

    def add_followers_to_task(self, task_gid, data):
        return self.client.tasks.add_followers_for_task(task_gid, data)

    def add_a_user_to_a_team(self, team_gid, data):
        return self.client.teams.add_user_for_team(team_gid, data)

    def get_goals(self, data):
        return self.client.goals.get_goals(data)

    def get_a_goal(self, goal_gid):
        return self.client.goals.get_goal(goal_gid)

    def get_parent_of_goal(self, goal_gid):
        return self.client.goals.get_parent_goals_for_goal(goal_gid, opt_pretty=True)

    def get_goals_relationships(self, goal_gid):
        return self.client.goal_relationships.get_goal_relationships(
            {"supported_goal": goal_gid}
        )

    def add_support_goal(self, goal_gid, data):
        return self.client.goal_relationships.add_supporting_relationship(
            goal_gid, data
        )

    def create_goal_metric(self, goal_gid, data):
        return self.client.goals.create_goal_metric(goal_gid, data)

    def update_a_goal(self, goal_gid, data):
        return self.client.goals.update_goal(goal_gid, data)

    def add_followers_to_goal(self, goal_gid, data):
        return self.client.goals.add_followers(goal_gid, data)

    def get_tags_of_workspace(self, data):
        return self.client.tags.get_tags(data)

    def get_a_tag(self, tag_gid):
        return self.client.tags.get_tag(tag_gid)

    def create_tag(self, data):
        return self.client.tags.create_tag(data)

    def get_tags_from_task(self, task_gid):
        return self.client.tags.get_tags_for_task(task_gid)

    def add_tag_to_task(self, task_gid, data):
        return self.client.tags.add_tag_to_task(task_gid, data)

    def add_followers_to_project(self, project_gid, data):
        return self.client.projects.add_followers_for_project(project_gid, data)

    def create_team(self, data):
        return self.client.teams.create_team(data)

    def get_subtasks_of_a_task(self, task_gid):
        return self.client.tasks.get_subtasks_for_task(task_gid)

    def delete_webhook(self, webhook_gid):
        return self.client.webhooks.delete_webhook(webhook_gid, opt_pretty=True)
