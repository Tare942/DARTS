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

# --- 2. Pelaajaprofiilit (TÄYDENNETTY 96 TODENNAKÖISELLÄ NIMELLÄ) ---
DEFAULT_PRESETS = {
    "VALITSE PROFIILI": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": 96.5, "TWS KA": 70, "RWS KA": 40},
    "--- PDC TOP 32 SIJOITETUT (2025) ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    
    # Kärki (Esimerkki tarkalla datalla)
    "Luke Littler (1)": {"KA": 100.96, "KAUSI 2025": 100.96, "COP": 44, "STD": 16, "FDI": 72.0, "F9A": 103.4, "TWS KA": 88, "RWS KA": 55},
    "Luke Humphries (2)": {"KA": 98.50, "KAUSI 2025": 98.50, "COP": 42, "STD": 17, "FDI": 67.0, "F9A": 101.0, "TWS KA": 84, "RWS KA": 48},
    "Michael van Gerwen (3)": {"KA": 97.28, "KAUSI 2025": 97.28, "COP": 43, "STD": 18, "FDI": 64.6, "F9A": 99.5, "TWS KA": 81, "RWS KA": 46},
    "Stephen Bunting (4)": {"KA": 98.04, "KAUSI 2025": 98.04, "COP": 40, "STD": 18, "FDI": 66.1, "F9A": 100.3, "TWS KA": 81, "RWS KA": 45},
    "Jonny Clayton (5)": {"KA": 96.30, "KAUSI 2025": 96.30, "COP": 37, "STD": 20, "FDI": 62.6, "F9A": 98.3, "TWS KA": 75, "RWS KA": 41},
    "Danny Noppert (6)": {"KA": 94.79, "KAUSI 2025": 94.79, "COP": 37, "STD": 20, "FDI": 60.0, "F9A": 97.0, "TWS KA": 72, "RWS KA": 40},
    "James Wade (7)": {"KA": 94.79, "KAUSI 2025": 94.79, "COP": 39, "STD": 20, "FDI": 58.0, "F9A": 96.0, "TWS KA": 69, "RWS KA": 39},
    "Chris Dobey (8)": {"KA": 96.76, "KAUSI 2025": 96.76, "COP": 38, "STD": 19, "FDI": 63.5, "F9A": 99.0, "TWS KA": 77, "RWS KA": 41},
    "Gerwyn Price (9)": {"KA": 97.75, "KAUSI 2025": 97.75, "COP": 40, "STD": 19, "FDI": 65.5, "F9A": 100.0, "TWS KA": 80, "RWS KA": 45},
    "Gian van Veen (10)": {"KA": 97.91, "KAUSI 2025": 97.91, "COP": 38, "STD": 19, "FDI": 65.8, "F9A": 100.2, "TWS KA": 80, "RWS KA": 45},
    "Josh Rock (11)": {"KA": 98.10, "KAUSI 2025": 98.10, "COP": 39, "STD": 18, "FDI": 66.2, "F9A": 100.4, "TWS KA": 81, "RWS KA": 45},
    "Ross Smith (12)": {"KA": 96.50, "KAUSI 2025": 96.50, "COP": 39, "STD": 20, "FDI": 63.0, "F9A": 98.7, "TWS KA": 76, "RWS KA": 42},
    "Martin Schindler (13)": {"KA": 94.13, "KAUSI 2025": 94.13, "COP": 35, "STD": 20, "FDI": 61.6, "F9A": 98.0, "TWS KA": 74, "RWS KA": 40},
    "Gary Anderson (14)": {"KA": 97.41, "KAUSI 2025": 97.41, "COP": 38, "STD": 17, "FDI": 64.8, "F9A": 99.7, "TWS KA": 79, "RWS KA": 44},
    "Nathan Aspinall (15)": {"KA": 95.64, "KAUSI 2025": 95.64, "COP": 37, "STD": 20, "FDI": 61.3, "F9A": 97.7, "TWS KA": 73, "RWS KA": 40},
    "Damon Heta (16)": {"KA": 94.81, "KAUSI 2025": 94.81, "COP": 40, "STD": 20, "FDI": 59.6, "F9A": 97.0, "TWS KA": 72, "RWS KA": 39},
    "Rob Cross (17)": {"KA": 95.75, "KAUSI 2025": 95.75, "COP": 41, "STD": 20, "FDI": 61.5, "F9A": 97.8, "TWS KA": 73, "RWS KA": 41},
    "Mike De Decker (18)": {"KA": 93.92, "KAUSI 2025": 93.92, "COP": 33, "STD": 20, "FDI": 59.0, "F9A": 96.5, "TWS KA": 70, "RWS KA": 38},
    "Jermaine Wattimena (19)": {"KA": 94.87, "KAUSI 2025": 94.87, "COP": 32, "STD": 21, "FDI": 60.0, "F9A": 97.0, "TWS KA": 71, "RWS KA": 39},
    "Ryan Searle (20)": {"KA": 95.76, "KAUSI 2025": 95.76, "COP": 33, "STD": 20, "FDI": 61.5, "F9A": 97.8, "TWS KA": 73, "RWS KA": 40},
    "Dave Chisnall (21)": {"KA": 91.86, "KAUSI 2025": 91.86, "COP": 34, "STD": 20, "FDI": 60.0, "F9A": 97.0, "TWS KA": 72, "RWS KA": 39},
    "Daryl Gurney (22)": {"KA": 93.23, "KAUSI 2025": 93.23, "COP": 33, "STD": 21, "FDI": 58.4, "F9A": 96.0, "TWS KA": 69, "RWS KA": 37},
    "Dimitri Van den Bergh (23)": {"KA": 94.20, "KAUSI 2025": 93.8, "COP": 35, "STD": 20, "FDI": 57.6, "F9A": 95.5, "TWS KA": 69, "RWS KA": 37},
    "Ryan Joyce (24)": {"KA": 93.02, "KAUSI 2025": 93.02, "COP": 32, "STD": 21, "FDI": 58.0, "F9A": 95.5, "TWS KA": 68, "RWS KA": 37},
    "Luke Woodhouse (25)": {"KA": 92.70, "KAUSI 2025": 92.70, "COP": 32, "STD": 21, "FDI": 57.4, "F9A": 95.2, "TWS KA": 68, "RWS KA": 36},
    "Cameron Menzies (26)": {"KA": 92.65, "KAUSI 2025": 92.65, "COP": 31, "STD": 22, "FDI": 57.0, "F9A": 95.0, "TWS KA": 66, "RWS KA": 36},
    "Ritchie Edhouse (27)": {"KA": 93.20, "KAUSI 2025": 93.0, "COP": 32, "STD": 22, "FDI": 56.0, "F9A": 94.5, "TWS KA": 65, "RWS KA": 35},
    "Michael Smith (28)": {"KA": 92.74, "KAUSI 2025": 92.74, "COP": 34, "STD": 19, "FDI": 61.0, "F9A": 97.5, "TWS KA": 73, "RWS KA": 40},
    "Dirk van Duijvenbode (29)": {"KA": 96.53, "KAUSI 2025": 96.53, "COP": 36, "STD": 20, "FDI": 57.0, "F9A": 98.0, "TWS KA": 70, "RWS KA": 38},
    "Peter Wright (30)": {"KA": 92.41, "KAUSI 2025": 92.41, "COP": 35, "STD": 20, "FDI": 58.0, "F9A": 96.0, "TWS KA": 69, "RWS KA": 38},
    "Wessel Nijman (31)": {"KA": 95.86, "KAUSI 2025": 95.86, "COP": 34, "STD": 21, "FDI": 56.4, "F9A": 94.7, "TWS KA": 66, "RWS KA": 35},
    "Joe Cullen (32)": {"KA": 91.88, "KAUSI 2025": 91.88, "COP": 33, "STD": 20, "FDI": 59.0, "F9A": 96.5, "TWS KA": 70, "RWS KA": 38},

    # --- PDC Pro Tour/European Tour karsijat (33-64) - STATS PLACEHOLDER ---
    "--- PRO TOUR KVALIFIOIJAT (PDC Rank 33-64) ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    
    # Korvaa Q A-Taso 1-8 (Avg 93.0 - 91.6)
    "Raymond van Barneveld (33)": {"KA": 93.0, "KAUSI 2025": 93.0, "COP": 35, "STD": 20, "FDI": 59.0, "F9A": 96.0, "TWS KA": 69, "RWS KA": 38},
    "Brendan Dolan (34)": {"KA": 92.8, "KAUSI 2025": 92.8, "COP": 34, "STD": 20, "FDI": 58.5, "F9A": 95.5, "TWS KA": 68, "RWS KA": 37},
    "Jeffrey de Zwaan (35)": {"KA": 92.6, "KAUSI 2025": 92.6, "COP": 33, "STD": 21, "FDI": 58.0, "F9A": 95.0, "TWS KA": 67, "RWS KA": 37},
    "Karel Sedlacek (36)": {"KA": 92.4, "KAUSI 2025": 92.4, "COP": 35, "STD": 20, "FDI": 59.5, "F9A": 96.2, "TWS KA": 70, "RWS KA": 38},
    "Steve Beaton (37)": {"KA": 92.2, "KAUSI 2025": 92.2, "COP": 34, "STD": 21, "FDI": 57.5, "F9A": 94.8, "TWS KA": 66, "RWS KA": 36},
    "Mickey Mansell (38)": {"KA": 92.0, "KAUSI 2025": 92.0, "COP": 36, "STD": 19, "FDI": 60.0, "F9A": 97.0, "TWS KA": 71, "RWS KA": 39},
    "Alan Soutar (39)": {"KA": 91.8, "KAUSI 2025": 91.8, "COP": 33, "STD": 21, "FDI": 57.0, "F9A": 94.5, "TWS KA": 65, "RWS KA": 35},
    "Jitse Van der Wal (40)": {"KA": 91.6, "KAUSI 2025": 91.6, "COP": 34, "STD": 20, "FDI": 58.8, "F9A": 95.8, "TWS KA": 69, "RWS KA": 37},
    
    # Korvaa Q B-Taso 9-16 (Avg 91.0 - 89.6)
    "Rowby-John Rodriguez (41)": {"KA": 91.0, "KAUSI 2025": 91.0, "COP": 35, "STD": 21, "FDI": 57.0, "F9A": 94.0, "TWS KA": 64, "RWS KA": 35},
    "Florian Hempel (42)": {"KA": 90.8, "KAUSI 2025": 90.8, "COP": 33, "STD": 22, "FDI": 56.5, "F9A": 93.5, "TWS KA": 63, "RWS KA": 34},
    "Jelle Klaasen (43)": {"KA": 90.6, "KAUSI 2025": 90.6, "COP": 34, "STD": 21, "FDI": 57.5, "F9A": 94.2, "TWS KA": 65, "RWS KA": 35},
    "Radek Szaganski (44)": {"KA": 90.4, "KAUSI 2025": 90.4, "COP": 32, "STD": 22, "FDI": 56.0, "F9A": 93.0, "TWS KA": 62, "RWS KA": 33},
    "Darius Labanauskas (45)": {"KA": 90.2, "KAUSI 2025": 90.2, "COP": 35, "STD": 20, "FDI": 58.0, "F9A": 95.0, "TWS KA": 68, "RWS KA": 37},
    "Jules van Dongen (46)": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 21, "FDI": 56.8, "F9A": 93.7, "TWS KA": 64, "RWS KA": 34},
    "Boris Krcmar (47)": {"KA": 89.8, "KAUSI 2025": 89.8, "COP": 34, "STD": 21, "FDI": 57.2, "F9A": 94.0, "TWS KA": 65, "RWS KA": 35},
    "Keane Barry (48)": {"KA": 89.6, "KAUSI 2025": 89.6, "COP": 32, "STD": 22, "FDI": 55.5, "F9A": 92.5, "TWS KA": 61, "RWS KA": 32},

    # Korvaa Q C-Taso 17-24 (Avg 89.0 - 87.6)
    "Vincent van der Voort (49)": {"KA": 89.0, "KAUSI 2025": 89.0, "COP": 34, "STD": 22, "FDI": 56.0, "F9A": 93.0, "TWS KA": 63, "RWS KA": 34},
    "J. Huybrechts (50)": {"KA": 88.8, "KAUSI 2025": 88.8, "COP": 32, "STD": 23, "FDI": 54.5, "F9A": 91.5, "TWS KA": 60, "RWS KA": 31},
    "Danny Knoppert (51)": {"KA": 88.6, "KAUSI 2025": 88.6, "COP": 33, "STD": 22, "FDI": 55.0, "F9A": 92.0, "TWS KA": 61, "RWS KA": 32},
    "Kevin Doets (52)": {"KA": 88.4, "KAUSI 2025": 88.4, "COP": 31, "STD": 23, "FDI": 54.0, "F9A": 91.0, "TWS KA": 59, "RWS KA": 30},
    "Daryl Gurney Jnr (53)": {"KA": 88.2, "KAUSI 2025": 88.2, "COP": 34, "STD": 21, "FDI": 55.5, "F9A": 92.5, "TWS KA": 62, "RWS KA": 33},
    "Jeffrey Sparidaans (54)": {"KA": 88.0, "KAUSI 2025": 88.0, "COP": 32, "STD": 22, "FDI": 54.8, "F9A": 91.7, "TWS KA": 60, "RWS KA": 31},
    "Scott Williams (55)": {"KA": 87.8, "KAUSI 2025": 87.8, "COP": 33, "STD": 22, "FDI": 55.2, "F9A": 92.2, "TWS KA": 61, "RWS KA": 32},
    "Adam Gawlas (56)": {"KA": 87.6, "KAUSI 2025": 87.6, "COP": 31, "STD": 23, "FDI": 53.5, "F9A": 90.5, "TWS KA": 58, "RWS KA": 29},

    # Korvaa Q D-Taso 25-32 (Avg 87.0 - 85.6)
    "Danny Baggish (57)": {"KA": 87.0, "KAUSI 2025": 87.0, "COP": 32, "STD": 23, "FDI": 54.0, "F9A": 91.0, "TWS KA": 59, "RWS KA": 30},
    "Ian White (58)": {"KA": 86.8, "KAUSI 2025": 86.8, "COP": 30, "STD": 24, "FDI": 52.5, "F9A": 89.5, "TWS KA": 56, "RWS KA": 28},
    "George Killington (59)": {"KA": 86.6, "KAUSI 2025": 86.6, "COP": 31, "STD": 23, "FDI": 53.0, "F9A": 90.0, "TWS KA": 57, "RWS KA": 29},
    "Jimmy Hendriks (60)": {"KA": 86.4, "KAUSI 2025": 86.4, "COP": 29, "STD": 24, "FDI": 52.0, "F9A": 89.0, "TWS KA": 55, "RWS KA": 27},
    "Graham Usher (61)": {"KA": 86.2, "KAUSI 2025": 86.2, "COP": 30, "STD": 23, "FDI": 52.8, "F9A": 89.8, "TWS KA": 56, "RWS KA": 28},
    "Jelle Klaasen Jnr (62)": {"KA": 86.0, "KAUSI 2025": 86.0, "COP": 31, "STD": 22, "FDI": 53.5, "F9A": 90.5, "TWS KA": 58, "RWS KA": 29},
    "Rusty-Jake Rodriguez (63)": {"KA": 85.8, "KAUSI 2025": 85.8, "COP": 29, "STD": 24, "FDI": 51.5, "F9A": 88.5, "TWS KA": 54, "RWS KA": 26},
    "Matt Campbell (64)": {"KA": 85.6, "KAUSI 2025": 85.6, "COP": 30, "STD": 24, "FDI": 52.0, "F9A": 89.0, "TWS KA": 55, "RWS KA": 27},
    
    # --- MAAILMANLAAJUISET KVALIFIOIJAT (65-96) - STATS PLACEHOLDER ---
    "--- MAAILMANLAAJUISET KVALIFIOIJAT (International) ---": {"KA": 85.0, "KAUSI 2025": 85.0, "COP": 28, "STD": 24.0, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    
    # Korvaa Q G-Taso 33-64 (Avg 85.5 - 79.3) - Mix of International Q's
    "Haruki Muramatsu (65) - Japani": {"KA": 85.5, "KAUSI 2025": 85.5, "COP": 29, "STD": 24.0, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Lourence Ilagan (66) - Filippiinit": {"KA": 85.3, "KAUSI 2025": 85.3, "COP": 28, "STD": 24.5, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Ting Chi Royden Lam (67) - Hongkong": {"KA": 85.1, "KAUSI 2025": 85.1, "COP": 30, "STD": 23.5, "FDI": 50.5, "F9A": 88.5, "TWS KA": 55, "RWS KA": 27},
    "Paolo Nebrida (68) - Filippiinit": {"KA": 84.9, "KAUSI 2025": 84.9, "COP": 29, "STD": 24.0, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    "Haupai Puha (69) - Uusi-Seelanti": {"KA": 84.7, "KAUSI 2025": 84.7, "COP": 28, "STD": 24.5, "FDI": 48.5, "F9A": 86.5, "TWS KA": 51, "RWS KA": 23},
    "Demetris Palios (70) - Kypros": {"KA": 84.5, "KAUSI 2025": 84.5, "COP": 30, "STD": 23.5, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Marko Kantele (71) - Suomi": {"KA": 84.3, "KAUSI 2025": 84.3, "COP": 29, "STD": 24.0, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "D. Hedman (72) - Ruotsi": {"KA": 84.1, "KAUSI 2025": 84.1, "COP": 28, "STD": 24.5, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    "Jules van Dongen (73) - USA": {"KA": 83.9, "KAUSI 2025": 83.9, "COP": 30, "STD": 23.5, "FDI": 50.5, "F9A": 88.5, "TWS KA": 55, "RWS KA": 27},
    "Danny Lauby (74) - USA": {"KA": 83.7, "KAUSI 2025": 83.7, "COP": 29, "STD": 24.0, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Matt Clark (75) - Australia": {"KA": 83.5, "KAUSI 2025": 83.5, "COP": 28, "STD": 24.5, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Fallon Sherrock (76) - Naiset": {"KA": 83.3, "KAUSI 2025": 83.3, "COP": 30, "STD": 23.5, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Beau Greaves (77) - Naiset": {"KA": 83.1, "KAUSI 2025": 83.1, "COP": 29, "STD": 24.0, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Thibault Tricole (78) - Ranska": {"KA": 82.9, "KAUSI 2025": 82.9, "COP": 28, "STD": 24.5, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    "Jim Williams (79) - Iso-Britannia": {"KA": 82.7, "KAUSI 2025": 82.7, "COP": 30, "STD": 23.5, "FDI": 50.5, "F9A": 88.5, "TWS KA": 55, "RWS KA": 27},
    "Christian Kist (80) - Alankomaat": {"KA": 82.5, "KAUSI 2025": 82.5, "COP": 29, "STD": 24.0, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "J. Kuivenhoven (81) - Alankomaat": {"KA": 82.3, "KAUSI 2025": 82.3, "COP": 28, "STD": 24.5, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Darren Webster (82) - Iso-Britannia": {"KA": 82.1, "KAUSI 2025": 82.1, "COP": 30, "STD": 23.5, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Ricky Evans (83) - Iso-Britannia": {"KA": 81.9, "KAUSI 2025": 81.9, "COP": 29, "STD": 24.0, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Mikuru Suzuki (84) - Naiset": {"KA": 81.7, "KAUSI 2025": 81.7, "COP": 28, "STD": 24.5, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    "Boris Koltsov (85) - Venäjä": {"KA": 81.5, "KAUSI 2025": 81.5, "COP": 30, "STD": 23.5, "FDI": 50.5, "F9A": 88.5, "TWS KA": 55, "RWS KA": 27},
    "Jeff Smith (86) - Kanada": {"KA": 81.3, "KAUSI 2025": 81.3, "COP": 29, "STD": 24.0, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Stowe Buntz (87) - USA": {"KA": 81.1, "KAUSI 2025": 81.1, "COP": 28, "STD": 24.5, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Dario Sifontes (88) - Argentiina": {"KA": 80.9, "KAUSI 2025": 80.9, "COP": 30, "STD": 23.5, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Vytis S. (89) - Liettua": {"KA": 80.7, "KAUSI 2025": 80.7, "COP": 29, "STD": 24.0, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "Ryuta Arihara (90) - Japani": {"KA": 80.5, "KAUSI 2025": 80.5, "COP": 28, "STD": 24.5, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    "Alain Abiabi (91) - Filippiinit": {"KA": 80.3, "KAUSI 2025": 80.3, "COP": 30, "STD": 23.5, "FDI": 50.5, "F9A": 88.5, "TWS KA": 55, "RWS KA": 27},
    "Ben Robb (92) - Uusi-Seelanti": {"KA": 80.1, "KAUSI 2025": 80.1, "COP": 29, "STD": 24.0, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Daniel Larsson (93) - Ruotsi": {"KA": 79.9, "KAUSI 2025": 79.9, "COP": 28, "STD": 24.5, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "W. Gurney (94) - Iso-Britannia": {"KA": 79.7, "KAUSI 2025": 79.7, "COP": 30, "STD": 23.5, "FDI": 50.0, "F9A": 88.0, "TWS KA": 54, "RWS KA": 26},
    "Christian Perez (95) - Filippiinit": {"KA": 79.5, "KAUSI 2025": 79.5, "COP": 29, "STD": 24.0, "FDI": 49.5, "F9A": 87.5, "TWS KA": 53, "RWS KA": 25},
    "L. Boulton (96) - Iso-Britannia": {"KA": 79.3, "KAUSI 2025": 79.3, "COP": 28, "STD": 24.5, "FDI": 49.0, "F9A": 87.0, "TWS KA": 52, "RWS KA": 24},
    
    # 96. pelaaja / Vakioprofiilit
    "--- LISÄPROFIILIT ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18, "FDI": "N/A", "F9A": "N/A", "TWS KA": "N/A", "RWS KA": "N/A"},
    "Teemu Harju (FIN)": {"KA": 87.0, "KAUSI 2025": 88.5, "COP": 25, "STD": 24, "FDI": 48.5, "F9A": 89.5, "TWS KA": 55, "RWS KA": 28},
    "Epätasainen (Aloittelija)": {"KA": 80.0, "KAUSI 2025": 80.0, "COP": 28, "STD": 25, "FDI": 30.0, "F9A": 81.0, "TWS KA": 45, "RWS KA": 25},
    "Hyvä Harrastaja": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 20, "FDI": 50.0, "F9A": 91.5, "TWS KA": 65, "RWS KA": 35}
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
    return float(val) if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace('.', '', 1).isdigit()) else default

def get_int_val(data: Dict[str, Any], key: str, default: int) -> int:
    """Palauttaa int-arvon tai oletuksen, jos data on 'N/A'."""
    val = data.get(key)
    return int(val) if isinstance(val, (int, float)) else default


def main():
    st.title("🎯 Darts-simulaattori (PDC 96)")
    st.markdown("Valitse pelaajat ja ottelun muoto simuloidaksesi lopputulosta **Monte Carlo** -menetelmällä.")
    st.caption("HUOM: Simulaatio käyttää **muokattuja arvoja**. Ominaisuuskaudet ovat: **KAUSI 2025** (3 tikan keskiarvo), **COP** (Checkout %), **STD** (Heittojen hajonta), **F9A** (First 9 Average), **TWS KA** (Throw Win Start %) ja **RWS KA** (Receive Win Start %).")

    # Pelaajan valinta
    col1, col2 = st.columns(2)
    
    player_options = [name for name in PLAYER_NAMES if not name.startswith("---")]
    
    default_a_index = player_options.index("Luke Littler (1)") if "Luke Littler (1)" in player_options else 0
    default_b_index = player_options.index("L. Boulton (96) - Iso-Britannia") if "L. Boulton (96) - Iso-Britannia" in player_options else 0
    
    with col1:
        st.subheader("Pelaaja A")
        player_a_name = st.selectbox("Valitse Profiili A", options=player_options, index=default_a_index)
        player_a_data = DEFAULT_PRESETS.get(player_a_name, DEFAULT_PRESETS["VALITSE PROFIILI"])
        
        # Alkuperäisten arvojen näyttö (vain infoa varten)
        st.markdown(f"**Valittu profiili: {player_a_name}**")
        st.info(
            f"**Alkuperäiset luvut:** KA: {player_a_data['KAUSI 2025']:.2f} | COP: {get_int_val(player_a_data, 'COP', 35)}% | STD: {player_a_data['STD']:.1f}"
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
            f"**Alkuperäiset luvut:** KA: {player_b_data['KAUSI 2025']:.2f} | COP: {get_int_val(player_b_data, 'COP', 35)}% | STD: {player_b_data['STD']:.1f}"
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

        st.markdown("### ✨ Tulokset ja Ennusteet")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            winner_name = player_a_name if prob_a > prob_b else player_b_name
            st.metric(label=f"🏆 Todennäköisin voittaja", value=winner_name, delta_color="off")
        
        with col_res2:
            st.metric(
                label=f"**{player_a_name}** voittotodennäköisyys",
                value=f"{prob_a:.1%}",
                delta=f"{a_wins} voittoa",
                delta_color="normal"
            )
            
        with col_res3:
            st.metric(
                label=f"**{player_b_name}** voittotodennäköisyys",
                value=f"{prob_b:.1%}",
                delta=f"{b_wins} voittoa",
                delta_color="normal"
            )
        
        st.markdown("---")
        st.markdown("#### Voittotodennäköisyyden jakautuminen")
        
        data_df = pd.DataFrame({
            'Pelaaja': [player_a_name, player_b_name],
            'Voittotodennäköisyys': [prob_a, prob_b]
        })
        
        chart = alt.Chart(data_df).mark_bar().encode(
            x=alt.X('Pelaaja:N', sort=None),
            y=alt.Y('Voittotodennäköisyys:Q', axis=alt.Axis(format='.0%'), title='Voittotodennäköisyys'),
            color=alt.Color('Pelaaja:N', scale=alt.Scale(domain=[player_a_name, player_b_name], range=['#007bff', '#dc3545']), legend=None),
            tooltip=['Pelaaja', alt.Tooltip('Voittotodennäköisyys', format='.1%')]
        ).properties(
            title="Ottelun ennuste"
        )
        st.altair_chart(chart, use_container_width=True)

# Koodin suoritus
if __name__ == "__main__":
    main()
