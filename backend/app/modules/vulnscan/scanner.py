"""
Vulnerability Scanner Module
"""
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class VulnerabilityScanner:
    def __init__(self):
        self.available_tools = {
            "nuclei": self._check_tool("nuclei"),
            "nmap": self._check_tool("nmap"),
            "nikto": self._check_tool("nikto")
        }
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available in the system"""
        try:
            subprocess.run([tool_name, "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def scan_with_nuclei(self, target: str, templates: str = "cves,vulnerabilities") -> List[Dict[str, Any]]:
        """Scan using Nuclei"""
        if not self.available_tools["nuclei"]:
            return []
        
        try:
            # Try to find nuclei installation
            nuclei_path = None
            possible_paths = [
                "nuclei",
                "/home/appuser/.pdtm/go/bin/nuclei",
                "/usr/local/bin/nuclei"
            ]
            
            for path in possible_paths:
                try:
                    result = subprocess.run([path, "--version"], 
                                         capture_output=True, check=True, timeout=5)
                    if result.returncode == 0:
                        nuclei_path = path
                        break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if not nuclei_path:
                print("Nuclei not found locally")
                return []
            
            cmd = [
                nuclei_path, "-u", target, "-t", templates,
                "-j", "-silent"  # Changed from -json to -j
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                results = []
                for line in stdout.decode().splitlines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            results.append({
                                "id": data.get("info", {}).get("name", ""),
                                "title": data.get("info", {}).get("name", ""),
                                "severity": data.get("info", {}).get("severity", "unknown"),
                                "description": data.get("info", {}).get("description", ""),
                                "url": data.get("host", ""),
                                "template": data.get("template", ""),
                                "matcher_name": data.get("matcher_name", ""),
                                "extracted_results": data.get("extracted_results", [])
                            })
                        except json.JSONDecodeError:
                            continue
                return results
        except Exception as e:
            print(f"Error running nuclei: {e}")
        
        return []
    
    async def scan_with_nmap(self, target: str, script: str = "vuln") -> List[Dict[str, Any]]:
        """Scan using Nmap with vulnerability scripts"""
        if not self.available_tools["nmap"]:
            return []
        
        try:
            cmd = [
                "nmap", "--script", script, "-oJ", "-", target
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    nmap_output = json.loads(stdout.decode())
                    results = []
                    
                    for host in nmap_output.get("nmaprun", {}).get("host", []):
                        for port in host.get("ports", {}).get("port", []):
                            for script_output in port.get("script", []):
                                if script_output.get("id") == "vulners":
                                    vulns = script_output.get("output", "").split("\n")
                                    for vuln in vulns:
                                        if "CVE-" in vuln:
                                            results.append({
                                                "id": vuln.split()[0],
                                                "title": f"Vulnerability in {port.get('service', {}).get('name', 'unknown')}",
                                                "severity": "medium",
                                                "description": vuln,
                                                "port": port.get("portid"),
                                                "service": port.get("service", {}).get("name", "")
                                            })
                    
                    return results
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Error running nmap: {e}")
        
        return []
    
    async def scan_with_nikto(self, target: str) -> List[Dict[str, Any]]:
        """Scan using Nikto"""
        if not self.available_tools["nikto"]:
            return []
        
        try:
            cmd = [
                "nikto", "-h", target, "-Format", "json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    nikto_output = json.loads(stdout.decode())
                    results = []
                    
                    for vuln in nikto_output.get("vulnerabilities", []):
                        results.append({
                            "id": f"NIKTO-{vuln.get('id', 'unknown')}",
                            "title": vuln.get("title", ""),
                            "severity": "medium",
                            "description": vuln.get("description", ""),
                            "url": target,
                            "method": vuln.get("method", ""),
                            "osvdb": vuln.get("osvdb", "")
                        })
                    
                    return results
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Error running nikto: {e}")
        
        return []
    
    async def run_web_scan(self, target: str) -> Dict[str, Any]:
        """Run web application vulnerability scan"""
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": "web",
            "vulnerabilities": []
        }
        
        # Run Nuclei scan
        nuclei_results = await self.scan_with_nuclei(target)
        results["vulnerabilities"].extend(nuclei_results)
        
        # Run Nikto scan
        nikto_results = await self.scan_with_nikto(target)
        results["vulnerabilities"].extend(nikto_results)
        
        # Calculate summary
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for vuln in results["vulnerabilities"]:
            severity = vuln.get("severity", "unknown").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        results["summary"] = {
            "total_vulnerabilities": len(results["vulnerabilities"]),
            **severity_counts
        }
        
        return results
    
    async def run_network_scan(self, target: str) -> Dict[str, Any]:
        """Run network vulnerability scan"""
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": "network",
            "vulnerabilities": []
        }
        
        # Run Nmap vulnerability scan
        nmap_results = await self.scan_with_nmap(target)
        results["vulnerabilities"].extend(nmap_results)
        
        # Calculate summary
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for vuln in results["vulnerabilities"]:
            severity = vuln.get("severity", "unknown").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        results["summary"] = {
            "total_vulnerabilities": len(results["vulnerabilities"]),
            **severity_counts
        }
        
        return results 