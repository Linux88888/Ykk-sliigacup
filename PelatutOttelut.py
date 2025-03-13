from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

def fetch_match_stats(match_id):
    url = f"https://tulospalvelu.palloliitto.fi/match/{match_id}/stats"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"Hakee ottelua {match_id} URL: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Odotetaan, että taulukko latautuu (muokkaa CSS-valitsinta tarpeen mukaan)
            page.wait_for_selector("table.stats-table", timeout=30000)
            
            # Haetaan ensimmäinen tilastotaulukko
            table = page.query_selector("table.stats-table")
            
            if table:
                # Haetaan taulukon otsikot
                headers = [th.inner_text().strip() for th in table.query_selector_all("thead th")]
                # Haetaan taulukon rivit
                rows = []
                for tr in table.query_selector_all("tbody tr"):
                    row = [td.inner_text().strip() for td in tr.query_selector_all("td")]
                    rows.append(row)
                
                # Tallennetaan Markdown-muotoon
                with open("PelatutOttelut.md", "w", encoding="utf-8") as md_file:
                    md_file.write(f"# Ottelun {match_id} tilastot ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n\n")
                    md_file.write("| " + " | ".join(headers) + " |\n")
                    md_file.write("|" + "|".join(["---"] * len(headers)) + "|\n")
                    for row in rows:
                        md_file.write("| " + " | ".join(row) + " |\n")
                
                # Tallennetaan CSV-muotoon
                with open("PelatutOttelut.csv", "w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(headers)
                    writer.writerows(rows)
                
                print("Tilastotiedot tallennettu: PelatutOttelut.md ja PelatutOttelut.csv")
            else:
                print("Tilastotaulukkoa ei löytynyt sivulta.")
            
        except Exception as e:
            print(f"Virhe haettaessa ottelua {match_id}: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Testataan ottelun 2748452 hakua
    fetch_match_stats(2748452)
