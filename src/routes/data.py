from fastapi import APIRouter, Depends, FastAPI,UploadFile
import os
from helpers.config import get_settings, Settings
from controllers import DataController
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data","api_v1"]
)
@data_router.get("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    # Validate file properties
    is_valid = DataController().validate_uploaded_file(file=file)