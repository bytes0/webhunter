from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
from app.modules.recon.scanner import ReconScanner
from app.core.database import get_db, Scan, Subdomain, Port, Technology, SessionLocal
from sqlalchemy.orm import Session
import asyncio
from app.api.v1.endpoints.telegram import send_scan_notification

router = APIRouter()
scanner = ReconScanner()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReconScanRequest(BaseModel):
    target: str
    scan_type: str = "basic"  # basic, full, custom
    tools: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None


class ReconScanResponse(BaseModel):
    scan_id: str
    status: str
    target: str
    created_at: datetime
    estimated_duration: Optional[int] = None


class ReconScanStatusResponse(BaseModel):
    scan_id: str
    status: str
    target: str
    progress: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Dict[str, Any]
    error: Optional[str] = None


def run_scan_background_sync(scan_id: str, target: str, tools: Optional[List[str]] = None):
    """Run scan in background and update database - synchronous version"""
    try:
        logger.info(f"Starting background scan for {scan_id}")
        
        # Send Telegram notification for scan start
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_scan_notification(
                "recon", 
                "scan_started", 
                f"🚀 Recon scan started for {target}",
                target
            ))
            loop.close()
        except Exception as e:
            logger.error(f"Failed to send Telegram notification for scan start: {e}")
        
        # Create a new database session for this background task
        db = SessionLocal()
        try:
            # Update status to running
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "running")
                setattr(scan, 'progress', 10.0)
                db.commit()
                logger.info(f"Scan {scan_id} status updated to running")
            
            # Run the actual scan (this is async, so we need to handle it)
            # For now, let's create a simple event loop for this
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if tools and "hackertarget_api" in tools:
                    # For HackerTarget API, we'll run it with progress updates
                    logger.info(f"Running HackerTarget API for {target}")
                    results = loop.run_until_complete(scanner.run_selected_tools(target, tools))
                    
                    # Update progress as we get results
                    if results.get("subdomains"):
                        scan = db.query(Scan).filter(Scan.id == scan_id).first()
                        if scan:
                            setattr(scan, 'progress', 50.0)  # 50% when subdomains found
                            db.commit()
                            logger.info(f"Scan {scan_id} progress updated to 50% - found {len(results.get('subdomains', []))} subdomains")
                else:
                    results = loop.run_until_complete(scanner.run_full_scan(target))
            finally:
                loop.close()
            
            # Update database with results
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "completed")
                setattr(scan, 'progress', 100.0)
                setattr(scan, 'completed_at', datetime.utcnow())
                
                # Save subdomains
                for subdomain_data in results.get("subdomains", []):
                    subdomain = Subdomain(
                        scan_id=scan_id,
                        subdomain=subdomain_data["subdomain"],
                        source=subdomain_data.get("source", "hackertarget_api"),
                        discovered_at=datetime.utcnow()
                    )
                    db.add(subdomain)
                
                # Save ports
                for port_data in results.get("ports", []):
                    port = Port(
                        scan_id=scan_id,
                        port=port_data["port"],
                        protocol=port_data["protocol"],
                        service=port_data.get("service", "unknown"),
                        version=port_data.get("version", ""),
                        state=port_data.get("state", "open")
                    )
                    db.add(port)
                
                # Save technologies
                for tech_data in results.get("technologies", []):
                    technology = Technology(
                        scan_id=scan_id,
                        technology=tech_data["technology"],
                        version=tech_data.get("version", ""),
                        confidence=tech_data.get("confidence", "high"),
                        source=tech_data.get("source", "nuclei")
                    )
                    db.add(technology)
                
                db.commit()
                logger.info(f"Scan {scan_id} completed with {len(results.get('subdomains', []))} subdomains found")
                
                # Send Telegram notification for scan completion
                try:
                    subdomain_count = len(results.get('subdomains', []))
                    port_count = len(results.get('ports', []))
                    tech_count = len(results.get('technologies', []))
                    
                    message = f"✅ Recon scan completed for {target}\n"
                    message += f"📊 Results:\n"
                    message += f"• Subdomains: {subdomain_count}\n"
                    message += f"• Open ports: {port_count}\n"
                    message += f"• Technologies: {tech_count}"
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send_scan_notification(
                        "recon", 
                        "scan_completed", 
                        message,
                        target
                    ))
                    loop.close()
                except Exception as e:
                    logger.error(f"Failed to send Telegram notification for scan completion: {e}")
            
        except Exception as e:
            # Update database with error
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "failed")
                setattr(scan, 'error', str(e))
                setattr(scan, 'progress', 0.0)
                db.commit()
            
            logger.error(f"Error during scan {scan_id}: {str(e)}")
            
            # Send Telegram notification for scan failure
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_scan_notification(
                    "recon", 
                    "scan_failed", 
                    f"❌ Recon scan failed for {target}\nError: {str(e)}",
                    target
                ))
                loop.close()
            except Exception as telegram_error:
                logger.error(f"Failed to send Telegram notification for scan failure: {telegram_error}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Critical error during scan {scan_id}: {str(e)}")


