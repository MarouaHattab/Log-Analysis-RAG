from celery import Celery
from helpers.config import  get_settings

settings = get_settings()

#create celery app instance
celery_app = Celery(
    'minirag',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# configure celery with essential settings
celery_app.conf.update(
    task_serializer = settings.CELERY_TASK_SERIALIZER,
    result_serializer= settings.CELERY_TASK_SERIALIZER,
   accept_content = [
       settings.CELERY_TASK_SERIALIZER
       ],
       task_acks_late = settings.CELERY_TASK_ACKS_LATE,
       task_time_limit = settings.CELERY_TASK_TIME_LIMIT,
       task_ignore_result = False,
       result_expires = 3600,
    worker_concurrency = settings.CELERY_WORKER_CONCURRENCY,

    # connection settings for better reliability
    broker_connection_retry_on_startup = True,
    broker_connection_retry = True,
    broker_connection_max_retries = 10,
    worker_cancel_long_running_tasks_on_connection_loss = True,
)
celery_app.conf.task_default_queue = "default"