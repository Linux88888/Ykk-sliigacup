import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import traceback

def get_match_data():
    url = "https://tulospalvelu.lentopalloliitto.fi/sarjat/2023-2024/ykl/"
    
    print(f"Fetching data from {url}...")
    
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
    
    # Etsi ottelutaulukko
    ottelut_table = soup.find('table', class_='ottelutaulukko')
    
    if not ottelut_table:
        print("Ottelutaulukkoa ei löytynyt. Tulostetaan sivun HTML rakenne:")
        # Debug: Print a snippet of the HTML to diagnose structure changes
        print(soup.prettify()[:1500])  # Print first 1500 chars of HTML
        
        # Try alternative table finders
        print("Yritetään löytää taulukkoa vaihtoehtoisilla tavoilla...")
        tables = soup.find_all('table')
        print(f"Löydetty {len(tables)} taulukkoa")
        
        if tables:
            print("Käytetään ensimmäistä taulukkoa...")
            ottelut_table = tables[0]
        else:
            print("Taulukoita ei löydy ollenkaan.")
            return None
    
    # Kerää ottelutiedot
    ottelut = []
    rows = ottelut_table.find_all('tr')
    print(f"Found {len(rows)} rows in table")
    
    for i, row in enumerate(rows[1:], 1):  # Skip header row
        try:
            cells = row.find_all('td')
            if len(cells) >= 5:
                print(f"Processing row {i} with {len(cells)} cells")
                pvm_text = cells[0].text.strip()
                klo = cells[1].text.strip()
                joukkueet = cells[2].text.strip()
                tulos = cells[3].text.strip()
                paikka = cells[4].text.strip()
                
                print(f"Row {i}: Date={pvm_text}, Time={klo}, Teams={joukkueet}, Score={tulos}")
                
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
        print("No match data found, cannot update CSV")
        return None
    
    # Debug: Print first match for verification
    if ottelut:
        print("First match data:")
        print(ottelut[0])
    
    # Save data to CSV
    try:
        df = pd.DataFrame(ottelut)
        
        # Check if we have existing data to compare
        existing_df = None
        if os.path.exists('tulokset.csv'):
            try:
                existing_df = pd.read_csv('tulokset.csv')
                print(f"Existing data has {len(existing_df)} rows")
            except Exception as e:
                print(f"Error reading existing CSV: {e}")
        
        # Save new data
        df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
        df.to_csv('tulokset.csv', index=False, encoding='utf-8')
        print(f"Saved match data to tulokset.csv and Ottelut.csv with {len(df)} rows")
        
        # Compare with existing data
        if existing_df is not None:
            if df.equals(existing_df):
                print("WARNING: New data is identical to existing data")
            else:
                print("Data has changed from previous version")
    except Exception as e:
        print(f"Error saving CSV: {e}")
        traceback.print_exc()
        return None
    
    # Update timestamp
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('timestamp.txt', 'w') as f:
            f.write(timestamp)
        print(f"Updated timestamp: {timestamp}")
    except Exception as e:
        print(f"Error updating timestamp: {e}")
    
    return df

if __name__ == "__main__":
    print("Starting scraper...")
    try:
        match_data = get_match_data()
        
        if match_data is not None:
            print(f"Successfully retrieved {len(match_data)} matches.")
            # Force file modification time update
            for filename in ['tulokset.csv', 'Ottelut.csv', 'timestamp.txt']:
                if os.path.exists(filename):
                    os.utime(filename, None)
                    print(f"Updated modification time for {filename}")
        else:
            print("Failed to retrieve match data.")
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        traceback.print_exc()
