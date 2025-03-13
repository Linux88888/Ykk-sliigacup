from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import os

def fetch_match_stats(match_id):
    # Määritä tiedostopolut
    base_dir = os.getcwd()
    md_path = os.path.join(base_dir, f"PelatutOttelut_{match_id}.md")
    csv_path = os.path.join(base_dir, f"PelatutOttelut_{match_id}.csv")
    
    with sync_playwright() as p:
        # Konfiguroi selain
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = context.new_page()
        
        try:
            # 1. Navigoi sivulle
            url = f"https://tulospalvelu.palloliitto.fi/match/{match_id}/stats"
            print(f"🔄 Haetaan ottelua {match_id}...")
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            # 2. Debug: Tallenna koko sivun HTML
            html_content = page.content()
            with open(f"debug_{match_id}.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"📄 Sivun HTML tallennettu tiedostoon debug_{match_id}.html")
            
            # 3. Etsi taulukko uudella logiikalla
            table = page.query_selector('table')  # Yleinen taulukon valitsin
            if not table:
                raise Exception("❌ Taulukkoa ei löytynyt - tarkista debug_{match_id}.html")
            
            # 4. Kerää data
            headers = [th.inner_text().strip() for th in table.query_selector_all("thead th")]
            rows = [
                [td.inner_text().strip() for td in tr.query_selector_all("td")]
                for tr in table.query_selector_all("tbody tr")
            ]
            
            # 5. Tallennus
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(f"# Ottelun {match_id} tilastot ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n\n")
                md_file.write("| " + " | ".join(headers) + " |\n")
                md_file.write("|" + "|".join(["---"] * len(headers)) + "|\n")
                for row in rows:
                    md_file.write("| " + " | ".join(row) + " |\n")
            
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"✅ Tallennettu {len(rows)} riviä tiedostoihin:")
            print(f"📄 {md_path}")
            print(f"📊 {csv_path}")
            return True
            
        except Exception as e:
            print(f"🔥 Kriittinen virhe: {str(e)}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    import sys
    # Käytä komentorivin argumenttia tai testi-ID:tä
    match_id = sys.argv[1] if len(sys.argv) > 1 else 2748452
    success = fetch_match_stats(match_id)
    sys.exit(0 if success else 1)
