from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import os

def fetch_match_stats(match_id):
    base_dir = os.getcwd()
    md_path = os.path.join(base_dir, f"PelatutOttelut_{match_id}.md")
    csv_path = os.path.join(base_dir, f"PelatutOttelut_{match_id}.csv")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = context.new_page()
        
        try:
            # 1. Navigoi sivulle
            url = f"https://tulospalvelu.palloliitto.fi/match/{match_id}/stats"
            print(f"🔄 Haetaan ottelua {match_id}...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)  # Odota DOM:n latautumista
            
            # 2. Odota pääsisältöä (pidempi timeout)
            page.wait_for_selector('div.match-header', timeout=60000)
            
            # 3. Kerää perustiedot
            date_element = page.query_selector('div.match-header >> text=/\\d+\\.\\d+\\.\\d+/')
            teams_element = page.query_selector('div.teams')
            score_element = page.query_selector('div.score')
            
            match_info = {
                'match_id': match_id,
                'date': date_element.inner_text().strip() if date_element else "N/A",
                'teams': teams_element.inner_text().strip() if teams_element else "N/A",
                'score': score_element.inner_text().strip() if score_element else "N/A",
                'goals': [],
                'warnings': []
            }
            
            # 4. Kerää maalit (jos saatavilla)
            goals_section = page.query_selector('div.goals-section')
            if goals_section:
                for team_block in goals_section.query_selector_all('div.team-block'):
                    team_name = team_block.query_selector('h4.team-name').inner_text().strip()
                    goals = [
                        li.inner_text().strip() 
                        for li in team_block.query_selector_all('ul.goals-list li')
                    ]
                    match_info['goals'].append({team_name: goals})
            
            # 5. Tallennus
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(f"## {match_info['teams']} ({match_info['date']})\n")
                md_file.write(f"**Tulos:** {match_info['score']}\n\n")
                
                if match_info['goals']:
                    md_file.write("### Maalit\n")
                    for team_goals in match_info['goals']:
                        for team, goals in team_goals.items():
                            md_file.write(f"**{team}**\n")
                            for goal in goals:
                                md_file.write(f"- {goal}\n")
            
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Match ID", "Päivämäärä", "Joukkueet", "Tulos", "Maalit"])
                writer.writerow([
                    match_id,
                    match_info['date'],
                    match_info['teams'],
                    match_info['score'],
                    "\n".join([f"{team}: {', '.join(goals)}" for team_goals in match_info['goals'] for team, goals in team_goals.items()])
                ])
            
            print(f"✅ Tallennettu!")
            return True
            
        except Exception as e:
            print(f"🔥 Virhe: {str(e)}")
            page.screenshot(path=f"error_{match_id}.png")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    import sys
    match_id = sys.argv[1] if len(sys.argv) > 1 else 2748452
    success = fetch_match_stats(match_id)
    sys.exit(0 if success else 1)
