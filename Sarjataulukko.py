import pandas as pd
import os
from datetime import datetime

print("Starting Sarjataulukko.py...")

def process_league_table():
    """Process league table data from available sources"""
    try:
        # Try to read source data
        if os.path.exists('tulokset.csv'):
            df = pd.read_csv('tulokset.csv')
            print(f"Read data from tulokset.csv: {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            
            # Figure out what kind of data we have
            if 'Pelaaja' in df.columns:
                # This is player statistics, create a simple table
                return create_player_statistics_table(df)
            elif 'Koti' in df.columns and 'Vieras' in df.columns:
                # This is match data, create league table
                return create_league_table_from_matches(df)
            else:
                print("Unrecognized data format")
                return False
        else:
            print("No source data found")
            return False
    except Exception as e:
        print(f"Error processing league table: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_player_statistics_table(df):
    """Create a table from player statistics"""
    try:
        # Sort by points, then goals
        df = df.sort_values(by=['P', 'M'], ascending=False)
        
        # Add ranking
        df.insert(0, 'Sija', range(1, len(df) + 1))
        
        # Save as CSV
        df.to_csv('Sarjataulukko.csv', index=False)
        print(f"Created player statistics table with {len(df)} players")
        
        # Create markdown
        with open('Sarjataulukko.md', 'w', encoding='utf-8') as f:
            f.write('# Pelaajatilasto\n\n')
            f.write('| Sija | Pelaaja | Joukkue | O | M | S | P | Min |\n')
            f.write('| ---- | ------- | ------- | - | - | - | - | --- |\n')
            
            for _, row in df.iterrows():
                f.write(f"| {row['Sija']} | {row['Pelaaja']} | {row['Joukkue']} | {row['O']} | {row['M']} | {row['S']} | {row['P']} | {row['Min']} |\n")
        
        return True
    except Exception as e:
        print(f"Error creating player statistics table: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_league_table_from_matches(df):
    """Create a league table from match data"""
    try:
        # Alusta sarjataulukko
        teams = set()
        teams.update(df['Koti'].unique())
        teams.update(df['Vieras'].unique())
        
        sarjataulukko = {
            team: {'Ottelut': 0, 'Voitot': 0, 'Tasapelit': 0, 'Tappiot': 0, 
                'Tehdyt maalit': 0, 'Päästetyt maalit': 0, 'Maaliero': 0, 'Pisteet': 0}
            for team in teams if pd.notna(team)
        }
        
        # Käy läpi ottelut ja päivitä sarjataulukko
        for _, ottelu in df.iterrows():
            try:
                home_team = ottelu['Koti']
                away_team = ottelu['Vieras']
                
                # Skip if teams are NaN
                if pd.isna(home_team) or pd.isna(away_team):
                    continue
                    
                kotitulos = ottelu.get('Kotitulos', None)
                vierastulos = ottelu.get('Vierastulos', None)
                
                # Skip if scores are missing
                if pd.isna(kotitulos) or pd.isna(vierastulos):
                    continue
                    
                try:
                    home_score = int(kotitulos)
                    away_score = int(vierastulos)
                    
                    # Update home team stats
                    sarjataulukko[home_team]['Ottelut'] += 1
                    sarjataulukko[home_team]['Tehdyt maalit'] += home_score
                    sarjataulukko[home_team]['Päästetyt maalit'] += away_score
                    
                    # Update away team stats
                    sarjataulukko[away_team]['Ottelut'] += 1
                    sarjataulukko[away_team]['Tehdyt maalit'] += away_score
                    sarjataulukko[away_team]['Päästetyt maalit'] += home_score
                    
                    # Update wins, draws, losses and points
                    if home_score > away_score:
                        sarjataulukko[home_team]['Voitot'] += 1
                        sarjataulukko[away_team]['Tappiot'] += 1
                        sarjataulukko[home_team]['Pisteet'] += 3
                    elif home_score < away_score:
                        sarjataulukko[away_team]['Voitot'] += 1
                        sarjataulukko[home_team]['Tappiot'] += 1
                        sarjataulukko[away_team]['Pisteet'] += 3
                    else:  # Draw
                        sarjataulukko[home_team]['Tasapelit'] += 1
                        sarjataulukko[away_team]['Tasapelit'] += 1
                        sarjataulukko[home_team]['Pisteet'] += 1
                        sarjataulukko[away_team]['Pisteet'] += 1
                except (ValueError, TypeError):
                    # Skip matches with invalid scores
                    continue
            except Exception as e:
                print(f"Error processing match: {e}")
                continue
                
        # Calculate goal differences
        for team in sarjataulukko:
            sarjataulukko[team]['Maaliero'] = sarjataulukko[team]['Tehdyt maalit'] - sarjataulukko[team]['Päästetyt maalit']
        
        # Create DataFrame from league table
        league_df = pd.DataFrame.from_dict(sarjataulukko, orient='index')
        
        # Sort by points, goal difference and goals scored
        league_df = league_df.sort_values(by=['Pisteet', 'Maaliero', 'Tehdyt maalit'], ascending=False)
        
        # Add ranking column
        league_df.insert(0, 'Sijoitus', range(1, len(league_df) + 1))
        
        # Save as CSV
        league_df.to_csv('Sarjataulukko.csv')
        
        # Create Markdown table
        with open('Sarjataulukko.md', 'w', encoding='utf-8') as f:
            f.write('# Sarjataulukko\n\n')
            f.write('| Sij. | Joukkue | O | V | T | H | TM | PM | ME | P |\n')
            f.write('| ---- | ------- | - | - | - | - | -- | -- | -- | - |\n')
            
            for index, row in league_df.iterrows():
                f.write(f"| {row['Sijoitus']} | {index} | {row['Ottelut']} | {row['Voitot']} | {row['Tasapelit']} | "
                        f"{row['Tappiot']} | {row['Tehdyt maalit']} | {row['Päästetyt maalit']} | "
                        f"{row['Maaliero']} | {row['Pisteet']} |\n")
                        
        return True
    except Exception as e:
        print(f"Error creating league table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        if process_league_table():
            print("League table created successfully")
        else:
            print("Failed to create league table")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
