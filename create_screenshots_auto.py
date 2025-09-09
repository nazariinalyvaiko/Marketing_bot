#!/usr/bin/env python3
"""
Automated screenshot creation for Marketing Bot Pro
Uses Selenium to capture screenshots of the web interface
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Setup Chrome driver with headless mode"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome driver not available: {e}")
        print("Please install Chrome and chromedriver")
        return None

def take_screenshots():
    """Take screenshots of the Marketing Bot Pro interface"""
    print("🚀 Starting automated screenshot creation...")
    
    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("❌ Could not setup Chrome driver")
        return
    
    try:
        # Navigate to the app
        print("🌐 Navigating to http://localhost:8501...")
        driver.get("http://localhost:8501")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("📸 Taking screenshots...")
        
        # 1. Main Dashboard
        print("  📊 Capturing main dashboard...")
        driver.save_screenshot("screenshots/main_dashboard.png")
        
        # 2. Content Generation Tab
        print("  ✍️ Capturing content generation tab...")
        try:
            content_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Content Generation') or contains(text(), '✍️')]")
            content_tab.click()
            time.sleep(2)
            driver.save_screenshot("screenshots/content_generation.png")
        except:
            print("    ⚠️ Content generation tab not found, using main view")
            driver.save_screenshot("screenshots/content_generation.png")
        
        # 3. Customer Segmentation Tab
        print("  📊 Capturing customer segmentation tab...")
        try:
            segment_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Customer Segmentation') or contains(text(), '📊')]")
            segment_tab.click()
            time.sleep(2)
            driver.save_screenshot("screenshots/rfm_analysis.png")
        except:
            print("    ⚠️ Customer segmentation tab not found, using main view")
            driver.save_screenshot("screenshots/rfm_analysis.png")
        
        # 4. Campaign Management Tab
        print("  📧 Capturing campaign management tab...")
        try:
            campaign_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Campaign Management') or contains(text(), '📧')]")
            campaign_tab.click()
            time.sleep(2)
            driver.save_screenshot("screenshots/campaign_dashboard.png")
        except:
            print("    ⚠️ Campaign management tab not found, using main view")
            driver.save_screenshot("screenshots/campaign_dashboard.png")
        
        print("✅ Screenshots created successfully!")
        print("📁 Check the screenshots/ directory for your images")
        
    except Exception as e:
        print(f"❌ Error taking screenshots: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    take_screenshots()
