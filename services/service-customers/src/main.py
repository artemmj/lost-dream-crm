import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from src.dependencies.db_dependency import db_dependency
from src.dao.outbox_dao import OutboxDAO
from src.kafka.relay import OutboxRelay
from src.routes.customer import router as customers_router

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
        # Запуск Outbox Relay
        logger.info("Initializing OutboxRelay...")
        outbox_dao = OutboxDAO(db_dependency)
        relay = OutboxRelay(outbox_dao)

        logger.info("Starting OutboxRelay...")
        await relay.start()
        logger.info("✅ OutboxRelay started successfully")

    except Exception as e:
        logger.error(f"❌ Failed to start OutboxRelay: {e}", exc_info=True)
        raise

    yield

    # Остановка
    logger.info("Stopping OutboxRelay...")
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


app.include_router(router)
app.include_router(customers_router)
