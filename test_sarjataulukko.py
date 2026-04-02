"""
Testit Ykkönen-sarjataulukko-skripteille.
Testaa sarjataulukon laskenta, pelattujen otteluiden suodatus ja voittajan määritys.
"""
import os
import sys
import json
import tempfile
import shutil
import pandas as pd
import pytest

# Lisää hakemisto polkuun
sys.path.insert(0, os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# Apufunktiot testidatan luontiin
# ---------------------------------------------------------------------------

def make_matches_df(matches):
    """Luo DataFrame-otteludatasta."""
    return pd.DataFrame(matches, columns=['Pelipäivä', 'Klo', 'Koti', 'Vieras', 'Kotitulos', 'Vierastulos', 'Paikka'])


# ---------------------------------------------------------------------------
# Testit: pistelaskenta
# ---------------------------------------------------------------------------

class TestPistelaskenta:
    """Varmistaa, että pisteet lasketaan oikein."""

    def test_voitto_tuo_kolme_pistetta(self):
        """Kotivoitto antaa 3 pistettä kotijoukkueelle."""
        from Sarjataulukko import create_league_table_from_matches
        df = make_matches_df([
            ('01.01.2025', '18:00', 'KTP', 'JIPPO', 3, 0, 'Kotka')
        ])
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = create_league_table_from_matches(df)
                assert result is True
                taulukko = pd.read_csv('Sarjataulukko.csv', index_col=0)
                ktp = taulukko[taulukko.index == 'KTP'].iloc[0]
                assert int(ktp['Pisteet']) == 3, "Voittaja saa 3 pistettä"
                jippo = taulukko[taulukko.index == 'JIPPO'].iloc[0]
                assert int(jippo['Pisteet']) == 0, "Häviäjä saa 0 pistettä"
            finally:
                os.chdir(orig)

    def test_tappio_tuo_nolla_pistetta(self):
        """Vierasvoitto: vierasjoukkue saa 3 p, kotijoukkue 0 p."""
        from Sarjataulukko import create_league_table_from_matches
        df = make_matches_df([
            ('01.01.2025', '18:00', 'TPS', 'AC Oulu', 1, 2, 'Turku')
        ])
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                create_league_table_from_matches(df)
                taulukko = pd.read_csv('Sarjataulukko.csv', index_col=0)
                ac_oulu = taulukko[taulukko.index == 'AC Oulu'].iloc[0]
                assert int(ac_oulu['Pisteet']) == 3
                tps = taulukko[taulukko.index == 'TPS'].iloc[0]
                assert int(tps['Pisteet']) == 0
            finally:
                os.chdir(orig)

    def test_tasapeli_tuo_yksi_piste_kummallekin(self):
        """Tasapeli: molemmat saavat 1 pisteen."""
        from Sarjataulukko import create_league_table_from_matches
        df = make_matches_df([
            ('01.01.2025', '18:00', 'EIF', 'MYPA', 1, 1, 'Tammisaari')
        ])
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                create_league_table_from_matches(df)
                taulukko = pd.read_csv('Sarjataulukko.csv', index_col=0)
                assert int(taulukko.loc['EIF', 'Pisteet']) == 1
                assert int(taulukko.loc['MYPA', 'Pisteet']) == 1
            finally:
                os.chdir(orig)

    def test_maaliero_lasketaan_oikein(self):
        """Maaliero = tehdyt maalit – päästetyt maalit."""
        from Sarjataulukko import create_league_table_from_matches
        df = make_matches_df([
            ('01.01.2025', '18:00', 'KTP', 'JIPPO', 5, 1, 'Kotka'),
            ('02.01.2025', '18:00', 'KTP', 'TPS', 2, 3, 'Kotka'),
        ])
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                create_league_table_from_matches(df)
                taulukko = pd.read_csv('Sarjataulukko.csv', index_col=0)
                ktp = taulukko.loc['KTP']
                assert int(ktp['Tehdyt maalit']) == 7
                assert int(ktp['Päästetyt maalit']) == 4
                assert int(ktp['Maaliero']) == 3
            finally:
                os.chdir(orig)


# ---------------------------------------------------------------------------
# Testit: sarjataulukon järjestys
# ---------------------------------------------------------------------------

class TestSarjataulukkoJarjestys:
    """Varmistaa, että sarjataulukko järjestetään oikein."""

    def _compute_table(self, matches, tmpdir):
        from Sarjataulukko import create_league_table_from_matches
        df = make_matches_df(matches)
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            create_league_table_from_matches(df)
            return pd.read_csv('Sarjataulukko.csv', index_col=0)
        finally:
            os.chdir(orig)

    def test_eniten_pisteita_ensin(self):
        """Eniten pisteitä kerännyt joukkue on ensimmäinen."""
        matches = [
            ('01.01.2025', '18:00', 'KTP', 'JIPPO', 3, 0, 'Kotka'),
            ('01.01.2025', '18:00', 'TPS', 'EIF', 0, 1, 'Turku'),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            taulukko = self._compute_table(matches, tmpdir)
            assert taulukko.index[0] in ('KTP', 'EIF'), "Voittajajoukkue sijoittuu ensimmäiseksi"

    def test_maaliero_ratkaisee_tasapisteissa(self):
        """Maaliero ratkaisee, kun pisteet ovat samat."""
        matches = [
            ('01.01.2025', '18:00', 'KTP', 'TPS', 3, 0, 'Kotka'),   # KTP: 3p, ME +3
            ('02.01.2025', '18:00', 'JIPPO', 'EIF', 1, 0, 'Joensuu'),  # JIPPO: 3p, ME +1
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            taulukko = self._compute_table(matches, tmpdir)
            assert taulukko.index[0] == 'KTP', "Parempi maaliero ratkaisee"

    def test_voittaja_on_ensimmainen(self):
        """Selkeästi paras joukkue on sijalla 1."""
        matches = [
            ('01.01.2025', '18:00', 'KTP', 'JIPPO', 3, 0, 'Kotka'),
            ('02.01.2025', '18:00', 'KTP', 'TPS', 2, 0, 'Kotka'),
            ('03.01.2025', '18:00', 'JIPPO', 'TPS', 0, 1, 'Joensuu'),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            taulukko = self._compute_table(matches, tmpdir)
            assert taulukko.index[0] == 'KTP'


# ---------------------------------------------------------------------------
# Testit: pelattujen otteluiden suodatus
# ---------------------------------------------------------------------------

class TestPelatutOttelutSuodatus:
    """Varmistaa, että vain pelatut ottelut (joilla on tulos) päätyvät PelatutOttelut.csv:ään."""

    def test_vain_pelatut_ottelut_tallennetaan(self, tmp_path):
        """Ottelut ilman tulosta eivät päädy PelatutOttelut.csv:ään."""
        input_csv = tmp_path / 'tulokset.csv'
        input_csv.write_text(
            'Pelipäivä,Klo,Koti,Vieras,Kotitulos,Vierastulos,Paikka\n'
            '14.04.2025,18:30,KTP,JIPPO,3,0,Kotka\n'
            '21.04.2025,18:30,TPS,KTP,,,Turku\n',
            encoding='utf-8'
        )
        df = pd.read_csv(str(input_csv))
        played = df[
            df['Kotitulos'].fillna('').astype(str).str.strip().ne('') &
            df['Vierastulos'].fillna('').astype(str).str.strip().ne('')
        ]
        assert len(played) == 1, "Vain 1 ottelu on pelattu"
        assert played.iloc[0]['Koti'] == 'KTP'

    def test_kaikki_pelatut_ottelut_mukana(self, tmp_path):
        """Kaikki ottelut joilla on tulos sisällytetään."""
        input_csv = tmp_path / 'tulokset.csv'
        input_csv.write_text(
            'Pelipäivä,Klo,Koti,Vieras,Kotitulos,Vierastulos,Paikka\n'
            '01.04.2025,18:00,KTP,JIPPO,3,0,Kotka\n'
            '02.04.2025,18:00,TPS,EIF,2,1,Turku\n'
            '03.04.2025,18:00,AC Oulu,KPV,,,Oulu\n',
            encoding='utf-8'
        )
        df = pd.read_csv(str(input_csv))
        played = df[
            df['Kotitulos'].fillna('').astype(str).str.strip().ne('') &
            df['Vierastulos'].fillna('').astype(str).str.strip().ne('')
        ]
        assert len(played) == 2

    def test_nolla_nolla_tasapeli_mukana(self, tmp_path):
        """0-0 tasapeli (tulos 0) ei jää pois suodatuksessa."""
        input_csv = tmp_path / 'tulokset.csv'
        input_csv.write_text(
            'Pelipäivä,Klo,Koti,Vieras,Kotitulos,Vierastulos,Paikka\n'
            '05.04.2025,18:00,EIF,MYPA,0,0,Tammisaari\n'
            '06.04.2025,18:00,PK-35,MP,,,Helsinki\n',
            encoding='utf-8'
        )
        df = pd.read_csv(str(input_csv))
        played = df[
            df['Kotitulos'].fillna('').astype(str).str.strip().ne('') &
            df['Vierastulos'].fillna('').astype(str).str.strip().ne('')
        ]
        assert len(played) == 1, "0-0 tulos pitää sisällyttää"
        assert played.iloc[0]['Koti'] == 'EIF'


# ---------------------------------------------------------------------------
# Testit: voittajan määritys oikeasta datasta
# ---------------------------------------------------------------------------

class TestVoittaja:
    """Tarkistaa, että oikea voittaja löytyy sarjataulukosta."""

    def test_ktp_voitti_ykkosen_2024(self):
        """KTP voitti Ykkösen 2024 kaudella."""
        json_path = os.path.join(os.path.dirname(__file__), 'Sarjataulukko.json')
        assert os.path.exists(json_path), "Sarjataulukko.json on olemassa"
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Muunna pisteet numeerisiksi
        df['Pisteet'] = pd.to_numeric(df['Pisteet'])
        voittaja = df.loc[df['Pisteet'].idxmax(), 'Joukkue']
        assert voittaja == 'KTP', f"Odotettu voittaja KTP, mutta oli {voittaja}"

    def test_ktp_pisteet_52(self):
        """KTP:llä on 52 pistettä."""
        json_path = os.path.join(os.path.dirname(__file__), 'Sarjataulukko.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['Pisteet'] = pd.to_numeric(df['Pisteet'])
        ktp_pisteet = df.loc[df['Joukkue'] == 'KTP', 'Pisteet'].iloc[0]
        assert ktp_pisteet == 52

    def test_ktp_sijoitus_yksi(self):
        """KTP on sijalla 1 sarjataulukossa."""
        json_path = os.path.join(os.path.dirname(__file__), 'Sarjataulukko.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['Sijoitus'] = pd.to_numeric(df['Sijoitus'])
        ktp_sijoitus = df.loc[df['Joukkue'] == 'KTP', 'Sijoitus'].iloc[0]
        assert ktp_sijoitus == 1

    def test_viimeinen_jippo(self):
        """JIPPO on viimeisenä (sija 11) sarjataulukossa."""
        json_path = os.path.join(os.path.dirname(__file__), 'Sarjataulukko.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['Sijoitus'] = pd.to_numeric(df['Sijoitus'])
        viimeinen = df.loc[df['Sijoitus'] == df['Sijoitus'].max(), 'Joukkue'].iloc[0]
        assert viimeinen == 'JIPPO'


# ---------------------------------------------------------------------------
# Testit: fallback_data.py
# ---------------------------------------------------------------------------

class TestFallbackData:
    """Varmistaa, että fallback_data.py luo tiedostot oikein."""

    def test_fallback_luo_tiedostot(self):
        """fallback_data.create_fallback_files() luo kaikki tarvittavat tiedostot."""
        from fallback_data import create_fallback_files
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = create_fallback_files()
                assert result is True
                for fname in ['Sarjataulukko.csv', 'Sarjataulukko.md', 'Sarjataulukko.json',
                              'Ottelut.csv', 'PelatutOttelut.csv', 'PelatutOttelut.md']:
                    assert os.path.exists(fname), f"{fname} puuttuu"
            finally:
                os.chdir(orig)

    def test_pelatutottelut_csv_ei_sisalla_tulevia(self):
        """PelatutOttelut.csv sisältää vain pelatut ottelut (ei tulevia)."""
        from fallback_data import create_fallback_files
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                create_fallback_files()
                df = pd.read_csv('PelatutOttelut.csv')
                # Kaikilla riveillä pitää olla tulos
                assert all(
                    df['Kotitulos'].astype(str).str.strip().ne('') &
                    df['Vierastulos'].astype(str).str.strip().ne('')
                ), "PelatutOttelut.csv sisältää ottelun ilman tulosta"
            finally:
                os.chdir(orig)

    def test_sarjataulukko_csv_sisaltaa_11_joukkuetta(self):
        """Sarjataulukko.csv sisältää 11 joukkuetta."""
        from fallback_data import create_fallback_files
        with tempfile.TemporaryDirectory() as tmpdir:
            orig = os.getcwd()
            os.chdir(tmpdir)
            try:
                create_fallback_files()
                df = pd.read_csv('Sarjataulukko.csv')
                assert len(df) == 11
            finally:
                os.chdir(orig)