@router.post("/scan", response_model=ReconScanResponse)
async def start_recon_scan(request: ReconScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> ReconScanResponse:
    """
    Start a reconnaissance scan
    """
    scan_id = str(uuid.uuid4())
    
    logger.info(f"Starting recon scan {scan_id} for target: {request.target}")
    
    # Validate target
    if not request.target or "." not in request.target:
        raise HTTPException(status_code=400, detail="Invalid target domain")
    
    # Create scan record in database
    scan = Scan(
        id=scan_id,
        target=request.target,
        status="started",
        progress=0.0,
        created_at=datetime.utcnow(),
        scan_type="recon"
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # Start the actual scan in the background using BackgroundTasks
    background_tasks.add_task(run_scan_background_sync, scan_id, request.target, request.tools)
    
    return ReconScanResponse(
        scan_id=scan_id,
        status="started",
        target=request.target,
        created_at=scan.created_at,
        estimated_duration=300  # 5 minutes
    )


@router.get("/scan/{scan_id}/status", response_model=ReconScanStatusResponse)
async def get_scan_status(scan_id: str, db: Session = Depends(get_db)) -> ReconScanStatusResponse:
    """
    Get the status of a reconnaissance scan
    """
    logger.info(f"Status request for scan_id: {scan_id}")
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        logger.error(f"Scan {scan_id} not found in database")
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get results from related tables
    subdomains = db.query(Subdomain).filter(Subdomain.scan_id == scan_id).all()
    ports = db.query(Port).filter(Port.scan_id == scan_id).all()
    technologies = db.query(Technology).filter(Technology.scan_id == scan_id).all()
    
    # Convert to dict format for response
    results = {
        "subdomains": [
            {
                "subdomain": s.subdomain,
                "source": s.source,
                "discovered_at": s.discovered_at.isoformat()
            }
            for s in subdomains
        ],
        "ports": [
            {
                "port": p.port,
                "protocol": p.protocol,
                "service": p.service,
                "version": p.version,
                "state": p.state
            }
            for p in ports
        ],
        "technologies": [
            {
                "technology": t.technology,
                "version": t.version,
                "confidence": t.confidence,
                "source": t.source
            }
            for t in technologies
        ]
    }
    
    return ReconScanStatusResponse(
        scan_id=scan.id,
        status=scan.status,
        target=scan.target,
        progress=scan.progress,
        created_at=scan.created_at,
        completed_at=scan.completed_at,
        results=results,
        error=scan.error
    )


@router.get("/scan/{scan_id}")
async def get_scan_debug(scan_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Debug endpoint to see what URL is being called
    """
    logger.info(f"DEBUG: Called /scan/{scan_id} endpoint")
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        logger.error(f"Scan {scan_id} not found in database")
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get results from related tables
    subdomains = db.query(Subdomain).filter(Subdomain.scan_id == scan_id).all()
    ports = db.query(Port).filter(Port.scan_id == scan_id).all()
    technologies = db.query(Technology).filter(Technology.scan_id == scan_id).all()
    
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "target": scan.target,
        "progress": scan.progress,
        "created_at": scan.created_at,
        "results": {
            "subdomains": [s.subdomain for s in subdomains],
            "ports": [f"{p.port}/{p.protocol}" for p in ports],
            "technologies": [t.technology for t in technologies]
        }
    }


@router.get("/scans")
async def list_scans(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    List all reconnaissance scans
    """
    scans = db.query(Scan).filter(Scan.scan_type == "recon").order_by(Scan.created_at.desc()).all()
    
    scan_list = []
    for scan in scans:
        # Get actual subdomains, ports, and technologies
        subdomains = db.query(Subdomain).filter(Subdomain.scan_id == scan.id).all()
        ports = db.query(Port).filter(Port.scan_id == scan.id).all()
        technologies = db.query(Technology).filter(Technology.scan_id == scan.id).all()
        
        scan_list.append({
            "scan_id": scan.id,
            "target": scan.target,
            "status": scan.status,
            "progress": scan.progress,
            "created_at": scan.created_at.isoformat(),
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "counts": {
                "subdomains": len(subdomains),
                "ports": len(ports),
                "technologies": len(technologies)
            },
            "results": {
                "subdomains": [
                    {
                        "subdomain": s.subdomain,
                        "source": s.source,
                        "discovered_at": s.discovered_at.isoformat()
                    }
                    for s in subdomains
                ],
                "ports": [
                    {
                        "port": p.port,
                        "protocol": p.protocol,
                        "service": p.service,
                        "version": p.version,
                        "state": p.state
                    }
                    for p in ports
                ],
                "technologies": [
                    {
                        "technology": t.technology,
                        "version": t.version,
                        "confidence": t.confidence,
                        "source": t.source
                    }
                    for t in technologies
                ]
            }
        })
    
    return {
        "scans": scan_list,
        "total": len(scan_list)
    }


@router.post("/scan/{scan_id}/execute")
async def execute_recon_scan(scan_id: str, target: str) -> Dict[str, Any]:
    """
    Execute a reconnaissance scan immediately and return results
    """
    logger.info(f"Executing recon scan {scan_id} for target: {target}")
    
    try:
        # Run the actual scan
        results = await scanner.run_full_scan(target)
        
        logger.info(f"Scan {scan_id} completed successfully")
        
        return {
            "scan_id": scan_id,
            "status": "completed",
            "target": target,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error executing scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/subdomains")
async def scan_subdomains(target: str) -> Dict[str, Any]:
    """
    Scan for subdomains only
    """
    logger.info(f"Scanning subdomains for: {target}")
    
    try:
        subdomains = await scanner.scan_subdomains(target)
        
        return {
            "target": target,
            "subdomains": subdomains,
            "count": len(subdomains)
        }
    except Exception as e:
        logger.error(f"Error scanning subdomains for {target}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Subdomain scan failed: {str(e)}")


@router.post("/ports")
async def scan_ports(target: str, ports: str = "80,443,8080,8443") -> Dict[str, Any]:
    """
    Scan ports only
    """
    logger.info(f"Scanning ports for: {target}")
    
    try:
        port_results = await scanner.scan_ports(target, ports)
        
        return {
            "target": target,
            "ports": port_results,
            "count": len(port_results)
        }
    except Exception as e:
        logger.error(f"Error scanning ports for {target}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Port scan failed: {str(e)}")


@router.get("/tools")
async def list_recon_tools() -> Dict[str, Any]:
    """
    List available reconnaissance tools
    """
    return {
        "tools": [
            {
                "name": "hackertarget_api",
                "description": "Subdomain discovery via HackerTarget API",
                "enabled": True  # API is always available
            },
            {
                "name": "nmap",
                "description": "Port scanner",
                "enabled": scanner.available_tools["nmap"]
            },
            {
                "name": "nuclei",
                "description": "Vulnerability scanner",
                "enabled": scanner.available_tools.get("nuclei", False)
            }
        ]
    }


@router.post("/scan/{scan_id}/stop")
async def stop_scan(scan_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Stop a running scan
    """
    logger.info(f"Stopping scan {scan_id}")
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.status != "running":
        raise HTTPException(status_code=400, detail="Scan is not running")
    
    # Update scan status to stopped
    scan.status = "stopped"
    scan.progress = 0.0
    db.commit()
    
    return {
        "scan_id": scan_id,
        "status": "stopped",
        "message": "Scan stopped successfully"
    }


@router.delete("/scan/{scan_id}")
async def delete_scan(scan_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Delete a scan and all its results
    """
    logger.info(f"Deleting scan {scan_id}")
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Delete related data first
    db.query(Subdomain).filter(Subdomain.scan_id == scan_id).delete()
    db.query(Port).filter(Port.scan_id == scan_id).delete()
    db.query(Technology).filter(Technology.scan_id == scan_id).delete()
    
    # Delete the scan
    db.delete(scan)
    db.commit()
    
    return {
        "scan_id": scan_id,
        "message": "Scan deleted successfully"
    } 