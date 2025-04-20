import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import traceback
import json

def save_html_snapshot(html, filename):
    """Save HTML snapshot for debugging"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Saved HTML snapshot to {filename}")

def fetch_url(url, filename_prefix):
    """Fetch URL with detailed logging and save HTML snapshot"""
    print(f"\n{'=' * 50}")
    print(f"FETCHING: {url}")
    print(f"{'=' * 50}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Make the request with a timeout
        response = requests.get(url, headers=headers, timeout=30)
        
        # Log response details
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.content)} bytes")
        print(f"Response content type: {response.headers.get('Content-Type', 'unknown')}")
        
        # Check if response is successful
        if response.status_code != 200:
            print(f"ERROR: Failed to fetch {url}, status code {response.status_code}")
            return None
            
        # Save HTML snapshot for debugging
        html_filename = f"{filename_prefix}_snapshot.html"
        save_html_snapshot(response.text, html_filename)
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Log page title
        page_title = soup.title.text.strip() if soup.title else "No title found"
        print(f"Page title: {page_title}")
        
        return soup
    except Exception as e:
        print(f"ERROR fetching {url}: {e}")
        traceback.print_exc()
        return None

def get_league_table():
    """Get league standings table"""
    # Important: Using direct URL for Ykkönen league standings
    url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/"
    
    soup = fetch_url(url, "league_table")
    if not soup:
        return None
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the league page")
    
    # Create a file with all tables for debugging
    with open("league_all_tables.txt", "w", encoding="utf-8") as f:
        for i, table in enumerate(tables):
            f.write(f"\n=== TABLE {i+1} ===\n")
            headers = [th.text.strip() for th in table.find_all('th')]
            f.write(f"Headers: {headers}\n")
            
            rows = table.find_all('tr')
            f.write(f"Row count: {len(rows)}\n")
            
            # Print first two rows for sample
            for j, row in enumerate(rows[:2]):
                if j == 0:
                    continue  # Skip header row in sample
                cells = [td.text.strip() for td in row.find_all('td')]
                f.write(f"Sample row: {cells}\n")
    
    # Find the league table - usually the first table with team standings
    league_table = []
    table_found = False
    
    for table_index, table in enumerate(tables):
        print(f"\nExamining table {table_index+1}...")
        
        # Get headers
        headers = [th.text.strip() for th in table.find_all('th')]
        print(f"Table {table_index+1} headers: {headers}")
        
        # Check if this looks like a standings table (has common headers like position, team, points)
        if any(header in headers for header in ['#', 'Team', 'P', 'PTS', 'Joukkue', 'Sija']):
            print(f"Table {table_index+1} appears to be the standings table")
            
            rows = table.find_all('tr')
            print(f"Found {len(rows)} rows in table {table_index+1}")
            
            # Create header mapping
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
            
            # Process each data row
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                
                if len(cells) >= len(headers):
                    team_data = {}
                    
                    # Extract data using our header mapping
                    for i, cell in enumerate(cells):
                        if i in header_mapping:
                            # For team name, extract text but also check for team image
                            if header_mapping[i] == 'Joukkue':
                                team_name = cell.text.strip()
                                team_img = cell.find('img')
                                if team_img and team_img.get('alt'):
                                    team_name = team_img.get('alt').strip()
                                team_data[header_mapping[i]] = team_name
                            else:
                                team_data[header_mapping[i]] = cell.text.strip()
                    
                    league_table.append(team_data)
            
            table_found = True
            break  # Stop after finding the standings table
    
    if not league_table or not table_found:
        print("WARNING: Could not find a valid standings table!")
        return None
    
    print(f"Extracted {len(league_table)} teams")
    
    # Print first team for verification
    if league_table:
        print(f"Sample team data: {league_table[0]}")
    
    # Convert to DataFrame
    df = pd.DataFrame(league_table)
    
    print(f"Standings columns: {df.columns.tolist()}")
    
    # Save both as CSV and JSON for better debugging
    df.to_csv('Sarjataulukko.csv', index=False, encoding='utf-8')
    
    # Also save as JSON for easier inspection
    with open('Sarjataulukko.json', 'w', encoding='utf-8') as f:
        json.dump(league_table, f, ensure_ascii=False, indent=2)
    
    print(f"Saved standings with {len(df)} teams to Sarjataulukko.csv and Sarjataulukko.json")
    
    # Create Markdown
    create_league_table_markdown(df)
    
    return df

def get_fixtures():
    """Get fixtures (matches)"""
    # Direct URL for fixtures
    url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
    
    soup = fetch_url(url, "fixtures")
    if not soup:
        return None
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the fixtures page")
    
    # Save all tables content for debugging
    with open("fixtures_all_tables.txt", "w", encoding="utf-8") as f:
        for i, table in enumerate(tables):
            f.write(f"\n=== TABLE {i+1} ===\n")
            headers = [th.text.strip() for th in table.find_all('th')]
            f.write(f"Headers: {headers}\n")
            
            rows = table.find_all('tr')
            f.write(f"Row count: {len(rows)}\n")
            
            # Print first two rows for sample
            for j, row in enumerate(rows[:3]):
                cells = [td.text.strip() for td in row.find_all('td')]
                f.write(f"Row {j}: {cells}\n")
    
    fixtures = []
    table_found = False
    
    # Go through each table looking for match data
    for table_index, table in enumerate(tables):
        print(f"\nExamining table {table_index+1} for fixtures...")
        
        rows = table.find_all('tr')
        if len(rows) <= 1:  # Skip tables with just headers or empty
            continue
        
        # Get headers if available
        headers = []
        header_row = rows[0].find_all('th')
        if header_row:
            headers = [th.text.strip() for th in header_row]
            print(f"Table {table_index+1} headers: {headers}")
        
        # Check if this looks like a fixtures table
        # Look for date and team columns
        date_col = -1
        teams_col = -1
        time_col = -1
        result_col = -1
        venue_col = -1
        
        # Try to identify column positions based on headers
        if headers:
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
        
        # Process each data row
        for row_index, row in enumerate(rows[1:], 1):  # Skip header row
            cells = row.find_all('td')
            
            if len(cells) >= 3:  # Need at least date, time, and teams
                match_data = {'Row': row_index}  # Add row number for debugging
                
                # Extract data based on identified columns
                if date_col >= 0 and date_col < len(cells):
                    match_data['Pelipäivä'] = cells[date_col].text.strip()
                else:
                    match_data['Pelipäivä'] = ""
                
                if time_col >= 0 and time_col < len(cells):
                    match_data['Klo'] = cells[time_col].text.strip()
                else:
                    match_data['Klo'] = ""
                
                # Teams - might be in format "Home - Away"
                if teams_col >= 0 and teams_col < len(cells):
                    teams_text = cells[teams_col].text.strip()
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
                    result_text = cells[result_col].text.strip()
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
                    match_data['Paikka'] = cells[venue_col].text.strip()
                else:
                    match_data['Paikka'] = ""
                
                # Only add if we have meaningful data
                if match_data['Pelipäivä'] and (match_data['Koti'] or match_data['Vieras']):
                    fixtures.append(match_data)
            
            # If we found at least 5 fixtures in this table, consider it valid
            if len(fixtures) >= 5:
                table_found = True
        
        # If we found fixtures in this table, stop looking
        if table_found:
            break
    
    if not fixtures:
        print("WARNING: Could not find valid fixtures data!")
        return None
    
    print(f"Extracted {len(fixtures)} fixtures")
    
    # Print first fixture for verification
    if fixtures:
        print(f"Sample fixture data: {fixtures[0]}")
    
    # Convert to DataFrame
    df = pd.DataFrame(fixtures)
    
    print(f"Fixtures columns: {df.columns.tolist()}")
    
    # Save both as CSV and JSON for better debugging
    df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
    df.to_csv('tulokset.csv', index=False, encoding='utf-8')
    
    # Also save as JSON for easier inspection
    with open('Ottelut.json', 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(df)} fixtures to Ottelut.csv, tulokset.csv and Ottelut.json")
    
    # Create Markdown
    create_fixtures_markdown(df)
    
    return df

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
                if pd.notna(row.get('Kotitulos')) and pd.notna(row.get('Vierastulos')):
                    if row['Kotitulos'] and row['Vierastulos']:
                        tulos = f"{row['Kotitulos']}-{row['Vierastulos']}"
                
                f.write(f"| {row.get('Pelipäivä', '')} | {row.get('Klo', '')} | " +
                        f"{row.get('Koti', '')} | {row.get('Vieras', '')} | " +
                        f"{tulos} | {row.get('Paikka', '')} |\n")
        
        # Also create PelatutOttelut.csv for compatibility
        df.to_csv('PelatutOttelut.csv', index=False)
        
        print("Created PelatutOttelut.md and PelatutOttelut.csv successfully")
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

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("STARTING FOOTBALL DATA SCRAPER - YKKÖNEN")
    print("=" * 80)
    
    timestamp = update_timestamp()
    print(f"Starting at: {timestamp}")

    try:
        # Clear any previous snapshots
        for filename in ['league_table_snapshot.html', 'fixtures_snapshot.html',
                        'league_all_tables.txt', 'fixtures_all_tables.txt']:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Removed previous {filename}")
        
        # Fetch league table
        print("\n=== FETCHING LEAGUE TABLE ===")
        league_data = get_league_table()
        
        # Fetch fixtures
        print("\n=== FETCHING FIXTURES ===")
        fixtures_data = get_fixtures()
        
        # Create a log summary
        with open('scraper_log.txt', 'w') as f:
            f.write(f"Scraper run at: {timestamp}\n\n")
            
            f.write("=== LEAGUE TABLE ===\n")
            if league_data is not None:
                f.write(f"Successfully scraped league table with {len(league_data)} teams\n")
            else:
                f.write("Failed to scrape league table\n")
            
            f.write("\n=== FIXTURES ===\n")
            if fixtures_data is not None:
                f.write(f"Successfully scraped fixtures with {len(fixtures_data)} matches\n")
            else:
                f.write("Failed to scrape fixtures\n")
        
        print("\n=== SCRAPER COMPLETED ===")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        
        # Save error to log
        with open('scraper_error.txt', 'w') as f:
            f.write(f"Error at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Exception: {str(e)}\n\n")
            traceback.print_exc(file=f)
