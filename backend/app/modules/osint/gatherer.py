"""
OSINT Information Gatherer Module
"""
import asyncio
import aiohttp
import dns.resolver
import whois
import subprocess
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import os
import re
import tempfile


class OSINTGatherer:
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def gather_whois(self, domain: str) -> Dict[str, Any]:
        """Gather WHOIS information"""
        try:
            w = whois.whois(domain)
            return {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": w.creation_date.isoformat() if w.creation_date else None,
                "expiration_date": w.expiration_date.isoformat() if w.expiration_date else None,
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else []
            }
        except Exception as e:
            print(f"Error in WHOIS lookup for {domain}: {e}")
            return {"error": str(e)}
    
    async def gather_dns(self, domain: str) -> Dict[str, Any]:
        """Gather DNS information"""
        results = {
            "domain": domain,
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": []
        }
        
        record_types = {
            "A": "a_records",
            "AAAA": "aaaa_records", 
            "MX": "mx_records",
            "NS": "ns_records",
            "TXT": "txt_records",
            "CNAME": "cname_records"
        }
        
        for record_type, key in record_types.items():
            try:
                answers = dns.resolver.resolve(domain, record_type)
                if answers.rrset:
                    results[key] = [str(answer) for answer in answers.rrset]
                else:
                    results[key] = []
            except Exception as e:
                print(f"Error resolving {record_type} records for {domain}: {e}")
                results[key] = []
        
        return results
    
    async def gather_wayback_urls(self, domain: str) -> List[str]:
        """Gather URLs from Wayback Machine using waybackurls tool, streaming output and logging each line."""
        try:
            print(f"[waybackurls] Starting waybackurls for domain: {domain}")
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                "waybackurls", domain,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            urls = []
            url_regex = re.compile(r'https?://[^\s]+')
            try:
                while True:
                    try:
                        line = await asyncio.wait_for(process.stdout.readline(), timeout=60)
                    except asyncio.TimeoutError:
                        print(f"[waybackurls] Timeout reached while reading output for domain: {domain}")
                        process.kill()
                        break
                    if not line:
                        break
                    decoded_line = line.decode().strip()
                    print(f"[waybackurls] {decoded_line}")
                    if url_regex.match(decoded_line):
                        urls.append(decoded_line)
                        if len(urls) >= 1000:
                            print(f"[waybackurls] Reached 1000 URLs, stopping collection.")
                            process.kill()
                            break
                # Wait for process to exit (with a short timeout)
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    print(f"[waybackurls] Process did not exit cleanly, killing.")
                    process.kill()
            except Exception as e:
                print(f"[waybackurls] Error while reading output: {e}")
                process.kill()
            duration = time.time() - start_time
            print(f"[waybackurls] Finished waybackurls for domain: {domain} in {duration:.2f} seconds, collected {len(urls)} URLs.")
            return urls
        except Exception as e:
            print(f"[waybackurls] Error running waybackurls: {e}")
            return []
    
    async def run_full_gathering(self, target: str) -> Dict[str, Any]:
        """Run full OSINT gathering"""
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "whois": {},
            "dns": {},
            "wayback_urls": []
        }
        
        # Gather WHOIS information
        results["whois"] = await self.gather_whois(target)
        
        # Gather DNS information
        results["dns"] = await self.gather_dns(target)
        
        # Gather Wayback URLs
        results["wayback_urls"] = await self.gather_wayback_urls(target)
        
        return results
    
    async def run_selected_tools(self, target: str, tools: List[str]) -> Dict[str, Any]:
        """Run OSINT gathering with only selected tools"""
        results = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "whois": {},
            "dns": {},
            "wayback_urls": []
        }
        
        # Run only the selected tools
        for tool in tools:
            if tool == "whois":
                results["whois"] = await self.gather_whois(target)
            elif tool == "dns":
                results["dns"] = await self.gather_dns(target)
            elif tool == "waybackurls":
                results["wayback_urls"] = await self.gather_wayback_urls(target)
        
        return results
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close() 