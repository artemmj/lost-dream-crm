from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="CRM Service",
    root_path="/api/v1/crm",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
