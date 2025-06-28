from fastapi import APIRouter
from app.api.v1.endpoints import health, modules, recon, osint, vulnscan, reporting

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(recon.router, prefix="/recon", tags=["recon"])
api_router.include_router(osint.router, prefix="/osint", tags=["osint"])
api_router.include_router(vulnscan.router, prefix="/vulnscan", tags=["vulnscan"])
api_router.include_router(reporting.router, prefix="/reporting", tags=["reporting"]) 