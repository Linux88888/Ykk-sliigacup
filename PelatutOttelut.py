from playwright.sync_api import sync_playwright
import csv
import os

def get_all_played_matches():
    fixtures_url = "https://tulospalvelu.palloliitto.fi/category/M1L!spljp25/group/1/fixtures"
    match_ids = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(fixtures_url, wait_until="networkidle", timeout=60000)
            links = page.query_selector_all('a[href*="/match/"]')
            for link in links:
                href = link.get_attribute('href')
                if href and "/match/" in href:
                    match_id = href.split("/match/")[1].split("/")[0]
                    match_ids.append(match_id)
        finally:
            browser.close()
    print(f"DEBUG: Löytyi {len(match_ids)} ottelua fixture-sivulta.")
    return match_ids

def fetch_match_stats(match_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            url = f"https://tulospalvelu.palloliitto.fi/match/{match_id}/stats"
            print(f"DEBUG: Haetaan ottelun {match_id} tiedot...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_selector('div.match-header', timeout=30000)
            date = page.query_selector('div.match-header >> text=/\\d+\\.\\d+\\.\\d+/')
            teams = page.query_selector('div.teams')
            score = page.query_selector('div.score')
            goals_section = page.query_selector('div.goals-section')
            goals = []
            if goals_section:
                for team_block in goals_section.query_selector_all('div.team-block'):
                    team_name = team_block.query_selector('h4.team-name').inner_text().strip()
                    goal_list = [
                        li.inner_text().strip()
                        for li in team_block.query_selector_all('ul.goals-list li')
                    ]
                    goals.append({team_name: goal_list})
            match_info = {
                'match_id': match_id,
                'date': date.inner_text().strip() if date else "",
                'teams': teams.inner_text().strip() if teams else "",
                'score': score.inner_text().strip() if score else "",
                'goals': goals
            }
            print(f"DEBUG: Ottelu {match_id} haettu: {match_info['teams']} ({match_info['date']}) tulos: {match_info['score']}")
            return match_info
        except Exception as e:
            print(f"VIRHE OTTELUSSA {match_id}: {e}")
            return None
        finally:
            browser.close()

def save_matches_to_csv_md(matches, csv_path="PelatutOttelut.csv", md_path="PelatutOttelut.md"):
    # CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Match ID", "Päivämäärä", "Joukkueet", "Tulos", "Maalit"])
        for match in matches:
            if match:
                goalstr = "\n".join([f"{team}: {', '.join(goals)}"
                                     for team_goals in match['goals']
                                     for team, goals in team_goals.items()])
                writer.writerow([
                    match['match_id'],
                    match['date'],
                    match['teams'],
                    match['score'],
                    goalstr
                ])
    print(f"DEBUG: Kirjoitettu {len(matches)} ottelua tiedostoon {csv_path}")

    # MD
    with open(md_path, "w", encoding="utf-8") as md_file:
        if not matches:
            md_file.write("# Pelatut ottelut\n\nEi pelattuja otteluita.\n")
        else:
            md_file.write("# Pelatut ottelut\n\n")
            for match in matches:
                if match:
                    md_file.write(f"## {match['teams']} ({match['date']})\n")
                    md_file.write(f"**Tulos:** {match['score']}\n\n")
                    if match['goals']:
                        md_file.write("### Maalit\n")
                        for team_goals in match['goals']:
                            for team, goals in team_goals.items():
                                md_file.write(f"**{team}**\n")
                                for goal in goals:
                                    md_file.write(f"- {goal}\n")
                        md_file.write("\n")
    print(f"DEBUG: Kirjoitettu {len(matches)} ottelua tiedostoon {md_path}")

if __name__ == "__main__":
    match_ids = get_all_played_matches()
    matches = []
    for match_id in match_ids:
        match = fetch_match_stats(match_id)
        if match:
            matches.append(match)
    save_matches_to_csv_md(matches)
    if not matches:
        print("DEBUG: Ei yhtään ottelua tallennettu.")
    else:
        print(f"DEBUG: Tallennettu {len(matches)} ottelun tiedot.")
