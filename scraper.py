from playwright.sync_api import sync_playwright
import csv

def fetch_data():
    url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Odotetaan, että taulukko latautuu
        page.wait_for_selector('table')

        # Haetaan taulukon rivit
        rows = page.query_selector_all('table tr')

        data = []
        for row in rows[1:]:  # Ohitetaan otsikkorivi
            cells = row.query_selector_all('td')
            player_data = [cell.inner_text() for cell in cells]
            data.append(player_data)

        browser.close()

    # Tallennetaan CSV-muotoon
    with open('tulokset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])
        writer.writerows(data)

if __name__ == "__main__":
    fetch_data()
