from playwright.sync_api import sync_playwright
import csv
import re

def fetch_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Odotetaan, että sivu latautuu
        page.wait_for_selector('body')

        # Haetaan koko sivun tekstisisältö
        text_content = page.locator('body').inner_text()

        # Suljetaan selain
        browser.close()

    # Etsitään vain relevantit rivit (joissa on pelaajatietoja)
    pattern = re.compile(r"([A-Za-zÅÄÖåäö\s-]+)\s+([A-Za-zÅÄÖåäö\s-]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    matches = pattern.findall(text_content)

    # Tallennetaan CSV-tiedostoon
    with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
        writer.writerows(matches)

    # Tulostetaan data myös terminaaliin
    for row in matches:
        print("\t".join(row))

if __name__ == "__main__":
    fetch_data()
