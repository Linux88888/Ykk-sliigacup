from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time

def scrape_data():
    with sync_playwright() as p:
        # Alustetaan selain stealth-tilassa
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            # Navigoidaan sivustolle
            page.goto("https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points", 
                      wait_until="networkidle",
                      timeout=60000)

            # Odotetaan dynaamisen sisällön latautumista
            page.wait_for_function(
                """() => {
                    const rows = document.querySelectorAll('table tr');
                    return rows.length > 10;
                }""",
                timeout=30000
            )

            # Etsitään taulukko
            table = page.wait_for_selector('div.v-data-table table', timeout=20000)
            
            # Kerätään tiedot
            data = []
            rows = table.query_selector_all('tbody tr')
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 7:
                    row_data = [cell.inner_text().strip() for cell in cells]
                    data.append(row_data)
                    print(f"Haettu: {row_data}")

            # Tallennetaan CSV-tiedostoon
            with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
                writer.writerows(data)

            # Päivitetään timestamp
            with open('timestamp.txt', 'w') as f:
                f.write(datetime.utcnow().isoformat())

            print("Datan haku ja tallennus onnistui!")

        except Exception as e:
            print(f"Virhe: {str(e)}")
            page.screenshot(path='error.png')
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_data()
