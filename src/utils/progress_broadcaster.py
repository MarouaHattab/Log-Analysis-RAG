import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)


class ProgressBroadcaster:
    """
    Helper class for Celery tasks to update progress and broadcast to WebSocket clients.
    
    This class updates the database with progress information. The FastAPI WebSocket
    endpoint polls the database or receives notifications to push updates to clients.
    
    For immediate updates, it can also publish to Redis pub/sub.
    """

    def __init__(self, db_client, db_engine, redis_client=None):
        self.db_client = db_client
        self.db_engine = db_engine
        self.redis_client = redis_client
        
        # Import here to avoid circular imports
        from utils.progress_manager import ProgressManager
        self.progress_manager = ProgressManager(db_client, db_engine)

    async def initialize_workflow(
        self,
        workflow_id: str,
        project_id: int,
        total_steps: int = 2
    ):
        """Initialize a new workflow progress record."""
        await self.progress_manager.create_workflow_progress(
            workflow_id=workflow_id,
            project_id=project_id,
            total_steps=total_steps
        )
        
        # Publish to Redis for immediate notification (optional)
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="PENDING",
            message="Workflow initialized...",
            overall_progress=0.0
        )

    async def start_chunking(
        self,
        workflow_id: str,
        project_id: int,
        total_files: int = 1
    ):
        """Mark the start of chunking phase."""
        await self.progress_manager.mark_chunking_start(
            workflow_id=workflow_id,
            total_files=total_files
        )
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="CHUNKING",
            current_step="chunking",
            current_step_number=1,
            message=f"Starting chunking phase for {total_files} file(s)...",
            overall_progress=5.0
        )

    async def update_chunking(
        self,
        workflow_id: str,
        project_id: int,
        files_processed: int,
        total_files: int,
        chunks_created: int = 0
    ):
        """Update chunking progress."""
        await self.progress_manager.update_chunking_progress(
            workflow_id=workflow_id,
            files_processed=files_processed,
            total_files=total_files,
            chunks_created=chunks_created
        )
        
        step_progress = (files_processed / max(total_files, 1)) * 100
        overall_progress = 5 + (step_progress * 0.45)
        
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="CHUNKING",
            current_step="chunking",
            step_progress=step_progress,
            overall_progress=overall_progress,
            message=f"Chunking: Processed {files_processed}/{total_files} files ({chunks_created} chunks)"
        )

    async def complete_chunking(
        self,
        workflow_id: str,
        project_id: int,
        total_chunks: int
    ):
        """Mark chunking as complete."""
        await self.progress_manager.mark_chunking_complete(
            workflow_id=workflow_id,
            total_chunks=total_chunks
        )
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="CHUNKING",
            current_step="chunking",
            step_progress=100.0,
            overall_progress=50.0,
            message=f"Chunking complete! Created {total_chunks} chunks. Starting embedding..."
        )

    async def start_embedding(
        self,
        workflow_id: str,
        project_id: int,
        total_chunks: int
    ):
        """Mark the start of embedding phase."""
        await self.progress_manager.mark_embedding_start(
            workflow_id=workflow_id,
            total_chunks=total_chunks
        )
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="EMBEDDING",
            current_step="embedding",
            current_step_number=2,
            step_progress=0.0,
            overall_progress=50.0,
            message=f"Starting embedding phase for {total_chunks} chunks..."
        )

    async def update_embedding(
        self,
        workflow_id: str,
        project_id: int,
        chunks_embedded: int,
        total_chunks: int
    ):
        """Update embedding progress."""
        await self.progress_manager.update_embedding_progress(
            workflow_id=workflow_id,
            chunks_embedded=chunks_embedded,
            total_chunks=total_chunks
        )
        
        step_progress = (chunks_embedded / max(total_chunks, 1)) * 100
        overall_progress = 50 + (step_progress * 0.48)
        
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="EMBEDDING",
            current_step="embedding",
            step_progress=step_progress,
            overall_progress=overall_progress,
            message=f"Embedding: Indexed {chunks_embedded}/{total_chunks} chunks"
        )

    async def complete_workflow(
        self,
        workflow_id: str,
        project_id: int,
        result: Dict[str, Any]
    ):
        """Mark workflow as successfully completed."""
        await self.progress_manager.mark_workflow_success(
            workflow_id=workflow_id,
            result=result
        )
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="SUCCESS",
            step_progress=100.0,
            overall_progress=100.0,
            message="Workflow completed successfully! Your data is ready for querying.",
            result=result
        )

    async def fail_workflow(
        self,
        workflow_id: str,
        project_id: int,
        error_message: str
    ):
        """Mark workflow as failed."""
        await self.progress_manager.mark_workflow_failure(
            workflow_id=workflow_id,
            error_message=error_message
        )
        await self._publish_to_redis(
            workflow_id=workflow_id,
            project_id=project_id,
            status="FAILURE",
            message=f"Workflow failed: {error_message}",
            error_message=error_message
        )

    async def _publish_to_redis(
        self,
        workflow_id: str,
        project_id: int,
        status: str,
        message: str,
        current_step: Optional[str] = None,
        current_step_number: Optional[int] = None,
        step_progress: Optional[float] = None,
        overall_progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """
        Publish progress update to Redis pub/sub channel for immediate WebSocket notification.
        This is optional and only works if Redis is configured.
        """
        if not self.redis_client:
            return
        
        try:
            channel = f"workflow_progress:{project_id}"
            message_data = {
                "type": "progress_update",
                "workflow_id": workflow_id,
                "project_id": project_id,
                "status": status,
                "current_step": current_step,
                "current_step_number": current_step_number,
                "step_progress": step_progress,
                "overall_progress": overall_progress,
                "message": message,
                "result": result,
                "error_message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.redis_client.publish(channel, json.dumps(message_data))
            logger.debug(f"Published progress update to Redis channel: {channel}")
            
        except Exception as e:
            # Redis publishing is optional, don't fail if it doesn't work
            logger.warning(f"Failed to publish to Redis: {e}")


def get_parent_workflow_id(celery_task_instance) -> Optional[str]:
    """
    Get the parent workflow ID from a Celery task instance.
    This is used by child tasks to report progress to the parent workflow.
    
    Args:
        celery_task_instance: The Celery task instance (self in @celery_app.task)
    
    Returns:
        The parent workflow ID or None
    """
    try:
        # Check if this task was called as part of a chain/workflow
        if hasattr(celery_task_instance.request, 'parent_id') and celery_task_instance.request.parent_id:
            return str(celery_task_instance.request.parent_id)
        
        # Check for root_id (the original task that started the chain)
        if hasattr(celery_task_instance.request, 'root_id') and celery_task_instance.request.root_id:
            return str(celery_task_instance.request.root_id)
        
        return None
    except Exception:
        return None
