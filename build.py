#!/usr/bin/env python3
"""
Build script for WACSA-MD2 UI
Creates Windows executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
            
    # Clean .pyc files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))
    
    # Clean spec files
    for spec_file in ["WACSA-MD2-UI.spec", "WACSA-MD2-UI-v2.spec"]:
        if os.path.exists(spec_file):
            os.remove(spec_file)

def build_executable():
    """Build Windows executable"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name", "WACSA-MD2-UI",
        "--windowed",
        "--onefile",
        "--hidden-import=requests",
        "--hidden-import=customtkinter",
        "--hidden-import=loguru",
        "--add-data", "src;src",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print(f"Executable created: {os.path.join('dist', 'WACSA-MD2-UI.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

def main():
    """Main build process"""
    print("WACSA-MD2 UI Build Process")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # Clean previous builds
        clean_build()
        
        # Build executable
        build_executable()
        
        print("\nBuild process completed!")
        print("=" * 40)
        print("Executable: dist/WACSA-MD2-UI.exe")
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
