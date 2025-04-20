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
    
    # Debug: Print first few rows
    print("First 3 rows of data:")
    print(df.head(3))
    
    # Muuta pelipäivä datetime-muotoon ja järjestä
    try:
        df['Pelipäivä'] = pd.to_datetime(df['Pelipäivä'], format='%d.%m.%Y')
        df = df.sort_values(by=['Pelipäivä', 'Klo'], ascending=[True, True])
        print("Data sorted successfully")
    except Exception as e:
        print(f"Error sorting data: {e}")
    
    # Muuta pelipäivä takaisin merkkijonoksi halutussa muodossa
    df['Pelipäivä'] = df['Pelipäivä'].dt.strftime('%d.%m.%Y')
    
    # Tallenna filtteröity data CSV-tiedostoon
    try:
        df.to_csv('PelatutOttelut.csv', index=False)
        print(f"Saved {len(df)} rows to PelatutOttelut.csv")
    except Exception as e:
        print(f"Error saving CSV: {e}")
    
    # Luo Markdown-tiedosto
    try:
        with open('PelatutOttelut.md', 'w', encoding='utf-8') as f:
            f.write('# Pelatut ottelut\n\n')
            f.write('| Päivä | Aika | Koti | Vieras | Tulos | Paikka |\n')
            f.write('| ----- | ---- | ---- | ------ | ----- | ------ |\n')
            
            for _, row in df.iterrows():
                f.write(f"| {row['Pelipäivä']} | {row['Klo']} | {row['Koti']} | {row['Vieras']} | {row['Kotitulos']}-{row['Vierastulos']} | {row['Paikka']} |\n")
        
        print("Created PelatutOttelut.md successfully")
    except Exception as e:
        print(f"Error creating Markdown: {e}")
    
    print("PelatutOttelut.py completed successfully")

except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
