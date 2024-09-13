from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Union

from .lambdas.write_queue.lambda_function import lambda_handler as write_queue
from .lambdas.write_queue.types import ParticipantEntry
from .lambdas.read_influx.lambda_function import lambda_handler as read_influx
from .lambdas.read_influx.types import ParticipantRequest
from .lambdas.researcher_read.lambda_function import lambda_handler as researcher_read
from .lambdas.researcher_push.lambda_function import (
    lambda_handler as push_notifications,
)

import os

app = FastAPI()


download_folder = os.environ.get("DOWNLOAD_FOLDER")
# In-memory storage for demonstration purposes
participants_data = {}
researchers_data = {}


class ResearcherData(BaseModel):
    researcher_id: str
    data: Dict


class ResearcherRead(BaseModel):
    researcher_id: str
    data: Dict


@app.post("/participant_write")
async def participant_write(data: Union[ParticipantEntry, List[ParticipantEntry]]):
    return write_queue(data)


@app.post("/participant_read")
async def participant_read(data: ParticipantRequest):
    return read_influx(data)


@app.post("/researcher_read")
async def read_research_data(
    id_participant: str,
    id_experiment: str,
    id_password: str,
    columns: List[str] = [],
    days: int = -1,
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
async def push_notifications(data: ResearcherData):
    return push_notifications(data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
