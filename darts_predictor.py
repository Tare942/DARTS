import streamlit as st
import numpy as np
import random
import pandas as pd # Lisätty DataFramen käyttöön
import altair as alt # Lisätty kaavion korjaamiseen
from typing import Dict, Any

# --- Streamlit-sivun asetukset (Tumma teema oletuksena) ---
st.set_page_config(
    page_title="🎯 Darts-simulaattori (PDC 96)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Optimal Checkout Taulukko & Apumuuttujat ---
# Tässä osiossa ei ole toiminnallisia muutoksia
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

# --- 2. Pelaajaprofiilit (SISÄLTÄÄ TWS ja RWS tiedot) ---
# TWS = Throw Win % (Voitto% aloittaessa), RWS = Receive Win % (Voitto% heitettäessä toisena)
DEFAULT_PRESETS = {
    "VALITSE PROFIILI": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": 96.5, "TWS": 70, "RWS": 40},
    "--- PDC TOP 32 (Sijoitetut) ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS": "N/A", "RWS": "N/A"},
    
    # 1. Neljännes 
    "Luke Littler (1)": {"KA": 100.96, "KAUSI 2025": 100.96, "COP": 41, "STD": 16, "FDI": 72.0, "F9A": 103.4, "TWS": 85, "RWS": 52},
    "Joe Cullen (32)": {"KA": 94.20, "KAUSI 2025": 94.5, "COP": 33, "STD": 20, "FDI": 59.0, "F9A": 96.5, "TWS": 70, "RWS": 38},
    "Damon Heta (16)": {"KA": 94.81, "KAUSI 2025": 94.81, "COP": 39, "STD": 20, "FDI": 59.6, "F9A": 97.0, "TWS": 72, "RWS": 39},
    "Rob Cross (17)": {"KA": 95.75, "KAUSI 2025": 95.75, "COP": 41, "STD": 20, "FDI": 61.5, "F9A": 97.8, "TWS": 73, "RWS": 41},
    "Chris Dobey (8)": {"KA": 96.76, "KAUSI 2025": 96.76, "COP": 34, "STD": 19, "FDI": 63.5, "F9A": 99.0, "TWS": 77, "RWS": 41},
    "Luke Woodhouse (25)": {"KA": 93.50, "KAUSI 2025": 93.7, "COP": 32, "STD": 21, "FDI": 57.4, "F9A": 95.2, "TWS": 68, "RWS": 36},
    "Gerwyn Price (9)": {"KA": 97.75, "KAUSI 2025": 97.75, "COP": 40, "STD": 19, "FDI": 65.5, "F9A": 100.0, "TWS": 80, "RWS": 45},
    "Ryan Joyce (24)": {"KA": 93.80, "KAUSI 2025": 94.0, "COP": 32, "STD": 21, "FDI": 58.0, "F9A": 95.5, "TWS": 68, "RWS": 37},
    
    # 2. Neljännes
    "Stephen Bunting (4)": {"KA": 98.04, "KAUSI 2025": 98.04, "COP": 40, "STD": 18, "FDI": 66.1, "F9A": 100.3, "TWS": 81, "RWS": 45},
    "Dirk van Duijvenbode (29)": {"KA": 94.00, "KAUSI 2025": 93.5, "COP": 36, "STD": 21, "FDI": 57.0, "F9A": 95.0, "TWS": 68, "RWS": 38},
    "Martin Schindler (13)": {"KA": 95.50, "KAUSI 2025": 95.8, "COP": 33, "STD": 20, "FDI": 61.6, "F9A": 98.0, "TWS": 74, "RWS": 40},
    "Ryan Searle (20)": {"KA": 95.76, "KAUSI 2025": 95.76, "COP": 33, "STD": 20, "FDI": 61.5, "F9A": 97.8, "TWS": 73, "RWS": 40},
    "Jonny Clayton (5)": {"KA": 96.30, "KAUSI 2025": 96.30, "COP": 34, "STD": 20, "FDI": 62.6, "F9A": 98.3, "TWS": 75, "RWS": 41},
    "Michael Smith (28)": {"KA": 94.60, "KAUSI 2025": 95.5, "COP": 34, "STD": 19, "FDI": 61.0, "F9A": 97.5, "TWS": 73, "RWS": 40}, 
    "Ross Smith (12)": {"KA": 96.50, "KAUSI 2025": 96.50, "COP": 38, "STD": 20, "FDI": 63.0, "F9A": 98.7, "TWS": 76, "RWS": 42},
    "Dave Chisnall (21)": {"KA": 94.50, "KAUSI 2025": 95.0, "COP": 34, "STD": 20, "FDI": 60.0, "F9A": 97.0, "TWS": 72, "RWS": 39},

    # 3. Neljännes
    "Luke Humphries (2)": {"KA": 98.50, "KAUSI 2025": 98.50, "COP": 37, "STD": 17, "FDI": 67.0, "F9A": 101.0, "TWS": 82, "RWS": 46},
    "Wessel Nijman (31)": {"KA": 93.00, "KAUSI 2025": 93.2, "COP": 31, "STD": 22, "FDI": 56.4, "F9A": 94.7, "TWS": 66, "RWS": 35},
    "Nathan Aspinall (15)": {"KA": 95.64, "KAUSI 2025": 95.64, "COP": 37, "STD": 20, "FDI": 61.3, "F9A": 97.7, "TWS": 73, "RWS": 40},
    "Mike De Decker (18)": {"KA": 95.0, "KAUSI 2025": 94.5, "COP": 33, "STD": 20, "FDI": 59.0, "F9A": 96.5, "TWS": 70, "RWS": 38},
    "James Wade (7)": {"KA": 94.79, "KAUSI 2025": 94.0, "COP": 38, "STD": 20, "FDI": 58.0, "F9A": 96.0, "TWS": 69, "RWS": 39},
    "Cameron Menzies (26)": {"KA": 93.30, "KAUSI 2025": 93.5, "COP": 31, "STD": 22, "FDI": 57.0, "F9A": 95.0, "TWS": 66, "RWS": 36},
    "Gian van Veen (10)": {"KA": 97.91, "KAUSI 2025": 97.91, "COP": 33, "STD": 19, "FDI": 65.8, "F9A": 100.2, "TWS": 80, "RWS": 45},
    "Dimitri Van den Bergh (23)": {"KA": 94.20, "KAUSI 2025": 93.8, "COP": 35, "STD": 20, "FDI": 57.6, "F9A": 95.5, "TWS": 69, "RWS": 37},
    
    # 4. Neljännes
    "Michael van Gerwen (3)": {"KA": 97.28, "KAUSI 2025": 97.28, "COP": 42, "STD": 18, "FDI": 64.6, "F9A": 99.5, "TWS": 81, "RWS": 46},
    "Peter Wright (30)": {"KA": 93.50, "KAUSI 2025": 94.0, "COP": 35, "STD": 20, "FDI": 58.0, "F9A": 96.0, "TWS": 69, "RWS": 38}, 
    "Gary Anderson (14)": {"KA": 97.41, "KAUSI 2025": 97.41, "COP": 35, "STD": 17, "FDI": 64.8, "F9A": 99.7, "TWS": 79, "RWS": 44},
    "Jermaine Wattimena (19)": {"KA": 94.87, "KAUSI 2025": 95.0, "COP": 32, "STD": 21, "FDI": 60.0, "F9A": 97.0, "TWS": 71, "RWS": 39},
    "Danny Noppert (6)": {"KA": 94.79, "KAUSI 2025": 95.0, "COP": 37, "STD": 20, "FDI": 60.0, "F9A": 97.0, "TWS": 72, "RWS": 40},
    "Ritchie Edhouse (27)": {"KA": 93.20, "KAUSI 2025": 93.0, "COP": 32, "STD": 22, "FDI": 56.0, "F9A": 94.5, "TWS": 65, "RWS": 35},
    "Josh Rock (11)": {"KA": 98.10, "KAUSI 2025": 98.10, "COP": 37, "STD": 18, "FDI": 66.2, "F9A": 100.4, "TWS": 81, "RWS": 45},
    "Daryl Gurney (22)": {"KA": 94.00, "KAUSI 2025": 94.2, "COP": 33, "STD": 21, "FDI": 58.4, "F9A": 96.0, "TWS": 69, "RWS": 37},

    "--- SIJOITTAMATTOMAT & KVALIFIOIJAT ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS": "N/A", "RWS": "N/A"},
    
    # Esimerkkejä muista (R1):
    "Darius Labanauskas (LTU)": {"KA": 89.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 21, "FDI": 50.0, "F9A": 91.5, "TWS": 60, "RWS": 30},
    "Mensur Suljovic (AUT)": {"KA": 91.0, "KAUSI 2025": 90.5, "COP": 36, "STD": 20, "FDI": 50.5, "F9A": 92.0, "TWS": 63, "RWS": 33},
    "Raymond van Barneveld (NED)": {"KA": 92.5, "KAUSI 2025": 92.0, "COP": 34, "STD": 19, "FDI": 52.0, "F9A": 93.8, "TWS": 66, "RWS": 34},
    "Krzysztof Ratajski (POL)": {"KA": 92.0, "KAUSI 2025": 92.5, "COP": 34, "STD": 20, "FDI": 52.5, "F9A": 94.3, "TWS": 66, "RWS": 35},
    "Fallon Sherrock (ENG)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 32, "STD": 21, "FDI": 48.5, "F9A": 89.5, "TWS": 57, "RWS": 29},
    "Teemu Harju (FIN)": {"KA": 87.0, "KAUSI 2025": 88.5, "COP": 25, "STD": 24, "FDI": 48.5, "F9A": 89.5, "TWS": 55, "RWS": 28},
    
    "--- LISÄPROFIILIT ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS": "N/A", "RWS": "N/A"},
    "Epätasainen (Aloittelija)": {"KA": 80.0, "KAUSI 2025": 80.0, "COP": 28, "STD": 25, "FDI": 30.0, "F9A": 81.0, "TWS": 45, "RWS": 25},
    "Hyvä Harrastaja": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 20, "FDI": 50.0, "F9A": 91.5, "TWS": 65, "RWS": 35}
}
PLAYER_NAMES = list(DEFAULT_PRESETS.keys())

