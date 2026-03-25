# Backend Standards

> Backend development standards: Python, FastAPI, error handling, testing

**Compiled**: 2026-03-09 07:00
**Source**: evolv-coder-standards
**Domain Version**: 1.0.0

---

## Contents

- [Tech Stack](#tech-stack)
- [Python](#python)
- [Error Handling](#error-handling)
- [Testing](#testing)

---

<!-- Source: standards/backend/tech-stack.md (v1.0.0) -->

# Backend Tech Stack Standard

**Version**: 1.0.0
**Last Updated**: 2026-01-04
**Status**: Active

## Overview
This document establishes the comprehensive backend technology stack, architecture patterns, and best practices for building scalable, maintainable, and performant Python APIs with FastAPI.

## Tech Stack Summary

### Core Framework
- **Python 3.12+** - Programming language
- **uv** - Fast Python package manager and project tool
- **FastAPI 0.115+** - Modern async web framework
- **Pydantic v2** - Data validation and settings
- **uvicorn + gunicorn** - ASGI server

### Database & ORM
- **PostgreSQL 16+** - Primary database
- **SQLAlchemy 2.0+** - Async ORM
- **asyncpg** - Async PostgreSQL driver
- **Alembic** - Database migrations

### Caching & Task Queue
- **Redis 7+** - Caching and message broker
- **Celery 5.4+** - Distributed task queue
- **redis-py** - Redis client

### Authentication & Security
- **python-jose[cryptography]** - JWT tokens
- **passlib[bcrypt]** - Password hashing
- **python-multipart** - File uploads

### Email Services
- **Resend** - Modern transactional email API
- **resend-python** - Official Python SDK

### HTTP & Networking
- **httpx** - Async HTTP client
- **slowapi** - Rate limiting

### Code Quality
- **Black** - Code formatter
- **Ruff** - Fast Python linter
- **mypy** - Static type checker
- **pre-commit** - Git hook framework

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage
- **httpx** - Test client
- **faker** - Test data generation

### Logging & Monitoring
- **loguru** - Enhanced logging
- **Sentry** - Error tracking and performance monitoring

### Configuration & Environment
- **pydantic-settings** - Settings management
- **python-dotenv** - Environment variables

### Container & Deployment
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration

## Package Management with uv

### Why uv?
- **10-100x faster** than pip and pip-tools
- **Drop-in replacement** for pip, pip-tools, and virtualenv
- **Unified toolchain** for Python version management, virtual environments, and package management
- **Lockfile support** for reproducible builds
- **Project management** with `pyproject.toml`

### Installation
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew
brew install uv
```

### Project Setup
```bash
# Initialize a new project
uv init my-project
cd my-project

# Or initialize in existing directory
uv init

# Create virtual environment with specific Python version
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

### pyproject.toml Configuration
```toml
[project]
name = "my-fastapi-app"
version = "1.0.0"
description = "FastAPI backend application"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "redis>=5.2.0",
    "celery>=5.4.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.12",
    "httpx>=0.28.0",
    "resend>=2.5.0",
    "loguru>=0.7.2",
    "sentry-sdk[fastapi]>=2.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "faker>=33.0.0",
    "black>=24.10.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "faker>=33.0.0",
    "black>=24.10.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
]
```

### Common Commands
```bash
# Install dependencies from pyproject.toml
uv sync

# Install with dev dependencies
uv sync --all-extras

# Add a production dependency
uv add fastapi

# Add a dev dependency
uv add --dev pytest

# Remove a dependency
uv remove httpx

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add fastapi --upgrade

# Run a command in the virtual environment
uv run python -m pytest
uv run uvicorn app.main:app --reload

# Export requirements.txt (for Docker compatibility)
uv pip compile pyproject.toml -o requirements.txt

# Install from requirements.txt
uv pip install -r requirements.txt
```

### Lock File
uv generates a `uv.lock` file for reproducible builds:
```bash
# Generate/update lock file
uv lock

# Install from lock file (exact versions)
uv sync --frozen

# Check if lock file is up to date
uv lock --check
```

### CI/CD Integration
```yaml
# GitHub Actions example
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest

      - name: Run linting
        run: |
          uv run ruff check .
          uv run black --check .
          uv run mypy .
```

### Docker Integration
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev dependencies)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration and settings
├── dependencies.py         # Shared dependencies
│
├── api/                    # API layer
│   ├── __init__.py
│   ├── deps.py             # API-specific dependencies
│   └── routers/            # Route handlers
│       ├── __init__.py
│       ├── users.py
│       ├── orders.py
│       └── health.py
│
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── security.py         # Authentication/authorization
│   ├── exceptions.py       # Custom exceptions
│   └── middleware.py       # Custom middleware
│
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py             # Base model class
│   ├── user.py
│   └── order.py
│
├── schemas/                # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   ├── order.py
│   └── common.py           # Shared schemas
│
├── crud/                   # CRUD operations
│   ├── __init__.py
│   ├── base.py             # Base CRUD class
│   ├── user.py
│   └── order.py
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── user_service.py
│   └── order_service.py
│
├── tasks/                  # Celery tasks
│   ├── __init__.py
│   └── email_tasks.py
│
└── utils/                  # Utilities
    ├── __init__.py
    └── helpers.py

alembic/                    # Database migrations
├── env.py
├── script.py.mako
└── versions/

tests/                      # Test files
├── __init__.py
├── conftest.py             # Pytest fixtures
├── test_api/
├── test_crud/
└── test_services/
```

## FastAPI Application Setup

### Main Application (`app/main.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sentry_sdk

from app.config import settings
from app.api.routers import users, orders, health
from app.core.middleware import LoggingMiddleware
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
    yield
    # Shutdown
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(LoggingMiddleware)

    # Exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
    app.include_router(orders.router, prefix=f"{settings.API_V1_PREFIX}/orders", tags=["orders"])

    return app


app = create_app()
```

### Configuration (`app/config.py`)

```python
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    PROJECT_NAME: str = "FastAPI Application"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Clerk (Authentication)
    CLERK_SECRET_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""

    # Email
    RESEND_API_KEY: str = ""

    # Monitoring
    SENTRY_DSN: str = ""


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

## Database Setup

### Database Connection (`app/core/database.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Base Model (`app/models/base.py`)

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declared_attr

from app.core.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class BaseModel(Base, TimestampMixin):
    """Base model with common fields."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # UserModel -> users, OrderItem -> order_items
        import re
        name = re.sub(r"Model$", "", cls.__name__)
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return f"{name}s"
```

### Example Model (`app/models/user.py`)

```python
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
```

## Pydantic Schemas

### Schema Patterns (`app/schemas/user.py`)

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# Base schema with common fields
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


# Schema for creating
class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


# Schema for updating
class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


# Schema for reading (from database)
class UserResponse(UserBase):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Schema for internal use (includes sensitive data)
class UserInDB(UserResponse):
    """Schema for user in database (internal use)."""
    hashed_password: str
```

## CRUD Operations

### Base CRUD (`app/crud/base.py`)

```python
from typing import Generic, TypeVar, Type, Optional, List, Any
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel as DBBaseModel


ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class with common operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """Count total records."""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
```

## API Router Pattern

### Router Example (`app/api/routers/users.py`)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserResponse]:
    """List all users with pagination."""
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get a specific user by ID."""
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Create a new user."""
    # Check if user already exists
    existing = await user_crud.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await user_crud.create(db, obj_in=user_in)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update an existing user."""
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = await user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a user."""
    user = await user_crud.delete(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
```

## Exception Handling

### Custom Exceptions (`app/core/exceptions.py`)

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "APP_ERROR",
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    """Unauthorized access."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """Access forbidden."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up exception handlers for the application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "detail": "An unexpected error occurred",
            },
        )
```

## Logging Configuration

### Loguru Setup

```python
import sys
from loguru import logger

from app.config import settings


def setup_logging() -> None:
    """Configure loguru logging."""

    # Remove default handler
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    # File handler for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # File handler for all logs
    if not settings.DEBUG:
        logger.add(
            "logs/app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            rotation="50 MB",
            retention="7 days",
            compression="zip",
        )
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Type checking passes (`uv run mypy .`)
- [ ] Code formatted (`uv run black .`)
- [ ] Database migrations up to date
- [ ] Environment variables documented
- [ ] Secrets rotated if needed

### Production Configuration

- [ ] DEBUG = False
- [ ] Proper DATABASE_URL with SSL
- [ ] Secure SECRET_KEY (32+ random bytes)
- [ ] CORS_ORIGINS restricted to actual domains
- [ ] Sentry DSN configured
- [ ] Rate limiting enabled
- [ ] Logging configured for production
- [ ] Health checks implemented

### Infrastructure

- [ ] Database connection pooling configured
- [ ] Redis configured for caching/sessions
- [ ] SSL/TLS certificates installed
- [ ] Reverse proxy (nginx) configured
- [ ] Process manager (gunicorn) configured
- [ ] Monitoring/alerting set up

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)
- [Resend Documentation](https://resend.com/docs)
- [loguru Documentation](https://loguru.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

---

*Last updated: December 2025*

---

<!-- Source: standards/backend/python.md (v1.0.0) -->

# Python Coding Standards

**Version**: 1.0.0
**Last Updated**: 2026-01-04
**Status**: Active

## Overview
This document outlines Python coding standards and best practices for consistent, maintainable, and high-quality code.

## Style Guide Foundation
- **PEP 8**: The official Python style guide - foundation for all Python code
- **PEP 257**: Documentation conventions for docstrings
- **Type Hints (PEP 484)**: Use type annotations for better code clarity and IDE support

## Code Formatting

### Line Length
- Maximum line length: **88 characters** (Black formatter default)
- For comments and docstrings: **72 characters**

### Imports
```python
# Standard library imports
import os
import sys
from typing import List, Optional, Dict

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local application imports
from app.models import User
from app.services import UserService
```

**Import Order:**
1. Standard library imports
2. Related third-party imports
3. Local application/library specific imports
4. Separate each group with a blank line

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables/Functions | snake_case | `user_name`, `get_user()` |
| Classes | PascalCase | `UserModel`, `DataProcessor` |
| Constants | UPPER_SNAKE_CASE | `MAX_CONNECTIONS`, `API_KEY` |
| Private methods | _leading_underscore | `_internal_method()` |
| "Dunder" methods | __double_underscore__ | `__init__()`, `__str__()` |
| Modules/Files | snake_case.py | `user_service.py`, `api_client.py` |
| Packages/Folders | snake_case | `api/`, `services/`, `user_management/` |
| Pydantic Models | PascalCase | `UserCreate`, `OrderResponse` |
| SQLAlchemy Models | PascalCase (singular) | `User`, `Order`, `OrderItem` |

## Type Hints

Always use type hints for function parameters and return values:

```python
from typing import Optional, List, Dict

def process_user_data(
    user_id: int,
    name: str,
    email: Optional[str] = None
) -> Dict[str, any]:
    """Process user data and return formatted result."""
    return {"id": user_id, "name": name, "email": email}

def get_users(limit: int = 10) -> List[Dict[str, any]]:
    """Retrieve list of users."""
    pass
```

## Documentation

### Docstrings
Use Google-style or NumPy-style docstrings:

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate the final price after applying discount.

    Args:
        price: Original price of the item
        discount_percent: Discount percentage (0-100)

    Returns:
        Final price after discount

    Raises:
        ValueError: If discount_percent is not between 0 and 100
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

### Comments
- Use comments sparingly - code should be self-documenting
- Explain **why**, not **what**
- Keep comments up-to-date with code changes

## Error Handling

### Use Specific Exceptions
```python
# Good
try:
    user = get_user(user_id)
except UserNotFoundError:
    raise HTTPException(status_code=404, detail="User not found")

# Avoid bare except
try:
    risky_operation()
except Exception as e:  # Be specific when possible
    logger.error(f"Operation failed: {e}")
    raise
```

### FastAPI Error Handling
```python
from fastapi import HTTPException, status

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> User:
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user
```

## Best Practices

### 1. Use Context Managers
```python
# Good - automatic resource cleanup
with open("file.txt", "r") as f:
    content = f.read()

# Good - database sessions
async with get_db_session() as session:
    user = await session.get(User, user_id)
```

### 2. List Comprehensions
```python
# Good - concise and readable
active_users = [user for user in users if user.is_active]

# For complex logic, use regular loops
filtered_users = []
for user in users:
    if user.is_active and user.age > 18:
        filtered_users.append(user)
```

### 3. Use Enums for Constants
```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

### 4. Avoid Mutable Default Arguments
```python
# Bad
def add_item(item, items=[]):
    items.append(item)
    return items

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 5. Use Pathlib for File Operations
```python
from pathlib import Path

# Good - cross-platform
data_dir = Path("data")
config_file = data_dir / "config.json"

if config_file.exists():
    content = config_file.read_text()
```

## FastAPI Specific Standards

### Dependency Injection
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    return await db.get(User, user_id)
```

### Pydantic Models
```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8)
    age: Optional[int] = Field(None, ge=0, le=120)

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()
```

### Router Organization
```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}")
async def get_user(user_id: int):
    pass

