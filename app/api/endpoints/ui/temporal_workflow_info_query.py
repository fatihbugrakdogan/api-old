from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from temporalio.client import Client
import json
import time

router = APIRouter()


@router.websocket("/get-temporal-workflow-info")
async def get_temporal_workflow_info(websocket: WebSocket):
    await websocket.accept()
    # URL parametrelerinden workflow_id'yi alın
    query_params = websocket.query_params
    workflow_id = query_params.get("workflow_id")

    if not workflow_id:
        await websocket.close(code=1008, reason="workflow_id is required")
        return

    client = await Client.connect("localhost:7233")

    try:
        while True:
            # Temporal'dan görev durumlarını kontrol edin
            handle = client.get_workflow_handle(workflow_id)
            workflow_description_info = await handle.describe()
            workflow_status_info = workflow_description_info.status.name
            activity_list = []

            workflow_events_info = await handle.fetch_history()

            #### Get Count Of Project ID's

            for workflow_event in workflow_events_info.events:
                if (
                    workflow_event.activity_task_scheduled_event_attributes.activity_type.name
                    == "Asana Project is Creating..."
                ):
                    activity_list.append(workflow_event)

            activity_count = len(activity_list)
            latest_activity = workflow_events_info.events[-1]
            activity_name = (
                latest_activity.activity_task_scheduled_event_attributes.activity_type
            )
            workflow_input = json.loads(
                workflow_events_info.events[0]
                .workflow_execution_started_event_attributes.input.payloads[0]
                .data.decode("utf-8")
            )
            try:
                if activity_count == 0:
                    await websocket.send_json(
                        {
                            "workflow_status": workflow_status_info,
                            "workflow_name": workflow_description_info.workflow_type,
                            "latest_update": str(activity_name.name),
                            "project_name": "Waiting For Project Name",
                        }
                    )

                else:
                    await websocket.send_json(
                        {
                            "workflow_status": workflow_status_info,
                            "workflow_name": workflow_description_info.workflow_type,
                            "latest_update": str(activity_name.name),
                            "project_name": workflow_input["selected_projects"][
                                activity_count - 1
                            ]["name"],
                        }
                    )
            except:
                await websocket.send_json(
                    {
                        "workflow_status": workflow_status_info,
                        "workflow_name": workflow_description_info.workflow_type,
                        "latest_update": str(activity_name.name),
                        "project_name": "Waiting For Project Name",
                    }
                )
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
