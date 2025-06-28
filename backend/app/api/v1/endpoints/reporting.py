from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db, Scan, Subdomain, Port, Technology, WhoisRecord, DnsRecord, WaybackUrl
from sqlalchemy import or_

router = APIRouter()


class ReportGenerateRequest(BaseModel):
    report_type: str = "comprehensive"  # summary, detailed, executive
    scan_ids: List[str]
    format: str = "pdf"  # pdf, html, json
    options: Optional[Dict[str, Any]] = None


class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str
    report_type: str
    created_at: datetime
    estimated_duration: Optional[int] = None


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(request: ReportGenerateRequest) -> ReportGenerateResponse:
    """
    Genera un report basato sui risultati delle scansioni
    """
    report_id = str(uuid.uuid4())
    
    # TODO: Implement actual report generation logic
    
    return ReportGenerateResponse(
        report_id=report_id,
        status="started",
        report_type=request.report_type,
        created_at=datetime.utcnow(),
        estimated_duration=120  # 2 minutes
    )


@router.get("/reports")
async def list_reports(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """
    Lista tutti i report generati
    """
    # TODO: Implement actual report listing
    return {
        "reports": [
            {
                "id": "report-001",
                "title": "Security Assessment Report - example.com",
                "type": "comprehensive",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "scan_count": 3,
                "vulnerabilities_found": 5
            },
            {
                "id": "report-002",
                "title": "Quick Scan Report - test.com",
                "type": "summary",
                "status": "completed",
                "created_at": "2024-01-14T15:45:00Z",
                "scan_count": 1,
                "vulnerabilities_found": 2
            }
        ],
        "total": 2,
        "limit": limit,
        "offset": offset
    }


@router.get("/reports/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """
    Ottieni un report specifico
    """
    # TODO: Implement actual report retrieval
    return {
        "id": report_id,
        "title": "Security Assessment Report - example.com",
        "type": "comprehensive",
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:32:00Z",
        "summary": {
            "total_scans": 3,
            "total_vulnerabilities": 5,
            "critical": 0,
            "high": 1,
            "medium": 3,
            "low": 1
        },
        "scans": [
            {
                "id": "scan-001",
                "type": "recon",
                "target": "example.com",
                "status": "completed"
            },
            {
                "id": "scan-002",
                "type": "vulnscan",
                "target": "https://example.com",
                "status": "completed"
            }
        ],
        "vulnerabilities": [
            {
                "id": "VULN-001",
                "title": "SQL Injection",
                "severity": "high",
                "scan_id": "scan-002"
            }
        ]
    }


@router.get("/reports/{report_id}/download")
async def download_report(report_id: str, format: str = "pdf") -> Dict[str, Any]:
    """
    Scarica un report in formato specifico
    """
    # TODO: Implement actual report download
    return {
        "report_id": report_id,
        "format": format,
        "download_url": f"/api/v1/reporting/reports/{report_id}/files/report.{format}",
        "file_size": "2.5MB",
        "expires_at": "2024-02-15T10:30:00Z"
    }


@router.get("/templates")
async def list_report_templates() -> Dict[str, Any]:
    """
    Lista i template di report disponibili
    """
    return {
        "templates": [
            {
                "name": "executive_summary",
                "title": "Executive Summary",
                "description": "Report sintetico per dirigenti",
                "sections": ["overview", "key_findings", "recommendations"],
                "estimated_pages": 5
            },
            {
                "name": "technical_report",
                "title": "Technical Report",
                "description": "Report tecnico dettagliato",
                "sections": ["methodology", "findings", "remediation", "appendix"],
                "estimated_pages": 25
            },
            {
                "name": "compliance_report",
                "title": "Compliance Report",
                "description": "Report per compliance e audit",
                "sections": ["scope", "compliance_matrix", "findings", "remediation_plan"],
                "estimated_pages": 15
            }
        ]
    }


@router.get("/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get real dashboard data from database
    """
    try:
        # Get total scans
        total_scans = db.query(Scan).count()
        
        # Get active scans (running or started)
        active_scans = db.query(Scan).filter(
            Scan.status.in_(["started", "running"])
        ).count()
        
        # Get completed scans
        completed_scans = db.query(Scan).filter(Scan.status == "completed").count()
        
        # Get total subdomains found
        total_subdomains = db.query(Subdomain).count()
        
        # Get total ports found
        total_ports = db.query(Port).count()
        
        # Get total technologies found
        total_technologies = db.query(Technology).count()
        
        # Get recent scans (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = db.query(Scan).filter(
            Scan.created_at >= week_ago
        ).order_by(Scan.created_at.desc()).limit(5).all()
        
        # Format recent activity
        recent_activity = []
        for scan in recent_scans:
            activity_type = "scan_completed" if scan.status == "completed" else "scan_started"
            
            # Count results based on scan type
            if scan.scan_type == "osint":
                whois_count = db.query(WhoisRecord).filter(WhoisRecord.scan_id == scan.id).count()
                dns_count = db.query(DnsRecord).filter(DnsRecord.scan_id == scan.id).count()
                wayback_count = db.query(WaybackUrl).filter(WaybackUrl.scan_id == scan.id).count()
                total_results = whois_count + dns_count + wayback_count
                description = f"Found {whois_count} WHOIS, {dns_count} DNS, {wayback_count} Wayback records"
            elif scan.scan_type == "recon":
                subdomain_count = db.query(Subdomain).filter(Subdomain.scan_id == scan.id).count()
                port_count = db.query(Port).filter(Port.scan_id == scan.id).count()
                tech_count = db.query(Technology).filter(Technology.scan_id == scan.id).count()
                total_results = subdomain_count + port_count + tech_count
                description = f"Found {subdomain_count} subdomains, {port_count} ports, {tech_count} technologies"
            elif scan.scan_type == "vulnscan":
                # For vulnscan, we might need to add a Vulnerability table later
                # For now, use a placeholder
                total_results = 0
                description = "Vulnerability scan completed"
            else:
                total_results = 0
                description = "Scan completed"
            
            recent_activity.append({
                "type": activity_type,
                "target": scan.target,
                "scan_type": scan.scan_type,
                "status": scan.status,
                "results_count": total_results,
                "description": description,
                "timestamp": scan.created_at.isoformat(),
                "scan_id": scan.id
            })
        
        # Get scan statistics by type
        recon_scans = db.query(Scan).filter(Scan.scan_type == "recon").count()
        vuln_scans = db.query(Scan).filter(Scan.scan_type == "vulnscan").count()
        
        return {
            "overview": {
                "total_scans": total_scans,
                "completed_scans": completed_scans,
                "active_scans": active_scans,
                "total_subdomains": total_subdomains,
                "total_ports": total_ports,
                "total_technologies": total_technologies,
                "recon_scans": recon_scans,
                "vuln_scans": vuln_scans
            },
            "recent_activity": recent_activity,
            "scan_trends": {
                "total": total_scans,
                "completed": completed_scans,
                "active": active_scans,
                "failed": db.query(Scan).filter(Scan.status == "failed").count()
            },
            "discovery_summary": {
                "subdomains": total_subdomains,
                "ports": total_ports,
                "technologies": total_technologies
            }
        }
        
    except Exception as e:
        # Fallback to basic data if database query fails
        return {
            "overview": {
                "total_scans": 0,
                "completed_scans": 0,
                "active_scans": 0,
                "total_subdomains": 0,
                "total_ports": 0,
                "total_technologies": 0,
                "recon_scans": 0,
                "vuln_scans": 0
            },
            "recent_activity": [],
            "scan_trends": {
                "total": 0,
                "completed": 0,
                "active": 0,
                "failed": 0
            },
            "discovery_summary": {
                "subdomains": 0,
                "ports": 0,
                "technologies": 0
            }
        } 