import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import traceback

def get_league_table():
    """Get league standings table"""
    url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/"
    
    print(f"Fetching league table from {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching league table: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the league table
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page")
    
    if not tables:
        print("No tables found on the page")
        return None
    
    # The first table is typically the league standings
    league_table = []
    
    table = tables[0]  # Use the first table by default
    rows = table.find_all('tr')
    
    # Extract headers
    headers = [th.text.strip() for th in rows[0].find_all('th')]
    print(f"League table headers: {headers}")
    
    # Map expected headers to Finnish names
    header_mapping = {
        '#': 'Sijoitus',
        'Team': 'Joukkue',
        'P': 'Ottelut',  # Matches played
        'W': 'Voitot',   # Wins
        'D': 'Tasapelit', # Draws
        'L': 'Tappiot',  # Losses
        'GF': 'Tehdyt maalit',  # Goals for
        'GA': 'Päästetyt maalit',  # Goals against
        'GD': 'Maaliero',  # Goal difference
        'PTS': 'Pisteet'  # Points
    }
    
    # Process each row
    for row in rows[1:]:  # Skip header row
        cells = row.find_all('td')
        
        if len(cells) >= 8:  # Make sure we have enough cells
            team_data = {}
            
            # Extract data from each cell and map to our Finnish headers
            for i, header in enumerate(headers):
                if i < len(cells):
                    mapped_header = header_mapping.get(header, header)
                    team_data[mapped_header] = cells[i].text.strip()
            
            # Extract team name from the team cell which might contain an image
            if 'Joukkue' in team_data:
                team_name_cell = cells[headers.index('Team')]
                team_name = team_name_cell.text.strip()
                # If there's an image with alt text, that might be the team name
                team_img = team_name_cell.find('img')
                if team_img and team_img.get('alt'):
                    team_name = team_img.get('alt')
                team_data['Joukkue'] = team_name
            
            league_table.append(team_data)
    
    print(f"Extracted {len(league_table)} teams from league table")
    
    if not league_table:
        print("Failed to extract league table data")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(league_table)
    
    # Convert numeric columns
    numeric_columns = ['Sijoitus', 'Ottelut', 'Voitot', 'Tasapelit', 'Tappiot', 
                       'Tehdyt maalit', 'Päästetyt maalit', 'Maaliero', 'Pisteet']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Save to CSV
    df.to_csv('Sarjataulukko.csv', index=False, encoding='utf-8')
    print(f"Saved league table with {len(df)} teams to Sarjataulukko.csv")
    
    # Create Markdown
    create_league_table_markdown(df)
    
    return df

def get_fixtures():
    """Get upcoming matches"""
    url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
    
    print(f"Fetching fixtures from {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fixtures: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the matches table
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the fixtures page")
    
    fixtures = []
    
    for i, table in enumerate(tables):
        print(f"Examining table {i+1}...")
        rows = table.find_all('tr')
        
        # Check if this looks like a fixtures table
        if len(rows) > 1:
            # Try to find match data
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                
                if len(cells) >= 5:  # We need at least date, time, teams, etc.
                    match_data = {}
                    
                    # Common structure: Date | Time | Home - Away | Venue
                    match_data['Pelipäivä'] = cells[0].text.strip()
                    match_data['Klo'] = cells[1].text.strip()
                    
                    # Teams cell might contain "Home - Away"
                    teams_text = cells[2].text.strip()
                    if " - " in teams_text:
                        home, away = teams_text.split(" - ", 1)
                        match_data['Koti'] = home.strip()
                        match_data['Vieras'] = away.strip()
                    else:
                        match_data['Koti'] = teams_text
                        match_data['Vieras'] = ""
                    
                    # Look for result if available
                    result_cell = cells[3].text.strip() if len(cells) > 3 else ""
                    if result_cell and "-" in result_cell:
                        home_score, away_score = result_cell.split("-", 1)
                        match_data['Kotitulos'] = home_score.strip()
                        match_data['Vierastulos'] = away_score.strip()
                    else:
                        match_data['Kotitulos'] = ""
                        match_data['Vierastulos'] = ""
                    
                    # Venue is usually the last cell
                    if len(cells) > 4:
                        match_data['Paikka'] = cells[4].text.strip()
                    else:
                        match_data['Paikka'] = ""
                    
                    fixtures.append(match_data)
            
            if fixtures:
                print(f"Found {len(fixtures)} matches in table {i+1}")
                break  # Stop after finding a table with data
    
    if not fixtures:
        print("No fixtures found")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(fixtures)
    
    # Save to CSV
    df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
    df.to_csv('tulokset.csv', index=False, encoding='utf-8')
    print(f"Saved {len(df)} fixtures to Ottelut.csv and tulokset.csv")
    
    # Create Markdown for played matches
    create_fixtures_markdown(df)
    
    return df

def create_league_table_markdown(df):
    """Create a markdown file for the league table"""
    try:
        with open('Sarjataulukko.md', 'w', encoding='utf-8') as f:
            f.write('# Sarjataulukko\n\n')
            
            # Create headers based on available columns
            headers = []
            if 'Sijoitus' in df.columns:
                headers.append('Sij.')
            if 'Joukkue' in df.columns:
                headers.append('Joukkue')
            if 'Ottelut' in df.columns:
                headers.append('O')
            if 'Voitot' in df.columns:
                headers.append('V')
            if 'Tasapelit' in df.columns:
                headers.append('T')
            if 'Tappiot' in df.columns:
                headers.append('H')
            if 'Tehdyt maalit' in df.columns:
                headers.append('TM')
            if 'Päästetyt maalit' in df.columns:
                headers.append('PM')
            if 'Maaliero' in df.columns:
                headers.append('ME')
            if 'Pisteet' in df.columns:
                headers.append('P')
            
            # Write header row
            f.write('| ' + ' | '.join(headers) + ' |\n')
            
            # Write separator row
            f.write('| ' + ' | '.join(['----' for _ in headers]) + ' |\n')
            
            # Write data rows
            for _, row in df.iterrows():
                values = []
                
                if 'Sijoitus' in df.columns:
                    values.append(str(row['Sijoitus']))
                if 'Joukkue' in df.columns:
                    values.append(row['Joukkue'])
                if 'Ottelut' in df.columns:
                    values.append(str(row['Ottelut']))
                if 'Voitot' in df.columns:
                    values.append(str(row['Voitot']))
                if 'Tasapelit' in df.columns:
                    values.append(str(row['Tasapelit']))
                if 'Tappiot' in df.columns:
                    values.append(str(row['Tappiot']))
                if 'Tehdyt maalit' in df.columns:
                    values.append(str(row['Tehdyt maalit']))
                if 'Päästetyt maalit' in df.columns:
                    values.append(str(row['Päästetyt maalit']))
                if 'Maaliero' in df.columns:
                    values.append(str(row['Maaliero']))
                if 'Pisteet' in df.columns:
                    values.append(str(row['Pisteet']))
                
                f.write('| ' + ' | '.join(values) + ' |\n')
        
        print("Created Sarjataulukko.md successfully")
    except Exception as e:
        print(f"Error creating league table markdown: {e}")
        traceback.print_exc()

def create_fixtures_markdown(df):
    """Create a markdown file for fixtures"""
    try:
        with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
            f.write('# Ottelut\n\n')
            f.write('| Päivä | Aika | Koti | Vieras | Tulos | Paikka |\n')
            f.write('| ----- | ---- | ---- | ------ | ----- | ------ |\n')
            
            for _, row in df.iterrows():
                tulos = ""
                if row.get('Kotitulos') and row.get('Vierastulos'):
                    tulos = f"{row['Kotitulos']}-{row['Vierastulos']}"
                
                f.write(f"| {row['Pelipäivä']} | {row['Klo']} | {row['Koti']} | {row['Vieras']} | {tulos} | {row['Paikka']} |\n")
        
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
        return True
    except Exception as e:
        print(f"Error updating timestamp: {e}")
        return False

if __name__ == "__main__":
    print("Starting scraper...")
    success = False
    
    try:
        # Get league table
        print("\n=== Fetching League Table ===")
        league_data = get_league_table()
        if league_data is not None:
            print(f"Successfully retrieved league table with {len(league_data)} teams")
            success = True
        else:
            print("Failed to retrieve league table")
        
        # Get fixtures
        print("\n=== Fetching Fixtures ===")
        fixtures_data = get_fixtures()
        if fixtures_data is not None:
            print(f"Successfully retrieved {len(fixtures_data)} fixtures")
            success = True
        else:
            print("Failed to retrieve fixtures")
        
        # Update timestamp if any data was retrieved
        if success:
            update_timestamp()
            
            # Force file modification time update
            for filename in ['tulokset.csv', 'Ottelut.csv', 'Sarjataulukko.csv', 
                           'PelatutOttelut.csv', 'PelatutOttelut.md', 
                           'Sarjataulukko.md', 'timestamp.txt']:
                if os.path.exists(filename):
                    os.utime(filename, None)
                    print(f"Updated modification time for {filename}")
        else:
            print("No data was retrieved successfully")
        
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        traceback.print_exc()
