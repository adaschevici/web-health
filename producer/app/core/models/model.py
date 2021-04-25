import uuid
from typing import Optional
from http import HTTPStatus
from datetime import datetime

from pydantic import BaseModel, confloat, StrictStr, StrictBool, validator


class ProducerMessage(BaseModel):
    name: StrictStr
    elapsed: confloat(gt=0)
    status: HTTPStatus
    content_found: Optional[StrictBool] = None
    message_id: StrictStr = ""
    timestamp: StrictStr = ""

    @validator("message_id", pre=True, always=True)
    def set_id_from_name_uuid(cls, v, values):
        if "name" in values:
            return f"{values['name']}_{uuid.uuid4()}"
        else:
            raise ValueError("name not set")

    @validator("timestamp", pre=True, always=True)
    def set_datetime_utcnow(cls, v):
        return str(datetime.utcnow())


class ProducerResponse(BaseModel):
    name: StrictStr
    message_id: StrictStr
    topic: StrictStr
    timestamp: StrictStr = ""

    @validator("timestamp", pre=True, always=True)
    def set_datetime_utcnow(cls, v):
        return str(datetime.utcnow())
