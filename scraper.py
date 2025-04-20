import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import traceback
import time

def get_match_data():
    # Correct URL for football results
    url = "https://tulospalvelu.palloliitto.fi/sarjat/2023-2024/ykl/"
    alternative_url = "https://tulospalvelu.palloliitto.fi/sarjat/2024-2025/ykl/"
    
    print(f"Fetching data from {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        # If first URL fails, try alternative
        if response.status_code != 200:
            print(f"Failed to get data from primary URL (status code {response.status_code}), trying alternative...")
            response = requests.get(alternative_url, headers=headers, timeout=30)
            
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.content)} bytes")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return use_cached_data()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Debug: Print page title to verify content
    page_title = soup.title.text if soup.title else "No title found"
    print(f"Page title: {page_title}")
    
    # Etsi ottelutaulukko
    ottelut_table = soup.find('table', class_='ottelutaulukko')
    
    if not ottelut_table:
        print("Ottelutaulukkoa ei löytynyt. Yritetään etsiä muita taulukoita...")
        tables = soup.find_all('table')
        print(f"Löydetty {len(tables)} taulukkoa")
        
        if tables:
            print("Käytetään ensimmäistä taulukkoa...")
            ottelut_table = tables[0]
        else:
            print("Taulukoita ei löydy ollenkaan, käytetään välimuistia...")
            return use_cached_data()
    
    # Kerää ottelutiedot
    ottelut = []
    rows = ottelut_table.find_all('tr')
    print(f"Found {len(rows)} rows in table")
    
    for i, row in enumerate(rows[1:], 1):  # Skip header row
        try:
            cells = row.find_all('td')
            if len(cells) >= 5:
                pvm_text = cells[0].text.strip()
                klo = cells[1].text.strip()
                joukkueet = cells[2].text.strip()
                tulos = cells[3].text.strip()
                paikka = cells[4].text.strip()
                
                # Erottele koti- ja vierasjoukkueet
                if "-" in joukkueet:
                    koti, vieras = joukkueet.split("-", 1)
                    koti = koti.strip()
                    vieras = vieras.strip()
                else:
                    koti = joukkueet
                    vieras = ""
                
                # Erottele tulokset
                kotitulos = ""
                vierastulos = ""
                if tulos and "-" in tulos:
                    tulos_parts = tulos.split("-")
                    if len(tulos_parts) >= 2:
                        kotitulos = tulos_parts[0].strip()
                        vierastulos = tulos_parts[1].strip()
                
                ottelut.append({
                    'Pelipäivä': pvm_text,
                    'Klo': klo,
                    'Koti': koti,
                    'Vieras': vieras,
                    'Kotitulos': kotitulos,
                    'Vierastulos': vierastulos,
                    'Paikka': paikka
                })
            else:
                print(f"Skipping row {i}: not enough cells ({len(cells)})")
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            traceback.print_exc()
    
    print(f"Found {len(ottelut)} matches")
    
    if not ottelut:
        print("No match data found, using cached data")
        return use_cached_data()
    
    # Save data to CSV
    try:
        df = pd.DataFrame(ottelut)
        df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
        df.to_csv('tulokset.csv', index=False, encoding='utf-8')
        print(f"Saved match data to tulokset.csv and Ottelut.csv with {len(df)} rows")
    except Exception as e:
        print(f"Error saving CSV: {e}")
        traceback.print_exc()
        return use_cached_data()
    
    # Update timestamp
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('timestamp.txt', 'w') as f:
            f.write(timestamp)
        print(f"Updated timestamp: {timestamp}")
    except Exception as e:
        print(f"Error updating timestamp: {e}")
    
    return df

def use_cached_data():
    """Fall back to using cached data if web scraping fails"""
    print("Attempting to use previously cached data...")
    
    # Check if we have existing data
    if os.path.exists('tulokset.csv'):
        try:
            df = pd.read_csv('tulokset.csv')
            print(f"Using cached data with {len(df)} rows from tulokset.csv")
            
            # Update timestamp to indicate refresh attempt
            with open('timestamp.txt', 'w') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " (Using cached data)"
                f.write(timestamp)
                
            return df
        except Exception as e:
            print(f"Error reading cached data: {e}")
    else:
        print("No cached data available")
    
    # Create empty dataframe with correct columns if no cached data
    empty_df = pd.DataFrame(columns=['Pelipäivä', 'Klo', 'Koti', 'Vieras', 
                                    'Kotitulos', 'Vierastulos', 'Paikka'])
    return empty_df

if __name__ == "__main__":
    print("Starting scraper...")
    try:
        match_data = get_match_data()
        
        if match_data is not None and not match_data.empty:
            print(f"Successfully processed {len(match_data)} matches.")
            # Force file modification time update
            for filename in ['tulokset.csv', 'Ottelut.csv', 'timestamp.txt']:
                if os.path.exists(filename):
                    os.utime(filename, None)
                    print(f"Updated modification time for {filename}")
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        traceback.print_exc()
