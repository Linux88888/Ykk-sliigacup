import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os
import traceback
import json

async def save_screenshot(page, filename):
    """Save a screenshot of the page"""
    await page.screenshot(path=f"{filename}.png", full_page=True)
    print(f"Saved screenshot to {filename}.png")

async def save_html(page, filename):
    """Save the HTML content of the page"""
    html = await page.content()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Saved HTML to {filename}")
    return html

async def get_league_table():
    """Get the league table using Playwright"""
    print("\n=== FETCHING LEAGUE TABLE ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport size
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # Navigate to the league table page
        url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/"
        print(f"Loading URL: {url}")
        
        try:
            # Navigate with a timeout of 60 seconds
            await page.goto(url, timeout=60000)
            
            # Wait for the page to load completely
            await page.wait_for_load_state("networkidle")
            
            print("Page loaded successfully")
            
            # Save screenshot and HTML for debugging
            await save_screenshot(page, "league_table_screenshot")
            html = await save_html(page, "league_table.html")
            
            # Find all tables on the page
            tables = await page.query_selector_all('table')
            print(f"Found {len(tables)} tables on the page")
            
            if not tables:
                print("No tables found on the page!")
                await browser.close()
                return None
            
            # Process the first table (usually the standings table)
            league_table = []
            
            # Extract the table content
            table_html = await tables[0].inner_html()
            with open("league_table_content.html", "w", encoding="utf-8") as f:
                f.write(table_html)
            
            # Get headers
            headers = await page.eval_on_selector_all('table:first-of-type th', 
                                                    'elements => elements.map(e => e.textContent.trim())')
            print(f"Headers: {headers}")
            
            # Map headers to our standardized column names
            header_mapping = {}
            for i, header in enumerate(headers):
                if header == '#' or header == 'Sija':
                    header_mapping[i] = 'Sijoitus'
                elif header == 'Team' or header == 'Joukkue':
                    header_mapping[i] = 'Joukkue'
                elif header in ['P', 'Ottelut']:
                    header_mapping[i] = 'Ottelut'
                elif header in ['W', 'Voitot']:
                    header_mapping[i] = 'Voitot'
                elif header in ['D', 'Tasapelit']:
                    header_mapping[i] = 'Tasapelit'
                elif header in ['L', 'Tappiot']:
                    header_mapping[i] = 'Tappiot'
                elif header in ['GF', 'Tehdyt']:
                    header_mapping[i] = 'Tehdyt maalit'
                elif header in ['GA', 'Päästetyt']:
                    header_mapping[i] = 'Päästetyt maalit'
                elif header in ['GD', 'Maaliero']:
                    header_mapping[i] = 'Maaliero'
                elif header in ['PTS', 'Pisteet']:
                    header_mapping[i] = 'Pisteet'
                else:
                    header_mapping[i] = header
            
            print(f"Header mapping: {header_mapping}")
            
            # Get all rows (skip header row)
            rows = await page.query_selector_all('table:first-of-type tr:not(:first-child)')
            print(f"Found {len(rows)} data rows")
            
            for row in rows:
                cells = await row.query_selector_all('td')
                
                if len(cells) >= len(headers):
                    team_data = {}
                    
                    for i, cell in enumerate(cells):
                        if i in header_mapping:
                            # For team names, extract the text but also check for images with alt text
                            if header_mapping[i] == 'Joukkue':
                                team_name = await cell.text_content()
                                team_img = await cell.query_selector('img')
                                if team_img:
                                    alt_text = await team_img.get_attribute('alt')
                                    if alt_text:
                                        team_name = alt_text
                                team_data[header_mapping[i]] = team_name.strip()
                            else:
                                cell_text = await cell.text_content()
                                team_data[header_mapping[i]] = cell_text.strip()
                    
                    league_table.append(team_data)
            
            print(f"Extracted {len(league_table)} teams")
            
            # Print first team for verification
            if league_table:
                print(f"Sample team data: {league_table[0]}")
            
            # Convert to DataFrame
            df = pd.DataFrame(league_table)
            
            # Save data
            df.to_csv('Sarjataulukko.csv', index=False, encoding='utf-8')
            with open('Sarjataulukko.json', 'w', encoding='utf-8') as f:
                json.dump(league_table, f, ensure_ascii=False, indent=2)
            
            # Create Markdown
            create_league_table_markdown(df)
            
            await browser.close()
            return df
            
        except Exception as e:
            print(f"Error fetching league table: {e}")
            traceback.print_exc()
            
            # Save error screenshot
            await save_screenshot(page, "league_table_error")
            
            await browser.close()
            return None

async def get_fixtures():
    """Get fixtures using Playwright"""
    print("\n=== FETCHING FIXTURES ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport size
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # Navigate to the fixtures page
        url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
        print(f"Loading URL: {url}")
        
        try:
            # Navigate with a timeout of 60 seconds
            await page.goto(url, timeout=60000)
            
            # Wait for the page to load completely
            await page.wait_for_load_state("networkidle")
            
            print("Page loaded successfully")
            
            # Save screenshot and HTML for debugging
            await save_screenshot(page, "fixtures_screenshot")
            html = await save_html(page, "fixtures.html")
            
            # Find all tables on the page
            tables = await page.query_selector_all('table')
            print(f"Found {len(tables)} tables on the page")
            
            if not tables:
                print("No tables found on the page!")
                await browser.close()
                return None
            
            # Process the first table (usually the fixtures table)
            fixtures = []
            
            # Extract the table content
            table_html = await tables[0].inner_html()
            with open("fixtures_table_content.html", "w", encoding="utf-8") as f:
                f.write(table_html)
            
            # Get headers
            headers = await page.eval_on_selector_all('table:first-of-type th', 
                                                   'elements => elements.map(e => e.textContent.trim())')
            print(f"Headers: {headers}")
            
            # Try to identify column positions based on headers
            date_col = -1
            time_col = -1
            teams_col = -1
            result_col = -1
            venue_col = -1
            
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if any(date_term in header_lower for date_term in ['date', 'päivä', 'pvm']):
                    date_col = i
                elif any(time_term in header_lower for time_term in ['time', 'aika', 'klo']):
                    time_col = i
                elif any(teams_term in header_lower for teams_term in ['teams', 'joukkueet']):
                    teams_col = i
                elif any(result_term in header_lower for result_term in ['result', 'tulos']):
                    result_col = i
                elif any(venue_term in header_lower for venue_term in ['venue', 'paikka', 'stadion']):
                    venue_col = i
            
            # If headers don't help, guess based on common positions
            if date_col == -1:
                date_col = 0  # First column often contains date
            if time_col == -1:
                time_col = 1  # Second column often contains time
            if teams_col == -1:
                teams_col = 2  # Third column often contains teams
            if result_col == -1:
                result_col = 3  # Fourth column often contains results
            if venue_col == -1:
                venue_col = 4  # Fifth column often contains venue
            
            print(f"Column positions - Date: {date_col}, Time: {time_col}, Teams: {teams_col}, Result: {result_col}, Venue: {venue_col}")
            
            # Get all rows (skip header row)
            rows = await page.query_selector_all('table:first-of-type tr:not(:first-child)')
            print(f"Found {len(rows)} data rows")
            
            for i, row in enumerate(rows):
                cells = await row.query_selector_all('td')
                
                if len(cells) >= 3:  # Need at least date, time, and teams
                    match_data = {'Row': i+1}  # Add row number for debugging
                    
                    # Extract data based on identified columns
                    if date_col >= 0 and date_col < len(cells):
                        date_text = await cells[date_col].text_content()
                        match_data['Pelipäivä'] = date_text.strip()
                    else:
                        match_data['Pelipäivä'] = ""
                    
                    if time_col >= 0 and time_col < len(cells):
                        time_text = await cells[time_col].text_content()
                        match_data['Klo'] = time_text.strip()
                    else:
                        match_data['Klo'] = ""
                    
                    # Teams - might be in format "Home - Away"
                    if teams_col >= 0 and teams_col < len(cells):
                        teams_text = await cells[teams_col].text_content()
                        teams_text = teams_text.strip()
                        
                        if " - " in teams_text:
                            home, away = teams_text.split(" - ", 1)
                            match_data['Koti'] = home.strip()
                            match_data['Vieras'] = away.strip()
                        else:
                            match_data['Koti'] = teams_text
                            match_data['Vieras'] = ""
                    else:
                        match_data['Koti'] = ""
                        match_data['Vieras'] = ""
                    
                    # Result - might be in format "0-0"
                    if result_col >= 0 and result_col < len(cells):
                        result_text = await cells[result_col].text_content()
                        result_text = result_text.strip()
                        
                        if "-" in result_text:
                            try:
                                home_score, away_score = result_text.split("-", 1)
                                match_data['Kotitulos'] = home_score.strip()
                                match_data['Vierastulos'] = away_score.strip()
                            except ValueError:
                                match_data['Kotitulos'] = ""
                                match_data['Vierastulos'] = ""
                        else:
                            match_data['Kotitulos'] = ""
                            match_data['Vierastulos'] = ""
                    else:
                        match_data['Kotitulos'] = ""
                        match_data['Vierastulos'] = ""
                    
                    # Venue
                    if venue_col >= 0 and venue_col < len(cells):
                        venue_text = await cells[venue_col].text_content()
                        match_data['Paikka'] = venue_text.strip()
                    else:
                        match_data['Paikka'] = ""
                    
                    # Only add if we have meaningful data
                    if match_data['Pelipäivä'] and (match_data['Koti'] or match_data['Vieras']):
                        fixtures.append(match_data)
            
            print(f"Extracted {len(fixtures)} fixtures")
            
            # Print first fixture for verification
            if fixtures:
                print(f"Sample fixture data: {fixtures[0]}")
            
            # Convert to DataFrame
            df = pd.DataFrame(fixtures)
            
            # Save data
            df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
            df.to_csv('tulokset.csv', index=False, encoding='utf-8')
            df.to_csv('PelatutOttelut.csv', index=False, encoding='utf-8')
            
            with open('Ottelut.json', 'w', encoding='utf-8') as f:
                json.dump(fixtures, f, ensure_ascii=False, indent=2)
            
            # Create Markdown
            create_fixtures_markdown(df)
            
            await browser.close()
            return df
            
        except Exception as e:
            print(f"Error fetching fixtures: {e}")
            traceback.print_exc()
            
            # Save error screenshot
            await save_screenshot(page, "fixtures_error")
            
            await browser.close()
            return None

def create_league_table_markdown(df):
    """Create a markdown file for the league table"""
    try:
        with open('Sarjataulukko.md', 'w', encoding='utf-8') as f:
            f.write('# Sarjataulukko - Ykkönen\n\n')
            
            # Determine which columns we have
            columns = []
            headers = []
            
            if 'Sijoitus' in df.columns:
                columns.append('Sijoitus')
                headers.append('Sij.')
            if 'Joukkue' in df.columns:
                columns.append('Joukkue')
                headers.append('Joukkue')
            if 'Ottelut' in df.columns:
                columns.append('Ottelut')
                headers.append('O')
            if 'Voitot' in df.columns:
                columns.append('Voitot')
                headers.append('V')
            if 'Tasapelit' in df.columns:
                columns.append('Tasapelit')
                headers.append('T')
            if 'Tappiot' in df.columns:
                columns.append('Tappiot')
                headers.append('H')
            if 'Tehdyt maalit' in df.columns:
                columns.append('Tehdyt maalit')
                headers.append('TM')
            if 'Päästetyt maalit' in df.columns:
                columns.append('Päästetyt maalit')
                headers.append('PM')
            if 'Maaliero' in df.columns:
                columns.append('Maaliero')
                headers.append('ME')
            if 'Pisteet' in df.columns:
                columns.append('Pisteet')
                headers.append('P')
            
            # If we don't have the expected columns, use all available columns
            if len(columns) < 5:
                columns = df.columns.tolist()
                headers = columns.copy()
            
            # Create header row
            f.write('| ' + ' | '.join(headers) + ' |\n')
            f.write('| ' + ' | '.join(['---' for _ in headers]) + ' |\n')
            
            # Write data rows
            for _, row in df.iterrows():
                values = []
                for col in columns:
                    values.append(str(row.get(col, '')))
                f.write('| ' + ' | '.join(values) + ' |\n')
        
        print("Created Sarjataulukko.md successfully")
    except Exception as e:
        print(f"Error creating league table markdown: {e}")
        traceback.print_exc()

def create_fixtures_markdown(df):
    """Create a markdown file for fixtures"""
    try:
        with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
            f.write('# Ottelut - Ykkönen\n\n')
            f.write('| Päivä | Aika | Koti | Vieras | Tulos | Paikka |\n')
            f.write('| ----- | ---- | ---- | ------ | ----- | ------ |\n')
            
            for _, row in df.iterrows():
                # Format the score if available
                tulos = ""
                if 'Kotitulos' in df.columns and 'Vierastulos' in df.columns:
                    if pd.notna(row['Kotitulos']) and pd.notna(row['Vierastulos']):
                        if row['Kotitulos'] and row['Vierastulos']:
                            tulos = f"{row['Kotitulos']}-{row['Vierastulos']}"
                
                f.write(f"| {row.get('Pelipäivä', '')} | {row.get('Klo', '')} | " +
                        f"{row.get('Koti', '')} | {row.get('Vieras', '')} | " +
                        f"{tulos} | {row.get('Paikka', '')} |\n")
        
        print("Created PelatutOttelut.md successfully")
    except Exception as e:
        print(f"Error creating fixtures markdown: {e}")
        traceback.print_exc()

def update_timestamp():
    """Update the timestamp file"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('timestamp.txt', 'w') as f:
            f.write(timestamp)
        print(f"Updated timestamp: {timestamp}")
        return timestamp
    except Exception as e:
        print(f"Error updating timestamp: {e}")
        return None

async def main():
    print("\n" + "=" * 80)
    print("STARTING FOOTBALL DATA SCRAPER - YKKÖNEN (PLAYWRIGHT VERSION)")
    print("=" * 80)
    
    timestamp = update_timestamp()
    print(f"Starting at: {timestamp}")
    success = False
    
    try:
        # Get league table
        league_data = await get_league_table()
        
        # Get fixtures
        fixtures_data = await get_fixtures()
        
        # Create a log summary
        with open('scraper_log.txt', 'w') as f:
            f.write(f"Scraper run at: {timestamp}\n\n")
            
            f.write("=== LEAGUE TABLE ===\n")
            if league_data is not None:
                f.write(f"Successfully scraped league table with {len(league_data)} teams\n")
                success = True
            else:
                f.write("Failed to scrape league table\n")
            
            f.write("\n=== FIXTURES ===\n")
            if fixtures_data is not None:
                f.write(f"Successfully scraped fixtures with {len(fixtures_data)} matches\n")
                success = True
            else:
                f.write("Failed to scrape fixtures\n")
        
        # Update files' modification time
        if success:
            for filename in ['tulokset.csv', 'Ottelut.csv', 'Sarjataulukko.csv', 
                            'PelatutOttelut.csv', 'PelatutOttelut.md', 
                            'Sarjataulukko.md', 'timestamp.txt']:
                if os.path.exists(filename):
                    os.utime(filename, None)
                    print(f"Updated modification time for {filename}")
        
        print("\n=== SCRAPER COMPLETED ===")
        return success
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        
        # Save error to log
        with open('scraper_error.txt', 'w') as f:
            f.write(f"Error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Exception: {str(e)}\n\n")
            traceback.print_exc(file=f)
        
        return False

if __name__ == "__main__":
    asyncio.run(main())
