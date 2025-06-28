#!/usr/bin/env python3
import subprocess
import os
import sys

def check_tool(tool_name):
    print(f"\n=== Checking {tool_name} ===")
    
    # Set PATH to include Go bin directory
    go_path = os.environ.get('GOPATH', '/app/go')
    go_bin = os.path.join(go_path, 'bin')
    if go_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = f"{os.environ.get('PATH', '')}:{go_bin}"
    
    print(f"PATH: {os.environ.get('PATH', '')}")
    
    # Try different possible locations for Go tools
    possible_paths = [
        tool_name,
        f"/app/go/bin/{tool_name}",
        f"/usr/local/go/bin/{tool_name}",
        f"/root/go/bin/{tool_name}"
    ]
    
    for path in possible_paths:
        print(f"Trying: {path}")
        try:
            result = subprocess.run([path, "--version"], 
                                 capture_output=True, check=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ {tool_name} found at: {path}")
                print(f"Output: {result.stdout.decode()}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"✗ Failed: {e}")
            continue
    
    print(f"✗ {tool_name} not found")
    return False

if __name__ == "__main__":
    tools = ["sublist3r", "nmap"]
    
    print("Checking all tools...")
    for tool in tools:
        check_tool(tool) 