@router.post("/")
async def create_user(user: UserCreate):
    pass
```

## Testing Standards

### Test Structure
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test user creation endpoint."""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "securepass123"
    }

    # Act
    response = await client.post("/users", json=user_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### Fixtures
```python
@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user."""
    user = User(email="test@example.com")
    db.add(user)
    await db.commit()
    yield user
    await db.delete(user)
    await db.commit()
```

## Code Quality Tools

### Essential Tools
- **Black**: Code formatter (opinionated)
- **isort**: Import sorting
- **flake8** or **ruff**: Linting
- **mypy**: Static type checking
- **pytest**: Testing framework

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
```

## Security Best Practices

1. **Never commit secrets** - use environment variables
2. **Validate all input** - use Pydantic models
3. **Use parameterized queries** - prevent SQL injection
4. **Hash passwords** - use bcrypt or argon2
5. **Enable CORS properly** - don't use `allow_origins=["*"]` in production

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Considerations

1. **Use async/await** for I/O operations
2. **Implement connection pooling** for databases
3. **Add appropriate indexes** to database tables
4. **Use caching** for frequently accessed data
5. **Implement pagination** for large datasets

```python
@app.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[User]:
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()
```

## Version Control

- Commit messages: Use conventional commits format
  - `feat: add user authentication`
  - `fix: resolve email validation bug`
  - `docs: update API documentation`
  - `refactor: simplify user service logic`
- Keep commits atomic and focused
- Write descriptive pull request descriptions

## Related Patterns

For implementation approaches and code examples:

- [Python Patterns](../../patterns/backend/python-patterns.md) - Error handling, DI, async, Pydantic, testing
- [Backend Examples](../../examples/backend/) - Filled implementations

## References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Real Python Style Guide](https://realpython.com/python-pep8/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

*Last updated: January 2026*

---

<!-- Source: standards/backend/error-handling.md (v1.0.0) -->

# Backend Error Handling Standard

**Version**: 1.0.0
**Last Updated**: 2025-12-30
**Status**: Active

## Purpose

This standard defines error handling patterns for FastAPI backend applications, including exception hierarchy, error responses, validation handling, and error recovery strategies.

**Error format**: All errors must follow the contract defined in [Error Response Contract](../architecture/error-contract.md). This document covers backend-specific implementation patterns.

## Scope

- Custom exception hierarchy
- Standardized error response format
- HTTP status code mapping
- Validation error handling
- Database error handling
- External service error handling
- Error logging and recovery

---

## Standard Error Response Format

### JSON Schema

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": {
      "resource_type": "user",
      "resource_id": "123"
    },
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Pydantic Schema

```python
# app/schemas/error.py
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Standard error response."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        None, description="Additional error context"
    )
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ValidationErrorItem(BaseModel):
    """Single validation error."""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    code: str = "VALIDATION_ERROR"
    message: str = "Request validation failed"
    errors: list[ValidationErrorItem]
    request_id: Optional[str] = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

---

## Exception Hierarchy

### Base Exceptions

```python
# app/core/exceptions.py
from typing import Any, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation errors (422)."""

    def __init__(
        self,
        message: str = "Validation failed",
        errors: list[dict] | None = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": errors or []},
        )
        self.errors = errors or []


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(
        self,
        resource: str,
        identifier: Any,
        message: str | None = None,
    ):
        super().__init__(
            message=message or f"{resource} with ID {identifier} not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictException(AppException):
    """Resource conflict (409)."""

    def __init__(
        self,
        message: str,
        resource: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(
            message=message,
            code="RESOURCE_CONFLICT",
            status_code=409,
            details=details or {"resource": resource},
        )


class UnauthorizedException(AppException):
    """Authentication required (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenException(AppException):
    """Access denied (403)."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: str | None = None,
        action: str | None = None,
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details={"resource": resource, "action": action},
        )


class BadRequestException(AppException):
    """Bad request (400)."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=400,
            details=details,
        )


class RateLimitException(AppException):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after},
        )
        self.retry_after = retry_after


class ServiceUnavailableException(AppException):
    """Service unavailable (503)."""

    def __init__(
        self,
        service: str,
        message: str | None = None,
    ):
        super().__init__(
            message=message or f"Service {service} is temporarily unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"service": service},
        )
```

### Domain-Specific Exceptions

```python
# app/core/exceptions.py (continued)

class DatabaseException(AppException):
    """Database operation errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: str | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details={
                "operation": operation,
                "original_error": str(original_error) if original_error else None,
            },
        )


