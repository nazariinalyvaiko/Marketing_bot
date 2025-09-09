#!/usr/bin/env python3
"""
Create final screenshots with proper tab navigation and dark theme
"""

import asyncio
import time
from playwright.async_api import async_playwright
from pathlib import Path

async def create_final_screenshots():
    """Create screenshots with proper tab navigation"""
    print("🚀 Creating final screenshots with proper tab navigation...")
    
    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            color_scheme='dark'
        )
        page = await context.new_page()
        
        try:
            # Navigate to the app
            print("🌐 Navigating to http://localhost:8501...")
            await page.goto("http://localhost:8501", wait_until="networkidle")
            
            # Wait for the page to load completely
            await page.wait_for_timeout(5000)
            
            print("📸 Taking screenshots...")
            
            # 1. Main Dashboard (Segmentation tab - default)
            print("  📊 Capturing Segmentation tab (main dashboard)...")
            await page.screenshot(path="screenshots/main_dashboard.png", full_page=True)
            
            # 2. AI Content Generation Tab
            print("  ✍️ Capturing AI Content Generation tab...")
            try:
                # Click on the second tab (AI Content Generation)
                tabs = await page.query_selector_all('[role="tab"]')
                if len(tabs) >= 2:
                    await tabs[1].click()  # Click second tab
                    await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Content generation tab not found: {e}")
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            
            # 3. Campaign Management Tab
            print("  📧 Capturing Campaign Management tab...")
            try:
                # Click on the third tab (Campaign Management)
                tabs = await page.query_selector_all('[role="tab"]')
                if len(tabs) >= 3:
                    await tabs[2].click()  # Click third tab
                    await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Campaign management tab not found: {e}")
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            
            # 4. Send Messages Tab (RFM Analysis)
            print("  📤 Capturing Send Messages tab...")
            try:
                # Click on the fourth tab (Send Messages)
                tabs = await page.query_selector_all('[role="tab"]')
                if len(tabs) >= 4:
                    await tabs[3].click()  # Click fourth tab
                    await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            except Exception as e:
                print(f"    ⚠️ Send messages tab not found: {e}")
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            
            print("✅ Final screenshots created successfully!")
            print("📁 Check the screenshots/ directory for your images")
            
        except Exception as e:
            print(f"❌ Error taking screenshots: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(create_final_screenshots())
