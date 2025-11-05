def format_task_id_workflow(
    user_id: str,
    increment_id: int,
    project_gid: str,
    key: str,
    prefix,
    email,
    create_date,
):
    return {
        "last_increment": increment_id,
        "user_id": user_id,
        "parent_type": "project",
        "parent_gid": project_gid,
        "create_date": create_date,
        "name": "Task ID Workflow",
        "workflow_type": "Power-UP",
        "resource": project_gid,
        "webhook": {
            "key": key,
            "resource": project_gid,
            "resource_type": "task",
            "action": "added",
            "target_path": "taskid/webhook",
            "email": email,
            "resource_subtype": "task",
        },
        "prefix": prefix,
    }
