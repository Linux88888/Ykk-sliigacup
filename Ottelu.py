from playwright.sync_api import sync_playwright
import csv

def get_fixtures():
    fixtures_url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
    match_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(fixtures_url, wait_until="networkidle", timeout=60000)
            # Etsi kaikki ottelulinkit (tarkista selector tarvittaessa selaimella!)
            links = page.query_selector_all('a[href*="/match/"]')
            for link in links:
                href = link.get_attribute('href')
                if href and "/match/" in href:
                    # Rakennetaan täysi URL
                    if href.startswith("/"):
                        match_urls.append("https://tulospalvelu.palloliitto.fi" + href)
                    else:
                        match_urls.append("https://tulospalvelu.palloliitto.fi/" + href)
        finally:
            browser.close()
    return match_urls

def scrape_match_info(match_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(match_url, wait_until="networkidle", timeout=60000)
            # Odota että perustiedot löytyvät
            page.wait_for_selector('.match-header', timeout=30000)
            date = page.query_selector('.match-date')
            teams = page.query_selector('.match-teams')
            score = page.query_selector('.match-score')
            return {
                "url": match_url,
                "date": date.inner_text() if date else "",
                "teams": teams.inner_text() if teams else "",
                "score": score.inner_text() if score else "",
            }
        except Exception as e:
            print(f"Virhe {match_url}: {e}")
            return None
        finally:
            browser.close()

def save_all_fixtures_csv(matches, filename="TulevatOttelut.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Päivämäärä", "Joukkueet", "Tulos"])
        for match in matches:
            if match:
                writer.writerow([match["url"], match["date"], match["teams"], match["score"]])

if __name__ == "__main__":
    match_urls = get_fixtures()
    print(f"Löytyi {len(match_urls)} tulevaa ottelua.")
    all_matches = []
    for url in match_urls:
        print(f"Käsitellään: {url}")
        info = scrape_match_info(url)
        if info:
            all_matches.append(info)
    save_all_fixtures_csv(all_matches)
    print("Tulevat ottelut tallennettu tiedostoon TulevatOttelut.csv")
