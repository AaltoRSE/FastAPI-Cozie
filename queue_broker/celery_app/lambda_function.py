# Cozie Apple Write API
# Purpose: Transfer data from SQS queue to InfluxDB
# Project: Cozie-Apple
# Experiment: Hwesta, Dev
# Author: Mario Frei, 2024
# Test with Colcab notebook and Cloudwatch instead of test payload provded with 'Test' button on AWS

import os
import json
from influxdb import InfluxDBClient, DataFrameClient
import time
from datetime import datetime
from pprint import pprint
import requests
import logging
from pprint import pformat
from .check_type import check_type
from .add_timestamp_lambda import add_timestamp_lambda

# Configure the logging format
root_logger = logging.getLogger("app")

# influx authentication
db_user = os.environ["INFLUXDB_USER"]
db_password = os.environ["INFLUXDB_PASSWORD"]
db_host = "influxdb"
db_port = 8086
db_name = os.environ["INFLUXDB_NAME"]


def lambda_handler(event: dict):

    # Influx client
    # No need for SSL due to communication within docker network
    client = InfluxDBClient(db_host, db_port, db_user, db_password, db_name)

    # Debugging
    root_logger.debug(
        "##################################### Start #####################################"
    )
    root_logger.debug(pformat(event))

    root_logger.debug("Iterate through all paylods in list:")
    payload_counter = 0
    for payload in event:
        payload_counter += 1
        root_logger.debug(
            f"######################## Payload {payload_counter} ########################"
        )
        if payload_counter == 1:
            root_logger.debug("*** Payload ***")
            root_logger.debug(f"Type: {type(payload)}")
            root_logger.debug(payload)
        # root_logger.debug("type(payload):", type(payload))
        # logging.debug(pformat(payload))

        # Check for minimal presence of required fields/tags
        required_keys = [
            "time",
            "id_participant",
            "measurement",
        ]  # XXX add id_password, measurement is synonym for id_experiment
        if (
            ("time" not in payload)
            or ("measurement" not in payload)
            or ("id_participant" not in payload["tags"])
        ):
            root_logger.error(
                f"On or more of the required keys ({required_keys}) were not in the payload"
            )

        root_logger.debug(
            f"id_experiment  = {payload['measurement']}",
        )
        root_logger.debug(f"id_participant = {payload['tags']['id_participant']}")

        # Check value types in payload
        payload = check_type(payload)

        # Get timestamp from call of lambda function for entry (might get overwritten by later data insertions)
        timestamp_lambda = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Add timestamp lambda as field  for entire row (might get overwritten by later data insertions with the same timestamp and tag)
        payload["fields"]["timestamp_lambda"] = timestamp_lambda

        # Add timestamp lambda as specific field, e.g., ts_heart_rate -> ts_heart_rate_lambda
        payload = add_timestamp_lambda(payload, timestamp_lambda)

        # Debug print
        # root_logger.debug("type(payload):", type(payload))
        # logging.debug(pformat(payload))

        # Convert payload back to json
        json_body = [payload]

        # root_logger.debug("json.dumps(json_body):")
        # logging.debug(json.dumps(json_body))

        try:
            feedback = client.write_points(
                json_body, batch_size=5000
            )  # write to InfluxDB
            root_logger.debug(f"Client write done {feedback}")
        except Exception as e:
            root_logger.error(e)

    root_logger.debug(
        "##################################### END #####################################"
    )
