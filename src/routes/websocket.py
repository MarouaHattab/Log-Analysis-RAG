import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Request
from sqlalchemy import select

from utils.connection_manager import connection_manager
from utils.progress_manager import ProgressManager
from models.db_schemes.minirag.schemes.workflow_progress import WorkflowProgress

logger = logging.getLogger(__name__)

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)


@websocket_router.websocket("/progress/{project_id}")
async def websocket_progress_endpoint(
    websocket: WebSocket,
    project_id: int,
    workflow_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for receiving real-time workflow progress updates.
    
    Connect to this endpoint to receive progress updates for:
    - A specific workflow (if workflow_id is provided)
    - All workflows for a project (if only project_id is provided)
    
    Messages received will be JSON objects with the structure:
    {
        "type": "progress_update",
        "workflow_id": "...",
        "project_id": 123,
        "status": "CHUNKING|EMBEDDING|SUCCESS|FAILURE",
        "current_step": "chunking|embedding",
        "current_step_number": 1,
        "total_steps": 2,
        "step_progress": 0-100,
        "overall_progress": 0-100,
        "message": "Human readable progress message",
        "timestamp": "ISO datetime"
    }
    
    Client can send messages to subscribe to additional workflows:
    {
        "action": "subscribe",
        "workflow_id": "..."
    }
    """
    connection_id = await connection_manager.connect(
        websocket=websocket,
        project_id=project_id,
        workflow_id=workflow_id
    )
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_json()
            
            # Handle client actions
            if data.get("action") == "subscribe" and data.get("workflow_id"):
                await connection_manager.subscribe_to_workflow(
                    connection_id=connection_id,
                    workflow_id=data["workflow_id"]
                )
                await connection_manager.send_personal_message(
                    connection_id,
                    {
                        "type": "subscribed",
                        "workflow_id": data["workflow_id"],
                        "message": f"Subscribed to workflow {data['workflow_id']}"
                    }
                )
            
            elif data.get("action") == "ping":
                await connection_manager.send_personal_message(
                    connection_id,
                    {
                        "type": "pong",
                        "message": "Connection alive"
                    }
                )
            
            elif data.get("action") == "get_status" and data.get("workflow_id"):
                # Get current progress status from database
                app = websocket.app
                progress_manager = ProgressManager(db_client=app.db_client)
                progress = await progress_manager.get_progress(data["workflow_id"])
                
                if progress:
                    await connection_manager.send_personal_message(
                        connection_id,
                        {
                            "type": "progress_update",
                            "workflow_id": progress.workflow_id,
                            "project_id": progress.project_id,
                            "status": progress.status,
                            "current_step": progress.current_step,
                            "current_step_number": progress.current_step_number,
                            "total_steps": progress.total_steps,
                            "step_progress": progress.step_progress,
                            "overall_progress": progress.overall_progress,
                            "message": progress.message,
                            "result": progress.result,
                            "error_message": progress.error_message
                        }
                    )
                else:
                    await connection_manager.send_personal_message(
                        connection_id,
                        {
                            "type": "error",
                            "message": f"Workflow {data['workflow_id']} not found"
                        }
                    )
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        connection_manager.disconnect(connection_id)


@websocket_router.get("/connections/status")
async def get_websocket_status():
    """
    Get the status of WebSocket connections (for debugging/monitoring).
    
    Returns:
        Connection statistics
    """
    return {
        "active_connections": connection_manager.get_active_connections_count(),
        "status": "healthy"
    }
