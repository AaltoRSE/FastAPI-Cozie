import logging
import logging.config

logging.config.fileConfig("app/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger("app")

from fastapi import FastAPI, Security, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Union, Any


from .lambdas.read_influx.types import REQUESTABLE_PARAMETERS
from .lambdas.write_queue.lambda_function import lambda_handler as write_queue
from .lambdas.write_queue.types import ParticipantEntry
from .lambdas.read_influx.lambda_function import lambda_handler as read_influx

from .lambdas.researcher_read.lambda_function import lambda_handler as researcher_read
from .lambdas.researcher_push.lambda_function import (
    lambda_handler as push_notifications,
)

import os
import json
from .setup import setup_db

setup_db()

app = FastAPI(title="Cozie-Backend", summary="API for Cozie backend")


api_key = APIKeyHeader(name="x-api-key")


def check_user_read_key(api_key: str = Security(api_key)):
    if api_key == None or not api_key == os.environ["USER_READ_KEY"]:
        raise HTTPException(401, "Invalid or missing API key")
    return True


def check_user_write_key(api_key: str = Security(api_key)):
    if api_key == None or not api_key == os.environ["USER_WRITE_KEY"]:
        raise HTTPException(401, "Invalid or missing API key")
    return True


def check_researcher_key(api_key: str = Security(api_key)):
    if api_key == None or not api_key == os.environ["RESEARCHER_KEY"]:
        raise HTTPException(401, "Invalid or missing API key")
    return True


download_folder = os.environ.get("DOWNLOAD_FOLDER")
# In-memory storage for demonstration purposes
participants_data = {}
researchers_data = {}


@app.post("/participant_write")
async def participant_write(
    data: Union[ParticipantEntry, List[ParticipantEntry]],
    accessOK=Security(check_user_write_key),
):

    return write_queue(data)


@app.get("/participant_read")
async def participant_read(
    id_participant: str = Query(..., example="dev01"),
    id_experiment: str = Query(..., example="myexperiment"),
    id_password: str = Query(..., example="mypassword"),
    request: str = Query(..., example=str(REQUESTABLE_PARAMETERS)),
    weeks: int = 1,
    duration: Any = None,
    access=Security(check_user_read_key),
):
    return read_influx(
        id_participant=id_participant,
        id_experiment=id_experiment,
        id_password=id_password,
        weeks=weeks,
        duration=duration,
        request=json.loads(request),
    )


@app.post("/researcher_read")
async def read_research_data(
    id_participant: str = Query(..., example="dev01"),
    id_experiment: str = Query(..., example="myexperiment"),
    id_password: str = Query(..., example="mypassword"),
    columns: List[str] = Query(
        ..., example='["q_preference_thermal","q_preference_noise"]'
    ),
    days: int = -1,
    accessOK=Security(check_researcher_key),
):
    dlID = researcher_read(
        {
            "id_participant": id_participant,
            "id_experiment": id_experiment,
            "id_password": id_password,
            "columns": columns,
            "days": days,
        }
    )
    return {"url": dlID}


def remove_file(file_path: str):
    os.remove(file_path)
    print(f"File {file_path} has been deleted")


@app.post("/load_data/{file_id}")
async def load_data(
    file_id: str,
    background_tasks: BackgroundTasks,
    accessOK=Security(check_researcher_key),
):
    file_path = os.path.join(download_folder, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    response = FileResponse(
        file_path, media_type="application/zip", filename=f"{file_path}.zip"
    )
    background_tasks.add_task(remove_file, file_path)
    return response


@app.post("/researcher_push")
async def push_notifications(data: str, accessOK=Security(check_researcher_key)):
    return push_notifications(data)
