from playwright.sync_api import sync_playwright
import csv

def fetch_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Odotetaan, että sivu latautuu
        page.wait_for_selector('body')

        # Haetaan kaikki tekstisisällöt
        text_content = page.locator('body').inner_text()

        # Erotellaan pelaajatiedot riveittäin
        rows = text_content.split("\n")
        data = []

        for row in rows:
            row = row.strip()
            # Etsitään rivejä, joissa on numeroita (O, M, S, P, Min)
            if row and any(char.isdigit() for char in row):
                parts = row.split("\t")  # Erotellaan sarakkeet tab-merkin perusteella
                if len(parts) >= 7:  # Varmistetaan, että kaikki tiedot löytyvät
                    data.append(parts[:7])

        browser.close()

    # Tallennetaan CSV-tiedostoon
    with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
        writer.writerows(data)

    # Tulostetaan tiedot terminaaliin
    print("\n".join(["\t".join(row) for row in data]))

if __name__ == "__main__":
    fetch_data()