class ExternalServiceException(AppException):
    """External service errors."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = 502,
        response_status: int | None = None,
    ):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status_code,
            details={
                "service": service,
                "response_status": response_status,
            },
        )


class BusinessRuleException(AppException):
    """Business rule violations."""

    def __init__(
        self,
        rule: str,
        message: str,
        details: dict | None = None,
    ):
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            status_code=422,
            details={"rule": rule, **(details or {})},
        )
```

---

## Exception Handlers

### Global Exception Handler

```python
# app/core/exception_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppException, DatabaseException
from app.core.logging import logger, correlation_id_var
from app.schemas.error import ErrorDetail, ValidationErrorResponse, ValidationErrorItem


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.error(
            exc.message,
            code=exc.code,
            status_code=exc.status_code,
            details=exc.details,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorDetail(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(
                ValidationErrorItem(
                    field=field,
                    message=error["msg"],
                    value=error.get("input"),
                )
            )

        logger.warning(
            "Validation error",
            errors=[e.model_dump() for e in errors],
            path=request.url.path,
        )

        return JSONResponse(
            status_code=422,
            content=ValidationErrorResponse(
                errors=errors,
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle Starlette HTTP exceptions."""
        logger.warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorDetail(
                code=HTTP_STATUS_CODES.get(exc.status_code, "HTTP_ERROR"),
                message=exc.detail or "An error occurred",
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """Handle database integrity errors."""
        logger.error(
            "Database integrity error",
            error=str(exc.orig),
            path=request.url.path,
        )

        # Parse constraint violation
        message = "Database constraint violation"
        if "unique" in str(exc.orig).lower():
            message = "A record with this value already exists"

        return JSONResponse(
            status_code=409,
            content=ErrorDetail(
                code="INTEGRITY_ERROR",
                message=message,
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle general SQLAlchemy errors."""
        logger.exception(
            "Database error",
            error=str(exc),
            path=request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content=ErrorDetail(
                code="DATABASE_ERROR",
                message="A database error occurred",
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        logger.exception(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                request_id=correlation_id_var.get(),
            ).model_dump(mode="json"),
        )


# HTTP status code to error code mapping
HTTP_STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
    504: "GATEWAY_TIMEOUT",
}
```

---

## Using Exceptions in Code

### Service Layer

```python
# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    BusinessRuleException,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        """Get user by ID or raise NotFoundException."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User", user_id)

        return user

    async def create(self, data: UserCreate) -> User:
        """Create a new user."""
        # Check for existing email
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                message=f"User with email {data.email} already exists",
                resource="user",
                details={"email": data.email},
            )

        user = User(**data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        user = await self.get_by_id(user_id)

        # Business rule check
        if user.is_admin:
            raise BusinessRuleException(
                rule="admin_deletion",
                message="Admin users cannot be deleted",
                details={"user_id": user_id},
            )

        await self.db.delete(user)
        await self.db.commit()
```

### Router Layer

```python
# app/api/routers/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.exceptions import ForbiddenException
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    service = UserService(db)
    return await service.get_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    service = UserService(db)
    return await service.create(data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only)."""
    if "admin" not in current_user.get("roles", []):
        raise ForbiddenException(
            message="Only admins can delete users",
            resource="user",
            action="delete",
        )

    service = UserService(db)
    await service.delete(user_id)
```

---

## External Service Error Handling

### HTTP Client Wrapper

```python
# app/services/http_client.py
import httpx
from typing import Any, TypeVar, Type
from pydantic import BaseModel

from app.core.exceptions import (
    ExternalServiceException,
    ServiceUnavailableException,
)
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class HttpClient:
    """HTTP client with error handling."""

    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: float = 30.0,
    ):
        self.base_url = base_url
        self.service_name = service_name
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def get(
        self,
        path: str,
        response_model: Type[T],
        **kwargs,
    ) -> T:
        """GET request with error handling."""
        return await self._request("GET", path, response_model, **kwargs)

    async def post(
        self,
        path: str,
        response_model: Type[T],
        json: dict | None = None,
        **kwargs,
    ) -> T:
        """POST request with error handling."""
        return await self._request(
            "POST", path, response_model, json=json, **kwargs
        )

    async def _request(
        self,
        method: str,
        path: str,
        response_model: Type[T],
        **kwargs,
    ) -> T:
        """Execute request with error handling."""
        try:
            response = await self.client.request(method, path, **kwargs)

            if response.status_code >= 500:
                logger.error(
                    f"{self.service_name} server error",
                    status_code=response.status_code,
                    path=path,
                )
                raise ServiceUnavailableException(self.service_name)

            if response.status_code >= 400:
                error_body = response.json() if response.content else {}
                logger.warning(
                    f"{self.service_name} client error",
                    status_code=response.status_code,
                    path=path,
                    error=error_body,
                )
                raise ExternalServiceException(
                    service=self.service_name,
                    message=error_body.get("message", "External service error"),
                    status_code=response.status_code,
                    response_status=response.status_code,
                )

            return response_model.model_validate(response.json())

        except httpx.TimeoutException:
            logger.error(
                f"{self.service_name} timeout",
                path=path,
            )
            raise ServiceUnavailableException(
                self.service_name,
                message=f"{self.service_name} request timed out",
            )

        except httpx.ConnectError:
            logger.error(
                f"{self.service_name} connection failed",
                path=path,
            )
            raise ServiceUnavailableException(
                self.service_name,
                message=f"Could not connect to {self.service_name}",
            )
```

### Using External Services

```python
# app/services/payment_service.py
from app.services.http_client import HttpClient
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.core.exceptions import ExternalServiceException
from app.core.logging import logger


class PaymentService:
    def __init__(self, api_key: str):
        self.client = HttpClient(
            base_url="https://api.payments.example.com",
            service_name="payment_api",
        )
        self.api_key = api_key

    async def process_payment(
        self,
        request: PaymentRequest,
    ) -> PaymentResponse:
        """Process a payment with error handling."""
        try:
            return await self.client.post(
                "/v1/payments",
                response_model=PaymentResponse,
                json=request.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        except ExternalServiceException as e:
            # Map external errors to domain errors
            if "insufficient_funds" in str(e.details):
                raise BusinessRuleException(
                    rule="payment_insufficient_funds",
                    message="Payment failed due to insufficient funds",
                )
            raise
```

---

## Database Error Handling

### Transaction Error Handling

```python
# app/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import DatabaseException
from app.core.logging import logger


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order_with_items(
        self,
        order_data: OrderCreate,
        items: list[OrderItemCreate],
    ) -> Order:
        """Create order with items in a transaction."""
        try:
            # Start transaction
            async with self.db.begin_nested():
                # Create order
                order = Order(**order_data.model_dump())
                self.db.add(order)
                await self.db.flush()  # Get order ID

                # Create items
                for item_data in items:
                    item = OrderItem(
                        order_id=order.id,
                        **item_data.model_dump(),
                    )
                    self.db.add(item)

                await self.db.commit()
                await self.db.refresh(order)
                return order

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(
                "Failed to create order",
                error=str(e),
            )
            raise DatabaseException(
                message="Failed to create order",
                operation="create_order",
                original_error=e,
            )
```

### Retry Pattern for Deadlocks

```python
# app/core/database.py
import asyncio
from functools import wraps
from sqlalchemy.exc import OperationalError

from app.core.logging import logger


def retry_on_deadlock(max_retries: int = 3, delay: float = 0.1):
    """Retry decorator for database deadlocks."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except OperationalError as e:
                    if "deadlock" not in str(e).lower():
                        raise
                    last_error = e
                    logger.warning(
                        "Deadlock detected, retrying",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                    )
                    await asyncio.sleep(delay * (2 ** attempt))
            raise last_error

        return wrapper
    return decorator


# Usage
class InventoryService:
    @retry_on_deadlock(max_retries=3)
    async def update_stock(self, product_id: int, quantity: int):
        """Update stock with deadlock retry."""
        # Database operation that might deadlock
        pass
```

---

## Validation Error Handling

### Custom Validators

```python
# app/schemas/user.py
from pydantic import BaseModel, field_validator, model_validator
from app.core.exceptions import ValidationException


class UserCreate(BaseModel):
    email: str
    password: str
    password_confirm: str
    age: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a number")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

### Business Validation

```python
# app/services/order_service.py
from app.core.exceptions import ValidationException, BusinessRuleException


class OrderService:
    async def validate_order(self, order: OrderCreate) -> None:
        """Validate order before creation."""
        errors = []

        # Check minimum order amount
        if order.total < 10.00:
            errors.append({
                "field": "total",
                "message": "Minimum order amount is $10.00",
            })

        # Check item availability
        for i, item in enumerate(order.items):
            if not await self.is_available(item.product_id, item.quantity):
                errors.append({
                    "field": f"items[{i}].quantity",
                    "message": f"Insufficient stock for product {item.product_id}",
                })

        if errors:
            raise ValidationException(
                message="Order validation failed",
                errors=errors,
            )
```

---

## Error Recovery Strategies

### Circuit Breaker

```python
# app/core/circuit_breaker.py
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, TypeVar

from app.core.logging import logger

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime | None = None

    async def call(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise ServiceUnavailableException(
                    self.name,
                    message=f"Circuit breaker open for {self.name}",
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker opened",
                service=self.name,
                failure_count=self.failure_count,
            )

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if not self.last_failure_time:
            return True
        return datetime.now() > self.last_failure_time + timedelta(
            seconds=self.recovery_timeout
        )


# Usage
payment_circuit = CircuitBreaker("payment_api")

async def process_payment(data: dict):
    return await payment_circuit.call(payment_service.charge, data)
```

---

## Best Practices

### Do

- Use specific exception types for different error cases
- Include request IDs in all error responses
- Log errors with sufficient context
- Map external errors to domain exceptions
- Use transactions for multi-step operations
- Implement retry logic for transient failures
- Return consistent error response format
- Validate input at API boundaries

### Don't

- Expose internal error details in production
- Catch and swallow exceptions silently
- Use generic Exception for everything
- Return raw database errors to clients
- Mix HTTP status codes inconsistently
- Log sensitive data in error messages
- Retry non-idempotent operations blindly
- Forget to rollback failed transactions

---

## Related Standards

- [Python Standards](./python.md)
- [Backend Testing](./testing.md)
- [Frontend Error Handling](../frontend/error-handling.md)
- [Observability](../architecture/observability.md)

---

*Proper error handling makes applications robust and debugging efficient.*

---

<!-- Source: standards/backend/testing.md (v1.0.0) -->

# Backend Testing Standard

**Version**: 1.0.0
**Last Updated**: 2025-12-30
**Status**: Active

## Purpose

This standard defines testing patterns and best practices for FastAPI backend applications using pytest, async testing, and proper fixture management.

## Scope

- Unit testing with pytest
- Async testing patterns for FastAPI
- Database fixtures and cleanup
- API endpoint testing
- Mock/patch patterns for external services
- Coverage targets and CI integration

---

## Testing Stack

| Tool | Purpose | Use For |
|------|---------|---------|
| pytest | Test framework | All test types |
| pytest-asyncio | Async support | Async function tests |
| httpx | Async HTTP client | API endpoint tests |
| pytest-cov | Coverage reporting | Code coverage metrics |
| factory-boy | Test data factories | Consistent test data |
| freezegun | Time mocking | Date/time dependent tests |

---

## Project Setup

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "-ra",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 80
show_missing = true
```

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── factories/               # Factory Boy factories
│   ├── __init__.py
│   └── user.py
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── services/
│   │   └── test_user_service.py
│   └── utils/
│       └── test_validators.py
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_user_endpoints.py
└── fixtures/                # Test data fixtures
    └── sample_data.json
```

---

## Core Fixtures

### Database Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.main import app
from app.api.deps import get_db


# Test database URL (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session-scoped async fixtures."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession):
    """Create test client with database session override."""
    from httpx import AsyncClient, ASGITransport

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

### PostgreSQL Test Database (Alternative)

```python
# tests/conftest.py (PostgreSQL variant)
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine with transaction rollback."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """Create session with automatic rollback after each test."""
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
```

---

## Authentication Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_current_user():
    """Mock authenticated user for tests."""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "roles": ["user"],
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user for tests."""
    return {
        "user_id": "admin-user-456",
        "email": "admin@example.com",
        "roles": ["admin", "user"],
    }


@pytest.fixture
def authenticated_client(client, mock_current_user):
    """Client with mocked authentication."""
    with patch("app.api.deps.get_current_user", return_value=mock_current_user):
        yield client


@pytest.fixture
def admin_client(client, mock_admin_user):
    """Client with admin authentication."""
    with patch("app.api.deps.get_current_user", return_value=mock_admin_user):
        yield client
```

---

## Factory Patterns

### Using Factory Boy

```python
# tests/factories/user.py
import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        sqlalchemy_session = None  # Set in conftest.py
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker("email")
    name = factory.Faker("name")
    is_active = True
    created_at = factory.Faker("date_time_this_year")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to support async session."""
        return super()._create(model_class, *args, **kwargs)


class AdminUserFactory(UserFactory):
    """Factory for admin users."""
    is_admin = True
    email = factory.LazyAttribute(lambda o: f"admin_{o.id}@example.com")
```

### Configuring Factories with Session

```python
# tests/conftest.py
import pytest
from tests.factories.user import UserFactory


@pytest.fixture(autouse=True)
def configure_factories(db_session):
    """Configure factories to use test session."""
    UserFactory._meta.sqlalchemy_session = db_session


@pytest.fixture
async def user(db_session) -> User:
    """Create a single test user."""
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def users(db_session) -> list[User]:
    """Create multiple test users."""
    users = [UserFactory.build() for _ in range(5)]
    db_session.add_all(users)
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users
```

---

## Unit Testing

### Testing Services

```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.user_service import UserService
from app.schemas.user import UserCreate


class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_db):
        """Create UserService with mock database."""
        return UserService(db=mock_db)

    async def test_create_user_success(self, user_service, mock_db):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreate(
            email="new@example.com",
            name="New User",
            password="securepass123"
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        # Act
        result = await user_service.create(user_data)

        # Assert
        assert result.email == "new@example.com"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_create_user_duplicate_email(self, user_service, mock_db):
        """Test user creation with duplicate email."""
        # Arrange
        user_data = UserCreate(
            email="existing@example.com",
            name="User",
            password="password123"
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            await user_service.create(user_data)

    async def test_get_user_by_id(self, user_service, mock_db):
        """Test fetching user by ID."""
        # Arrange
        mock_user = MagicMock(id=1, email="test@example.com")
        mock_db.get.return_value = mock_user

        # Act
        result = await user_service.get_by_id(1)

        # Assert
        assert result.id == 1
        mock_db.get.assert_called_once()

    async def test_get_user_not_found(self, user_service, mock_db):
        """Test fetching non-existent user."""
        # Arrange
        mock_db.get.return_value = None

        # Act
        result = await user_service.get_by_id(999)

        # Assert
        assert result is None
```

### Testing Utility Functions

```python
# tests/unit/utils/test_validators.py
import pytest
from app.utils.validators import validate_email, validate_password, slugify


class TestEmailValidator:
    """Tests for email validation."""

    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("user.name@domain.co.uk", True),
        ("user+tag@example.com", True),
        ("invalid-email", False),
        ("@nodomain.com", False),
        ("spaces in@email.com", False),
        ("", False),
    ])
    def test_validate_email(self, email: str, expected: bool):
        """Test email validation with various inputs."""
        assert validate_email(email) == expected


class TestPasswordValidator:
    """Tests for password validation."""

    def test_valid_password(self):
        """Test password meeting all requirements."""
        result = validate_password("SecurePass123!")
        assert result.is_valid
        assert not result.errors

    def test_password_too_short(self):
        """Test password below minimum length."""
        result = validate_password("Short1!")
        assert not result.is_valid
        assert "at least 8 characters" in result.errors[0]

    def test_password_no_uppercase(self):
        """Test password without uppercase letter."""
        result = validate_password("nouppercase123!")
        assert not result.is_valid
        assert "uppercase" in result.errors[0].lower()

    @pytest.mark.parametrize("password", [
        "NoNumber!",
        "nonumber!lowercase",
    ])
    def test_password_no_number(self, password: str):
        """Test password without number."""
        result = validate_password(password)
        assert not result.is_valid


class TestSlugify:
    """Tests for slug generation."""

    @pytest.mark.parametrize("input_str,expected", [
        ("Hello World", "hello-world"),
        ("Multiple   Spaces", "multiple-spaces"),
        ("Special @#$ Characters!", "special-characters"),
        ("Already-Slugified", "already-slugified"),
        ("  Trim Spaces  ", "trim-spaces"),
    ])
    def test_slugify(self, input_str: str, expected: str):
        """Test slug generation from various inputs."""
        assert slugify(input_str) == expected
```

---

## Integration Testing

### API Endpoint Tests

```python
# tests/integration/test_user_endpoints.py
import pytest
from httpx import AsyncClient


class TestUserEndpoints:
    """Integration tests for user API endpoints."""

    async def test_create_user(self, client: AsyncClient):
        """Test POST /api/users creates a new user."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "SecurePass123!"
        }

        # Act
        response = await client.post("/api/users", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    async def test_create_user_invalid_email(self, client: AsyncClient):
        """Test POST /api/users with invalid email."""
        # Arrange
        user_data = {
            "email": "invalid-email",
            "name": "User",
            "password": "SecurePass123!"
        }

        # Act
        response = await client.post("/api/users", json=user_data)

        # Assert
        assert response.status_code == 422
        assert "email" in response.json()["detail"][0]["loc"]

    async def test_get_user(self, client: AsyncClient, user):
        """Test GET /api/users/{id} returns user."""
        # Act
        response = await client.get(f"/api/users/{user.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    async def test_get_user_not_found(self, client: AsyncClient):
        """Test GET /api/users/{id} with non-existent ID."""
        # Act
        response = await client.get("/api/users/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_list_users(self, client: AsyncClient, users):
        """Test GET /api/users returns paginated list."""
        # Act
        response = await client.get("/api/users?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) <= 10

    async def test_update_user(self, authenticated_client: AsyncClient, user):
        """Test PUT /api/users/{id} updates user."""
        # Arrange
        update_data = {"name": "Updated Name"}

        # Act
        response = await authenticated_client.put(
            f"/api/users/{user.id}",
            json=update_data
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    async def test_delete_user(self, admin_client: AsyncClient, user):
        """Test DELETE /api/users/{id} removes user."""
        # Act
        response = await admin_client.delete(f"/api/users/{user.id}")

        # Assert
        assert response.status_code == 204

        # Verify deletion
        get_response = await admin_client.get(f"/api/users/{user.id}")
        assert get_response.status_code == 404

    async def test_delete_user_unauthorized(self, client: AsyncClient, user):
        """Test DELETE /api/users/{id} requires authentication."""
        # Act
        response = await client.delete(f"/api/users/{user.id}")

        # Assert
        assert response.status_code == 401
```

---

## Mocking External Services

### Mocking HTTP Calls

```python
# tests/unit/services/test_external_api.py
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.services.payment_service import PaymentService


class TestPaymentService:
    """Tests for external payment API integration."""

    @pytest.fixture
    def payment_service(self):
        return PaymentService(api_key="test-key")

    async def test_process_payment_success(self, payment_service):
        """Test successful payment processing."""
        mock_response = httpx.Response(
            200,
            json={"transaction_id": "txn_123", "status": "completed"}
        )

        with patch.object(
            payment_service._client,
            "post",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await payment_service.process_payment(
                amount=100.00,
                currency="USD",
                card_token="card_abc"
            )

        assert result.transaction_id == "txn_123"
        assert result.status == "completed"

    async def test_process_payment_failure(self, payment_service):
        """Test payment processing failure."""
        mock_response = httpx.Response(
            400,
            json={"error": "insufficient_funds"}
        )

        with patch.object(
            payment_service._client,
            "post",
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            with pytest.raises(PaymentError, match="insufficient_funds"):
                await payment_service.process_payment(
                    amount=100.00,
                    currency="USD",
                    card_token="card_abc"
                )

    async def test_process_payment_timeout(self, payment_service):
        """Test payment processing timeout handling."""
        with patch.object(
            payment_service._client,
            "post",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("Connection timed out")
        ):
            with pytest.raises(PaymentError, match="timeout"):
                await payment_service.process_payment(
                    amount=100.00,
                    currency="USD",
                    card_token="card_abc"
                )
```

### Mocking Database Queries

```python
# tests/unit/test_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.user_repository import UserRepository


class TestUserRepository:
    """Tests for UserRepository with mocked database."""

    @pytest.fixture
    def mock_session(self):
        """Create mock async session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    async def test_find_by_email(self, mock_session):
        """Test finding user by email."""
        # Arrange
        mock_user = MagicMock(id=1, email="test@example.com")
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user

        repo = UserRepository(mock_session)

        # Act
        result = await repo.find_by_email("test@example.com")

        # Assert
        assert result.email == "test@example.com"
        mock_session.execute.assert_called_once()
```

---

## Time-Dependent Tests

```python
# tests/unit/services/test_subscription.py
import pytest
from freezegun import freeze_time
from datetime import datetime, timedelta

from app.services.subscription_service import SubscriptionService


class TestSubscriptionService:
    """Tests for subscription expiration logic."""

    @freeze_time("2025-01-15 12:00:00")
    async def test_subscription_active(self, db_session):
        """Test subscription is active before expiry."""
        # Arrange
        service = SubscriptionService(db_session)
        expires_at = datetime(2025, 2, 15)  # One month from now

        # Act
        is_active = await service.is_active(expires_at)

        # Assert
        assert is_active is True

    @freeze_time("2025-03-01 12:00:00")
    async def test_subscription_expired(self, db_session):
        """Test subscription is expired after expiry date."""
        # Arrange
        service = SubscriptionService(db_session)
        expires_at = datetime(2025, 2, 15)  # Two weeks ago

        # Act
        is_active = await service.is_active(expires_at)

        # Assert
        assert is_active is False

    @freeze_time("2025-02-10 12:00:00")
    async def test_subscription_expiring_soon(self, db_session):
        """Test subscription expiring within warning period."""
        # Arrange
        service = SubscriptionService(db_session)
        expires_at = datetime(2025, 2, 15)  # 5 days from now

        # Act
        days_remaining = await service.days_until_expiry(expires_at)

        # Assert
        assert days_remaining == 5
        assert await service.is_expiring_soon(expires_at) is True
```

---

## Test Markers and Selection

```python
# tests/integration/test_slow_operations.py
import pytest


@pytest.mark.slow
async def test_bulk_import(client, db_session):
    """Test bulk data import (slow operation)."""
    # This test takes several seconds
    pass


@pytest.mark.integration
async def test_database_migration(engine):
    """Test database migration scripts."""
    pass


@pytest.mark.unit
def test_pure_function():
    """Test pure utility function."""
    pass
```

### Running Specific Tests

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"

# Run specific test file
uv run pytest tests/integration/test_user_endpoints.py

# Run specific test class
uv run pytest tests/integration/test_user_endpoints.py::TestUserEndpoints

# Run specific test method
uv run pytest tests/integration/test_user_endpoints.py::TestUserEndpoints::test_create_user

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

---

## Coverage Requirements

### Minimum Coverage Targets

| Category | Target | Rationale |
|----------|--------|-----------|
| Overall | 80% | Industry standard for production code |
| Services | 90% | Business logic requires thorough testing |
| API Routes | 85% | Critical paths must be tested |
| Utilities | 95% | Pure functions are easy to test |
| Models | 70% | ORM models have less testable logic |

### Coverage Commands

```bash
# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Fail if coverage below threshold
uv run pytest --cov=app --cov-fail-under=80
```

---

## CI Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
        run: |
          uv run pytest --cov=app --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

---

## Best Practices

### Do

- Use descriptive test names that explain the scenario
- Follow Arrange-Act-Assert (AAA) pattern
- Use fixtures for shared setup
- Test both success and failure paths
- Use parameterized tests for multiple inputs
- Mock external dependencies
- Keep tests independent and isolated
- Use factories for consistent test data

### Don't

- Test implementation details, test behavior
- Share state between tests
- Use production database for tests
- Skip error case testing
- Write tests that depend on execution order
- Mock too much - test real integrations where practical
- Ignore flaky tests - fix or remove them

---

## Related Standards

- [Python Standards](./python.md)
- [Backend Tech Stack](./tech-stack.md)
- [Frontend Testing](../frontend/testing.md)
- [Architecture Testing Strategy](../architecture/testing-strategy.md)

---

*Comprehensive backend testing ensures reliability and catches bugs before they reach production.*

---

<!-- Compilation Metadata
  domain: backend-standards
  domain_version: 1.0.0
  compiled_at: 2026-03-09 07:00
  source: evolv-coder-standards
  files_compiled: 4/4
-->