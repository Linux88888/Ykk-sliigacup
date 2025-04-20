import asyncio
from playwright.async_api import async_playwright
import time
import os

async def check_website_access():
    """Basic diagnostic check for website access"""
    async with async_playwright() as p:
        # IMPORTANT: Must use headless=True in GitHub Actions
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # First, check a known good site to verify internet access
        await page.goto('https://example.com', timeout=30000)
        await page.screenshot(path="example_com.png")
        print("Successfully accessed example.com")
        
        # Now try the target site
        print("\nAttempting to access palloliitto.fi...")
        try:
            await page.goto('https://palloliitto.fi', timeout=60000)
            await page.screenshot(path="palloliitto_home.png")
            main_page_title = await page.title()
            print(f"Main site title: {main_page_title}")
            print("Successfully accessed palloliitto.fi")
        except Exception as e:
            print(f"Error accessing palloliitto.fi: {e}")
        
        # Try the specific results service
        print("\nAttempting to access tulospalvelu.palloliitto.fi...")
        try:
            await page.goto('https://tulospalvelu.palloliitto.fi/', timeout=60000)
            await page.screenshot(path="tulospalvelu_home.png")
            tulospalvelu_title = await page.title()
            print(f"Results service title: {tulospalvelu_title}")
            print("Successfully accessed tulospalvelu.palloliitto.fi")
        except Exception as e:
            print(f"Error accessing tulospalvelu.palloliitto.fi: {e}")
            
        await browser.close()

if __name__ == "__main__":
    print(f"Starting diagnostics at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(check_website_access())
    print(f"Diagnostics completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
