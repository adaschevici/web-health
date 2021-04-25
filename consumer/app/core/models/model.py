from http import HTTPStatus
from typing import Optional
from pydantic import BaseModel, StrictStr, confloat, StrictBool


class ConsumerResponse(BaseModel):
    topic: StrictStr
    timestamp: str
    name: StrictStr
    message_id: StrictStr
    elapsed: confloat(gt=0)
    status: HTTPStatus
    content_found: Optional[StrictBool] = None
