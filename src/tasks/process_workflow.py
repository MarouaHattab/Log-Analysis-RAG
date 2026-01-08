from celery import chain
from celery_app import celery_app, get_setup_utils
from helpers.config import get_settings
import asyncio
from tasks.file_processing import process_project_files
from tasks.data_indexing import _index_data_content
from utils.progress_manager import ProgressManager

import logging
import traceback
logger = logging.getLogger(__name__)

@celery_app.task(
                 bind=True, name="tasks.process_workflow.push_after_process_task",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )
def push_after_process_task(self, prev_task_result):

    project_id = prev_task_result.get("project_id")
    do_reset = prev_task_result.get("do_reset")
    workflow_id = prev_task_result.get("workflow_id")
    total_chunks = prev_task_result.get("inserted_chunks", 0)

    # Run all async operations in a single event loop
    task_results = asyncio.run(
        _run_embedding_phase(self, project_id, do_reset, workflow_id, total_chunks)
    )

    return {
        "project_id": project_id,
        "do_reset": do_reset,
        "workflow_id": workflow_id,
        "task_results": task_results
    }


async def _run_embedding_phase(task_instance, project_id: int, do_reset: int, workflow_id: str, total_chunks: int):
    """Run the embedding phase with progress tracking - all in one async context."""
    db_engine = None
    try:
        (db_engine, db_client, llm_provider_factory, 
        vectordb_provider_factory,
        generation_client, embedding_client,
        vectordb_client, template_parser) = await get_setup_utils()
        
        # Update progress: start embedding
        if workflow_id:
            try:
                progress_manager = ProgressManager(db_client, db_engine)
                await progress_manager.mark_embedding_start(workflow_id, total_chunks)
            except Exception as e:
                logger.error(f"Failed to mark embedding start: {e}")
        
        # Run the actual embedding
        task_results = await _index_data_content(task_instance, project_id, do_reset, workflow_id=workflow_id)
        
        # Update progress: complete workflow
        if workflow_id:
            try:
                progress_manager = ProgressManager(db_client, db_engine)
                await progress_manager.mark_workflow_success(workflow_id, task_results)
            except Exception as e:
                logger.error(f"Failed to mark workflow success: {e}")
        
        return task_results
        
    except Exception as e:
        # Update progress: failure
        if workflow_id:
            try:
                db_engine2, db_client2 = (await get_setup_utils())[0:2]
                progress_manager = ProgressManager(db_client2, db_engine2)
                await progress_manager.mark_workflow_failure(workflow_id, str(e))
                if db_engine2:
                    await db_engine2.dispose()
            except Exception as inner_e:
                logger.error(f"Failed to mark workflow failure: {inner_e}")
        raise
    finally:
        if db_engine:
            await db_engine.dispose()


from utils.idempotency_manager import IdempotencyManager

@celery_app.task(
                 bind=True, name="tasks.process_workflow.process_and_push_workflow",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )
def process_and_push_workflow(  self, project_id: int, 
                                file_id: int, chunk_size: int,
                                overlap_size: int, do_reset: int, chunking_method: str = "simple"):

    # Use the current task's ID as the workflow ID, as this is what the frontend receives
    workflow_id = self.request.id
    logger.warning(f"Starting workflow with ID: {workflow_id} for project: {project_id}")

    # Initialize workflow progress and create task record in a SINGLE async context
    try:
        asyncio.run(_initialize_all(workflow_id, project_id, file_id, chunk_size, overlap_size, do_reset, chunking_method))
        logger.warning(f"Workflow initialized successfully: {workflow_id}")
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {e}")
        logger.error(traceback.format_exc())

    # Start the actual workflow chain
    workflow = chain(
        process_project_files.s(project_id, file_id, chunk_size, overlap_size, do_reset, chunking_method, workflow_id=workflow_id),
        push_after_process_task.s()
    )

    result = workflow.apply_async()
    
    return {
        "signal": "WORKFLOW_STARTED",
        "workflow_id": workflow_id,
        "tasks": ["tasks.file_processing.process_project_files", 
                  "tasks.data_indexing.index_data_content"]
    }


async def _initialize_all(workflow_id: str, project_id: int, file_id: int, 
                          chunk_size: int, overlap_size: int, do_reset: int, chunking_method: str):
    """Initialize workflow progress and task record in a single async context."""
    db_engine = None
    try:
        db_engine, db_client = (await get_setup_utils())[0:2]
        
        # 1. Create workflow progress record
        progress_manager = ProgressManager(db_client, db_engine)
        await progress_manager.create_workflow_progress(
            workflow_id=workflow_id,
            project_id=project_id,
            total_steps=2
        )
        logger.info(f"Created workflow progress record for: {workflow_id}")
        
        # 2. Create idempotency task record
        idempotency_manager = IdempotencyManager(db_client, db_engine)
        task_args = {
            "project_id": project_id,
            "file_id": file_id,
            "chunk_size": chunk_size,
            "overlap_size": overlap_size,
            "do_reset": do_reset,
            "chunking_method": chunking_method
        }
        await idempotency_manager.create_task_record(
            task_name="tasks.process_workflow.process_and_push_workflow",
            task_args=task_args,
            celery_task_id=workflow_id
        )
        logger.info(f"Created task record for: {workflow_id}")
        
    except Exception as e:
        logger.error(f"Error in _initialize_all: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        if db_engine:
            await db_engine.dispose()
