import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from src.dependencies.db_dependency import DBDependency
from src.dao.customer import CustomerDAO
from src.services.customer import (
    CustomerService,
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


# ===== Pydantic схемы =====


class CustomerCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    phone: str = Field(..., min_length=5, max_length=20, example="+1234567890")
    password_hash: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")
    middle_name: str = Field(..., min_length=1, max_length=100, example="Smith")


class CustomerUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    password_hash: Optional[str] = Field(None, min_length=8)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=100)


class CustomerResponse(BaseModel):
    id: int
    created_at: datetime.datetime  # datetime приходит как строка из JSON
    updated_at: datetime.datetime
    email: str
    phone: str
    password_hash: str
    first_name: str
    last_name: str
    middle_name: str

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    per_page: int


class BulkCreateRequest(BaseModel):
    customers: List[CustomerCreateRequest] = Field(..., min_items=1, max_items=100)


class BulkCreateResponse(BaseModel):
    created: int
    skipped: int
    skipped_emails: List[str]
    customers: List[CustomerResponse]


class EmailCheckRequest(BaseModel):
    emails: List[EmailStr] = Field(..., min_items=1, max_items=50)


class EmailCheckResponse(BaseModel):
    emails: dict


# ===== Dependency Injection =====


def get_customer_service(db: DBDependency = Depends()) -> CustomerService:
    """Фабрика сервиса с правильным графом зависимостей"""
    customer_dao = CustomerDAO(db)
    return CustomerService(customer_dao=customer_dao)


# ===== CRUD endpoints =====


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    request: CustomerCreateRequest,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Создание нового клиента"""
    try:
        dto = CustomerCreateDTO(**request.model_dump())
        return await customer_service.register_customer(dto)
    except CustomerAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Получение клиента по ID"""
    try:
        return await customer_service.get_customer(customer_id)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Список клиентов с пагинацией"""
    customers, total = await customer_service.list_customers(
        page=page,
        per_page=per_page,
    )
    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Частичное обновление клиента. Обновляются только переданные поля."""
    try:
        dto = CustomerUpdateDTO(**request.model_dump(exclude_unset=True))
        return await customer_service.update_customer(customer_id, dto)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CustomerAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Удаление клиента"""
    try:
        await customer_service.delete_customer(customer_id)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===== Специализированные endpoints =====


@router.post("/check-emails", response_model=EmailCheckResponse)
async def check_emails(
    request: EmailCheckRequest,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Проверка доступности email"""
    availability = await customer_service.check_emails_availability(request.emails)
    return EmailCheckResponse(emails=availability)


@router.post(
    "/bulk", response_model=BulkCreateResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_customers(
    request: BulkCreateRequest,
    customer_service: CustomerService = Depends(get_customer_service),
):
    """Массовое создание клиентов"""
    dtos = [CustomerCreateDTO(**c.model_dump()) for c in request.customers]
    result = await customer_service.bulk_create_customers(dtos)
    return result
