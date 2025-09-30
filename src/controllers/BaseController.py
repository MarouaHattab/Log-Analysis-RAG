from helpers.config import get_settings,Settings
import os
import random
import string
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        # Set file_dir to src/assets/files (project-level assets)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src directory
        self.file_dir = os.path.join(self.base_dir, "assets", "files")
        # self.file_dir=self.base_dir+"/"+"assets/files" # this also works but not recommended for cross platform compatibility

    def generate_random_string(self,length:int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))