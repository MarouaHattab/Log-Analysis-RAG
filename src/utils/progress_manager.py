import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_schemes.minirag.schemes.workflow_progress import WorkflowProgress

logger = logging.getLogger(__name__)


from models import ProgressStatusEnum

class ProgressManager:
    """
    Manages workflow progress tracking and updates.
    Used by Celery tasks to report progress that can be consumed by WebSocket clients.
    """

    # Step definitions
    STEP_CHUNKING = ProgressStatusEnum.STEP_CHUNKING.value
    STEP_EMBEDDING = ProgressStatusEnum.STEP_EMBEDDING.value
    
    # Status definitions
    STATUS_PENDING = ProgressStatusEnum.STATUS_PENDING.value
    STATUS_STARTED = ProgressStatusEnum.STATUS_STARTED.value
    STATUS_CHUNKING = ProgressStatusEnum.STATUS_CHUNKING.value
    STATUS_EMBEDDING = ProgressStatusEnum.STATUS_EMBEDDING.value
    STATUS_SUCCESS = ProgressStatusEnum.STATUS_SUCCESS.value
    STATUS_FAILURE = ProgressStatusEnum.STATUS_FAILURE.value

    def __init__(self, db_client, db_engine=None):
        self.db_client = db_client
        self.db_engine = db_engine

    async def create_workflow_progress(
        self,
        workflow_id: str,
        project_id: int,
        total_steps: int = 2
    ) -> WorkflowProgress:
        """
        Initialize a new workflow progress record.
        
        Args:
            workflow_id: The Celery workflow task ID
            project_id: The project being processed
            total_steps: Total number of steps in the workflow (default: 2 for chunking + embedding)
        
        Returns:
            The created WorkflowProgress record
        """
        progress_record = WorkflowProgress(
            workflow_id=workflow_id,
            project_id=project_id,
            status=self.STATUS_PENDING,
            current_step=None,
            current_step_number=0,
            total_steps=total_steps,
            step_progress=0.0,
            overall_progress=0.0,
            message="Workflow initialized, waiting to start...",
            started_at=datetime.now(timezone.utc)
        )
        
        session: AsyncSession = self.db_client()
        try:
            session.add(progress_record)
            await session.flush()
            await session.commit()
            await session.refresh(progress_record)
            logger.info(f"Created workflow progress record for workflow_id: {workflow_id}")
            return progress_record
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create workflow progress: {e}")
            raise e
        finally:
            await session.close()

    async def update_progress(
        self,
        workflow_id: str,
        status: Optional[str] = None,
        current_step: Optional[str] = None,
        current_step_number: Optional[int] = None,
        step_progress: Optional[float] = None,
        overall_progress: Optional[float] = None,
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        completed: bool = False
    ) -> Optional[WorkflowProgress]:
        """
        Update workflow progress in the database.
        
        Args:
            workflow_id: The workflow ID to update
            status: New status (PENDING, STARTED, CHUNKING, EMBEDDING, SUCCESS, FAILURE)
            current_step: Current step name (e.g., "chunking", "embedding")
            current_step_number: Current step number (1, 2, etc.)
            step_progress: Progress within current step (0-100)
            overall_progress: Overall workflow progress (0-100)
            message: Human-readable progress message
            result: JSON result data (on success)
            error_message: Error message (on failure)
            completed: Whether the workflow is complete
        
        Returns:
            Updated WorkflowProgress record or None if not found
        """
        session: AsyncSession = self.db_client()
        try:
            # Build update values
            update_values = {"updated_at": datetime.now(timezone.utc)}
            
            if status is not None:
                update_values["status"] = status
            if current_step is not None:
                update_values["current_step"] = current_step
            if current_step_number is not None:
                update_values["current_step_number"] = current_step_number
            if step_progress is not None:
                update_values["step_progress"] = step_progress
            if overall_progress is not None:
                update_values["overall_progress"] = overall_progress
            if message is not None:
                update_values["message"] = message
            if result is not None:
                update_values["result"] = result
            if error_message is not None:
                update_values["error_message"] = error_message
            if completed:
                update_values["completed_at"] = datetime.now(timezone.utc)
            
            # Update the record
            stmt = (
                update(WorkflowProgress)
                .where(WorkflowProgress.workflow_id == workflow_id)
                .values(**update_values)
            )
            await session.execute(stmt)
            await session.commit()
            
            # Fetch and return the updated record
            select_stmt = select(WorkflowProgress).where(
                WorkflowProgress.workflow_id == workflow_id
            )
            result_obj = await session.execute(select_stmt)
            progress_record = result_obj.scalar_one_or_none()
            
            if progress_record:
                logger.debug(f"Updated workflow progress: {workflow_id} -> {status or 'no status change'}")
            
            return progress_record
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to update workflow progress: {e}")
            raise e
        finally:
            await session.close()

    async def get_progress(self, workflow_id: str) -> Optional[WorkflowProgress]:
        """
        Get the current progress for a workflow.
        
        Args:
            workflow_id: The workflow ID to look up
        
        Returns:
            WorkflowProgress record or None if not found
        """
        session: AsyncSession = self.db_client()
        try:
            stmt = select(WorkflowProgress).where(
                WorkflowProgress.workflow_id == workflow_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        finally:
            await session.close()

    async def get_project_active_workflows(self, project_id: int) -> list:
        """
        Get all active (non-completed) workflows for a project.
        
        Args:
            project_id: The project ID
        
        Returns:
            List of active WorkflowProgress records
        """
        session: AsyncSession = self.db_client()
        try:
            stmt = select(WorkflowProgress).where(
                WorkflowProgress.project_id == project_id,
                WorkflowProgress.status.notin_([self.STATUS_SUCCESS, self.STATUS_FAILURE])
            ).order_by(WorkflowProgress.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()
        finally:
            await session.close()

    async def mark_chunking_start(
        self,
        workflow_id: str,
        total_files: int = 1
    ) -> Optional[WorkflowProgress]:
        """Convenience method to mark the start of chunking phase."""
        return await self.update_progress(
            workflow_id=workflow_id,
            status=self.STATUS_CHUNKING,
            current_step=self.STEP_CHUNKING,
            current_step_number=1,
            step_progress=0.0,
            overall_progress=5.0,
            message=f"Starting chunking phase for {total_files} file(s)..."
        )

    async def update_chunking_progress(
        self,
        workflow_id: str,
        files_processed: int,
        total_files: int,
        chunks_created: int = 0
    ) -> Optional[WorkflowProgress]:
        """Convenience method to update chunking progress."""
        step_progress = (files_processed / max(total_files, 1)) * 100
        # Chunking is step 1 of 2, so it covers 0-50% of overall progress
        overall_progress = 5 + (step_progress * 0.45)  # 5% to 50%
        
        return await self.update_progress(
            workflow_id=workflow_id,
            step_progress=step_progress,
            overall_progress=overall_progress,
            message=f"Chunking: Processed {files_processed}/{total_files} files ({chunks_created} chunks created)"
        )

    async def mark_chunking_complete(
        self,
        workflow_id: str,
        total_chunks: int
    ) -> Optional[WorkflowProgress]:
        """Convenience method to mark chunking as complete."""
        return await self.update_progress(
            workflow_id=workflow_id,
            step_progress=100.0,
            overall_progress=50.0,
            message=f"Chunking complete! Created {total_chunks} chunks. Starting embedding..."
        )

    async def mark_embedding_start(
        self,
        workflow_id: str,
        total_chunks: int
    ) -> Optional[WorkflowProgress]:
        """Convenience method to mark the start of embedding phase."""
        return await self.update_progress(
            workflow_id=workflow_id,
            status=self.STATUS_EMBEDDING,
            current_step=self.STEP_EMBEDDING,
            current_step_number=2,
            step_progress=0.0,
            overall_progress=50.0,
            message=f"Starting embedding phase for {total_chunks} chunks..."
        )

    async def update_embedding_progress(
        self,
        workflow_id: str,
        chunks_embedded: int,
        total_chunks: int
    ) -> Optional[WorkflowProgress]:
        """Convenience method to update embedding progress."""
        step_progress = (chunks_embedded / max(total_chunks, 1)) * 100
        # Embedding is step 2 of 2, so it covers 50-100% of overall progress
        overall_progress = 50 + (step_progress * 0.48)  # 50% to 98%
        
        return await self.update_progress(
            workflow_id=workflow_id,
            step_progress=step_progress,
            overall_progress=overall_progress,
            message=f"Embedding: Indexed {chunks_embedded}/{total_chunks} chunks into vector database"
        )

    async def mark_workflow_success(
        self,
        workflow_id: str,
        result: Dict[str, Any]
    ) -> Optional[WorkflowProgress]:
        """Convenience method to mark workflow as successfully completed."""
        return await self.update_progress(
            workflow_id=workflow_id,
            status=self.STATUS_SUCCESS,
            step_progress=100.0,
            overall_progress=100.0,
            message="Workflow completed successfully! Your data is ready for querying.",
            result=result,
            completed=True
        )

    async def mark_workflow_failure(
        self,
        workflow_id: str,
        error_message: str
    ) -> Optional[WorkflowProgress]:
        """Convenience method to mark workflow as failed."""
        return await self.update_progress(
            workflow_id=workflow_id,
            status=self.STATUS_FAILURE,
            message=f"Workflow failed: {error_message}",
            error_message=error_message,
            completed=True
        )


def calculate_overall_progress(step_number: int, total_steps: int, step_progress: float) -> float:
    """
    Calculate overall progress based on current step and step progress.
    
    Args:
        step_number: Current step number (1-indexed)
        total_steps: Total number of steps
        step_progress: Progress within current step (0-100)
    
    Returns:
        Overall progress percentage (0-100)
    """
    if total_steps == 0:
        return 0.0
    
    step_weight = 100.0 / total_steps
    completed_steps_progress = (step_number - 1) * step_weight
    current_step_contribution = (step_progress / 100.0) * step_weight
    
    return min(completed_steps_progress + current_step_contribution, 100.0)
