from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.routes.user import router as users_router
from src.routes.permissions import router as perm_router
from src.routes.testing import router as testing_router

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app = FastAPI(
    title="CRM Service",
    root_path="/api/v1/crm",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешает запросы с указанных сайтов
    allow_credentials=True,  # Разрешает передачу куки и заголовков авторизации
    allow_methods=["*"],  # Разрешает все HTTP-методы (GET, POST, PUT и т.д.)
    allow_headers=["*"],  # Разрешает все HTTP-заголовки
)

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
app.include_router(users_router)
app.include_router(perm_router)
app.include_router(testing_router)
