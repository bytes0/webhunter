from fastapi import APIRouter
from typing import Dict, Any, List
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def list_modules() -> Dict[str, Any]:
    """
    Lista tutti i moduli disponibili
    """
    modules_info = {
        "recon": {
            "name": "Reconnaissance",
            "description": "Strumenti di ricognizione e discovery",
            "endpoints": ["/api/v1/recon/scan", "/api/v1/recon/status"],
            "enabled": "recon" in settings.enabled_modules
        },
        "osint": {
            "name": "OSINT",
            "description": "Open Source Intelligence gathering",
            "endpoints": ["/api/v1/osint/gather", "/api/v1/osint/search"],
            "enabled": "osint" in settings.enabled_modules
        },
        "vulnscan": {
            "name": "Vulnerability Scanner",
            "description": "Vulnerability scanning e assessment",
            "endpoints": ["/api/v1/vulnscan/scan", "/api/v1/vulnscan/results"],
            "enabled": "vulnscan" in settings.enabled_modules
        },
        "reporting": {
            "name": "Reporting",
            "description": "Generazione report e dashboard",
            "endpoints": ["/api/v1/reporting/reports", "/api/v1/reporting/generate"],
            "enabled": "reporting" in settings.enabled_modules
        }
    }
    
    return {
        "modules": modules_info,
        "total": len(modules_info),
        "enabled": len([m for m in modules_info.values() if m["enabled"]])
    }


@router.get("/{module_name}")
async def get_module_info(module_name: str) -> Dict[str, Any]:
    """
    Informazioni dettagliate su un modulo specifico
    """
    modules_info = {
        "recon": {
            "name": "Reconnaissance",
            "description": "Strumenti di ricognizione e discovery",
            "version": "1.0.0",
            "author": "Bug Bounty Platform",
            "endpoints": ["/api/v1/recon/scan", "/api/v1/recon/status"],
            "enabled": "recon" in settings.enabled_modules
        },
        "osint": {
            "name": "OSINT",
            "description": "Open Source Intelligence gathering",
            "version": "1.0.0",
            "author": "Bug Bounty Platform",
            "endpoints": ["/api/v1/osint/gather", "/api/v1/osint/search"],
            "enabled": "osint" in settings.enabled_modules
        },
        "vulnscan": {
            "name": "Vulnerability Scanner",
            "description": "Vulnerability scanning e assessment",
            "version": "1.0.0",
            "author": "Bug Bounty Platform",
            "endpoints": ["/api/v1/vulnscan/scan", "/api/v1/vulnscan/results"],
            "enabled": "vulnscan" in settings.enabled_modules
        },
        "reporting": {
            "name": "Reporting",
            "description": "Generazione report e dashboard",
            "version": "1.0.0",
            "author": "Bug Bounty Platform",
            "endpoints": ["/api/v1/reporting/reports", "/api/v1/reporting/generate"],
            "enabled": "reporting" in settings.enabled_modules
        }
    }
    
    if module_name not in modules_info:
        return {"error": "Module not found"}
    
    return modules_info[module_name] 