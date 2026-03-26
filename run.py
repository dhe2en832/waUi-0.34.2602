#!/usr/bin/env python3
"""
Quick run script for WACSA-MD2 UI
Installs dependencies and runs the application
"""

import subprocess
import sys
import os

def main():
    """Install dependencies and run application"""
    print("WACSA-MD2 UI Quick Start")
    print("=" * 30)
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please run: pip install -r requirements.txt")
        return
    
    # Run application
    print("Starting WACSA-MD2 UI...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
