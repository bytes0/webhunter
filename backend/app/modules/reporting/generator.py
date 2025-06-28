"""
Report Generator Module
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class ReportGenerator:
    def __init__(self):
        self.templates = {
            "executive_summary": self._executive_summary_template,
            "technical_report": self._technical_report_template,
            "compliance_report": self._compliance_report_template
        }
    
    def _executive_summary_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary report"""
        return {
            "report_type": "executive_summary",
            "title": f"Executive Summary - {data.get('target', 'Security Assessment')}",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {
                "overview": {
                    "title": "Executive Overview",
                    "content": f"Security assessment conducted on {data.get('target', 'target')}",
                    "key_metrics": {
                        "total_vulnerabilities": data.get('summary', {}).get('total_vulnerabilities', 0),
                        "critical_issues": data.get('summary', {}).get('critical', 0),
                        "high_issues": data.get('summary', {}).get('high', 0)
                    }
                },
                "key_findings": {
                    "title": "Key Findings",
                    "findings": self._extract_key_findings(data)
                },
                "recommendations": {
                    "title": "Recommendations",
                    "recommendations": self._generate_recommendations(data)
                }
            }
        }
    
    def _technical_report_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical report"""
        return {
            "report_type": "technical_report",
            "title": f"Technical Security Report - {data.get('target', 'Security Assessment')}",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {
                "methodology": {
                    "title": "Methodology",
                    "content": "Detailed methodology of the security assessment",
                    "tools_used": data.get('tools_used', []),
                    "scan_types": data.get('scan_types', [])
                },
                "findings": {
                    "title": "Detailed Findings",
                    "vulnerabilities": data.get('vulnerabilities', []),
                    "summary": data.get('summary', {})
                },
                "remediation": {
                    "title": "Remediation Plan",
                    "remediation_steps": self._generate_remediation_plan(data)
                },
                "appendix": {
                    "title": "Appendix",
                    "raw_data": data.get('raw_data', {}),
                    "logs": data.get('logs', [])
                }
            }
        }
    
    def _compliance_report_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report"""
        return {
            "report_type": "compliance_report",
            "title": f"Compliance Report - {data.get('target', 'Security Assessment')}",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {
                "scope": {
                    "title": "Assessment Scope",
                    "content": f"Compliance assessment scope for {data.get('target', 'target')}",
                    "frameworks": ["OWASP Top 10", "NIST Cybersecurity Framework"]
                },
                "compliance_matrix": {
                    "title": "Compliance Matrix",
                    "matrix": self._generate_compliance_matrix(data)
                },
                "findings": {
                    "title": "Compliance Findings",
                    "findings": self._map_findings_to_compliance(data)
                },
                "remediation_plan": {
                    "title": "Remediation Plan",
                    "plan": self._generate_compliance_remediation_plan(data)
                }
            }
        }
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from scan data"""
        findings = []
        vulnerabilities = data.get('vulnerabilities', [])
        
        # Group by severity
        severity_groups = {"critical": [], "high": [], "medium": [], "low": []}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium').lower()
            if severity in severity_groups:
                severity_groups[severity].append(vuln)
        
        # Add findings for each severity level
        for severity, vulns in severity_groups.items():
            if vulns:
                findings.append({
                    "severity": severity,
                    "count": len(vulns),
                    "description": f"{len(vulns)} {severity} severity vulnerabilities found",
                    "examples": vulns[:3]  # Top 3 examples
                })
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []
        vulnerabilities = data.get('vulnerabilities', [])
        
        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('title', 'Unknown').split()[0]
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)
        
        # Generate recommendations for each type
        for vuln_type, vulns in vuln_types.items():
            recommendations.append({
                "category": vuln_type,
                "priority": "high" if any(v.get('severity') in ['critical', 'high'] for v in vulns) else "medium",
                "description": f"Address {vuln_type} vulnerabilities",
                "count": len(vulns),
                "action_items": [
                    "Implement proper input validation",
                    "Update security headers",
                    "Conduct security training"
                ]
            })
        
        return recommendations
    
    def _generate_remediation_plan(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed remediation plan"""
        plan = []
        vulnerabilities = data.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            plan.append({
                "vulnerability_id": vuln.get('id', ''),
                "title": vuln.get('title', ''),
                "severity": vuln.get('severity', 'medium'),
                "description": vuln.get('description', ''),
                "remediation_steps": [
                    "Identify affected components",
                    "Implement security fix",
                    "Test the fix",
                    "Deploy to production",
                    "Verify fix effectiveness"
                ],
                "estimated_effort": "2-4 hours",
                "priority": "high" if vuln.get('severity') in ['critical', 'high'] else "medium"
            })
        
        return plan
    
    def _generate_compliance_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance matrix"""
        return {
            "owasp_top_10": {
                "A01:2021 - Broken Access Control": "Compliant",
                "A02:2021 - Cryptographic Failures": "Non-Compliant",
                "A03:2021 - Injection": "Partially Compliant",
                "A04:2021 - Insecure Design": "Compliant",
                "A05:2021 - Security Misconfiguration": "Non-Compliant"
            },
            "nist_framework": {
                "Identify": "Compliant",
                "Protect": "Partially Compliant", 
                "Detect": "Non-Compliant",
                "Respond": "Compliant",
                "Recover": "Compliant"
            }
        }
    
    def _map_findings_to_compliance(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map findings to compliance frameworks"""
        findings = []
        vulnerabilities = data.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            findings.append({
                "vulnerability": vuln.get('title', ''),
                "severity": vuln.get('severity', 'medium'),
                "compliance_impact": {
                    "owasp": "A02:2021 - Cryptographic Failures",
                    "nist": "Protect - Data Security"
                },
                "status": "Non-Compliant"
            })
        
        return findings
    
    def _generate_compliance_remediation_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance remediation plan"""
        return {
            "immediate_actions": [
                "Fix critical vulnerabilities",
                "Implement security headers",
                "Update encryption protocols"
            ],
            "short_term": [
                "Conduct security training",
                "Implement monitoring",
                "Update security policies"
            ],
            "long_term": [
                "Establish security program",
                "Implement DevSecOps",
                "Regular security assessments"
            ]
        }
    
    def generate_report(self, data: Dict[str, Any], template: str = "executive_summary") -> Dict[str, Any]:
        """Generate report using specified template"""
        if template not in self.templates:
            template = "executive_summary"
        
        report_data = self.templates[template](data)
        report_data["report_id"] = str(uuid.uuid4())
        
        return report_data
    
    def export_report(self, report_data: Dict[str, Any], format: str = "json") -> str:
        """Export report in specified format"""
        if format == "json":
            return json.dumps(report_data, indent=2)
        elif format == "html":
            return self._generate_html_report(report_data)
        elif format == "pdf":
            return self._generate_pdf_report(report_data)
        else:
            return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report (placeholder)"""
        # This would generate actual HTML
        return f"""
        <html>
        <head><title>{report_data.get('title', 'Report')}</title></head>
        <body>
            <h1>{report_data.get('title', 'Report')}</h1>
            <p>Generated at: {report_data.get('generated_at', '')}</p>
        </body>
        </html>
        """
    
    def _generate_pdf_report(self, report_data: Dict[str, Any]) -> str:
        """Generate PDF report (placeholder)"""
        # This would generate actual PDF
        return "PDF report content (placeholder)" 