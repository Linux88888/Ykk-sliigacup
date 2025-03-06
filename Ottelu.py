from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

def scrape_html():
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
            # Navigoi sivulle, joka näyttää pelatut ottelut
            page.goto("https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/results",
                      wait_until="networkidle",
                      timeout=60000)

            # Etsi kaikki ottelut ja kerää niiden numerot
            match_links = page.query_selector_all('.match-link')  # Korvaa tämä oikealla valitsimella
            match_ids = [link.get_attribute('href').split('/')[-1] for link in match_links]

            # Kerätään koko sivun HTML jokaisesta ottelusta
            html_data = []
            for match_id in match_ids:
                # Avaa ottelun tilastosivu
                match_page = context.new_page()
                match_page.goto(f"https://tulospalvelu.palloliitto.fi/match/3738924/stats",
                                wait_until="networkidle",
                                timeout=60000)

                # Tallenna koko sivun HTML
                html_content = match_page.content()
                html_data.append({'match_id': match_id, 'html': html_content})

                # Sulje ottelun sivu
                match_page.close()

            # Tallennetaan HTML-datat Ottelut.csv-tiedostoon
            with open('Ottelut.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['match_id', 'html'])
                writer.writeheader()
                writer.writerows(html_data)

            # Päivitetään timestamp
            with open('timestamp.txt', 'w') as f:
                f.write(datetime.utcnow().isoformat())

            print("HTML-datan haku ja tallennus onnistui!")

        except Exception as e:
            print(f"Virhe: {str(e)}")
            page.screenshot(path='error.png')
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_html()
