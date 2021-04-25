import asyncio
import json
import typing

from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
from app.core.config import KAFKA_INSTANCE, PROJECT_NAME, TOPIC_NAME
from app.core.models.model import ConsumerResponse
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from loguru import logger
from icecream import ic

app = FastAPI(title=PROJECT_NAME)
topicname = TOPIC_NAME
consumer = None


context = create_ssl_context(
    cafile="./ca.pem",  # CA used to sign certificate.
    # `CARoot` of JKS store container
    certfile="./service.cert",  # Signed certificate
    keyfile="./service.key",  # Private Key file of `certfile` certificate
)


async def consume(consumer, topicname):
    async for msg in consumer:
        return msg.value.decode()


@app.on_event("startup")
async def initialize_consumer():
    global consumer
    loop = asyncio.get_running_loop()
    consumer = AIOKafkaConsumer(
        topicname,
        loop=loop,
        client_id=PROJECT_NAME,
        bootstrap_servers=KAFKA_INSTANCE,
        security_protocol="SSL",
        ssl_context=context,
        enable_auto_commit=False,
    )

    await consumer.start()


@app.on_event("startup")
@repeat_every(seconds=0.5)
async def startup_event():
    async def send_consumer_message(db, topicname: str) -> None:
        counter = 0
        while True:
            data = await consume(consumer, topicname)
            response = ConsumerResponse(topic=topicname, **json.loads(data))
            logger.info(response)
            logger.info(response.json())
            logger.info(data)
            counter = counter + 1

    data = await consume(consumer, topicname)
    logger.info(data)
    await send_consumer_message(db=None, topicname=topicname)


@app.on_event("shutdown")
async def shutdown_event():
    await consumer.stop()


@app.get("/ping")
def ping():
    return {"ping": "pong!"}
