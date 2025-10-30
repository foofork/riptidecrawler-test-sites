"""
Pydantic models for request/response validation.
Define site-specific models here.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    site: str
    uptime: int
    data_generated: bool
    faker_seed: int


class StatsResponse(BaseModel):
    """Site statistics response model."""
    site: str
    total_entities: int
    faker_seed: int
    uptime: int
    endpoints: int


class GroundTruthResponse(BaseModel):
    """Ground truth data response model."""
    site: str
    seed: int
    generated_at: float
    data: List[dict]
    checksum: int


class PaginatedResponse(BaseModel):
    """Paginated data response model."""
    total: int
    skip: int
    limit: int
    data: List[dict]


class BaseEntity(BaseModel):
    """Base entity model for all generated items."""
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserModel(BaseEntity):
    """User data model."""
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_active: bool = True


class PostModel(BaseEntity):
    """Post/article data model."""
    title: str
    content: str
    author_id: int
    views: int = 0
    likes: int = 0
    published: bool = False


class ProductModel(BaseEntity):
    """Product data model."""
    description: str
    price: float = Field(gt=0)
    category: str
    sku: str
    stock: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)
    reviews_count: int = 0
