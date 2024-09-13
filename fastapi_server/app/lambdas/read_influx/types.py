from typing import List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, field_validator

REQUESTABLE_PARAMETERS = [
    "ws_survey_count_valid",
    "ws_survey_count_invalid",
    "ws_timestamp_survey_last",
]
DEFAULT_WEEKS = 100


class ParticipantData(BaseModel):
    id_experiment: str
    id_participant: str
    id_password: str
    weeks: float = DEFAULT_WEEKS
    duration: bool = False
    request: List[str] = []

    @field_validator("request")
    def check_elements(cls, value):
        if not value:
            raise ValueError("The list must contain at least one element.")
        invalid_elements = [v for v in value if v not in REQUESTABLE_PARAMETERS]
        if invalid_elements:
            raise ValueError(
                f"Invalid elements found: {invalid_elements}. Allowed values are: {REQUESTABLE_PARAMETERS}."
            )
        return value


# Needs to be updated to the actual models!
class ParticipantRequest(BaseModel):
    queryStringParameters: ParticipantData
