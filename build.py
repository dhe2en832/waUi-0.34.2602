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

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def build_executable():
    """Build Windows executable"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", "WACSA-MD2-UI",
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--icon=icon.ico",  # Application icon (if available)
        "--add-data=*.json;.",  # Include JSON files
        "--hidden-import=requests",
        "--hidden-import=aiohttp", 
        "--hidden-import=customtkinter",
        "--hidden-import=loguru",
        "main.py"
    ]
    
    # Remove icon option if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print(f"Executable created: {os.path.join('dist', 'WACSA-MD2-UI.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

def create_installer():
    """Create NSIS installer (optional)"""
    nsis_script = """
; WACSA-MD2 UI Installer Script
!define APP_NAME "WACSA-MD2 UI"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "WACSA Team"
!define APP_URL "http://localhost"
!define APP_EXE "WACSA-MD2-UI.exe"

Name "${APP_NAME}"
OutFile "${APP_NAME}-Setup-${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\${APP_EXE}"
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${APP_EXE}"
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    RMDir "$INSTDIR"
SectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    print("NSIS installer script created: installer.nsi")
    print("To create installer, run with NSIS: makensis installer.nsi")

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
        
        # Install dependencies
        install_dependencies()
        
        # Build executable
        build_executable()
        
        # Create installer script
        create_installer()
        
        print("\nBuild process completed!")
        print("=" * 40)
        print("Executable: dist/WACSA-MD2-UI.exe")
        print("Installer script: installer.nsi")
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
