from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="Auth Service",
    root_path="/api/v1/auth",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
router = APIRouter()


@router.post("/login")
async def login():
    return {"message": "Successfully access!", "service": "auth"}


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
