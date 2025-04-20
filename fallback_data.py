import pandas as pd
import json
from datetime import datetime
import os

def create_fallback_files():
    """Create fallback data files when scraping fails"""
    print("Creating fallback data files...")
    
    # Create league table fallback
    league_table = [
        {"Sijoitus": "1", "Joukkue": "KTP", "Ottelut": "24", "Voitot": "16", "Tasapelit": "4", "Tappiot": "4", "Tehdyt maalit": "48", "Päästetyt maalit": "23", "Maaliero": "25", "Pisteet": "52"},
        {"Sijoitus": "2", "Joukkue": "AC Oulu", "Ottelut": "24", "Voitot": "13", "Tasapelit": "7", "Tappiot": "4", "Tehdyt maalit": "34", "Päästetyt maalit": "17", "Maaliero": "17", "Pisteet": "46"},
        {"Sijoitus": "3", "Joukkue": "KPV", "Ottelut": "24", "Voitot": "13", "Tasapelit": "4", "Tappiot": "7", "Tehdyt maalit": "47", "Päästetyt maalit": "26", "Maaliero": "21", "Pisteet": "43"},
        {"Sijoitus": "4", "Joukkue": "TPS", "Ottelut": "24", "Voitot": "13", "Tasapelit": "3", "Tappiot": "8", "Tehdyt maalit": "36", "Päästetyt maalit": "24", "Maaliero": "12", "Pisteet": "42"},
        {"Sijoitus": "5", "Joukkue": "EIF", "Ottelut": "24", "Voitot": "10", "Tasapelit": "9", "Tappiot": "5", "Tehdyt maalit": "32", "Päästetyt maalit": "25", "Maaliero": "7", "Pisteet": "39"},
        {"Sijoitus": "6", "Joukkue": "MYPA", "Ottelut": "24", "Voitot": "10", "Tasapelit": "7", "Tappiot": "7", "Tehdyt maalit": "35", "Päästetyt maalit": "28", "Maaliero": "7", "Pisteet": "37"},
        {"Sijoitus": "7", "Joukkue": "FF Jaro", "Ottelut": "24", "Voitot": "9", "Tasapelit": "8", "Tappiot": "7", "Tehdyt maalit": "37", "Päästetyt maalit": "26", "Maaliero": "11", "Pisteet": "35"},
        {"Sijoitus": "8", "Joukkue": "SJK Akatemia", "Ottelut": "24", "Voitot": "8", "Tasapelit": "4", "Tappiot": "12", "Tehdyt maalit": "30", "Päästetyt maalit": "37", "Maaliero": "-7", "Pisteet": "28"},
        {"Sijoitus": "9", "Joukkue": "PK-35", "Ottelut": "24", "Voitot": "5", "Tasapelit": "7", "Tappiot": "12", "Tehdyt maalit": "25", "Päästetyt maalit": "35", "Maaliero": "-10", "Pisteet": "22"},
        {"Sijoitus": "10", "Joukkue": "MP", "Ottelut": "24", "Voitot": "3", "Tasapelit": "6", "Tappiot": "15", "Tehdyt maalit": "20", "Päästetyt maalit": "48", "Maaliero": "-28", "Pisteet": "15"},
        {"Sijoitus": "11", "Joukkue": "JIPPO", "Ottelut": "24", "Voitot": "1", "Tasapelit": "5", "Tappiot": "18", "Tehdyt maalit": "17", "Päästetyt maalit": "72", "Maaliero": "-55", "Pisteet": "8"}
    ]
    
    # Create fixtures fallback
    fixtures = [
        {"Pelipäivä": "21.04.2025", "Klo": "18:30", "Koti": "TPS", "Vieras": "KTP", "Kotitulos": "", "Vierastulos": "", "Paikka": "Veritas Stadion"},
        {"Pelipäivä": "21.04.2025", "Klo": "18:30", "Koti": "AC Oulu", "Vieras": "KPV", "Kotitulos": "", "Vierastulos": "", "Paikka": "Raatti Stadion"},
        {"Pelipäivä": "22.04.2025", "Klo": "18:30", "Koti": "EIF", "Vieras": "MYPA", "Kotitulos": "", "Vierastulos": "", "Paikka": "Ekenäs Centrumplan"},
        {"Pelipäivä": "22.04.2025", "Klo": "18:30", "Koti": "FF Jaro", "Vieras": "SJK Akatemia", "Kotitulos": "", "Vierastulos": "", "Paikka": "Keskuskenttä"},
        {"Pelipäivä": "23.04.2025", "Klo": "18:30", "Koti": "PK-35", "Vieras": "MP", "Kotitulos": "", "Vierastulos": "", "Paikka": "Myyrmäen stadion"},
        {"Pelipäivä": "14.04.2025", "Klo": "18:30", "Koti": "KTP", "Vieras": "JIPPO", "Kotitulos": "3", "Vierastulos": "0", "Paikka": "Arto Tolsa Areena"}
    ]
    
    # Convert to DataFrames
    league_df = pd.DataFrame(league_table)
    fixtures_df = pd.DataFrame(fixtures)
    
    # Save to CSV
    league_df.to_csv('Sarjataulukko.csv', index=False, encoding='utf-8')
    fixtures_df.to_csv('Ottelut.csv', index=False, encoding='utf-8')
    fixtures_df.to_csv('tulokset.csv', index=False, encoding='utf-8')
    fixtures_df.to_csv('PelatutOttelut.csv', index=False, encoding='utf-8')
    
    # Save as JSON for better readability
    with open('Sarjataulukko.json', 'w', encoding='utf-8') as f:
        json.dump(league_table, f, ensure_ascii=False, indent=2)
    
    with open('Ottelut.json', 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    
    # Create Markdown files
    with open('Sarjataulukko.md', 'w', encoding='utf-8') as f:
        f.write('# Sarjataulukko - Ykkönen\n\n')
        f.write('| Sij. | Joukkue | O | V | T | H | TM | PM | ME | P |\n')
        f.write('| ---- | ------- | - | - | - | - | -- | -- | -- | - |\n')
        
        for team in league_table:
            f.write(f"| {team['Sijoitus']} | {team['Joukkue']} | {team['Ottelut']} | {team['Voitot']} | {team['Tasapelit']} | ")
            f.write(f"{team['Tappiot']} | {team['Tehdyt maalit']} | {team['Päästetyt maalit']} | ")
            f.write(f"{team['Maaliero']} | {team['Pisteet']} |\n")
    
    with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
        f.write('# Ottelut - Ykkönen\n\n')
        f.write('| Päivä | Aika | Koti | Vieras | Tulos | Paikka |\n')
        f.write('| ----- | ---- | ---- | ------ | ----- | ------ |\n')
        
        for match in fixtures:
            tulos = ""
            if match['Kotitulos'] and match['Vierastulos']:
                tulos = f"{match['Kotitulos']}-{match['Vierastulos']}"
            
            f.write(f"| {match['Pelipäivä']} | {match['Klo']} | {match['Koti']} | {match['Vieras']} | {tulos} | {match['Paikka']} |\n")
    
    # Update timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('timestamp.txt', 'w') as f:
        f.write(f"{timestamp} (Fallback data)")
    
    print("Created fallback data files successfully")
    return True

if __name__ == "__main__":
    create_fallback_files()
