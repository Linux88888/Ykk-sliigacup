from playwright.sync_api import sync_playwright

def fetch_match_stats(match_id):
    url = f"https://tulospalvelu.palloliitto.fi/match/{match_id}/stats"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"Hakee ottelua {match_id} URL: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Odotetaan hetki, jotta sivun sisältö ehtii latautua
            page.wait_for_timeout(5000)
            
            # Jos sivulla on jokin tunnistettava elementti tilastoille, voi odottaa sitä
            # Esim. jos taulukko näkyy: page.wait_for_selector("table.stats-table", timeout=10000)
            
            # Haetaan sivun HTML-sisältö
            html_content = page.content()
            print("Ottelun tilastosivun sisältö:")
            print(html_content)
            
        except Exception as e:
            print(f"Virhe haettaessa ottelua {match_id}: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Testataan ottelua 2748452
    fetch_match_stats(2748452)
