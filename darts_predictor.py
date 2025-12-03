import streamlit as st
import numpy as np
import random
import pandas as pd
import altair as alt
from typing import Dict, Any

# --- Streamlit-sivun asetukset (Tumma teema oletuksena) ---
st.set_page_config(
    page_title="🎯 Darts-simulaattori (PDC 96)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Optimal Checkout Taulukko & Apumuuttujat ---
CHECKOUT_MAP = {
    170: ["T20", "T20", "Bull"], 167: ["T20", "T19", "Bull"], 164: ["T20", "T18", "Bull"], 161: ["T20", "T17", "Bull"],
    160: ["T20", "T20", "D20"], 158: ["T20", "T20", "D19"], 157: ["T20", "T19", "D20"], 156: ["T20", "T20", "D18"],
    155: ["T20", "T19", "D19"], 154: ["T20", "T18", "D20"], 153: ["T20", "T19", "D18"], 152: ["T20", "T18", "D19"],
    151: ["T20", "T17", "D20"], 150: ["T20", "T18", "D18"], 149: ["T20", "T19", "D16"], 148: ["T20", "T16", "D20"],
    147: ["T20", "T17", "D18"], 146: ["T20", "T18", "D16"], 145: ["T20", "T15", "D20"], 144: ["T20", "T16", "D16"],
    143: ["T20", "T17", "D16"], 142: ["T20", "T14", "D20"], 141: ["T20", "T19", "D12"], 140: ["T20", "T20", "D10"],
    139: ["T20", "T13", "D20"], 138: ["T20", "T18", "D12"], 137: ["T20", "T19", "D10"], 136: ["T20", "T16", "D14"],
    135: ["T20", "T17", "D12"], 134: ["T20", "T14", "D16"], 133: ["T20", "T19", "D8"], 132: ["T20", "T16", "D12"],
    131: ["T20", "T13", "D16"], 130: ["T20", "T10", "D20"], 129: ["T19", "T16", "D12"], 128: ["T18", "T14", "D16"],
    127: ["T20", "T17", "D8"], 126: ["T19", "T19", "D6"], 125: ["Bull", "T19", "D18"], 124: ["T20", "T14", "D11"],
    123: ["T19", "T16", "D9"], 122: ["T18", "T18", "D7"], 121: ["T20", "T11", "D14"], 120: ["T20", "S20", "D20"],
    119: ["T19", "S20", "D20"], 118: ["T20", "S18", "D20"], 117: ["T20", "S17", "D20"], 116: ["T20", "S16", "D20"],
    115: ["T20", "S15", "D20"], 114: ["T20", "S14", "D20"], 113: ["T20", "S13", "D20"], 112: ["T20", "S12", "D20"],
    111: ["T20", "S19", "D16"], 110: ["T20", "S10", "D20"], 109: ["T20", "S19", "D15"], 108: ["T20", "S16", "D16"],
    107: ["T20", "S17", "D15"], 106: ["T20", "S18", "D14"], 105: ["T20", "S13", "D16"], 104: ["T20", "S12", "D16"],
    103: ["T19", "S14", "D20"], 102: ["T20", "S10", "D16"], 101: ["T17", "S10", "D20"], 100: ["T20", "S20", "D20"],
    99: ["T19", "S10", "D16"], 98: ["T20", "D19"], 97: ["T19", "D20"], 96: ["T20", "D18"], 95: ["T19", "D19"], 94: ["T18", "D20"],
    93: ["T19", "D18"], 92: ["T20", "D16"], 91: ["T17", "D20"], 90: ["T20", "D15"], 89: ["T19", "D16"], 88: ["T20", "D14"],
    87: ["T17", "D18"], 86: ["T18", "D16"], 85: ["T19", "D14"], 84: ["T20", "D12"], 83: ["T17", "D16"], 82: ["T15", "D18"],
    81: ["T19", "D12"], 80: ["T20", "D10"], 79: ["T19", "D11"], 78: ["T18", "D12"], 77: ["T15", "D16"], 76: ["T20", "D8"],
    75: ["T17", "D12"], 74: ["T14", "D16"], 73: ["T19", "D8"], 72: ["T12", "D18"], 71: ["T13", "D16"], 70: ["T10", "D20"],
    69: ["T15", "D12"], 68: ["T12", "D16"], 67: ["T17", "D8"], 66: ["T10", "D18"], 65: ["Bull", "D20"], 64: ["T16", "D8"],
    63: ["T13", "D12"], 62: ["T10", "D16"], 61: ["T15", "D8"], 60: ["S20", "D20"], 59: ["S19", "D20"], 58: ["S18", "D20"],
    57: ["S17", "D20"], 56: ["S16", "D20"], 55: ["S15", "D20"], 54: ["S14", "D20"], 53: ["S13", "D20"], 52: ["S12", "D20"],
    51: ["S11", "D20"], 50: ["S10", "D20"], 49: ["T17", "D4"], 48: ["S16", "D16"], 47: ["S7", "D20"], 46: ["S6", "D20"],
    45: ["S13", "D16"], 44: ["S4", "D20"], 43: ["S3", "D20"], 42: ["S10", "D16"], 41: ["S9", "D16"], 40: ["D20"], 39: ["S7", "D16"],
    38: ["S18", "D10"], 37: ["S5", "D16"], 36: ["D18"], 35: ["S3", "D16"], 34: ["D17"], 33: ["S1", "D16"], 32: ["D16"], 31: ["S15", "D8"],
    30: ["D15"], 29: ["S13", "D8"], 28: ["D14"], 27: ["S11", "D8"], 26: ["D13"], 25: ["S9", "D8"], 24: ["D12"], 23: ["S7", "D8"],
    22: ["D11"], 21: ["S5", "D8"], 20: ["D10"], 19: ["S3", "D8"], 18: ["D9"], 17: ["S1", "D8"], 16: ["D8"], 15: ["S7", "D4"],
    14: ["D7"], 13: ["S5", "D4"], 12: ["D6"], 11: ["S3", "D4"], 10: ["D5"], 9: ["S1", "D4"], 8: ["D4"], 7: ["S3", "D2"],
    6: ["D3"], 5: ["S1", "D2"], 4: ["D2"], 3: ["S1", "D1"], 2: ["D1"]
}
SCORING_MAP = {"S": 1, "D": 2, "T": 3, "Bull": 50, "B": 50}

# --- 2. Pelaajaprofiilit (TÄYDENNETTY CSV-DATALLA) ---
# Ladataan ja muokataan CSV-data
try:
    df_players = pd.read_csv("MM 25 csv - Voitko tehdä kaikista osallistujista docs listan... (1).csv", sep=',')
    
    # Korvataan pilkut desimaalipisteillä ja muutetaan float-tyypiksi
    cols_to_convert = ['KAUSI 2025 (3DA)', 'COP (%)', 'STD (Hajonta)', 'F9A', 'TWS KA', 'RWS KA']
    for col in cols_to_convert:
        if col in df_players.columns:
            # Poistetaan ylimääräiset lainausmerkit ja korvataan pilkut pisteillä
            df_players[col] = df_players[col].astype(str).str.replace('"', '', regex=False).str.replace(',', '.', regex=False)
            df_players[col] = pd.to_numeric(df_players[col], errors='coerce')
    
    # Sarakkeiden uudelleennimeäminen luettavuuden helpottamiseksi
    player_data = df_players.rename(columns={
        'Pelaajan Nimi': 'Name',
        'KAUSI 2025 (3DA)': 'KAUSI 2025',
        'COP (%)': 'COP',
        'STD (Hajonta)': 'STD',
        'F9A': 'F9A',
        'TWS KA': 'TWS KA',
        'RWS KA': 'RWS KA',
        'FDI': 'FDI' # Jätetään kokonaislukuna tai floatina
    }).set_index('Sija').to_dict('records')
    
    # Uusi sanakirja, johon pelaajat lisätään
    NEW_PRESETS = {}
    
    for i, player in enumerate(player_data):
        # Nimen normalisointi: "1. Luke Littler (England)" -> "Luke Littler (1)"
        if pd.notna(player['Name']):
            full_name = str(player['Name']).strip()
            # Yritetään poistaa sijaluku alusta, esim. "1. "
            if full_name and full_name[0].isdigit():
                name_parts = full_name.split('. ', 1)
                if len(name_parts) > 1:
                    full_name = name_parts[1].strip()
            
            # Lisätään Sija sulkuihin, jos nimi ei jo sisällä sijalukua (kuten alkuperäisissä profiileissa)
            # PDC TOP 32 pelaajat ovat jo koodissa, joten emme korvaa niitä uusilla tiedoilla
            if i >= 32: # Aloitetaan pelaajista, joita ei vielä ole koodissa
                 player_key = f"{full_name} ({player['Sija']})"
                 
                 # Konvertoidaan arvot, COP prosentiksi
                 NEW_PRESETS[player_key] = {
                    "KA": player.get('KAUSI 2025', 95.0), 
                    "KAUSI 2025": player.get('KAUSI 2025', 95.0), 
                    "COP": int(player.get('COP', 35)), 
                    "STD": player.get('STD', 18.0), 
                    "FDI": player.get('FDI', 60.0), # FDI voi olla myös kokonaisluku
                    "F9A": player.get('F9A', 95.0),
                    "TWS KA": int(player.get('TWS KA', 70)),
                    "RWS KA": int(player.get('RWS KA', 40))
                }
                
    # PDC TOP 32 Pelaajat (Päivitetty)
    NEW_PRESETS["Luke Littler (1)"] = {"KA": 100.96, "KAUSI 2025": 100.96, "COP": 43, "STD": 16.0, "FDI": 1976, "F9A": 111.51, "TWS KA": 99.44, "RWS KA": 102.72}
    NEW_PRESETS["Luke Humphries (2)"] = {"KA": 98.50, "KAUSI 2025": 98.50, "COP": 41, "STD": 17.0, "FDI": 1876, "F9A": 107.8, "TWS KA": 96.62, "RWS KA": 100.63}
    NEW_PRESETS["Michael van Gerwen (3)"] = {"KA": 97.28, "KAUSI 2025": 97.28, "COP": 39, "STD": 18.0, "FDI": 1809, "F9A": 106.42, "TWS KA": 95.85, "RWS KA": 98.87}
    NEW_PRESETS["Stephen Bunting (4)"] = {"KA": 98.04, "KAUSI 2025": 98.04, "COP": 39, "STD": 18.0, "FDI": 1823, "F9A": 107.65, "TWS KA": 96.95, "RWS KA": 99.24}
    NEW_PRESETS["Jonny Clayton (5)"] = {"KA": 96.30, "KAUSI 2025": 96.30, "COP": 42, "STD": 20.0, "FDI": 1790, "F9A": 104.69, "TWS KA": 95.05, "RWS KA": 97.71}
    NEW_PRESETS["Danny Noppert (6)"] = {"KA": 94.79, "KAUSI 2025": 94.79, "COP": 40, "STD": 20.0, "FDI": 1822, "F9A": 102.79, "TWS KA": 94.52, "RWS KA": 95.09}
    NEW_PRESETS["James Wade (7)"] = {"KA": 94.79, "KAUSI 2025": 94.79, "COP": 42, "STD": 20.0, "FDI": 1684, "F9A": 102.73, "TWS KA": 93.38, "RWS KA": 95.53}
    NEW_PRESETS["Chris Dobey (8)"] = {"KA": 96.76, "KAUSI 2025": 96.76, "COP": 38, "STD": 19.0, "FDI": 1819, "F9A": 104.91, "TWS KA": 96.06, "RWS KA": 97.35}
    NEW_PRESETS["Gerwyn Price (9)"] = {"KA": 97.75, "KAUSI 2025": 97.75, "COP": 40, "STD": 19.0, "FDI": 1836, "F9A": 106.94, "TWS KA": 97.3, "RWS KA": 99.04}
    NEW_PRESETS["Gian van Veen (10)"] = {"KA": 97.91, "KAUSI 2025": 97.91, "COP": 38, "STD": 19.0, "FDI": 1823, "F9A": 107.49, "TWS KA": 97.02, "RWS KA": 99.18}
    NEW_PRESETS["Josh Rock (11)"] = {"KA": 98.10, "KAUSI 2025": 98.10, "COP": 39, "STD": 18.0, "FDI": 1856, "F9A": 108.2, "TWS KA": 98.24, "RWS KA": 100.2}
    NEW_PRESETS["Ross Smith (12)"] = {"KA": 96.50, "KAUSI 2025": 96.50, "COP": 39, "STD": 20.0, "FDI": 1817, "F9A": 104.98, "TWS KA": 94.76, "RWS KA": 97.13}
    NEW_PRESETS["Martin Schindler (13)"] = {"KA": 94.13, "KAUSI 2025": 94.13, "COP": 35, "STD": 20.0, "FDI": 1780, "F9A": 102.34, "TWS KA": 93.61, "RWS KA": 94.71}
    NEW_PRESETS["Gary Anderson (14)"] = {"KA": 97.41, "KAUSI 2025": 97.41, "COP": 38, "STD": 17.0, "FDI": 1845, "F9A": 107.03, "TWS KA": 97.1, "RWS KA": 99.27}
    NEW_PRESETS["Nathan Aspinall (15)"] = {"KA": 95.64, "KAUSI 2025": 95.64, "COP": 37, "STD": 20.0, "FDI": 1731, "F9A": 103.62, "TWS KA": 94.02, "RWS KA": 95.96}
    NEW_PRESETS["Damon Heta (16)"] = {"KA": 94.81, "KAUSI 2025": 94.81, "COP": 40, "STD": 20.0, "FDI": 1718, "F9A": 103.24, "TWS KA": 94.27, "RWS KA": 95.4}
    NEW_PRESETS["Rob Cross (17)"] = {"KA": 95.75, "KAUSI 2025": 95.75, "COP": 41, "STD": 20.0, "FDI": 1774, "F9A": 104.42, "TWS KA": 95.17, "RWS KA": 96.6}
    NEW_PRESETS["Mike De Decker (18)"] = {"KA": 93.92, "KAUSI 2025": 93.92, "COP": 33, "STD": 20.0, "FDI": 1709, "F9A": 101.42, "TWS KA": 92.4, "RWS KA": 93.76}
    NEW_PRESETS["Jermaine Wattimena (19)"] = {"KA": 94.87, "KAUSI 2025": 94.87, "COP": 32, "STD": 21.0, "FDI": 1709, "F9A": 102.48, "TWS KA": 93.45, "RWS KA": 94.49}
    NEW_PRESETS["Ryan Searle (20)"] = {"KA": 95.76, "KAUSI 2025": 95.76, "COP": 33, "STD": 20.0, "FDI": 1730, "F9A": 103.58, "TWS KA": 94.61, "RWS KA": 95.71}
    NEW_PRESETS["Dave Chisnall (21)"] = {"KA": 91.86, "KAUSI 2025": 91.86, "COP": 34, "STD": 20.0, "FDI": 1705, "F9A": 99.31, "TWS KA": 91.42, "RWS KA": 92.23}
    NEW_PRESETS["Daryl Gurney (22)"] = {"KA": 93.23, "KAUSI 2025": 93.23, "COP": 33, "STD": 21.0, "FDI": 1706, "F9A": 100.86, "TWS KA": 91.88, "RWS KA": 92.93}
    NEW_PRESETS["Dimitri Van den Bergh (23)"] = {"KA": 94.20, "KAUSI 2025": 94.20, "COP": 35, "STD": 20.0, "FDI": 1690, "F9A": 102.5, "TWS KA": 93.29, "RWS KA": 94.5}
    NEW_PRESETS["Ryan Joyce (24)"] = {"KA": 93.02, "KAUSI 2025": 93.02, "COP": 32, "STD": 21.0, "FDI": 1664, "F9A": 100.86, "TWS KA": 91.68, "RWS KA": 92.73}
    NEW_PRESETS["Luke Woodhouse (25)"] = {"KA": 92.70, "KAUSI 2025": 92.70, "COP": 32, "STD": 21.0, "FDI": 1642, "F9A": 100.58, "TWS KA": 91.36, "RWS KA": 92.41}
    NEW_PRESETS["Cameron Menzies (26)"] = {"KA": 92.65, "KAUSI 2025": 92.65, "COP": 31, "STD": 22.0, "FDI": 1683, "F9A": 100.67, "TWS KA": 91.17, "RWS KA": 92.35}
    NEW_PRESETS["Ritchie Edhouse (27)"] = {"KA": 93.20, "KAUSI 2025": 93.20, "COP": 32, "STD": 22.0, "FDI": 1715, "F9A": 101.48, "TWS KA": 91.93, "RWS KA": 92.9}
    NEW_PRESETS["Michael Smith (28)"] = {"KA": 92.74, "KAUSI 2025": 92.74, "COP": 34, "STD": 19.0, "FDI": 1787, "F9A": 100.99, "TWS KA": 93.43, "RWS KA": 94.5}
    NEW_PRESETS["Dirk van Duijvenbode (29)"] = {"KA": 96.53, "KAUSI 2025": 96.53, "COP": 36, "STD": 20.0, "FDI": 1746, "F9A": 105.15, "TWS KA": 94.81, "RWS KA": 96.53}
    NEW_PRESETS["Peter Wright (30)"] = {"KA": 92.41, "KAUSI 2025": 92.41, "COP": 35, "STD": 20.0, "FDI": 1695, "F9A": 100.08, "TWS KA": 91.88, "RWS KA": 92.83}
    NEW_PRESETS["Wessel Nijman (31)"] = {"KA": 95.86, "KAUSI 2025": 95.86, "COP": 34, "STD": 21.0, "FDI": 1729, "F9A": 104.14, "TWS KA": 94.13, "RWS KA": 95.27}
    NEW_PRESETS["Joe Cullen (32)"] = {"KA": 91.88, "KAUSI 2025": 91.88, "COP": 33, "STD": 20.0, "FDI": 1693, "F9A": 99.22, "TWS KA": 91.3, "RWS KA": 92.17}
    
except Exception as e:
    st.error(f"Virhe CSV-tiedoston käsittelyssä tai datan muuntamisessa: {e}. Käytetään oletusprofiileja.")
    NEW_PRESETS = {}

DEFAULT_PRESETS = {
    "VALITSE PROFIILI": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    "--- PDC TOP 32 SIJOITETUT (2025) ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    **NEW_PRESETS, # Lisätään dynaamisesti luodut/päivitetyt pelaajat tähän
    "--- LISÄPROFIILIT ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    "Teemu Harju (FIN)": {"KA": 86.36, "KAUSI 2025": 86.36, "COP": 35, "STD": 20.0, "FDI": 1669, "F9A": 95.87, "TWS KA": 85.53, "RWS KA": 87.28},
    "Epätasainen (Aloittelija)": {"KA": 80.0, "KAUSI 2025": 80.0, "COP": 28, "STD": 25, "FDI": 1450, "F9A": 81.0, "TWS KA": 45, "RWS KA": 25},
    "Hyvä Harrastaja": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 20, "FDI": 1650, "F9A": 91.5, "TWS KA": 65, "RWS KA": 35}
}

