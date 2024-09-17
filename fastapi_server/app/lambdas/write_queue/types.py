from typing import List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class Tags(BaseModel):
    id_onesignal: str = Field(..., example="12345678-1234-1234-1234-123456789012")
    id_participant: str = Field(..., example="dev01")
    id_password: str = Field(..., example="mypassword")


# Needs to be updated to the actual models!
class ParticipantEntry(BaseModel):
    time: str = Field(..., example="2022-09-02T05:03:21.066+0800")
    measurement: str = Field(..., example="myexperiment")
    tags: Tags
    fields: Dict[str, Any] = Field(
        ...,
        example={
            "ws_survey_count": 3,
            "ws_timestamp_start": "2022-09-02T05:03:21.066+0800",
            "ws_timestamp_location": "2022-09-02T05:01:22.645+0800",
            "ws_longitude": 103.77041753262827,
            "ws_latitude": 1.2965471870539595,
            "ws_altitude": 73.4,
            "ws_location_floor": 3,
            "ws_location_accuracy_horizontal": 5.4,
            "ws_location_accuracy_vertical": 2.8,
            "ws_location_acquisition_method": "GPS",
            "ws_location_source_device": "Apple Watch",
            "q_preference_thermal": "No Change",
            "q_preference_noise": "Quieter",
            "q_noise_source": "Appliances",
            "q_headphones": "No",
            "q_preference": "Cooler",
            "transmit_trigger": "watch_survey",
        },
    )
