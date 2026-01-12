from enum import Enum

class ProgressStatusEnum(Enum):
    # Step definitions
    STEP_CHUNKING = "chunking"
    STEP_EMBEDDING = "embedding"
    
    # Status definitions
    STATUS_PENDING = "PENDING"
    STATUS_STARTED = "STARTED"
    STATUS_CHUNKING = "CHUNKING"
    STATUS_EMBEDDING = "EMBEDDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILURE = "FAILURE"
