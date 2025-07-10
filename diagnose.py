#!/usr/bin/env python3
"""
Environment Diagnostic Tool
==========================

This script helps diagnose the development environment and identify issues.

Author: GitHub Copilot Assistant
Date: July 2025
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_python():
    """Check Python version and installation."""
    print_header("Python Environment")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")

def check_modules():
    """Check required Python modules."""
    print_header("Python Modules")
    
    required_modules = [
        'flask', 'flask_cors', 'pathlib', 'json', 
        'base64', 'tempfile', 'subprocess'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError as e:
            print(f"❌ {module} - Not Available ({str(e)})")

def check_node():
    """Check Node.js and npm installation."""
    print_header("Node.js Environment")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js: Not available")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js: Not found")
    
    # Check npm - try multiple methods for Windows
    npm_found = False
    try:
        # Method 1: Direct npm command
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
            npm_found = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    if not npm_found:
        try:
            # Method 2: PowerShell command
            result = subprocess.run(['powershell', '-Command', 'npm --version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()}")
                npm_found = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    if not npm_found:
        print("❌ npm: Not found or not accessible")

def check_mermaid():
    """Check Mermaid CLI installation."""
    print_header("Mermaid CLI")
    
    found = False
    
    # Method 1: Check via npm list global packages
    try:
        result = subprocess.run(['npm', 'list', '-g', '--depth=0'], 
                              capture_output=True, text=True, timeout=15, 
                              shell=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0 and result.stdout and '@mermaid-js/mermaid-cli' in result.stdout:
            print("✅ @mermaid-js/mermaid-cli: Found in global packages")
            found = True
            # Extract version
            for line in result.stdout.split('\n'):
                if '@mermaid-js/mermaid-cli' in line:
                    print(f"   {line.strip()}")
                    break
    except (subprocess.TimeoutExpired, FileNotFoundError, UnicodeDecodeError):
        pass
    
    # Method 2: Try mmdc command directly
    if not found:
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=10, 
                                  shell=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0 and result.stdout:
                print(f"✅ mmdc: {result.stdout.strip()}")
                found = True
        except (subprocess.TimeoutExpired, FileNotFoundError, UnicodeDecodeError):
            print("❌ mmdc: Command not found in PATH")
    
    # Method 3: Simple check - if npm shows the package is installed globally
    if not found:
        try:
            # Simplified check
            result = subprocess.run(['powershell', '-Command', 
                                   'npm list -g 2>$null | Select-String "mermaid-cli"'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Mermaid CLI: Detected via PowerShell check")
                print(f"   {result.stdout.strip()}")
                found = True
        except:
            pass
    
    # Method 4: Check local node_modules
    if not found:
        local_mmdc = Path('./node_modules/.bin/mmdc')
        if local_mmdc.exists():
            print("✅ Local mermaid-cli found in node_modules/.bin/")
            found = True
    
    if found:
        print("✅ Mermaid CLI is available for use!")
        print("💡 Note: CLI detection works, but npm permissions may affect usage")
    else:
        print("❌ Mermaid CLI not detected")
        print("\n💡 Troubleshooting:")
        print("   1. Install: npm install -g @mermaid-js/mermaid-cli")
        print("   2. Or install locally: npm install @mermaid-js/mermaid-cli")
        print("   3. Run as Administrator if permission issues persist")
        print("   4. Check if antivirus is blocking npm operations")

def check_files():
    """Check project files."""
    print_header("Project Files")
    
    required_files = [
        'mermaid_to_png.py',
        'web_app.py',
        'package.json',
        'requirements.txt',
        'templates/index.html',
        'static/style.css'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - Missing")

def check_directories():
    """Check required directories."""
    print_header("Project Directories")
    
    required_dirs = [
        'templates',
        'static',
        'examples',
        'uploads',
        'outputs'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            files = list(path.iterdir())
            print(f"✅ {dir_path}/ ({len(files)} items)")
        else:
            print(f"❌ {dir_path}/ - Missing")
            # Create missing directories
            try:
                path.mkdir(exist_ok=True)
                print(f"   📁 Created {dir_path}/")
            except Exception as e:
                print(f"   ⚠️ Could not create: {str(e)}")

def check_ports():
    """Check if required ports are available."""
    print_header("Network Ports")
    
    import socket
    
    def is_port_available(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    ports = [5000, 8000, 3000]
    for port in ports:
        if is_port_available(port):
            print(f"✅ Port {port}: Available")
        else:
            print(f"⚠️ Port {port}: In use or blocked")

def generate_recommendations():
    """Generate recommendations based on checks."""
    print_header("Recommendations")
    
    print("1. 🔧 Environment Setup:")
    print("   - Ensure Python 3.6+ is installed and in PATH")
    print("   - Install required Python packages: pip install -r requirements.txt")
    print("")
    
    print("2. 🌐 Web Application:")
    print("   - Start with: python web_app.py")
    print("   - Access at: http://localhost:5000")
    print("")
    
    print("3. 📦 Optional - Mermaid CLI:")
    print("   - Install Node.js from https://nodejs.org/")
    print("   - Install Mermaid CLI: npm install -g @mermaid-js/mermaid-cli")
    print("")
    
    print("4. 🚀 Quick Start:")
    print("   - Run: python diagnose.py")
    print("   - Run: python web_app.py")
    print("   - Open: http://localhost:5000")

def main():
    """Main diagnostic function."""
    print("🔍 Mermaid to PNG Environment Diagnostic")
    print(f"Running on: {platform.system()} {platform.release()}")
    
    check_python()
    check_modules()
    check_node()
    check_mermaid()
    check_files()
    check_directories()
    check_ports()
    generate_recommendations()
    
    print(f"\n{'='*60}")
    print(" Diagnostic Complete")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
