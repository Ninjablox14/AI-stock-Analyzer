#!/usr/bin/env python3
"""
Setup script for AI Stock Dashboard
Helps users set up their environment and API keys
"""

import os
import sys

def setup():
    print("🚀 AI Stock Dashboard Setup")
    print("=" * 40)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False

    print(f"✅ Python {sys.version.split()[0]} detected")

    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        create_env = input("Would you like to create a .env file? (y/n): ").lower().strip()
        if create_env == 'y':
            api_key = input("Enter your Groq API key: ").strip()
            with open('.env', 'w') as f:
                f.write(f"GROQ_API_KEY={api_key}\n")
            print("✅ .env file created")

    # Check dependencies
    try:
        import flask
        import yfinance
        import groq
        import matplotlib
        print("✅ Core dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        install = input("Would you like to install dependencies? (y/n): ").lower().strip()
        if install == 'y':
            os.system(f"{sys.executable} -m pip install -r requirements.txt")
            print("✅ Dependencies installed")

    print("\n🎉 Setup complete!")
    print("Run 'python app.py' to start the dashboard")
    return True

if __name__ == "__main__":
    setup()