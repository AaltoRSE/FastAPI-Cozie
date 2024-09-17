from celery import Celery
import json
import os
from .lambda_function import lambda_handler

import logging
import logging.config

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

# Configure Celery to use Redis as the broker
app = Celery("tasks", broker=f"redis://redis:6379/0")


@app.task(name="celery_worker.process_message")
def process_message(message: str):
    # Run the lambda handler on the message
    lambda_handler(json.loads(message))
