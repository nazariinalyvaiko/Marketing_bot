#!/usr/bin/env python3
"""
Script to help create screenshots for Marketing Bot Pro
Run this script to start the app and get instructions for screenshots
"""

import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 Marketing Bot Pro - Screenshot Creator")
    print("=" * 50)
    
    # Check if screenshots directory exists
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    print("📸 Screenshot Requirements:")
    print("1. main_dashboard.png - Main interface")
    print("2. content_generation.png - AI content generation tab")
    print("3. rfm_analysis.png - Customer segmentation tab")
    print("4. campaign_dashboard.png - Campaign management tab")
    print()
    
    print("🎯 Instructions:")
    print("1. The Streamlit app will start automatically")
    print("2. Take screenshots of each section")
    print("3. Save them in the screenshots/ directory")
    print("4. Use high resolution (1920x1080 or higher)")
    print()
    
    input("Press Enter to start the Streamlit app...")
    
    print("🌐 Starting Streamlit app...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("📸 Take screenshots of each section as described above")
    print()
    print("🛑 Press Ctrl+C to stop the app when done")
    
    try:
        # Start Streamlit
        subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n✅ Screenshot session completed!")
        print("📁 Check the screenshots/ directory for your images")

if __name__ == "__main__":
    main()
