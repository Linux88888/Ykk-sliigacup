from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

# Funktio tietojen hakemiseen ja kirjoittamiseen CSV-tiedostoon
def scrape_and_save():
    # Käynnistetään Playwright
    with sync_playwright() as p:
        # Käynnistetään selain
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Avaa URL
        url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"
        page.goto(url)

        # Odotetaan, että sivu on ladattu ja tiedot ovat näkyvissä
        page.wait_for_selector("tr")  # Oletetaan, että taulukon rivit löytyvät 'tr' tagista

        # Haetaan taulukon rivit
        rows = page.query_selector_all('tr')

        # Avataan CSV-tiedosto kirjoitusta varten
        with open('tulokset.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])

            # Käydään läpi rivit ja tallennetaan tiedot CSV-tiedostoon
            for row in rows:
                row_text = row.inner_text()
                if any(char.isdigit() for char in row_text):  # Tarkistetaan, että rivillä on numeroita
                    parts = row_text.split("\n")
                    if len(parts) >= 7:
                        writer.writerow(parts)
                        print(f"Rivi tallennettu: {parts}")  # Tulostetaan, mitä tallennetaan

        # Tallennetaan myös aikaleima tiedostoon
        with open("timestamp.txt", "w") as timestamp_file:
            timestamp_file.write(f"Päivitetty: {datetime.utcnow().strftime('%a %b %d %H:%M:%S UTC %Y')}")

        # Suljetaan selain
        browser.close()

# Suoritetaan toiminto
scrape_and_save()
