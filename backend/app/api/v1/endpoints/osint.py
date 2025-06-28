from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
from app.modules.osint.gatherer import OSINTGatherer
from app.core.database import get_db, Scan, WhoisRecord, DnsRecord, WaybackUrl, SessionLocal
from sqlalchemy.orm import Session
import asyncio

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSINTGatherRequest(BaseModel):
    target: str
    search_type: str = "basic"  # basic, domain
    tools: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None


class OSINTGatherResponse(BaseModel):
    task_id: str
    status: str
    target: str
    created_at: datetime
    estimated_duration: Optional[int] = None


def run_osint_gathering_background(scan_id: str, target: str, tools: List[str]):
    """Run OSINT gathering in background and update database"""
    try:
        logger.info(f"Starting background OSINT gathering for {scan_id}")
        
        # Create a new database session for this background task
        db = SessionLocal()
        try:
            # Update status to running
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "running")
                setattr(scan, 'progress', 10.0)
                db.commit()
            
            # Run the actual gathering
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                gatherer = OSINTGatherer()
                if tools:
                    results = loop.run_until_complete(gatherer.run_selected_tools(target, tools))
                else:
                    results = loop.run_until_complete(gatherer.run_full_gathering(target))
                loop.run_until_complete(gatherer.close())
            finally:
                loop.close()
            
            # Update database with results
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "completed")
                setattr(scan, 'progress', 100.0)
                setattr(scan, 'completed_at', datetime.utcnow())
                
                # Save WHOIS records
                if results.get("whois") and not results["whois"].get("error"):
                    whois_data = results["whois"]
                    whois_record = WhoisRecord(
                        scan_id=scan_id,
                        domain=target,
                        registrar=whois_data.get("registrar"),
                        creation_date=None,
                        expiration_date=None,
                        name_servers=whois_data.get("name_servers", []),
                        emails=whois_data.get("emails", [])
                    )
                    db.add(whois_record)
                
                # Save DNS records
                if results.get("dns") and not results["dns"].get("error"):
                    dns_data = results["dns"]
                    record_types = {
                        "a_records": "A",
                        "aaaa_records": "AAAA", 
                        "mx_records": "MX",
                        "ns_records": "NS",
                        "txt_records": "TXT",
                        "cname_records": "CNAME"
                    }
                    
                    for key, record_type in record_types.items():
                        if dns_data.get(key):
                            for record_value in dns_data[key]:
                                dns_record = DnsRecord(
                                    scan_id=scan_id,
                                    domain=target,
                                    record_type=record_type,
                                    record_value=record_value
                                )
                                db.add(dns_record)
                
                # Save Wayback URLs
                if results.get("wayback_urls"):
                    for url in results["wayback_urls"][:1000]:  # Limit to 1000 URLs
                        wayback_url = WaybackUrl(
                            scan_id=scan_id,
                            domain=target,
                            url=url
                        )
                        db.add(wayback_url)
                
                db.commit()
            
            logger.info(f"OSINT gathering {scan_id} completed successfully")
            
        except Exception as e:
            # Update database with error
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                setattr(scan, 'status', "failed")
                setattr(scan, 'error', str(e))
                setattr(scan, 'progress', 0.0)
                db.commit()
            
            logger.error(f"Error during OSINT gathering {scan_id}: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Critical error during OSINT gathering {scan_id}: {str(e)}")


