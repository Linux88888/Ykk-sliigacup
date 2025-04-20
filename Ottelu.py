from playwright.sync_api import sync_playwright
import csv

def scrape_match_stats(match_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigoi ottelun tilastosivulle
            page.goto(match_url, wait_until="networkidle", timeout=60000)
            
            # Odota tilastojen latautumista
            page.wait_for_selector('div.stats-container', timeout=30000)
            
            # Kerää perustiedot
            match_info = {
                'match_id': match_url.split('/')[-2],  # Poimitaan ID URL:sta
                'date': page.query_selector('.match-date').inner_text(),
                'teams': page.query_selector('.match-teams').inner_text(),
                'score': page.query_selector('.match-score').inner_text(),
                'stats': {}
            }
            
            # Kerää tilastot
            stats_sections = page.query_selector_all('div.stats-section')
            for section in stats_sections:
                title = section.query_selector('h3').inner_text()
                stats = {}
                for row in section.query_selector_all('.stats-row'):
                    label = row.query_selector('.stats-label').inner_text()
                    value = row.query_selector('.stats-value').inner_text()
                    stats[label] = value
                match_info['stats'][title] = stats
            
            return match_info
            
        except Exception as e:
            print(f"Virhe ottelussa {match_url}: {str(e)}")
            return None
            
        finally:
            browser.close()

def get_fixtures():
    # Hakee tulevat ottelut fixtures-osoitteessa ja palauttaa niiden ID:t
    from playwright.sync_api import sync_playwright
    fixtures_url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
    match_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(fixtures_url, wait_until="networkidle", timeout=60000)
            # Oleta että otteluiden linkit löytyvät tietystä selectorista, esimerkki:
            links = page.query_selector_all('a[href*="/match/"]')
            for link in links:
                href = link.get_attribute('href')
                if href and "/match/" in href:
                    match_urls.append("https://tulospalvelu.palloliitto.fi" + href)
        finally:
            browser.close()
    return match_urls

def save_to_csv(match_data, filename="Ottelut.csv"):
    if match_data:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Otsikkorivi
            writer.writerow(['Match ID', 'Päivämäärä', 'Joukkueet', 'Tulos', 'Tilasto', 'Arvo'])
            
            # Data
            for stat_type, stats in match_data['stats'].items():
                for label, value in stats.items():
                    writer.writerow([
                        match_data['match_id'],
                        match_data['date'],
                        match_data['teams'],
                        match_data['score'],
                        f"{stat_type} - {label}",
                        value
                    ])
        
        print(f"Tilastot tallennettu tiedostoon {filename}")
    else:
        print("Ei tallennettavia tietoja")

if __name__ == "__main__":
    # Hae kaikki tulevat ottelut ja käsittele ne
    matches = get_fixtures()
    for match_url in matches:
        match_data = scrape_match_stats(match_url)
        if match_data:
            save_to_csv(match_data, filename=f"Ottelu_{match_data['match_id']}.csv")
