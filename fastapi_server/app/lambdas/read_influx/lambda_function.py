# Cozie Apple v3 Read API
# Purpose: Read data from Cozie-Apple app from InfluxDB
# Author: Mario Frei, 2023
# Status: Under development
# Project: Cozie
# Experiemnt: Osk

# To do:
#  - Optimize finding of time-zone. It currently takes 5.3s (78%)
#    The execution of the entire function takes 6.8s

import pandas as pd
from influxdb import InfluxDBClient
import os
from .valid_votes import keep_valid_votes
from .types import ParticipantRequest, DEFAULT_WEEKS, REQUESTABLE_PARAMETERS

from typing import Any, Union, List

# import timezonefinder

# Debugging
import time

# Influx authentication
db_user = os.environ["INFLUXDB_USER"]
db_password = os.environ["INFLUXDB_PASSWORD"]
db_host = "influxdb"
db_port = 8086
db_name = os.environ["INFLUXDB_NAME"]


def lambda_handler(
    id_participant: str,
    id_experiment: str,
    id_password: str,
    weeks: int,
    duration: Any,
    request: Union[List[str], None],
):

    print("Debugging")
    time_start = time.time()

    # Check if id_experiment, id_participant, id_password is provided, send error otherwise
    # if (("id_participant" not in event["queryStringParameters"]) or
    #    ("id_experiment" not in event["queryStringParameters"]) or
    #    ("id_password" not in event["queryStringParameters"])):
    #    return {
    #        "statusCode": 400,
    #        "body": json.dumps("id_participant, id_experiment, or id_password not in url-string"),
    #    }

    # Parse query string parameters
    #   id_participant = event["id_participant"]
    #   id_experiment = event["id_experiment"]
    #   id_password = event["id_password"]
    print("id_participant: ", id_participant)
    print("id_experiment: ", id_experiment)
    print("id_password: ", id_password)

    # Select the number of weeks to query data: Default is 2 weeks
    if not duration:
        weeks = DEFAULT_WEEKS

    # Influx client
    client = InfluxDBClient(db_host, db_port, db_user, db_password, db_name)

    # Query database
    # TODO: Fix this query and adjust it to the experiment in question
    query_influx = (
        f'SELECT "ws_survey_count", "ws_longitude", "ws_latitude", "ws_timestamp_start" '
        f'FROM "{db_name}"."autogen"."{id_experiment}" '
        f'WHERE "time" > now()-{weeks}w '
        f"AND \"id_participant\"='{id_participant}' "
        f'AND "ws_survey_count">=0 '
    )  #              f'AND "id_password"=\'{id_password}\''

    print("query influx: ", query_influx)
    result = client.query(query_influx)
    print("result: ", result)

    response_body = dict()

    # TODO: UPDATE According to the study
    if len(result) < 1:
        # Handle empty result set
        response_body["ws_survey_count_valid"] = "0"
        response_body["ws_survey_count_invalid"] = "0"
        response_body["ws_timestamp_survey_last"] = "-"
    else:
        # TODO: UPDATE According to the study
        # Convert result from database to dataframe
        df = pd.DataFrame.from_dict(result[id_experiment])
        # Convert 'time' column to datetime-index
        df["time"] = pd.to_datetime(df["time"])
        df["time"] = df["time"].dt.tz_localize(None)
        df.index = df["time"]
        df = df.drop(["time"], axis=1)

        # Check valid votes
        df_valid_only = keep_valid_votes(df)

        # Get last timestamp of last watch survey
        ws_timestamp_last = pd.to_datetime(
            df["ws_timestamp_start"][-1],
            format="%Y-%m-%dT%H:%M:%S.%f%z",
            errors="coerce",
        )

        # Get timezone from ws_timestamp_last
        # timezone_target = ws_timestamp_last.tzinfo

        # Retrieve requested parameters
        # response_body["ws_survey_count"]       = str(df["ws_survey_count"].notna().count())
        response_body["ws_survey_count_valid"] = str(
            df["ws_survey_count"].notna().count()
        )
        response_body["ws_survey_count_invalid"] = str(
            df["ws_survey_count"].notna().count()
            - df_valid_only["ws_survey_count"].notna().count()
        )
        # response_body["ws_timestamp_survey_last"]= df.index[-1].strftime('%d.%m.%Y - %H:%M')
        # response_body["ws_timestamp_survey_last"]= df.index[-1].tz_localize('UTC').tz_convert(timezone_target).strftime('%d.%m.%Y - %H:%M')
        response_body["ws_timestamp_survey_last"] = (
            df.index[-1].tz_localize("UTC").strftime("%d.%m.%Y - %H:%M")
        )

    print("response_body")
    print(response_body)

    # Remove parameters that were not requested
    request_parameters = []
    if not request == None:
        print(request)
        for parameter in REQUESTABLE_PARAMETERS:
            if parameter not in request:
                print("pop ", parameter)
                response_body.pop(parameter)

    # Return requested parameters to requestor
    return response_body
