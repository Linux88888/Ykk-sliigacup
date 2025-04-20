import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
import os

def get_match_data():
    url = "https://tulospalvelu.lentopalloliitto.fi/sarjat/2023-2024/ykl/"
    
    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Data fetched successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Etsi ottelutaulukko
    ottelut_table = soup.find('table', class_='ottelutaulukko')
    
    if not ottelut_table:
        print("Ottelutaulukkoa ei löytynyt.")
        return None
    
    # Kerää ottelutiedot
    ottelut = []
    
    for row in ottelut_table.find_all('tr')[1:]:  # Skip header row
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
    
    print(f"Found {len(ottelut)} matches")
    
    # Tallenna data
    df = pd.DataFrame(ottelut)
    df.to_csv('tulokset.csv', index=False, encoding='utf-8')
    print(f"Saved match data to tulokset.csv")
    
    # Tallenna aikaleima
    with open('timestamp.txt', 'w') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(timestamp)
        print(f"Updated timestamp: {timestamp}")
    
    return df

if __name__ == "__main__":
    print("Starting scraper...")
    match_data = get_match_data()
    
    if match_data is not None:
        print(f"Successfully retrieved {len(match_data)} matches.")
        # Force file modification time update
        for filename in ['tulokset.csv', 'timestamp.txt']:
            if os.path.exists(filename):
                os.utime(filename, None)
    else:
        print("Failed to retrieve match data.")
