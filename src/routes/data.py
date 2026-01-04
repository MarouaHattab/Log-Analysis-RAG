from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import NLPController
from tasks.file_processing import process_project_files
from tasks.process_workflow import process_and_push_workflow
from celery_app import celery_app

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.get("/chunking-methods")
async def get_chunking_methods():
    """
    Get available chunking methods for log analysis.
    """
    process_controller = ProcessController(project_id="temp")
    methods = process_controller.get_available_chunking_methods()
    
    method_descriptions = {
        "log_time_window": "Groups log entries by time periods (hour-based) - Best for time-series analysis",
        "log_error_block": "Groups errors and their context together - Best for error pattern analysis",
        "log_status_code": "Groups by HTTP status code category (2xx, 4xx, 5xx) - Best for status analysis",
        "log_component_based": "Groups by IP address/component - Best for client behavior analysis"
    }
    
    return JSONResponse(
        content={
            "methods": methods,
            "descriptions": method_descriptions
        }
    )

@data_router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status and progress of a processing task.
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        status_response = {
            "task_id": task_id,
            "status": task.status,
            "ready": task.ready(),
            "successful": task.successful() if task.ready() else None,
            "failed": task.failed() if task.ready() else None,
        }
        
        # Add progress information if available
        if task.status == 'PROGRESS':
            status_response["progress"] = task.info.get('current', 0)
            status_response["total"] = task.info.get('total', 100)
            status_response["percentage"] = (task.info.get('current', 0) / task.info.get('total', 100)) * 100
            status_response["message"] = task.info.get('status', 'Processing...')
        elif task.status == 'SUCCESS':
            status_response["result"] = task.result
            status_response["percentage"] = 100
            status_response["message"] = "Task completed successfully"
        elif task.status == 'FAILURE':
            status_response["error"] = str(task.info)
            status_response["percentage"] = 0
            status_response["message"] = "Task failed"
        elif task.status == 'PENDING':
            status_response["percentage"] = 0
            status_response["message"] = "Task pending..."
        else:  # STARTED, RETRY, etc
            status_response["percentage"] = 50
            status_response["message"] = f"Task {task.status.lower()}..."
        
        return JSONResponse(content=status_response)
    
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Could not get task status",
                "task_id": task_id
            }
        )

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: int, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
        
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # validate the file properties
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    # store the assets into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": asset_record.asset_name,
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    chunking_method = process_request.chunking_method

    task = process_project_files.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
        chunking_method=chunking_method,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "task_id": task.id
        }
    )

@data_router.post("/process-and-push/{project_id}")
async def process_and_push_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    chunking_method = process_request.chunking_method

    workflow_task = process_and_push_workflow.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
        chunking_method=chunking_method,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_AND_PUSH_WORKFLOW_READY.value,
            "workflow_task_id": workflow_task.id
        }
    )