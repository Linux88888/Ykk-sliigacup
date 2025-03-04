from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

def scrape_and_save():
    with sync_playwright() as p:
        # 1. Käynnistä selain stealth-tilassa (vähemmän botin näköinen)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            # 2. Avaa sivu ja odota verkkopyyntöjä
            page.goto("https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points", wait_until="networkidle")
            
            # 3. Odota konkreettista taulukon sisältöä
            page.wait_for_selector("td:has-text('Pelaaja')", timeout=30000)
            
            # 4. Etsi taulukko uudella valitsimella
            table = page.query_selector("div.v-data-table table")
            if not table:
                raise Exception("Taulukkoa ei löytynyt!")
                
            rows = table.query_selector_all("tbody tr")
            print(f"Löydetty {len(rows)} riviä")

            # 5. Tallenna CSV
            with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Pelaaja','Joukkue','O','M','S','P','Min'])
                
                for row in rows:
                    cells = [cell.inner_text().strip() for cell in row.query_selector_all("td")]
                    if len(cells) == 7:
                        writer.writerow(cells)
                        print(f"Tallennettu: {cells}")
                    else:
                        print(f"Ohitettu epätäydellinen rivi: {cells}")

            # 6. Päivitä timestamp
            with open("timestamp.txt", "w") as ts_file:
                ts_file.write(datetime.utcnow().isoformat())

        except Exception as e:
            print(f"VIRHE: {str(e)}")
            page.screenshot(path="error.png")
            raise e
            
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_and_save()