@router.post("/gather", response_model=OSINTGatherResponse)
async def start_osint_gathering(request: OSINTGatherRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> OSINTGatherResponse:
    """
    Start OSINT information gathering
    """
    scan_id = str(uuid.uuid4())
    
    logger.info(f"Starting OSINT gathering {scan_id} for target: {request.target}")
    
    # Default to all tools if none specified
    if not request.tools:
        request.tools = ["whois", "dns", "waybackurls"]
    
    # Validate tools
    valid_tools = ["whois", "dns", "waybackurls"]
    invalid_tools = [tool for tool in request.tools if tool not in valid_tools]
    if invalid_tools:
        raise HTTPException(status_code=400, detail=f"Invalid tools: {invalid_tools}")
    
    # Create scan record in database
    scan = Scan(
        id=scan_id,
        target=request.target,
        status="started",
        progress=0.0,
        created_at=datetime.utcnow(),
        scan_type="osint"
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # Start gathering in background
    background_tasks.add_task(run_osint_gathering_background, scan_id, request.target, request.tools)
    
    return OSINTGatherResponse(
        task_id=scan_id,
        status="started",
        target=request.target,
        created_at=scan.created_at,
        estimated_duration=120  # 2 minutes
    )


@router.get("/gather/{task_id}")
async def get_osint_task_status(task_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get OSINT task status
    """
    scan = db.query(Scan).filter(Scan.id == task_id, Scan.scan_type == "osint").first()
    if not scan:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": scan.id,
        "status": scan.status,
        "progress": scan.progress,
        "target": scan.target,
        "created_at": scan.created_at,
        "error": scan.error
    }


@router.get("/gather/{task_id}/results")
async def get_osint_results(task_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get OSINT task results
    """
    scan = db.query(Scan).filter(Scan.id == task_id, Scan.scan_type == "osint").first()
    if not scan:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # Get results from related tables
    whois_records = db.query(WhoisRecord).filter(WhoisRecord.scan_id == task_id).first()
    dns_records = db.query(DnsRecord).filter(DnsRecord.scan_id == task_id).all()
    wayback_urls = db.query(WaybackUrl).filter(WaybackUrl.scan_id == task_id).all()
    
    # Build results
    results = {
        "target": scan.target,
        "timestamp": scan.created_at.isoformat()
    }
    
    # Add WHOIS data
    if whois_records:
        results["whois"] = {
            "domain": whois_records.domain,
            "registrar": whois_records.registrar,
            "creation_date": None,
            "expiration_date": None,
            "name_servers": whois_records.name_servers or [],
            "emails": whois_records.emails or []
        }
    
    # Add DNS data
    if dns_records:
        dns_data = {
            "domain": scan.target,
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": []
        }
        
        for record in dns_records:
            if record.record_type == "A":
                dns_data["a_records"].append(record.record_value)
            elif record.record_type == "AAAA":
                dns_data["aaaa_records"].append(record.record_value)
            elif record.record_type == "MX":
                dns_data["mx_records"].append(record.record_value)
            elif record.record_type == "NS":
                dns_data["ns_records"].append(record.record_value)
            elif record.record_type == "TXT":
                dns_data["txt_records"].append(record.record_value)
            elif record.record_type == "CNAME":
                dns_data["cname_records"].append(record.record_value)
        
        results["dns"] = dns_data
    
    # Add Wayback URLs
    if wayback_urls:
        results["wayback_urls"] = [url.url for url in wayback_urls]
    
    return {
        "task_id": task_id,
        "status": scan.status,
        "target": scan.target,
        "results": results
    }


@router.get("/tasks")
async def list_osint_tasks(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    List all OSINT gathering tasks
    """
    scans = db.query(Scan).filter(Scan.scan_type == "osint").order_by(Scan.created_at.desc()).all()
    
    task_list = []
    for scan in scans:
        # Get actual results counts
        whois_records = db.query(WhoisRecord).filter(WhoisRecord.scan_id == scan.id).all()
        dns_records = db.query(DnsRecord).filter(DnsRecord.scan_id == scan.id).all()
        wayback_urls = db.query(WaybackUrl).filter(WaybackUrl.scan_id == scan.id).all()
        
        task_list.append({
            "task_id": scan.id,
            "target": scan.target,
            "status": scan.status,
            "progress": scan.progress,
            "created_at": scan.created_at.isoformat(),
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "tools": ["whois", "dns", "waybackurls"],
            "counts": {
                "whois_records": len(whois_records),
                "dns_records": len(dns_records),
                "wayback_urls": len(wayback_urls)
            }
        })
    
    return {
        "tasks": task_list,
        "total": len(task_list)
    }


@router.post("/search")
async def search_osint(query: str, source: str = "all") -> Dict[str, Any]:
    """
    Quick OSINT search
    """
    # TODO: Implement actual search logic
    return {
        "query": query,
        "source": source,
        "results": [
            {
                "title": f"Search result for {query}",
                "url": f"https://example.com/search?q={query}",
                "snippet": f"Information about {query} found in {source}"
            }
        ]
    }


@router.get("/sources")
async def list_osint_sources() -> Dict[str, Any]:
    """
    List available OSINT sources
    """
    return {
        "sources": [
            {
                "name": "whois",
                "description": "WHOIS database lookup",
                "enabled": True
            },
            {
                "name": "dns",
                "description": "DNS records lookup",
                "enabled": True
            },
            {
                "name": "waybackurls",
                "description": "Wayback Machine URL discovery",
                "enabled": True
            }
        ]
    }


@router.post("/gather/{task_id}/stop")
async def stop_osint_task(task_id: str) -> Dict[str, Any]:
    """
    Stop an OSINT gathering task
    """
    # TODO: Implement stop logic
    raise HTTPException(status_code=501, detail="Stop functionality not implemented")


@router.delete("/gather/{task_id}")
async def delete_osint_task(task_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Delete an OSINT gathering task and its results
    """
    scan = db.query(Scan).filter(Scan.id == task_id, Scan.scan_type == "osint").first()
    if not scan:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        # Delete related records
        db.query(WhoisRecord).filter(WhoisRecord.scan_id == task_id).delete()
        db.query(DnsRecord).filter(DnsRecord.scan_id == task_id).delete()
        db.query(WaybackUrl).filter(WaybackUrl.scan_id == task_id).delete()
        
        # Delete the scan itself
        db.delete(scan)
        db.commit()
        
        return {
            "message": "Task deleted successfully",
            "task_id": task_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting OSINT task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete task") 