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
            
            # 3. Kerää perustiedot
            match_info = {
                'match_id': match_id,
                'date': page.query_selector('.match-date').inner_text().strip(),
                'teams': page.query_selector('.match-teams').inner_text().strip(),
                'score': page.query_selector('.match-score').inner_text().strip(),
                'goals': [],
                'warnings': []
            }
            
            # 4. Kerää maalit
            goals_section = page.query_selector('div:has-text("Maalit")')
            if goals_section:
                for team_goals in goals_section.query_selector_all('div.team-goals'):
                    team_name = team_goals.query_selector('h4').inner_text().strip()
                    goals = [
                        goal.inner_text().strip()
                        for goal in team_goals.query_selector_all('ul li')
                    ]
                    match_info['goals'].append({team_name: goals})
            
            # 5. Kerää varoitukset ja kentältäpoistot
            warnings_section = page.query_selector('div:has-text("Varoitukset ja kentältäpoistot")')
            if warnings_section:
                for team_warnings in warnings_section.query_selector_all('div.team-warnings'):
                    team_name = team_warnings.query_selector('h4').inner_text().strip()
                    warnings = [
                        warning.inner_text().strip()
                        for warning in team_warnings.query_selector_all('ul li')
                    ]
                    match_info['warnings'].append({team_name: warnings})
            
            # 6. Tallennus Markdown-muotoon
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(f"# Ottelun {match_id} tilastot ({datetime.now().strftime('%d.%m.%Y %H:%M')})\n\n")
                md_file.write(f"**Päivämäärä:** {match_info['date']}\n")
                md_file.write(f"**Joukkueet:** {match_info['teams']}\n")
                md_file.write(f"**Tulos:** {match_info['score']}\n\n")
                
                md_file.write("## Maalit\n")
                for team_goals in match_info['goals']:
                    for team, goals in team_goals.items():
                        md_file.write(f"### {team}\n")
                        for goal in goals:
                            md_file.write(f"- {goal}\n")
                
                md_file.write("\n## Varoitukset ja kentältäpoistot\n")
                for team_warnings in match_info['warnings']:
                    for team, warnings in team_warnings.items():
                        md_file.write(f"### {team}\n")
                        for warning in warnings:
                            md_file.write(f"- {warning}\n")
            
            # 7. Tallennus CSV-muotoon
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Match ID", "Päivämäärä", "Joukkueet", "Tulos", "Tyyppi", "Tieto"])
                writer.writerow([match_id, match_info['date'], match_info['teams'], match_info['score'], "", ""])
                
                for team_goals in match_info['goals']:
                    for team, goals in team_goals.items():
                        for goal in goals:
                            writer.writerow([match_id, "", "", "", "Maali", f"{team}: {goal}"])
                
                for team_warnings in match_info['warnings']:
                    for team, warnings in team_warnings.items():
                        for warning in warnings:
                            writer.writerow([match_id, "", "", "", "Varoitus", f"{team}: {warning}"])
            
            print(f"✅ Tallennettu tiedot tiedostoihin:")
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
