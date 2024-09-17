from typing import List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel


class Tags(BaseModel):
    id_onesignal: str
    id_participant: str
    id_password: str


# Needs to be updated to the actual models!
class ParticipantEntry(BaseModel):
    time: str
    measurement: str
    tags: Tags
    fields: Dict[str, Any]
