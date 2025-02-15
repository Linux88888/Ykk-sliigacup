from playwright.sync_api import sync_playwright
import csv
import re

def fetch_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Odotetaan, että sivun sisältö latautuu
        page.wait_for_timeout(5000)  # Odotetaan 5 sekuntia

        # Etsitään kaikki pelaajien rivit
        players_locator = page.locator('table tr')  # Etsitään taulukon rivit
        players_count = players_locator.count()

        if players_count == 0:
            print("⚠️ Ei löytynyt pelaajatietoja taulukosta!")
        else:
            print(f"🔍 Löydettiin {players_count} pelaajan riviä!")

        # Haetaan koko sivun HTML ja tulostetaan se testimielessä
        page_html = page.content()  # Hakee koko HTML:n
        print("🔍 Koko HTML-sisältö:")
        print(page_html[:1000])  # Tulostetaan ensimmäiset 1000 merkkiä

        # Käytetään regexiä pelaajien hakemiseen
        pattern = re.compile(r"([A-Za-zÅÄÖåäö\s-]+)\s+([A-Za-zÅÄÖåäö\s-]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
        matches = pattern.findall(page_html)

        # Tulostetaan löydettyjen tietojen määrä ja tallennetaan ne CSV:hen
        if matches:
            with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
                writer.writerows(matches)

            print("📂 Tiedot tallennettu tulokset.csv -tiedostoon!")
        else:
            print("⚠️ Ei löydetty pelaajatietoja!")

        # Tulostetaan kaikki löydetyt rivit
        for row in matches:
            print("\t".join(row))

        # Suljetaan selain
        browser.close()

if __name__ == "__main__":
    fetch_data()
