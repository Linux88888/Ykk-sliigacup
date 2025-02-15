from playwright.sync_api import sync_playwright
import csv

def fetch_all_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Odotetaan, että sivu latautuu
        page.wait_for_timeout(5000)  # Odotetaan 5 sekuntia

        # Haetaan koko sivun HTML-sisältö
        page_html = page.content()  # Haetaan koko HTML
        print("🔍 Koko HTML-sisältö:")
        print(page_html)  # Tulostetaan koko HTML-sisältö

        # Tallennetaan HTML CSV-tiedostoon
        with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['HTML sisältö'])  # Kirjoitetaan otsikko CSV:hen
            writer.writerow([page_html])  # Tallennetaan koko HTML-sisältö tiedostoon

        # Suljetaan selain
        browser.close()

if __name__ == "__main__":
    fetch_all_data()

