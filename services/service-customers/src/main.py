import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from src.dependencies.db_dependency import db_dependency
from src.dao.outbox_dao import OutboxDAO
from src.kafka.consumer import customer_events_consumer
from src.kafka.event_stream import event_stream
from src.kafka.relay import OutboxRelay
from src.routes.customer import router as customers_router
from src.routes.demo import router as demo_router

from .settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
relay: OutboxRelay | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global relay

    logger.info("=== LIFESPAN START ===")
    logger.info(f"Kafka bootstrap: {settings.kafka.kafka_bootstrap_servers}")
    logger.info(f"Schema Registry: {settings.kafka.schema_registry_url}")

    try:
        logger.info("Initializing Kafka components...")
        outbox_dao = OutboxDAO(db_dependency)
        relay = OutboxRelay(outbox_dao)

        await relay.start()
        logger.info("✅ OutboxRelay started successfully")

        await customer_events_consumer.start()
        logger.info("✅ CustomerEventsConsumer started successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Kafka components: {e}", exc_info=True)
        raise

    yield

    logger.info("Stopping Kafka components...")
    await customer_events_consumer.stop()
    if relay:
        await relay.stop()
    logger.info("=== LIFESPAN END ===")


app = FastAPI(
    title="CUSTOMERS Service",
    root_path="/api/v1/customers",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/events")
async def customer_events():
    """SSE-поток клиентских событий Kafka в реальном времени."""
    from fastapi.responses import StreamingResponse

    async def event_generator():
        queue: asyncio.Queue[dict] = asyncio.Queue()

        async def subscriber(event):
            await queue.put(event)

        unsubscribe = event_stream.subscribe(subscriber)
        try:
            while True:
                payload = await queue.get()
                yield f"data: {json.dumps(payload, default=str)}\n\n"
        finally:
            unsubscribe()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


app.include_router(router)
app.include_router(demo_router)
app.include_router(customers_router)
