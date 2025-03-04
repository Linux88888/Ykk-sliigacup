from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time

def scrape_and_save():
    with sync_playwright() as p:
        # Launch with more stealth settings
        browser = p.chromium.launch(headless=False)  # Try with headless=False first for debugging
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="fi-FI"  # Set locale to Finnish
        )
        
        # Enable console logs to see what's happening
        page = context.new_page()
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        
        try:
            print("Navigating to page...")
            url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"
            response = page.goto(url, wait_until="domcontentloaded")
            
            # Check response status
            print(f"Page loaded with status: {response.status}")
            if response.status != 200:
                print(f"Warning: Page returned status code {response.status}")
            
            # Take screenshot for debugging
            page.screenshot(path="initial_load.png")
            print("Took initial screenshot")
            
            # Wait for page to stabilize
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Extra time for any JavaScript to execute
            
            # Check if we need to handle cookie consent
            if page.query_selector("button:has-text('Hyväksy kaikki')"):
                print("Accepting cookies...")
                page.click("button:has-text('Hyväksy kaikki')")
                time.sleep(2)
            
            # Save HTML for inspection
            html_content = page.content()
            with open("page_content.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Saved page HTML for inspection")
            
            # Check for different possible table selectors
            possible_selectors = [
                "table.v-data-table tbody tr",
                "div.v-data-table table tbody tr",
                ".v-data-table__wrapper table tbody tr",
                "table tbody tr"
            ]
            
            found_rows = None
            used_selector = None
            
            for selector in possible_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    # Just check if exists without waiting too long
                    if page.query_selector(selector):
                        rows = page.query_selector_all(selector)
                        print(f"Found {len(rows)} rows with selector '{selector}'")
                        if len(rows) > 0:
                            found_rows = rows
                            used_selector = selector
                            break
                except Exception as e:
                    print(f"Error with selector '{selector}': {str(e)}")
            
            # Take another screenshot after waiting
            page.screenshot(path="after_wait.png")
            print("Took second screenshot after waiting")
            
            if not found_rows:
                print("Could not find table rows with any selector. Checking for table presence...")
                tables = page.query_selector_all("table")
                print(f"Found {len(tables)} tables on the page")
                
                for i, table in enumerate(tables):
                    print(f"Table {i+1} structure:")
                    print(table.evaluate("el => el.outerHTML.substring(0, 300) + '...'"))
                
                raise Exception("Failed to find table rows with any selector")
            
            print(f"Successfully found rows using selector: {used_selector}")
            
            # Create CSV file
            with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
                
                for row in found_rows:
                    cells = row.query_selector_all("td")
                    if cells:
                        data = [cell.inner_text().strip() for cell in cells]
                        if len(data) >= 7:  # Ensure we have enough columns
                            writer.writerow(data[:7])  # Take first 7 columns
                            print(f"Saved row: {data[:7]}")
                        else:
                            print(f"Skipped incomplete row: {data}")
            
            # Update timestamp
            with open("timestamp.txt", "w", encoding="utf-8") as ts_file:
                ts_file.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("Scraping completed successfully!")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            # Take error screenshot
            page.screenshot(path="error.png")
            # Save page content for debugging
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            raise e
        
        finally:
            browser.close()
            print("Browser closed")

if __name__ == "__main__":
    scrape_and_save()
