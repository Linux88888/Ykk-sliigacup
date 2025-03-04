from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time
import os

def scrape_and_save():
    with sync_playwright() as p:
        # Always use headless mode in GitHub Actions
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="fi-FI"  # Set locale to Finnish
        )
        
        # Create debug directory
        os.makedirs("debug", exist_ok=True)
        
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
            page.screenshot(path="debug/initial_load.png")
            print("Took initial screenshot")
            
            # Save HTML for inspection immediately
            html_content = page.content()
            with open("debug/initial_content.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Saved initial page HTML")
            
            # Wait for page to stabilize
            page.wait_for_load_state("networkidle", timeout=60000)  # Extended timeout
            time.sleep(5)  # Extra time for any JavaScript to execute
            
            # Check if we need to handle cookie consent
            if page.query_selector("button:has-text('Hyväksy kaikki')"):
                print("Accepting cookies...")
                page.click("button:has-text('Hyväksy kaikki')")
                time.sleep(2)
            
            # Take another screenshot after waiting
            page.screenshot(path="debug/after_wait.png")
            print("Took second screenshot after waiting")
            
            # Save HTML after waiting
            html_after_wait = page.content()
            with open("debug/after_wait.html", "w", encoding="utf-8") as f:
                f.write(html_after_wait)
            print("Saved page HTML after waiting")
            
            # Gather information about what's on the page
            print("Analyzing page structure...")
            page.evaluate("""
            () => {
                const tables = document.querySelectorAll('table');
                console.log(`Found ${tables.length} tables on the page`);
                
                for (let i = 0; i < tables.length; i++) {
                    console.log(`Table ${i+1} class: ${tables[i].className}`);
                    console.log(`Table ${i+1} rows: ${tables[i].querySelectorAll('tr').length}`);
                }
                
                // Log all element classes for debugging
                const allElements = document.querySelectorAll('*');
                const classes = new Set();
                allElements.forEach(el => {
                    if (el.className && typeof el.className === 'string') {
                        el.className.split(' ').forEach(c => {
                            if (c.trim()) classes.add(c.trim());
                        });
                    }
                });
                console.log('Classes found on page:', Array.from(classes).join(', '));
            }
            """)
            
            # Try to find network requests for API data
            print("Monitoring network requests...")
            page.route("**/*", lambda route: (
                print(f"Network request: {route.request.url}") if route.request.url.endswith(".json") or "api" in route.request.url else None,
                route.continue_()
            ))
            
            # Refresh the page to see network requests
            page.reload(wait_until="networkidle")
            
            # Check for different possible table selectors
            possible_selectors = [
                "table.v-data-table tbody tr",
                "div.v-data-table table tbody tr",
                ".v-data-table__wrapper table tbody tr",
                "table tbody tr",
                ".v-data-table__wrapper tbody tr",
                "div[role='table'] div[role='row']",  # For non-table implementations
                "div.statistics-table div[role='row']",
                "[data-test='player-statistics-table'] tbody tr"
            ]
            
            found_rows = None
            used_selector = None
            
            for selector in possible_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    # Check if exists
                    if page.query_selector(selector):
                        rows = page.query_selector_all(selector)
                        print(f"Found {len(rows)} rows with selector '{selector}'")
                        if len(rows) > 0:
                            found_rows = rows
                            used_selector = selector
                            break
                except Exception as e:
                    print(f"Error with selector '{selector}': {str(e)}")
            
            if not found_rows:
                print("Could not find table rows with any selector. Trying direct data extraction...")
                
                # Try to extract table data from the HTML structure
                table_data = page.evaluate("""
                () => {
                    // Look for any tabular data on the page
                    const rows = [];
                    
                    // Try traditional tables
                    document.querySelectorAll('table tbody tr').forEach(tr => {
                        const rowData = [];
                        tr.querySelectorAll('td').forEach(td => {
                            rowData.push(td.textContent.trim());
                        });
                        if (rowData.length > 0) rows.push(rowData);
                    });
                    
                    // If no traditional tables, try div-based tables
                    if (rows.length === 0) {
                        document.querySelectorAll('div[role="row"]').forEach(row => {
                            const rowData = [];
                            row.querySelectorAll('div[role="cell"]').forEach(cell => {
                                rowData.push(cell.textContent.trim());
                            });
                            if (rowData.length > 0) rows.push(rowData);
                        });
                    }
                    
                    return rows;
                }
                """)
                
                print(f"Direct extraction found {len(table_data)} rows")
                
                if len(table_data) > 0:
                    print("Creating CSV from directly extracted data")
                    with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
                        
                        for row_data in table_data:
                            if len(row_data) >= 7:
                                writer.writerow(row_data[:7])
                                print(f"Saved row: {row_data[:7]}")
                            else:
                                print(f"Skipped incomplete row: {row_data}")
                    
                    # Update timestamp
                    with open("timestamp.txt", "w", encoding="utf-8") as ts_file:
                        ts_file.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    print("Direct extraction completed successfully!")
                    return
                
                # If we get here, we couldn't find the data
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
            page.screenshot(path="debug/error.png")
            # Save page content for debugging
            with open("debug/error_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            raise e
        
        finally:
            browser.close()
            print("Browser closed")

if __name__ == "__main__":
    scrape_and_save()
