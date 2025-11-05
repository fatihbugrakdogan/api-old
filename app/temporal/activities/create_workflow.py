from temporalio import activity
from app.repositories.workflow_repository import WorkflowRepository


@activity.defn
async def create_workflow(workflow):
    print("Workflow Created", workflow)
    created_workflow = await WorkflowRepository.create_workflow(workflow)
