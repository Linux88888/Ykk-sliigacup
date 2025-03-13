from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

def scrape_league_table():
    with sync_playwright() as p:
        # Alusta selain botin väistämisasetuksin
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = context.new_page()
        
        try:
            # Navigoi sivulle
            url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/"
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Odota taulukkoa eksplisiittisesti
            page.wait_for_selector('table', state='attached', timeout=15000)
            
            # Debug: Tallenna HTML
            html_content = page.content()
            with open('Sivu.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Kerää tiedot
            headers = [th.inner_text().strip() for th in page.query_selector_all('table thead th')]
            teams = [
                [td.inner_text().strip() for td in row.query_selector_all('td')] 
                for row in page.query_selector_all('table tbody tr')
            ]
            
            # Debug-tulosteet
            print("Löydetyt otsikot:", headers)
            print("Löydetyt joukkueet:", len(teams))
            
            # Tallennus
            with open('Sarjataulukko.md', 'w', encoding='utf-8') as md_file:
                md_file.write(f"# Sarjataulukko ({datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                md_file.write("| " + " | ".join(headers) + " |\n")
                md_file.write("|" + "|".join(["---"]*len(headers)) + "|\n")
                for team in teams:
                    md_file.write("| " + " | ".join(team) + " |\n")
            
            with open('Sarjataulukko.csv', 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
                writer.writerows(teams)
            
            return True
            
        except Exception as e:
            print(f"Kriittinen virhe: {str(e)}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    if scrape_league_table():
        print("Päivitys onnistui!")
    else:
        print("Päivitys epäonnistui. Tarkista Sivu.html ja virheilmoitukset.")
