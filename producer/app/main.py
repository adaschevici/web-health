import asyncio
from typing import Optional
from json import loads, dumps
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from icecream import ic
from loguru import logger

from app.core.config import (
    KAFKA_INSTANCE, PROJECT_NAME, ONCE_EVERY, URLS_FILE, TOPIC_NAME)
from app.core.models.model import ProducerMessage
from app.core.models.model import ProducerResponse
from app.metrics.gather import gather


app = FastAPI(title=PROJECT_NAME)

urls = []


aioproducer = None
topicname = TOPIC_NAME

context = create_ssl_context(
    cafile="./ca.pem",  # CA used to sign certificate.
    # `CARoot` of JKS store container
    certfile="./service.cert",  # Signed certificate
    keyfile="./service.key",  # Private Key file of `certfile` certificate
)


@app.on_event("startup")
async def startup_event():
    global aioproducer
    loop = asyncio.get_running_loop()
    aioproducer = AIOKafkaProducer(
        loop=loop,
        client_id=PROJECT_NAME,
        bootstrap_servers=KAFKA_INSTANCE,
        security_protocol="SSL",
        ssl_context=context
    )
    await aioproducer.start()


@app.on_event("startup")
def load_urls(urls_file: str = URLS_FILE):
    """
    Initialize the url list from config
    """
    with open(urls_file) as file_handler:
        urls.extend(loads(file_handler.read()))


@app.on_event("startup")
@repeat_every(seconds=ONCE_EVERY)
async def gather_metrics() -> None:
    """
    Gather metrics periodically for every url in list
    """
    for url in urls:
        regex = url.get("regex", None)
        link = url.get("url", None)
        if regex is None:
            res = gather(link)
        else:
            res = gather(link, regex)
        await aioproducer.send(topicname, dumps(res.dict()).encode("ascii"))


@app.on_event("shutdown")
async def shutdown_event():
    await aioproducer.stop()


@app.post("/check/")
async def check_url(
    url: str,
    regex: Optional[str] = None,
    topicname: str = "sitehealth"
) -> JSONResponse:
    """
    Endpoint to gather metrics for specified url
    """
    if regex is not None:
        res = gather(url, regex)
    else:
        res = gather(url)

    await aioproducer.send(topicname, dumps(res.dict()).encode("ascii"))
    response = ProducerResponse(
        name=res.name, message_id=res.message_id, topic=topicname
    )
    logger.info(response)
    return JSONResponse(status_code=200, content=response)


@app.get("/ping")
async def ping():
    """
    Sanity check endpoint
    """
    return {"ping": "pong!"}