PLAYER_NAMES = list(DEFAULT_PRESETS.keys())

# --- 3. Simulaatiofunktiot (Muuttumattomat) ---
# (Simulaatiofunktiot pysyvät samana)

def get_hit_score(segment: str) -> int:
    """Laskee segmentin pistearvon."""
    if segment in ["Bull", "B"]:
        return 50
    score_value = int(segment[1:]) if len(segment) > 1 else 0
    multiplier = SCORING_MAP.get(segment[0], 1)
    return score_value * multiplier

def simulate_score(average_score: float, std_dev: float) -> int:
    """Simuloi yhden kolmen tikan heiton pisteet normaalijakauman avulla."""
    score = int(np.random.normal(average_score, std_dev))
    return max(0, min(180, score))

def attempt_checkout(current_score: int, cop: float) -> tuple[int, bool]:
    """Simuloi tikkojen heiton ulosheittoetäisyydeltä (sis. bustin riskin)."""
    if current_score not in CHECKOUT_MAP or current_score <= 1:
        return current_score, False 

    if random.random() < cop:
        return 0, True
    else:
        route = CHECKOUT_MAP.get(current_score, ["S20", "S20", "S20"]) 
        
        if current_score > 100:
            score_taken = int(current_score * random.uniform(0.3, 0.6))
        else:
            score_taken = int(current_score * random.uniform(0.5, 0.9))
        
        score_taken = max(0, min(current_score - 2, score_taken))
        
        new_score = current_score - score_taken
        
        if new_score < 2:
            return current_score, False
        return new_score, False

