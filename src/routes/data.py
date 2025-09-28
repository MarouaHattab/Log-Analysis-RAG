from fastapi import APIRouter, Depends, FastAPI, UploadFile, File,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data","api_v1"]
)
@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    # Validate file properties
    is_valid,result_signal = DataController().validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )
    
    