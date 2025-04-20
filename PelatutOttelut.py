import pandas as pd
import os
from datetime import datetime

try:
    print("Starting PelatutOttelut.py...")
    
    # Check if source file exists
    if not os.path.exists('tulokset.csv'):
        print("Error: tulokset.csv not found")
        if os.path.exists('Ottelut.csv'):
            print("Ottelut.csv exists, using that instead")
            input_file = 'Ottelut.csv'
        else:
            print("No input files found!")
            exit(1)
    else:
        input_file = 'tulokset.csv'
    
    # Lue CSV-tiedosto
    print(f"Reading data from {input_file}")
    df = pd.read_csv(input_file)
    print(f"Read {len(df)} rows from {input_file}")
    
    # Debug: Print first few rows and column names
    print("First 3 rows of data:")
    print(df.head(3))
    print("Column names:", df.columns.tolist())
    
    # Check if this is player statistics or match data
    if 'Pelaaja' in df.columns and 'Pelipäivä' not in df.columns:
        print("Processing player statistics data")
        
        # Create a simple output for player statistics
        with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
            f.write('# Pelaajatilastot\n\n')
            f.write('| Pelaaja | Joukkue | Ottelut | Maalit | Syötöt | Pisteet | Minuutit |\n')
            f.write('| ------- | ------- | ------- | ------ | ------ | ------- | -------- |\n')
            
            for _, row in df.iterrows():
                f.write(f"| {row['Pelaaja']} | {row['Joukkue']} | {row['O']} | {row['M']} | {row['S']} | {row['P']} | {row['Min']} |\n")
        
        # Create empty PelatutOttelut.csv for consistency
        df.to_csv('PelatutOttelut.csv', index=False)
    else:
        # Original match data processing logic
        print("Processing match data")
        try:
            # Only try to process date if the column exists
            if 'Pelipäivä' in df.columns:
                df['Pelipäivä'] = pd.to_datetime(df['Pelipäivä'], format='%d.%m.%Y')
                df = df.sort_values(by=['Pelipäivä', 'Klo'], ascending=[True, True])
                df['Pelipäivä'] = df['Pelipäivä'].dt.strftime('%d.%m.%Y')
            
            # Tallenna filtteröity data CSV-tiedostoon
            df.to_csv('PelatutOttelut.csv', index=False)
            
            # Luo Markdown-tiedosto
            with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
                f.write('# Pelatut ottelut\n\n')
                
                # Check which columns we have available
                if 'Pelipäivä' in df.columns and 'Koti' in df.columns:
                    f.write('| Päivä | Aika | Koti | Vieras | Tulos | Paikka |\n')
                    f.write('| ----- | ---- | ---- | ------ | ----- | ------ |\n')
                    
                    for _, row in df.iterrows():
                        tulos = f"{row.get('Kotitulos', '')}-{row.get('Vierastulos', '')}" if 'Kotitulos' in df.columns else ""
                        f.write(f"| {row.get('Pelipäivä', '')} | {row.get('Klo', '')} | {row.get('Koti', '')} | {row.get('Vieras', '')} | {tulos} | {row.get('Paikka', '')} |\n")
                else:
                    # Handle player statistics
                    columns = df.columns.tolist()
                    header = ' | '.join(columns)
                    f.write(f"| {header} |\n")
                    f.write(f"| {' | '.join(['-----' for _ in columns])} |\n")
                    
                    for _, row in df.iterrows():
                        f.write(f"| {' | '.join([str(row.get(col, '')) for col in columns])} |\n")
        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
    
    print("PelatutOttelut.py completed successfully")

except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
