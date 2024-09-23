# Cozie Apple App API
# Purpose: Transfer Cozie-Apple data from the Cozie-Apple app into the SQS queue
# Author: Mario Frei, 2024
# Status: Under development
# Project: Cozie-Apple
# Experiment: Hwesta
# Note:
#  - The memory configuration for this Lambda function was deliberatly oversized.
#    The available CPU for the lambda scales with the memory.
#    Hence, there is more computational power with more memory, i.e., the Lambda
#    functions runs faster, which results in faster response times.
#    Source: https://docs.aws.amazon.com/lambda/latest/operatorguide/computing-power.html
#  - The payloads needs to be split into smaller chunks due to the message size
#    limit of 256 KiB.
#    Source: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html

import json
from celery import Celery
from typing import List, Dict, Any, Union
from .types import ParticipantEntry

# Define the celery broker
app = Celery("tasks", broker="redis://redis:6379/0")


def lambda_handler(payload: Union[ParticipantEntry, List[ParticipantEntry]]):

    # Read payload from Lamdba function URL call / API Gateway call with Lambda proxy integration

    # Single timestamp payloads (dicts) need to be put into a list
    if isinstance(payload, ParticipantEntry):
        payload = [payload]
    print(payload)
    payload = [x.model_dump() for x in payload]

    # Split payload and send it to SQS queue
    print("Split up payload")
    num_payloads_in_message = 100
    print(f"type(payload): {type(payload)}")
    print(f"len(payload): {len(payload)}")
    print(f"num_payloads_in_message: {num_payloads_in_message}")
    for i in range(0, len(payload), num_payloads_in_message):

        print("payload")
        print(payload)
        print(
            f"payload[i:i+num_payloads_in_message): payload[{i}:{i}+{num_payloads_in_message}]"
        )
        print(payload[i : i + num_payloads_in_message])
        print("Send payload to SQS queue")
        app.send_task(
            "celery_worker.process_message",
            args=[json.dumps(payload[i : i + num_payloads_in_message])],
        )
