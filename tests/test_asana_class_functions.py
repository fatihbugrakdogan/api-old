# import os

# from app.integrations.asana import AsanaWithAccessToken as Asana
# from .asana_test_infos import *


# def test_asana_class_funcs():
#     asana = Asana(access_token_1)

#     ####### GET REQUESTS #######

#     #### Try Get Projects ####
#     projects = asana.get_multiple_projects({"workspace": workspace_id_1})
#     assert projects, "Projects retrieval failed"

#     ### Try Get Tasks from Project ###

#     tasks_ = asana.get_tasks_from_project(task_id_test_project_id)
#     assert tasks_, "Tasks retrieval from project failed"

#     tasks = list(tasks_)
#     assert tasks, "Tasks retrieval from project failed"

#     #### Try Get Sections From Project ####
#     sections = asana.get_sections_in_project(task_id_test_project_id)
#     assert sections, "Sections retrieval from project failed"

#     ### Try Get Stories From Task ###
#     stories = asana.get_stories_from_task(list(tasks)[0]["gid"])
#     assert stories, "Stories retrieval from task failed"

#     ### Try Get Subtasks From Task ###
#     subtasks = asana.get_subtasks_of_a_task(list(tasks)[0]["gid"])
#     assert subtasks, "Subtasks retrieval from task failed"

#     ### Try Get Detail of Task ###
#     task_detail = asana.get_detail_of_task(list(tasks)[0]["gid"])
#     assert task_detail, "Task detail retrieval failed"

#     ### Try Get Detail of User ###
#     user_detail = asana.get_detail_of_user(user_asana_id)
#     assert user_detail, "User detail retrieval failed"

#     ####### POST REQUESTS #######

#     ### Try Create Project ###
#     project = asana.create_project(
#         {"name": "Test Project", "workspace": workspace_id_1, "team": team_id_1}
#     )
#     assert project, "Project creation failed"

#     ### Try Create Section in Project ###
#     section = asana.create_section_in_project(project["gid"], {"name": "Test Section"})
#     assert section, "Section creation in project failed"

#     ### Try Create Task ###
#     task = asana.create_task({"name": "Test Task", "projects": [project["gid"]]})
#     assert task, "Task creation failed"

#     ### Try Create Subtask ###
#     subtask = asana.create_subtask(task["gid"], {"name": "Test Subtask"})
#     assert subtask, "Subtask creation failed"

#     ### Try Create Story ###
#     story = asana.create_story(task["gid"], {"text": "Test Story"})
#     assert story, "Story creation failed"

#     ### Try Add Custom Field to Project ###
#     result = asana.add_custom_field_to_project(
#         project["gid"], {"name": "Test Custom Field", "type": "text"}
#     )
#     assert result, "Adding custom field to project failed"

#     ### Delete Created Projects ###
#     result = asana.delete_project(project["gid"])
