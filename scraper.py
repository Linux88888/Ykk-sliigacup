import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import traceback
import time
import re

def get_player_stats():
    """Get player statistics from palloliitto.fi"""
    url = "https://tulospalvelu.palloliitto.fi/sarjat/tilastot/2024"
    
    print(f"Fetching player statistics from {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.content)} bytes")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Debug: Print page title to verify content
    page_title = soup.title.text if soup.title else "No title found"
    print(f"Page title: {page_title}")
    
    # Find tables in the page
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page")
    
    if not tables:
        print("No tables found on the page. Printing page structure:")
        print(soup.prettify()[:1500])  # Print the first 1500 characters of HTML
        return None
    
    # Try to find the player statistics table
    player_stats = []
    
    # Try each table
    for i, table in enumerate(tables):
        print(f"Examining table {i+1}...")
        
        # Check if this looks like a player stats table
        headers = [th.text.strip() for th in table.find_all('th')]
        print(f"Table {i+1} headers: {headers}")
        
        if len(headers) >= 5:  # A reasonable player stats table should have several columns
            rows = table.find_all('tr')[1:]  # Skip header row
            print(f"Found {len(rows)} data rows in table {i+1}")
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    player_data = {}
                    
                    # Attempt to extract values based on position
                    # This is a best-effort approach and might need adjustments
                    if len(cells) >= 1:
                        player_data['Pelaaja'] = cells[0].text.strip()
                    if len(cells) >= 2:
                        player_data['Joukkue'] = cells[1].text.strip()
                    if len(cells) >= 3:
                        player_data['O'] = cells[2].text.strip()
                    if len(cells) >= 4:
                        player_data['M'] = cells[3].text.strip()
                    if len(cells) >= 5:
                        player_data['S'] = cells[4].text.strip()
                    if len(cells) >= 6:
                        player_data['P'] = cells[5].text.strip()
                    if len(cells) >= 7:
                        player_data['Min'] = cells[6].text.strip()
                    
                    player_stats.append(player_data)
            
            if player_stats:
                print(f"Successfully extracted {len(player_stats)} player statistics from table {i+1}")
                break  # Stop after finding a table with data
    
    if not player_stats:
        print("Could not extract player statistics from any table")
        return None
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(player_stats)
    
    # Convert numeric columns
    for col in ['O', 'M', 'S', 'P', 'Min']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Save data
    df.to_csv('tulokset.csv', index=False, encoding='utf-8')
    print(f"Saved {len(df)} player statistics to tulokset.csv")
    
    # Update timestamp
    with open('timestamp.txt', 'w') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(timestamp)
        print(f"Updated timestamp: {timestamp}")
    
    return df

if __name__ == "__main__":
    print("Starting scraper...")
    try:
        stats_data = get_player_stats()
        
        if stats_data is not None:
            print(f"Successfully retrieved {len(stats_data)} player statistics.")
            # Force file modification time update
            for filename in ['tulokset.csv', 'timestamp.txt']:
                if os.path.exists(filename):
                    os.utime(filename, None)
                    print(f"Updated modification time for {filename}")
        else:
            print("Failed to retrieve player statistics.")
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        traceback.print_exc()
