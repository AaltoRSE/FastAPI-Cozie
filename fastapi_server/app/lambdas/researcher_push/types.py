from typing import List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, field_validator


class PushData(BaseModel):
    id_experiment: str
    id_participant: str
    id_password: str
    message: str = ""
    heading: str = ""
    subtitle: str = ""
    buttons: Any = ""
