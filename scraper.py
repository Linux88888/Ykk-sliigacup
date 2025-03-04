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

        # Odotetaan, että taulukon rivit ovat näkyvissä (odotetaan jopa 20 sekuntia)
        page.wait_for_selector("table.v-data-table tbody tr", timeout=20000)

        # Tulostetaan koko sivun HTML tarkistusta varten
        print(page.content())  # Tarkistaa sivun sisällön

        # Haetaan taulukon rivit
        rows = page.query_selector_all('table.v-data-table tbody tr')  # Käytetään tarkempaa valitsinta
        print(f"Rivit löydetty: {len(rows)}")  # Debug-tulostus

        if len(rows) == 0:
            print("Yhtään riviä ei löytynyt. Varmista, että valitsimet ovat oikein.")

        # Avataan CSV-tiedosto kirjoitusta varten
        with open('tulokset.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
            print("CSV-tiedosto avattu kirjoitusta varten.")  # Debug

            # Käydään läpi rivit ja tallennetaan tiedot CSV-tiedostoon
            for row in rows:
                columns = row.query_selector_all('td')  # Hakee kaikki solut riviltä
                data = [col.inner_text().strip() for col in columns]  # Hakee solujen tekstin ja poistaa tyhjät välit
                if len(data) >= 7:  # Varmistetaan, että rivillä on vähintään 7 solua
                    writer.writerow(data)  # Kirjoitetaan tiedot CSV-tiedostoon
                    print(f"Rivi tallennettu: {data}")  # Tulostetaan, mitä tallennetaan
                else:
                    print(f"Riviä ei tallennettu, koska siinä ei ole tarpeeksi soluja: {data}")

        # Tallennetaan myös aikaleima tiedostoon
        with open("timestamp.txt", "w", encoding='utf-8') as timestamp_file:
            timestamp_file.write(f"Päivitetty: {datetime.utcnow().strftime('%a %b %d %H:%M:%S UTC %Y')}")
            print("Aikaleima tallennettu.")  # Debug

        # Suljetaan selain
        browser.close()
        print("Selaimen istunto suljettu.")  # Debug

# Suoritetaan toiminto
scrape_and_save()
