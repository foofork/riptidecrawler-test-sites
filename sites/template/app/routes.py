"""
Additional API routes for site-specific functionality.
Override or extend these routes in site-specific implementations.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

router = APIRouter()


@router.get("/search")
async def search(q: str, limit: int = 20) -> Dict[str, Any]:
    """
    Generic search endpoint.
    Override in site-specific implementation.
    """
    return {
        "query": q,
        "results": [],
        "total": 0,
        "message": "Search not implemented for this site"
    }


@router.get("/filter")
async def filter_data(
    category: Optional[str] = None,
    sort: Optional[str] = "created_at",
    order: Optional[str] = "desc"
) -> Dict[str, Any]:
    """
    Generic filter endpoint.
    Override in site-specific implementation.
    """
    return {
        "filters": {
            "category": category,
            "sort": sort,
            "order": order
        },
        "results": [],
        "total": 0
    }


@router.get("/detail/{item_id}")
async def get_detail(item_id: int) -> Dict[str, Any]:
    """
    Get single item detail.
    Override in site-specific implementation.
    """
    return {
        "id": item_id,
        "message": "Detail endpoint not implemented"
    }