def simulate_leg(player_a_avg: float, player_a_cop: float, player_a_std: float, 
                 player_b_avg: float, player_b_cop: float, player_b_std: float, starts_a: bool) -> str:
    """Simuloi yhden Leg-pelin."""
    score_a = 501
    score_b = 501
    turn_index = 0 if starts_a else 1 
    
    while score_a > 0 and score_b > 0:
        is_player_a = turn_index % 2 == 0
        current_score = score_a if is_player_a else score_b
        avg, cop, std = (player_a_avg, player_a_cop, player_a_std) if is_player_a else (player_b_avg, player_b_cop, player_b_std)
            
        if current_score <= 170 and current_score in CHECKOUT_MAP:
            new_score, win = attempt_checkout(current_score, cop)
            if win:
                return "A" if is_player_a else "B"
            current_score = new_score
        else:
            score = simulate_score(avg, std) 
            current_score -= score
            
            if current_score < 2:
                current_score += score
            
        if is_player_a:
            score_a = current_score
        else:
            score_b = current_score
                        
        turn_index += 1
    return "A" if score_a == 0 else "B" 


def simulate_match(params: Dict[str, Any]) -> tuple[str, int, int]:
    """Simuloi koko ottelun Leg- tai Set-muodossa."""
    p_a_avg, p_a_cop, p_a_std = params['P_A_AVG'], params['P_A_COP'], params['P_A_STD']
    p_b_avg, p_b_cop, p_b_std = params['P_B_AVG'], params['P_B_COP'], params['P_B_STD']
    match_type = params['MATCH_TYPE']
    
    match_wins_a = 0
    match_wins_b = 0
    
    overall_starts_a = random.random() < 0.5 
    
    if match_type == "SET":
        target_sets = (params['N_SETS'] // 2) + 1
        target_legs_per_set = 3 
        
        starts_a_in_set = overall_starts_a
        
        while match_wins_a < target_sets and match_wins_b < target_sets:
            set_wins_a = 0
            set_wins_b = 0
            starts_a = starts_a_in_set 
            
            while set_wins_a < target_legs_per_set and set_wins_b < target_legs_per_set:
                leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
                if leg_winner == "A": set_wins_a += 1
                else: set_wins_b += 1
                starts_a = not starts_a 
                
            if set_wins_a == target_legs_per_set: match_wins_a += 1
            else: match_wins_b += 1
            
            starts_a_in_set = not starts_a_in_set 
                
        winner = "A" if match_wins_a == target_sets else "B"
        return winner, match_wins_a, match_wins_b

    else: # LEG (Leg-muoto)
        target_legs = (params['N_LEGS'] // 2) + 1
        starts_a = overall_starts_a
        
        while match_wins_a < target_legs and match_wins_b < target_legs:
            leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
            if leg_winner == "A": match_wins_a += 1
            else: match_wins_b += 1
            starts_a = not starts_a 
            
        winner = "A" if match_wins_a == target_legs else "B"
        return winner, match_wins_a, match_wins_b


# --- 4. Streamlit UI ja Logiikka ---

# Apufunktiot N/A arvojen käsittelyyn syötteissä
def get_float_val(data: Dict[str, Any], key: str, default: float) -> float:
    """Palauttaa float-arvon tai oletuksen, jos data on 'N/A'."""
    val = data.get(key)
    # Käsittele FDI:n tapaus, jossa se voi olla int/float
    if key == 'FDI' and isinstance(val, (int, float)):
        return float(val)
    return float(val) if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace('.', '', 1).isdigit()) else default

def get_int_val(data: Dict[str, Any], key: str, default: int) -> int:
    """Palauttaa int-arvon tai oletuksen, jos data on 'N/A'."""
    val = data.get(key)
    return int(val) if isinstance(val, (int, float)) else default


def main():
    st.title("🎯 Darts-simulaattori (PDC 96)")
    st.markdown("Valitse pelaajat ja ottelun muoto simuloidaksesi lopputulosta **Monte Carlo** -menetelmällä.")
    st.caption("HUOM: Simulaatio käyttää **muokattuja arvoja**. Ominaisuuskaudet ovat: **KAUSI 2025** (3 tikan keskiarvo), **COP** (Checkout %), **STD** (Heittojen hajonta), **FDI**, **F9A** (First 9 Average), **TWS KA** (Throw Win Start %) ja **RWS KA** (Receive Win Start %).")

    # Pelaajan valinta
    col1, col2 = st.columns(2)
    
    # Poistetaan listasta otsikot, jotta ne eivät näy valintalaatikossa
    player_options = [name for name in PLAYER_NAMES if not name.startswith("---") and not name.startswith("VALITSE PROFIILI")]
    
    # Etsi oletusarvot (jos niitä ei ole, valitaan ensimmäinen)
    default_a_index = player_options.index("Luke Littler (1)") if "Luke Littler (1)" in player_options else 0
    default_b_name = "Teemu Harju (FIN)" # Käytetään Teemua esimerkkinä
    default_b_index = player_options.index(default_b_name) if default_b_name in player_options else min(len(player_options) - 1, 1)
    
    with col1:
        st.subheader("Pelaaja A")
        player_a_name = st.selectbox("Valitse Profiili A", options=player_options, index=default_a_index)
        player_a_data = DEFAULT_PRESETS.get(player_a_name, DEFAULT_PRESETS["VALITSE PROFIILI"])
        
        # Alkuperäisten arvojen näyttö (vain infoa varten)
        st.markdown(f"**Valittu profiili: {player_a_name}**")
        st.info(
            f"**Alkuperäiset luvut:** KA: {player_a_data.get('KAUSI 2025', 95.0):.2f} | COP: {get_int_val(player_a_data, 'COP', 35)}% | STD: {player_a_data.get('STD', 18.0):.1f}"
        )

        st.markdown("#### Muokkaa Tilastoja A")
        
        # --- Interaktiiviset Syötteet A ---
        a_avg = st.number_input("KAUSI 2025 Average (3DA)", min_value=70.0, max_value=120.0, step=0.1, 
            value=get_float_val(player_a_data, 'KAUSI 2025', 95.0), key='a_avg')
        
        a_cop = st.number_input("Checkout % (COP) [0-100]", min_value=10, max_value=60, step=1, 
            value=get_int_val(player_a_data, 'COP', 35), key='a_cop')
        
        a_std = st.number_input("Heittojen hajonta (STD)", min_value=10.0, max_value=30.0, step=0.1, 
            value=get_float_val(player_a_data, 'STD', 18.0), key='a_std')

        a_f9a = st.number_input("First 9 Average (F9A)", min_value=70.0, max_value=120.0, step=0.1,
            value=get_float_val(player_a_data, 'F9A', 95.0), key='a_f9a')
        
        a_tws = st.number_input("TWS KA (Aloitus Voitto%)", min_value=20, max_value=100, step=1,
            value=get_int_val(player_a_data, 'TWS KA', 70), key='a_tws')
            
        a_rws = st.number_input("RWS KA (Vastaanotto Voitto%)", min_value=10, max_value=70, step=1,
            value=get_int_val(player_a_data, 'RWS KA', 40), key='a_rws')
        # --- Lopeta Syötteet A ---

    with col2:
        st.subheader("Pelaaja B")
        player_b_name = st.selectbox("Valitse Profiili B", options=player_options, index=default_b_index)
        player_b_data = DEFAULT_PRESETS.get(player_b_name, DEFAULT_PRESETS["VALITSE PROFIILI"])
        
        # Alkuperäisten arvojen näyttö (vain infoa varten)
        st.markdown(f"**Valittu profiili: {player_b_name}**")
        st.info(
            f"**Alkuperäiset luvut:** KA: {player_b_data.get('KAUSI 2025', 95.0):.2f} | COP: {get_int_val(player_b_data, 'COP', 35)}% | STD: {player_b_data.get('STD', 18.0):.1f}"
        )

        st.markdown("#### Muokkaa Tilastoja B")

        # --- Interaktiiviset Syötteet B ---
        b_avg = st.number_input("KAUSI 2025 Average (3DA)", min_value=70.0, max_value=120.0, step=0.1, 
            value=get_float_val(player_b_data, 'KAUSI 2025', 95.0), key='b_avg')
        
        b_cop = st.number_input("Checkout % (COP) [0-100]", min_value=10, max_value=60, step=1, 
            value=get_int_val(player_b_data, 'COP', 35), key='b_cop')
        
        b_std = st.number_input("Heittojen hajonta (STD)", min_value=10.0, max_value=30.0, step=0.1, 
            value=get_float_val(player_b_data, 'STD', 18.0), key='b_std')

        b_f9a = st.number_input("First 9 Average (F9A)", min_value=70.0, max_value=120.0, step=0.1,
            value=get_float_val(player_b_data, 'F9A', 95.0), key='b_f9a')

        b_tws = st.number_input("TWS KA (Aloitus Voitto%)", min_value=20, max_value=100, step=1,
            value=get_int_val(player_b_data, 'TWS KA', 70), key='b_tws')
            
        b_rws = st.number_input("RWS KA (Vastaanotto Voitto%)", min_value=10, max_value=70, step=1,
            value=get_int_val(player_b_data, 'RWS KA', 40), key='b_rws')
        # --- Lopeta Syötteet B ---


    st.markdown("---")
    
    # Ottelun asetukset
    col3, col4, col5 = st.columns(3)
    with col3:
        match_type = st.radio("Ottelun tyyppi", ["SET", "LEG"], index=0, horizontal=True)
        
    with col4:
        if match_type == "SET":
            default_sets = 5
            num_legs_or_sets = st.number_input(f"Paras N:stä ({match_type}it)", min_value=3, step=2, value=default_sets)
            st.caption(f"Voittoon tarvitaan { (num_legs_or_sets // 2) + 1 } Set-voittoa.")
        else:
            default_legs = 11
            num_legs_or_sets = st.number_input(f"Paras N:stä ({match_type}iä)", min_value=3, step=2, value=default_legs)
            st.caption(f"Voittoon tarvitaan { (num_legs_or_sets // 2) + 1 } Leg-voittoa.")
            
    with col5:
        num_simulations = st.number_input("Simulointien määrä (kpl)", min_value=100, max_value=50000, step=100, value=10000)

    # Simulaatiopainike
    st.markdown("---")
    if st.button(f"Käynnistä {num_simulations} simulaatiota 🚀", type="primary"):
        
        if player_a_name == player_b_name:
            st.error("Pelaajat eivät voi olla samoja.")
            return

        if not 0 <= a_cop <= 100 or not 0 <= b_cop <= 100:
            st.error("COP (Checkout %) on annettava prosentteina 0-100 väliltä.")
            return
            
        # Valmistellaan parametrit TÄRKEÄÄ: Käytetään syötekenttien arvoja
        params = {
            'P_A_AVG': a_avg,
            'P_A_COP': a_cop / 100.0,
            'P_A_STD': a_std,
            'P_B_AVG': b_avg,
            'P_B_COP': b_cop / 100.0,
            'P_B_STD': b_std,
            'N_SIMULATIONS': num_simulations,
            'MATCH_TYPE': match_type,
            'N_LEGS': num_legs_or_sets if match_type == 'LEG' else None,
            'N_SETS': num_legs_or_sets if match_type == 'SET' else None
        }

        # Simulaation suoritus
        a_wins = 0
        b_wins = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(num_simulations):
            # Käytetään dynaamisia average/std/cop-arvoja
            winner, _, _ = simulate_match(params)
            if winner == "A":
                a_wins += 1
            else:
                b_wins += 1
                
            progress = (i + 1) / num_simulations
            progress_bar.progress(progress)
            
            if (i + 1) % 1000 == 0:
                status_text.text(f"Simuloidaan... {i + 1}/{num_simulations} suoritettu.")
                
        progress_bar.empty()
        status_text.empty()
        
        # --- Tulosten esitys ---
        total_wins = a_wins + b_wins
        prob_a = a_wins / total_wins
        prob_b = b_wins / total_wins

        st.markdown("## Simulaation Tulos 📊")
        st.write(f"Suoritettujen simulaatioiden määrä: **{num_simulations}**")

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(f"**{player_a_name}** voitto-osuus", f"{prob_a * 100:.2f} %", delta=f"{a_wins} voittoa")
        with col_res2:
            st.metric(f"**{player_b_name}** voitto-osuus", f"{prob_b * 100:.2f} %", delta=f"{b_wins} voittoa")

        # Visualisointi
        df_results = pd.DataFrame({
            'Pelaaja': [player_a_name, player_b_name],
            'Voitto-%': [prob_a, prob_b]
        })

        chart = alt.Chart(df_results).mark_bar().encode(
            x=alt.X('Pelaaja:N', axis=None),
            y=alt.Y('Voitto-%:Q', axis=alt.Axis(format='.0%', title='Voitto-%')),
            color='Pelaaja:N',
            tooltip=['Pelaaja', alt.Tooltip('Voitto-%', format='.2%')]
        ).properties(
            title=f"Ottelun Voittotodennäköisyys ({match_type}, Paras {num_legs_or_sets} )"
        )
        st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
