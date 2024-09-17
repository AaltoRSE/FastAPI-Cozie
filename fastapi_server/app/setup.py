from influxdb import InfluxDBClient
import os
import logging

logger = logging.getLogger("uvicorn.error")

# Initialize InfluxDB client


def setup_db():
    influx_client = InfluxDBClient(
        "influxdb",
        8086,
        os.environ["INFLUXDB_USER"],
        os.environ["INFLUXDB_PASSWORD"],
        os.environ["INFLUXDB_NAME"],
    )

    databases = influx_client.get_list_database()
    for db in databases:
        logger.debug(db)
        if db["name"] == os.environ["INFLUXDB_NAME"]:
            logger.debug("DB exists, returning")
            return
    logger.debug(f"Creating DB {os.environ['INFLUXDB_NAME']}")
    influx_client.create_database(os.environ["INFLUXDB_NAME"])
