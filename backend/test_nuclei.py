#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.vulnscan.scanner import VulnerabilityScanner

async def test_nuclei():
    print("Testing nuclei functionality in vulnscan module...")
    
    scanner = VulnerabilityScanner()
    
    # Test nuclei detection
    print(f"Nuclei available: {scanner.available_tools['nuclei']}")
    
    if scanner.available_tools['nuclei']:
        print("Running nuclei vulnerability scan...")
        try:
            results = await scanner.scan_with_nuclei("http://testphp.vulnweb.com")
            print(f"Found {len(results)} vulnerabilities")
            for result in results[:5]:  # Show first 5 results
                print(f"  - {result.get('title', 'Unknown')} ({result.get('severity', 'unknown')})")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Nuclei not available")

if __name__ == "__main__":
    asyncio.run(test_nuclei()) 