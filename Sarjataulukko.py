from playwright.sync_api import sync_playwright
import csv
from datetime import datetime

def scrape_league_table():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigoi sarjataulukon sivulle
            url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/"
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Odota sarjataulukon latautumista
            page.wait_for_selector('table.standings-table', timeout=30000)
            
            # Kerää otsikkotiedot
            headers = [th.inner_text() for th in page.query_selector_all('table.standings-table thead th')]
            
            # Kerää joukkueiden tiedot
            teams = []
            for row in page.query_selector_all('table.standings-table tbody tr'):
                team_data = [td.inner_text().strip() for td in row.query_selector_all('td')]
                teams.append(team_data)
            
            # Tallennus Markdown-muotoon
            with open('Sarjataulukko.md', 'w', encoding='utf-8') as md_file:
                # Otsikko
                md_file.write(f"# Sarjataulukko ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n\n")
                
                # Taulukko
                md_file.write("| " + " | ".join(headers) + " |\n")
                md_file.write("|" + "|".join(["---"] * len(headers)) + "|\n")
                for team in teams:
                    md_file.write("| " + " | ".join(team) + " |\n")
            
            # Tallennus CSV-muotoon
            with open('Sarjataulukko.csv', 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)
                writer.writerows(teams)
            
            return {
                'headers': headers,
                'teams': teams,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Virhe: {str(e)}")
            return None
            
        finally:
            browser.close()

if __name__ == "__main__":
    result = scrape_league_table()
    if result:
        print(f"Tallennettu {len(result['teams'])} joukkueen tiedot")
        print("Tiedostot:")
        print("- Sarjataulukko.md (Markdown-muoto)")
        print("- Sarjataulukko.csv (CSV-muoto)")
    else:
        print("Tallennus epäonnistui")
