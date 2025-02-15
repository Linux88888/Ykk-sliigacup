import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Määritellään URL, jolta data haetaan
url = "https://tulospalvelu.palloliitto.fi/category/M1LCUP!M1LCUP25/statistics/points"

# Haetaan sivu
response = requests.get(url)

# Tarkistetaan, että sivu on ladattu oikein
if response.status_code == 200:
    page_content = response.text

    # Käytetään BeautifulSoupia sivun analysoimiseen
    soup = BeautifulSoup(page_content, 'html.parser')

    # Etsitään taulukon rivit
    rows = soup.find_all('tr')

    # Debug: tulostetaan ensimmäiset 5 riviä, jotta voimme tarkistaa datan
    print("Ensimmäiset 5 riviä:")
    for i, row in enumerate(rows[:5]):
        print(f"Rivi {i+1}: {row.get_text()}")

    # Avataan CSV-tiedosto kirjoitusta varten
    with open('tulokset.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pelaaja', 'Joukkue', 'O', 'M', 'S', 'P', 'Min'])

        # Käydään läpi kaikki rivit
        for row in rows:
            row_text = row.get_text(separator="\t").strip()
            if any(char.isdigit() for char in row_text):  # Tarkistetaan, että rivillä on numeroita
                parts = row_text.split("\t")
                if len(parts) >= 7:
                    print(f"Rivi tallennettu: {parts}")  # Debug: tulostetaan tallennettavat rivit
                    writer.writerow(parts)

    # Tallennetaan myös aikaleima tiedostoon
    with open("timestamp.txt", "w") as timestamp_file:
        timestamp_file.write(f"Päivitetty: {datetime.utcnow().strftime('%a %b %d %H:%M:%S UTC %Y')}")
else:
    print("Virhe ladattaessa sivua.")