# --- 3. Simulaatiofunktiot (ei muutoksia) ---
# Simulointifunktiot (get_hit_score, simulate_score, attempt_checkout, 
# simulate_leg, simulate_match) pysyvät samoina

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

    # Käytetään COP-prosenttia (esim. 0.35) voittoon
    if random.random() < cop:
        return 0, True
    else:
        # Jos ei osu ulos, simuloidaan osumista reitillä
        route = CHECKOUT_MAP.get(current_score, ["S20", "S20", "S20"]) 
        # Tässä käytetään hyvin yksinkertaistettua mallia: vain osa reitin arvoista saadaan pisteiksi
        points_to_target = sum(get_hit_score(t) for t in route if not t.startswith('D'))
        score_taken = int(points_to_target * random.uniform(0.5, 0.9))
        
        new_score = current_score - score_taken
        
        if new_score < 2:
            # Jos bustaa, palautetaan alkuperäinen tulos
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
    
    # Random initial throw for the match/first set
    overall_starts_a = random.random() < 0.5 
    
    if match_type == "SET":
        target_sets = (params['N_SETS'] // 2) + 1
        target_legs_per_set = 3 
        
        starts_a_in_set = overall_starts_a
        
        while match_wins_a < target_sets and match_wins_b < target_sets:
            set_wins_a = 0
            set_wins_b = 0
            starts_a = starts_a_in_set 
            
            # Legien simulaatio setissä
            while set_wins_a < target_legs_per_set and set_wins_b < target_legs_per_set:
                leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
                if leg_winner == "A": set_wins_a += 1
                else: set_wins_b += 1
                starts_a = not starts_a 
                
            if set_wins_a == target_legs_per_set: match_wins_a += 1
            else: match_wins_b += 1
            
            # Seuraavan setin aloittaja vaihtuu
            starts_a_in_set = not starts_a_in_set 
                
        winner = "A" if match_wins_a == target_sets else "B"
        return winner, match_wins_a, match_wins_b

    else: # LEG (Leg-muoto)
        target_legs = (params['N_LEGS'] // 2) + 1
        starts_a = overall_starts_a
        
        # Legien simulaatio
        while match_wins_a < target_legs and match_wins_b < target_legs:
            leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
            if leg_winner == "A": match_wins_a += 1
            else: match_wins_b += 1
            starts_a = not starts_a # Aloittaja vaihtuu joka legissä
            
        winner = "A" if match_wins_a == target_legs else "B"
        return winner, match_wins_a, match_wins_b


# --- 4. Streamlit UI ja Logiikka ---

def main():
    st.title("🎯 Darts-simulaattori (PDC 96)")
    st.markdown("Valitse pelaajat ja ottelun muoto simuloidaksesi lopputulosta **Monte Carlo** -menetelmällä.")
    st.caption("HUOM: Tilastot (KAUSI 2025, COP, STD) ovat lähellä todellisia lukuja. **FDI, F9A, TWS ja RWS ovat arvioituja.**")

    # Pelaajan valinta
    col1, col2 = st.columns(2)
    
    player_options = [name for name in PLAYER_NAMES if not name.startswith("---")]
    
    # Käytetään oletuksena päivitettyjä Littleriä ja MvG:tä
    default_a_index = player_options.index("Luke Littler (1)") if "Luke Littler (1)" in player_options else 0
    default_b_index = player_options.index("Michael van Gerwen (3)") if "Michael van Gerwen (3)" in player_options else 0
    
    with col1:
        st.subheader("Pelaaja A (Musta hevonen)")
        player_a_name = st.selectbox("Valitse Pelaaja A", options=player_options, index=default_a_index)
        st.markdown(f"**Valittu:** **{player_a_name}**")
        
        player_a_data = DEFAULT_PRESETS.get(player_a_name, DEFAULT_PRESETS["VALITSE PROFIILI"])
        
        # Formatoidaan numerot, jos ne eivät ole "N/A"
        fdi_a = player_a_data['FDI'] if isinstance(player_a_data['FDI'], str) else f"{player_a_data['FDI']:.1f}"
        f9a_a = player_a_data['F9A'] if isinstance(player_a_data['F9A'], str) else f"{player_a_data['F9A']:.1f}"
        tws_a = player_a_data['TWS'] if isinstance(player_a_data['TWS'], str) else f"{player_a_data['TWS']}%"
        rws_a = player_a_data['RWS'] if isinstance(player_a_data['RWS'], str) else f"{player_a_data['RWS']}%"
        
        st.info(
            f"**📊 Keskiarvo (3DA):** {player_a_data['KAUSI 2025']:.2f} | **F9A:** {f9a_a} | **COP:** {player_a_data['COP']}% | **STD:** {player_a_data['STD']:.1f}\n\n"
            f"**✅ TWS (Aloitus Voitto%):** {tws_a} | **🔄 RWS (Vastaanotto Voitto%):** {rws_a} | **FDI:** {fdi_a}"
        )

    with col2:
        st.subheader("Pelaaja B (Haastaja)")
        player_b_name = st.selectbox("Valitse Pelaaja B", options=player_options, index=default_b_index)
        st.markdown(f"**Valittu:** **{player_b_name}**")
        
        player_b_data = DEFAULT_PRESETS.get(player_b_name, DEFAULT_PRESETS["VALITSE PROFIILI"])
        
        # Formatoidaan numerot, jos ne eivät ole "N/A"
        fdi_b = player_b_data['FDI'] if isinstance(player_b_data['FDI'], str) else f"{player_b_data['FDI']:.1f}"
        f9a_b = player_b_data['F9A'] if isinstance(player_b_data['F9A'], str) else f"{player_b_data['F9A']:.1f}"
        tws_b = player_b_data['TWS'] if isinstance(player_b_data['TWS'], str) else f"{player_b_data['TWS']}%"
        rws_b = player_b_data['RWS'] if isinstance(player_b_data['RWS'], str) else f"{player_b_data['RWS']}%"
        
        st.info(
            f"**📊 Keskiarvo (3DA):** {player_b_data['KAUSI 2025']:.2f} | **F9A:** {f9a_b} | **COP:** {player_b_data['COP']}% | **STD:** {player_b_data['STD']:.1f}\n\n"
            f"**✅ TWS (Aloitus Voitto%):** {tws_b} | **🔄 RWS (Vastaanotto Voitto%):** {rws_b} | **FDI:** {fdi_b}"
        )

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

        # Valmistellaan parametrit (simulaatio käyttää vain 3DA, COP ja STD)
        params = {
            'P_A_AVG': player_a_data['KAUSI 2025'],
            'P_A_COP': player_a_data['COP'] / 100.0,
            'P_A_STD': player_a_data['STD'],
            'P_B_AVG': player_b_data['KAUSI 2025'],
            'P_B_COP': player_b_data['COP'] / 100.0,
            'P_B_STD': player_b_data['STD'],
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
            winner, _, _ = simulate_match(params)
            if winner == "A":
                a_wins += 1
            else:
                b_wins += 1
                
            progress = (i + 1) / num_simulations
            progress_bar.progress(progress)
            
            if (i + 1) % 100 == 0:
                status_text.text(f"Simuloidaan... {i + 1}/{num_simulations} suoritettu.")
                
        progress_bar.empty()
        status_text.empty()
        
        # --- Tulosten esitys ---
        total_wins = a_wins + b_wins
        prob_a = a_wins / total_wins
        prob_b = b_wins / total_wins

        st.markdown("### ✨ Tulokset ja Ennusteet")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        # Voittotodennäköisyys
        with col_res1:
            winner_name = player_a_name if prob_a > prob_b else player_b_name
            st.metric(label=f"🏆 Todennäköisin voittaja", value=winner_name, delta_color="off")
        
        # Pelaaja A
        with col_res2:
            st.metric(
                label=f"**{player_a_name}** voittotodennäköisyys",
                value=f"{prob_a:.1%}",
                delta=f"{a_wins} voittoa",
                delta_color="normal"
            )
            
        # Pelaaja B
        with col_res3:
            st.metric(
                label=f"**{player_b_name}** voittotodennäköisyys",
                value=f"{prob_b:.1%}",
                delta=f"{b_wins} voittoa",
                delta_color="normal"
            )
        
        st.markdown("---")
        st.markdown("#### Voittotodennäköisyyden jakautuminen")
        
        # KORJATTU Osa: Käytetään Altairia virheen StreamlitColorLengthError välttämiseksi
        data_df = pd.DataFrame({
            'Pelaaja': [player_a_name, player_b_name],
            'Voittotodennäköisyys': [prob_a, prob_b]
        })
        
        chart = alt.Chart(data_df).mark_bar().encode(
            x=alt.X('Pelaaja:N', sort=None),
            y=alt.Y('Voittotodennäköisyys:Q', axis=alt.Axis(format='.0%'), title='Voittotodennäköisyys'),
            # Värit Pelaaja-sarakkeen mukaan:
            color=alt.Color('Pelaaja:N', scale=alt.Scale(domain=[player_a_name, player_b_name], range=['#007bff', '#dc3545']), legend=None),
            tooltip=['Pelaaja', alt.Tooltip('Voittotodennäköisyys', format='.1%')]
        ).properties(
            title="Ottelun ennuste"
        )
        st.altair_chart(chart, use_container_width=True)

# Koodin suoritus
if __name__ == "__main__":
    main()
