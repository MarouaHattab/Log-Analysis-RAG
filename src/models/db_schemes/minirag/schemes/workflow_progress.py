from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Index
import uuid

class WorkflowProgress(SQLAlchemyBase):
    """
    Tracks the progress of workflow tasks with detailed step information.
    This enables real-time progress tracking for the frontend.
    """

    __tablename__ = "workflow_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Task identification
    workflow_id = Column(String(64), nullable=False, unique=True)  # The Celery workflow task ID
    project_id = Column(Integer, nullable=False)
    
    # Overall status: PENDING, STARTED, CHUNKING, EMBEDDING, SUCCESS, FAILURE
    status = Column(String(32), nullable=False, default='PENDING')
    
    # Current step information
    current_step = Column(String(64), nullable=True)  # e.g., "chunking", "embedding"
    current_step_number = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=2)  # chunking + embedding = 2 steps
    
    # Progress within current step (0-100)
    step_progress = Column(Float, nullable=False, default=0.0)
    
    # Overall progress (0-100)
    overall_progress = Column(Float, nullable=False, default=0.0)
    
    # Human-readable message for the UI
    message = Column(Text, nullable=True)
    
    # Detailed result or error information
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index('idx_workflow_progress_workflow_id', workflow_id),
        Index('idx_workflow_progress_project_id', project_id),
        Index('idx_workflow_progress_status', status),
        Index('idx_workflow_progress_created_at', created_at),
    )
