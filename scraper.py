from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv

def fetch_and_parse_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Odotetaan, että sivu latautuu
        page.wait_for_timeout(5000)  # Odotetaan 5 sekuntia
        
        # Haetaan koko HTML-sisältö
        page_html = page.content()  
        
        # Käytetään BeautifulSoupia HTML:n jäsentämiseen
        soup = BeautifulSoup(page_html, "html.parser")
        
        # Etsitään taulukot, jotka sisältävät pelaajatiedot
        rows = soup.find_all("tr")  # Etsitään kaikki rivit
        
        with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])  # Kirjoitetaan otsikko CSV:hen
            
            # Käydään läpi kaikki rivit ja etsitään oikeat tiedot
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 7:  # Varmistetaan, että rivillä on tarpeeksi soluja
                    player = columns[0].text.strip()  # Pelaajan nimi
                    team = columns[1].text.strip()  # Joukkueen nimi
                    o = columns[2].text.strip()  # O
                    m = columns[3].text.strip()  # M
                    s = columns[4].text.strip()  # S
                    p = columns[5].text.strip()  # P
                    min = columns[6].text.strip()  # Min
                    
                    # Kirjoitetaan rivit CSV-tiedostoon
                    writer.writerow([player, team, o, m, s, p, min])
        
        # Suljetaan selain
        browser.close()

if __name__ == "__main__":
    fetch_and_parse_data()

