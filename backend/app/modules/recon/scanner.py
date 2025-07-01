"""
Reconnaissance Scanner Module
"""
import asyncio
import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import re
import aiohttp

logger = logging.getLogger(__name__)

class ReconScanner:
    def __init__(self):
        # Set PATH to include Go bin directory
        go_path = os.environ.get('GOPATH', '/app/go')
        go_bin = os.path.join(go_path, 'bin')
        if go_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{os.environ.get('PATH', '')}:{go_bin}"
        
        self.available_tools = {
            "nmap": self._check_tool("nmap")
        }
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available in the system"""
        try:
            if tool_name == "nuclei":
                # Check if nuclei Docker image is available
                try:
                    result = subprocess.run(["docker", "run", "--rm", "projectdiscovery/nuclei:latest", "--version"], 
                                         capture_output=True, check=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✓ {tool_name} found via Docker")
                        return True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    pass
                
                # Fallback to local installation check
                possible_paths = [
                    tool_name,
                    f"/app/go/bin/{tool_name}",
                    f"/usr/local/go/bin/{tool_name}",
                    f"/root/go/bin/{tool_name}",
                    "/home/appuser/.pdtm/go/bin/nuclei"
                ]
                
                for path in possible_paths:
                    try:
                        result = subprocess.run([path, "--version"], 
                                             capture_output=True, check=True, timeout=10)
                        if result.returncode == 0:
                            print(f"✓ {tool_name} found at: {path}")
                            return True
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                
                print(f"✗ {tool_name} not found")
                return False
            else:
                # For other tools, look for binaries
                possible_paths = [
                    tool_name,
                    f"/app/go/bin/{tool_name}",
                    f"/usr/local/go/bin/{tool_name}",
                    f"/root/go/bin/{tool_name}"
                ]
                
                for path in possible_paths:
                    try:
                        result = subprocess.run([path, "--version"], 
                                             capture_output=True, check=True, timeout=10)
                        if result.returncode == 0:
                            print(f"✓ {tool_name} found at: {path}")
                            return True
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                
                print(f"✗ {tool_name} not found")
                return False
        except Exception as e:
            print(f"Error checking {tool_name}: {e}")
            return False
    
    async def scan_subdomains_fast(self, domain: str) -> List[Dict[str, Any]]:
        """Fast subdomain discovery using common subdomain patterns"""
        common_subdomains = [
            "www", "mail", "ftp", "admin", "blog", "api", "dev", "test", "stage", "prod",
            "cdn", "static", "assets", "img", "images", "media", "files", "download",
            "support", "help", "docs", "wiki", "forum", "community", "shop", "store",
            "app", "mobile", "m", "web", "secure", "ssl", "vpn", "remote", "portal",
            "dashboard", "panel", "cpanel", "whm", "ns1", "ns2", "mx1", "mx2", "smtp",
            "pop", "imap", "webmail", "email", "calendar", "drive", "cloud", "backup"
        ]
        
        results = []
        
        # Add the main domain itself
        results.append({
            "subdomain": domain,
            "ip": "",
            "source": "main_domain"
        })
        
        # Try common subdomains
        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            results.append({
                "subdomain": subdomain,
                "ip": "",
                "source": "common_patterns"
            })
        
        print(f"Fast scan found {len(results)} potential subdomains")
        return results
    
    async def scan_subdomains(self, domain: str) -> List[Dict[str, Any]]:
        """Scan for subdomains using HackerTarget API"""
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            print(f"🚀 Starting HackerTarget API scan for {domain}...")
            print(f"API URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        results = []
                        
                        # Parse the API response
                        for line in content.splitlines():
                            line = line.strip()
                            if line and ',' in line:
                                # HackerTarget API returns: subdomain,ip
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    subdomain = parts[0].strip()
                                    ip = parts[1].strip()
                                    
                                    # Only include subdomains that contain the target domain
                                    if domain in subdomain:
                                        results.append({
                                            "subdomain": subdomain,
                                            "ip": ip,
                                            "source": "hackertarget_api"
                                        })
                                        print(f"✅ Found subdomain: {subdomain} ({ip})")
                        
                        print(f"🎉 HackerTarget API completed successfully! Found {len(results)} subdomains")
                        return results
                    else:
                        print(f"❌ HackerTarget API failed with status {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error running HackerTarget API: {e}")
            return []
    
    def _find_tool_path(self, tool_name: str) -> Optional[str]:
        """Find the full path to a tool"""
        # For tools, look for binaries
        possible_paths = [
            tool_name,
            f"/app/go/bin/{tool_name}",
            f"/usr/local/go/bin/{tool_name}",
            f"/root/go/bin/{tool_name}"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, check=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None
    
    async def scan_ports(self, target: str, ports: str = "80,443,8080,8443") -> List[Dict[str, Any]]:
        """Scan ports using nmap"""
        if not self.available_tools["nmap"]:
            print("nmap not available")
            return []
        
        try:
            nmap_path = self._find_tool_path("nmap")
            if not nmap_path:
                print("nmap path not found")
                return []
            
            cmd = [
                nmap_path, "-p", ports, "-sV", "--script=banner",
                "-oJ", "-", target
            ]
            print(f"Running: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)  # 2 minute timeout
            except asyncio.TimeoutError:
                print("nmap timed out after 2 minutes")
                process.kill()
                return []
            
            if process.returncode == 0:
                try:
                    nmap_output = json.loads(stdout.decode())
                    results = []
                    
                    for host in nmap_output.get("nmaprun", {}).get("host", []):
                        for port in host.get("ports", {}).get("port", []):
                            results.append({
                                "port": int(port.get("portid", 0)),
                                "protocol": port.get("protocol", "tcp"),
                                "service": port.get("service", {}).get("name", ""),
                                "version": port.get("service", {}).get("product", ""),
                                "banner": port.get("script", {}).get("banner", "")
                            })
                    
                    print(f"Found {len(results)} open ports")
                    return results
                except json.JSONDecodeError as e:
                    print(f"Error parsing nmap JSON: {e}")
                    return []
            else:
                print(f"nmap failed: {stderr.decode()}")
        except Exception as e:
            print(f"Error running nmap: {e}")
        
        return []
    
    async def scan_technologies(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Detect technologies using nuclei"""
        if not self.available_tools["nuclei"]:
            print("nuclei not available")
            return []
        
        try:
            nuclei_path = self._find_tool_path("nuclei")
            if not nuclei_path:
                print("nuclei path not found")
                return []
            
            # Create temporary file with URLs
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for url in urls:
                    f.write(f"{url}\n")
                temp_file = f.name
            
            try:
                cmd = [
                    nuclei_path, "-l", temp_file, "-t", "technologies",
                    "-json", "-silent", "-timeout", "30"
                ]
                print(f"Running: {' '.join(cmd)}")
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)  # 1 minute timeout
                except asyncio.TimeoutError:
                    print("nuclei timed out after 1 minute")
                    process.kill()
                    return []
                
                if process.returncode == 0:
                    results = []
                    output = stdout.decode()
                    
                    for line in output.splitlines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                results.append({
                                    "technology": data.get("info", {}).get("name", ""),
                                    "version": data.get("info", {}).get("reference", ""),
                                    "confidence": "high",
                                    "source": "nuclei"
                                })
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"Found {len(results)} technologies")
                    return results
                else:
                    print(f"nuclei failed: {stderr.decode()}")
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
        except Exception as e:
            print(f"Error running nuclei: {e}")
        
        return []
    
    async def run_selected_tools(self, target: str, tools: List[str]) -> Dict[str, Any]:
        """Run only the selected tools for reconnaissance"""
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "subdomains": [],
            "ports": [],
            "technologies": []
        }
        
        # Validate tools
        valid_tools = ["hackertarget_api", "nmap"]
        invalid_tools = [tool for tool in tools if tool not in valid_tools]
        if invalid_tools:
            print(f"Invalid tools: {invalid_tools}")
            return results
        
        # Run selected tools
        for tool in tools:
            try:
                if tool == "hackertarget_api":
                    # Use HackerTarget API for subdomain discovery
                    subdomains = await self.scan_subdomains(target)
                    results["subdomains"] = subdomains
                elif tool == "nmap":
                    ports = await self.scan_ports(target)
                    results["ports"] = ports
            except Exception as e:
                print(f"Error running {tool}: {e}")
        
        return results
    
    async def run_full_scan(self, target: str) -> Dict[str, Any]:
        """
        Run a full reconnaissance scan with real-time progress updates
        """
        logger.info(f"Starting full recon scan for target: {target}")
        
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "subdomains": [],
            "ports": []
        }
        
        try:
            # Step 1: Subdomain enumeration with HackerTarget API
            logger.info("Starting subdomain enumeration...")
            subdomains = await self._run_hackertarget_api(target)
            results["subdomains"] = subdomains
            
            # Step 2: Port scanning with nmap
            logger.info("Starting port scanning...")
            ports = await self._run_nmap(target)
            results["ports"] = ports
            
            logger.info(f"Scan completed. Found {len(subdomains)} subdomains, {len(ports)} ports")
            return results
            
        except Exception as e:
            logger.error(f"Error during scan: {str(e)}")
            raise
    
    async def _run_hackertarget_api(self, target: str) -> List[Dict]:
        """
        Run HackerTarget API for subdomain enumeration
        """
        try:
            logger.info(f"Running HackerTarget API on {target}")
            
            url = f"https://api.hackertarget.com/hostsearch/?q={target}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        subdomains = []
                        
                        # Parse the API response
                        for line in content.splitlines():
                            line = line.strip()
                            if line and ',' in line:
                                # HackerTarget API returns: subdomain,ip
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    subdomain = parts[0].strip()
                                    
                                    # Only include subdomains that contain the target domain
                                    if target in subdomain:
                                        subdomains.append(subdomain)
                        
                        logger.info(f"HackerTarget API found {len(subdomains)} subdomains")
                        
                        # Convert to our format
                        return [
                            {
                                "subdomain": subdomain,
                                "source": "hackertarget_api",
                                "discovered_at": "2024-01-01T00:00:00Z"
                            }
                            for subdomain in subdomains
                        ]
                    else:
                        logger.error(f"HackerTarget API failed with status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error running HackerTarget API: {str(e)}")
            return []
    
    async def _run_nmap(self, target: str) -> List[Dict]:
        """
        Run nmap for port scanning
        """
        try:
            logger.info(f"Running nmap on {target}")
            
            # Run nmap command
            cmd = [
                "nmap", "-sS", "-sV", "-O", "-p", "21-23,25,53,80,110-111,135,139,143,443,993,995,1723,3306,3389,5900,8080",
                "-oX", f"/tmp/nmap_{target}.xml",
                target
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
            
            if process.returncode != 0:
                logger.error(f"Nmap failed: {stderr.decode()}")
                return []
            
            # Parse nmap XML output
            ports = await self._parse_nmap_xml(f"/tmp/nmap_{target}.xml")
            
            logger.info(f"Nmap found {len(ports)} open ports")
            return ports
            
        except asyncio.TimeoutError:
            logger.error("Nmap timed out")
            return []
        except Exception as e:
            logger.error(f"Error running nmap: {str(e)}")
            return []
    
    async def _parse_nmap_xml(self, xml_file: str) -> List[Dict]:
        """
        Parse nmap XML output
        """
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            ports = []
            
            # Find all ports
            for port in root.findall(".//port"):
                port_id = port.get("portid")
                protocol = port.get("protocol")
                
                # Get service info
                service = port.find("service")
                service_name = service.get("name") if service is not None else "unknown"
                service_version = service.get("version") if service is not None else ""
                
                # Get state
                state = port.find("state")
                state_status = state.get("state") if state is not None else "unknown"
                
                if state_status == "open" and port_id is not None:
                    ports.append({
                        "port": int(port_id),
                        "protocol": protocol,
                        "service": service_name,
                        "version": service_version,
                        "state": state_status
                    })
            
            return ports
            
        except Exception as e:
            logger.error(f"Error parsing nmap XML: {str(e)}")
            return []
    
    # Note: _run_nuclei method moved to vulnscan module where it belongs 