#!/usr/bin/env python3
"""
Build script to create a standalone executable for the Stock Dashboard
"""

import os
import subprocess
import sys

def build_executable():
    """Build a standalone executable using PyInstaller"""

    print("Building Stock Dashboard executable...")

    # Install PyInstaller if not already installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Create the executable
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "StockDashboard",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "app.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("Executable created successfully!")
        print("Find it in the 'dist' folder as 'StockDashboard.exe'")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

    return True

if __name__ == "__main__":
    success = build_executable()
    if success:
        print("\nTo run the executable:")
        print("1. Go to the 'dist' folder")
        print("2. Double-click 'StockDashboard.exe'")
        print("3. Open http://127.0.0.1:5000 in your browser")
    else:
        print("Failed to build executable")