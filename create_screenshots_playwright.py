#!/usr/bin/env python3
"""
Create screenshots using Playwright
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def create_screenshots():
    """Create screenshots of the Marketing Bot Pro interface"""
    print("🚀 Creating screenshots with Playwright...")
    
    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            # Navigate to the app
            print("🌐 Navigating to http://localhost:8501...")
            await page.goto("http://localhost:8501", wait_until="networkidle")
            
            # Wait for the page to load completely
            await page.wait_for_timeout(3000)
            
            print("📸 Taking screenshots...")
            
            # 1. Main Dashboard
            print("  📊 Capturing main dashboard...")
            await page.screenshot(path="screenshots/main_dashboard.png", full_page=True)
            
            # 2. Content Generation Tab
            print("  ✍️ Capturing content generation tab...")
            try:
                # Look for content generation tab
                await page.click("text=Content Generation", timeout=5000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            except:
                print("    ⚠️ Content generation tab not found, using main view")
                await page.screenshot(path="screenshots/content_generation.png", full_page=True)
            
            # 3. Customer Segmentation Tab
            print("  📊 Capturing customer segmentation tab...")
            try:
                # Look for customer segmentation tab
                await page.click("text=Customer Segmentation", timeout=5000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            except:
                print("    ⚠️ Customer segmentation tab not found, using main view")
                await page.screenshot(path="screenshots/rfm_analysis.png", full_page=True)
            
            # 4. Campaign Management Tab
            print("  📧 Capturing campaign management tab...")
            try:
                # Look for campaign management tab
                await page.click("text=Campaign Management", timeout=5000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            except:
                print("    ⚠️ Campaign management tab not found, using main view")
                await page.screenshot(path="screenshots/campaign_dashboard.png", full_page=True)
            
            print("✅ Screenshots created successfully!")
            print("📁 Check the screenshots/ directory for your images")
            
        except Exception as e:
            print(f"❌ Error taking screenshots: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(create_screenshots())
