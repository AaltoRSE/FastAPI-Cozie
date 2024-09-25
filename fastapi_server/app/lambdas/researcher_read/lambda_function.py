# Cozie Apple Read API
# Purpose: Read data Cozie-Apple data from InfluxDB for researchers
# Author: Mario Frei, 2024
# Modifications by Thomas Pfau, 2024
# Status: Under development
# Project: Cozie-Apple

# Lesson learned: Saving dataframes as pickles is sensitive to the Pandas version.
# Pickle file made with one Pandas version, cannot necessarily be opened with another Pandas version
# Hence, the dataframe should be saved as as csv and then compressed as a zip
# lambda_function.py is in directory /var/task/
# /tmp/ is the directory for ephemeral storage

# For debugging:
# df_csv = pd.read_csv(filename_ephemeral_storage, compression={'method': 'zip', 'archive_name': 'sample.csv'})
# print("my test_csv:")
# print(df_csv.head())

import pandas as pd
import numpy as np
from influxdb import DataFrameClient
import os
from . import influx_prep
from typing import List
import tempfile

download_folder = os.environ.get("DOWNLOAD_FOLDER")


def lambda_handler(
    id_participant: str,
    id_password: str,
    id_experiment: str,
    columns: List[str],
    days: int,
):
    # Influx authentication
    db_user = os.environ["INFLUXDB_USER"]
    db_password = os.environ["INFLUXDB_PASSWORD"]
    db_host = "influxdb"
    db_port = 8086
    db_name = os.environ["INFLUXDB_NAME"]

    # Check if participant-id is provided, if not send 400 error
    print("id_participant", id_participant)
    print("id_experiment", id_experiment)
    print("id_password", id_password)
    print("columns", columns)
    print("days", days)

    # Influx client
    # No ned for SSL, since we cmmunicate within the docker network
    client = DataFrameClient(db_host, db_port, db_user, db_password, db_name)

    id_experiment = influx_prep.measurement(id_experiment)
    id_password = influx_prep.tag_value(id_password)
    id_participant = influx_prep.tag_value(id_participant)

    # Query all available tag keys
    query1 = f'SHOW FIELD KEYS FROM "{db_name}"."autogen"."{id_experiment}"'
    result1 = client.query(query1)
    points = result1.get_points()

    # Create list of all tag_keys in 'measurement'/'experiment_id'
    list_tag_key = []
    if columns == []:
        # Include all columns
        for item in points:
            list_tag_key.append(item["fieldKey"])
    else:
        # Only include specified columns
        for col in columns:
            if col in columns:
                list_tag_key.append(col)

    # Assemble query for Cozie data
    str_tag_keys = '"id_participant", "id_device", "id_password"'

    for my_tag_key in list_tag_key:
        str_tag_keys = str_tag_keys + ', "' + my_tag_key + '"'

    query2 = (
        "SELECT "
        + str_tag_keys
        + f' FROM "{db_name}"."autogen"."{id_experiment}" WHERE "id_participant"=\'{id_participant}\'AND "id_password"=\'{id_password}\''
    )
    if days != -1:
        query2 = query2 + f' AND "time">now()-{days}d'
    print(query2)

    # Query Cozie data
    result2 = client.query(query2, epoch="ns")

    try:
        df = pd.DataFrame.from_dict(result2[id_experiment])

    # no data for that query were available
    except KeyError:
        df = pd.DataFrame()

    # Drop columns with all elements equal to NaN
    df = df.dropna(axis=1, how="all")

    # Add nanosecond to preserve trail decimals for even timestamps
    # df.index  = df.index + pd.to_timedelta(1, unit='ns')

    # Replace None by NaN values
    df = df.fillna(value=np.nan)
    df = df.reset_index()

    print(df)

    # Convert to CSV
    file, path = tempfile.mkstemp(dir=download_folder, suffix=".h5")
    df.to_hdf(path, key="df", mode="w")

    return os.path.basename(path)
