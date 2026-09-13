from fastapi import FastAPI, APIRouter

from src.routes.auth import router as auth_router


app = FastAPI(
    title="AUTH Service",
    root_path="/api/v1/auth",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
app.include_router(auth_router)
