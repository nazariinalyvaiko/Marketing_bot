#!/usr/bin/env python3
"""
Create improved screenshots with dark theme and proper tab navigation
"""

import asyncio
import time
from playwright.async_api import async_playwright
from pathlib import Path

async def create_improved_screenshots():
    """Create screenshots with dark theme and proper tab navigation"""
    print("🚀 Creating improved screenshots with dark theme...")
    
    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser with dark theme
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            color_scheme='dark'  # Force dark theme
        )
        page = await context.new_page()
        
        try:
            # Navigate to the app
            print("🌐 Navigating to http://localhost:8501...")
            await page.goto("http://localhost:8501", wait_until="networkidle")
            
            # Wait for the page to load completely
            await page.wait_for_timeout(5000)
            
            print("📸 Taking screenshots...")
            
            # 1. Main Dashboard (Customer Segmentation tab)
            print("  📊 Capturing main dashboard (Customer Segmentation)...")
            await page.screenshot(path="screenshots/main_dashboard.png", full_page=True)
            
            # 2. Content Generation Tab
            print("  ✍️ Capturing content generation tab...")
            try:
                # Click on Content Generation tab
                await page.click("text=Content Generation", timeout=10000)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Content generation tab not found: {e}")
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            
            # 3. Customer Segmentation Tab (go back to it)
            print("  📊 Capturing customer segmentation tab...")
            try:
                # Click on Customer Segmentation tab
                await page.click("text=Customer Segmentation", timeout=10000)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Customer segmentation tab not found: {e}")
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            
            # 4. Campaign Management Tab
            print("  📧 Capturing campaign management tab...")
            try:
                # Click on Campaign Management tab
                await page.click("text=Campaign Management", timeout=10000)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Campaign management tab not found: {e}")
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            
            print("✅ Improved screenshots created successfully!")
            print("📁 Check the screenshots/ directory for your images")
            
        except Exception as e:
            print(f"❌ Error taking screenshots: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(create_improved_screenshots())
