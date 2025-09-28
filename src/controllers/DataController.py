from fastapi import UploadFile
from .BaseController import BaseController
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, f"File type {file.content_type} is not allowed."
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, f"File size {file.size} exceeds the maximum limit."
        return True, "File is valid."
