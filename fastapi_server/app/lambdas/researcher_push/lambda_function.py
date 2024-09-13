# Send notifications to Cozie-Apple app
# Author: Mario Frei, 2024
# Project: Cozie
# Sources:
#  - https://documentation.onesignal.com/reference/push-channel-properties

import requests
import json
import os
from . import influx_prep
from influxdb import InfluxDBClient
import pandas as pd
from .types import PushData


def lambda_handler(event: PushData, context):
    print(f"event ({type(event)})\n {event}")
    message = ""
    heading = ""
    subtitle = ""
    buttons = ""

    # Sanitize payload
    id_experiment = influx_prep.measurement(id_experiment)
    id_participant = influx_prep.tag_value(id_participant)
    id_password = influx_prep.tag_value(id_password)

    # Initialize InfluxDB client
    influx_client = InfluxDBClient(
        "influxdb",
        8086,
        os.environ["INFLUXDB_USER"],
        os.environ["INFLUXDB_PASSWORD"],
        os.environ["INFLUXDB_NAME"],
    )

    # Query DB
    db_name = os.environ["INFLUXDB_NAME"]
    influx_query = f'SELECT * FROM "cozie-apple"."autogen"."{id_experiment}" WHERE "id_participant"=\'{id_participant}\' AND "id_password"=\'{id_password}\' ORDER BY DESC LIMIT 1'
    print("query influx: ", influx_query)

    result = influx_client.query(influx_query)
    print("result:\n", result)

    # Get OneSignal ID
    response_body = dict()
    if len(result) < 1:
        # Handle empty result set
        id_onesignal = ""
        id_password_db = ""
    else:
        # Convert result from database to dataframe
        df = pd.DataFrame.from_dict(result[id_experiment])
        id_onesignal = df["id_onesignal"][0]
        print(f"id_onesignal: {id_onesignal}")

    if id_onesignal == "":
        return {"statusCode": 400, "body": "No valid OneSignal Player ID found."}

    # Send push notification
    token = os.environ[
        "ONESIGNAL_TOKEN"
    ]  # provided by OneSignal. Can be found on the Keys & IDs page on the OneSignal Dashboard for this particular app
    app_id = os.environ[
        "ONESIGNAL_APP_ID"
    ]  # provided by OneSignal, needs to be implemented in the app

    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic " + token,
    }

    payload_out = {
        "app_id": app_id,
        "include_player_ids": [id_onesignal],
        "contents": {"en": message},
        "headings": {"en": heading},
        "subtitle": {"en": subtitle},
    }
    if buttons != "":
        payload_out["buttons"] = buttons

    print("payload_out\n", payload_out)

    response = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers=header,
        data=json.dumps(payload_out),
    )
    print("response.content: ", response.content)
    print("req.reason: ", response.reason)

    return {
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "statusCode": response.status_code,
        "body": response.content,
    }
