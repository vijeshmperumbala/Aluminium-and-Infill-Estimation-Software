import os
from amoeba.settings import CELERY_BROKER_URL
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amoeba.settings")
app = Celery(
                "amoeba", 
                broker=CELERY_BROKER_URL,  
                broker_connection_retry_on_startup=True, 
                CELERY_DEFAULT_QUEUE={
                    "exchange": "amoeba_exchange",
                    "exchange_type": "direct",
                    "routing_key": "default_routing_key",
                    "time_limit": 36000,
                },
        )
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.task_queues = {
    "high_priority_queue": {
        "exchange": "amoeba_exchange",
        "routing_key": "high_priority_tasks",
    },
    "low_priority_queue": {
        "exchange": "amoeba_exchange",
        "routing_key": "low_priority_tasks",
    },
}