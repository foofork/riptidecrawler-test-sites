"""
Main FastAPI application template.
All test sites inherit from this structure.
"""
import os
import time
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.data_generator import DataGenerator
from app.routes import router

# Configuration
SITE_NAME = os.getenv("SITE_NAME", "template")
FAKER_SEED = int(os.getenv("FAKER_SEED", "42"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Application startup time
START_TIME = time.time()

# Initialize FastAPI app
app = FastAPI(
    title=f"Test Site - {SITE_NAME.title()}",
    description=f"Automated test site with deterministic data generation",
    version="1.0.0",
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize data generator
data_generator = DataGenerator(seed=FAKER_SEED)
SITE_DATA = data_generator.generate_all()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print(f"🚀 Starting {SITE_NAME} test site...")
    print(f"🎲 Faker seed: {FAKER_SEED}")
    print(f"📊 Data generated: {len(SITE_DATA)} entities")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Render homepage."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "site_name": SITE_NAME,
            "data": SITE_DATA
        }
    )


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for Docker."""
    uptime = int(time.time() - START_TIME)
    return {
        "status": "healthy",
        "site": SITE_NAME,
        "uptime": uptime,
        "data_generated": len(SITE_DATA) > 0,
        "faker_seed": FAKER_SEED
    }


@app.get("/api/stats")
async def site_stats() -> Dict[str, Any]:
    """Return site statistics."""
    return {
        "site": SITE_NAME,
        "total_entities": len(SITE_DATA),
        "faker_seed": FAKER_SEED,
        "uptime": int(time.time() - START_TIME),
        "endpoints": len(app.routes)
    }


@app.get("/api/ground-truth")
async def ground_truth() -> Dict[str, Any]:
    """
    Export complete ground-truth dataset.
    This endpoint returns all generated data for validation.
    """
    return {
        "site": SITE_NAME,
        "seed": FAKER_SEED,
        "generated_at": time.time(),
        "data": SITE_DATA,
        "checksum": hash(str(SITE_DATA))  # Simple integrity check
    }


@app.get("/api/data")
async def get_data(
    skip: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Paginated data endpoint.
    """
    total = len(SITE_DATA)
    data_slice = SITE_DATA[skip:skip + limit] if isinstance(SITE_DATA, list) else SITE_DATA

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": data_slice
    }


# Include additional routes
app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
