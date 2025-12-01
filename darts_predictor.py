import numpy as np
import streamlit as st
import json
import os

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

# --- 2. Päivitetyt Pelaajaprofiilit (Globaalit määritykset) ---
DEFAULT_PRESETS = {
    "VALITSE PROFIILI": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18},
    "--- PDC TOP 32 (Arviot) ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18},
    
    # Kärkipelaajat
    "Luke Littler (1)": {"KA": 99.33, "KAUSI 2025": 99.33, "COP": 41, "STD": 16},
    "Luke Humphries (2)": {"KA": 95.71, "KAUSI 2025": 99.01, "COP": 39, "STD": 17},
    "Michael van Gerwen (3)": {"KA": 99.93, "KAUSI 2025": 97.90, "COP": 41, "STD": 18},
    "Stephen Bunting (4)": {"KA": 94.79, "KAUSI 2025": 97.78, "COP": 37, "STD": 18},
    "Jonny Clayton (5)": {"KA": 94.86, "KAUSI 2025": 96.05, "COP": 34, "STD": 20},
    "Danny Noppert (6)": {"KA": 94.31, "KAUSI 2025": 95.03, "COP": 37, "STD": 20},
    "James Wade (7)": {"KA": 94.47, "KAUSI 2025": 94.62, "COP": 38, "STD": 20},
    "Chris Dobey (8)": {"KA": 95.24, "KAUSI 2025": 96.92, "COP": 34, "STD": 19},
    "Gerwyn Price (9)": {"KA": 96.76, "KAUSI 2025": 98.18, "COP": 36, "STD": 19},
    "Gian van Veen (10)": {"KA": 93.25, "KAUSI 2025": 95.86, "COP": 33, "STD": 19},
    "Josh Rock (11)": {"KA": 97.46, "KAUSI 2025": 97.46, "COP": 36, "STD": 18},
    "Ross Smith (12)": {"KA": 94.86, "KAUSI 2025": 96.66, "COP": 33, "STD": 20},
    "Martin Schindler (13)": {"KA": 93.16, "KAUSI 2025": 94.93, "COP": 33, "STD": 20},
    "Gary Anderson (14)": {"KA": 97.82, "KAUSI 2025": 98.6, "COP": 35, "STD": 17},
    "Nathan Aspinall (15)": {"KA": 95.22, "KAUSI 2025": 95.82, "COP": 34, "STD": 20},
    "Damon Heta (16)": {"KA": 94.60, "KAUSI 2025": 95.38, "COP": 35, "STD": 20},
    "Rob Cross (17)": {"KA": 97.10, "KAUSI 2025": 96.48, "COP": 34, "STD": 20},
    "Mike De Decker (18)": {"KA": 91.56, "KAUSI 2025": 94.27, "COP": 33, "STD": 20},
    "Jermaine Wattimena (19)": {"KA": 93.48, "KAUSI 2025": 94.69, "COP": 32, "STD": 21},
    "Ryan Searle (20)": {"KA": 93.88, "KAUSI 2025": 95.53, "COP": 33, "STD": 20},
    
    # Pelaajat 21-32
    "Dave Chisnall (21)": {"KA": 95.65, "KAUSI 2025": 93.99, "COP": 34, "STD": 20},
    "Daryl Gurney (22)": {"KA": 94.60, "KAUSI 2025": 94.27, "COP": 33, "STD": 21},
    "Dimitri Van den Bergh (23)": {"KA": 93.31, "KAUSI 2025": 92.39, "COP": 35, "STD": 20},
    "Ryan Joyce (24)": {"KA": 92.81, "KAUSI 2025": 93.47, "COP": 32, "STD": 21},
    "Luke Woodhouse (25)": {"KA": 91.96, "KAUSI 2025": 92.92, "COP": 32, "STD": 21},
    "Cameron Menzies (26)": {"KA": 91.50, "KAUSI 2025": 93.97, "COP": 31, "STD": 22},
    "Ritchie Edhouse (27)": {"KA": 90.89, "KAUSI 2025": 91.92, "COP": 32, "STD": 22},
    "Michael Smith (28)": {"KA": 95.38, "KAUSI 2025": 94.49, "COP": 34, "STD": 19}, 
    "Dirk van Duijvenbode (29)": {"KA": 94.01, "KAUSI 2025": 96.07, "COP": 33, "STD": 21},
    "Peter Wright (30)": {"KA": 96.42, "KAUSI 2025": 92.49, "COP": 35, "STD": 20}, 
    "Wessel Nijman (31)": {"KA": 92.63, "KAUSI 2025": 94.87, "COP": 31, "STD": 22},
    "Joe Cullen (32)": {"KA": 93.01, "KAUSI 2025": 92.64, "COP": 33, "STD": 20},
    "Darius Labanauskas (LTU)": {"KA": 89.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 21},
    "Mario Vandenbogaerde (BEL)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 32, "STD": 21},
    "David Davies (WAL)": {"KA": 88.0, "KAUSI 2025": 88.0, "COP": 30, "STD": 22},
    "Bradley Brooks (ENG)": {"KA": 89.5, "KAUSI 2025": 89.0, "COP": 33, "STD": 21},
    "Mensur Suljovic (AUT)": {"KA": 91.0, "KAUSI 2025": 90.5, "COP": 36, "STD": 20},
    "David Cameron (CAN)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 29, "STD": 22},
    "Steve Lennon (IRE)": {"KA": 90.0, "KAUSI 2025": 90.5, "COP": 34, "STD": 21},
    "Raymond van Barneveld (NED)": {"KA": 92.5, "KAUSI 2025": 92.0, "COP": 34, "STD": 19},
    "Stefan Bellmont (SUI)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 31, "STD": 22},
    "Cor Dekker (NED)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 28, "STD": 23},
    "Ian White (ENG)": {"KA": 91.0, "KAUSI 2025": 90.5, "COP": 34, "STD": 20},
    "Mervyn King (ENG)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 32, "STD": 21},
    "Xiaochen Zong (CHN)": {"KA": 87.5, "KAUSI 2025": 87.0, "COP": 29, "STD": 23},
    "Andrew Gilding (ENG)": {"KA": 91.5, "KAUSI 2025": 91.0, "COP": 34, "STD": 20},
    "Cam Crabtree (ENG)": {"KA": 86.5, "KAUSI 2025": 86.5, "COP": 30, "STD": 22},
    "Boris Krcmar (CRO)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 33, "STD": 21},
    "Martin Lukeman (ENG)": {"KA": 89.5, "KAUSI 2025": 90.0, "COP": 32, "STD": 21},
    "Max Hopp (GER)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 31, "STD": 22},
    "Adam Gawlas (CZE)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 31, "STD": 22},
    "Lukas Wenig (GER)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Wesley Plaisier (NED)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 32, "STD": 21},
    "Owen Bates (ENG)": {"KA": 87.5, "KAUSI 2025": 88.0, "COP": 30, "STD": 22},
    "Krzysztof Ratajski (POL)": {"KA": 92.0, "KAUSI 2025": 92.5, "COP": 34, "STD": 20},
    "Alexis Toylo (PHI)": {"KA": 85.0, "KAUSI 2025": 85.0, "COP": 28, "STD": 24},
    "Sebastian Bialecki (POL)": {"KA": 87.5, "KAUSI 2025": 88.0, "COP": 31, "STD": 22},
    "Richard Veenstra (NED)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 32, "STD": 21},
    "Nitin Kumar (IND)": {"KA": 85.0, "KAUSI 2025": 85.0, "COP": 27, "STD": 24},
    "Andy Baetens (BEL)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 32, "STD": 21},
    "James Hurrell (ENG)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Stowe Buntz (USA)": {"KA": 86.5, "KAUSI 2025": 87.0, "COP": 29, "STD": 23},
    "Stephen Burton (ENG)": {"KA": 87.5, "KAUSI 2025": 88.0, "COP": 30, "STD": 22},
    "Keane Barry (IRE)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 32, "STD": 21},
    "Tim Pusey (AUS)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Chris Landman (NED)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 31, "STD": 22},
    "Brendan Dolan (NIR)": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 35, "STD": 20},
    "Travis Dudeney (ENG)": {"KA": 86.0, "KAUSI 2025": 86.0, "COP": 28, "STD": 23},
    "Adam Lipscombe (ENG)": {"KA": 85.5, "KAUSI 2025": 86.0, "COP": 29, "STD": 23},
    "Dom Taylor (ENG)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Oskar Lukasiak (POL)": {"KA": 84.5, "KAUSI 2025": 85.0, "COP": 27, "STD": 24},
    "Lisa Ashton (ENG)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Niels Zonneveld (NED)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 31, "STD": 21},
    "Haupai Puha (NZL)": {"KA": 87.5, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Andreas Harrysson (SWE)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Thibault Tricole (FRA)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Motomu Sakai (JPN)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Fallon Sherrock (ENG)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 32, "STD": 21},
    "Ricardo Pietreczko (GER)": {"KA": 90.0, "KAUSI 2025": 90.5, "COP": 33, "STD": 21},
    "José de Sousa (POR)": {"KA": 91.5, "KAUSI 2025": 91.0, "COP": 35, "STD": 20},
    "Ted Evetts (ENG)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 32, "STD": 21},
    "Jeffrey de Graaf (NED)": {"KA": 87.5, "KAUSI 2025": 88.0, "COP": 31, "STD": 22},
    "Paul Lim (SGP)": {"KA": 84.5, "KAUSI 2025": 85.0, "COP": 27, "STD": 24},
    "Karel Sedlacek (CZE)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 33, "STD": 21},
    "Gabriel Clemens (GER)": {"KA": 92.5, "KAUSI 2025": 93.0, "COP": 34, "STD": 20},
    "Alex Spellman (USA)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Lourence Ilagan (PHI)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Mickey Mansell (NIR)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 31, "STD": 22},
    "Leonard Gates (USA)": {"KA": 87.5, "KAUSI 2025": 88.0, "COP": 30, "STD": 22},
    "David Munyua (KEN)": {"KA": 84.0, "KAUSI 2025": 84.5, "COP": 26, "STD": 25},
    "Kevin Doets (NED)": {"KA": 89.5, "KAUSI 2025": 90.0, "COP": 32, "STD": 21},
    "Matthew Dennant (ENG)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Ryusei Azemoto (JPN)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Ricky Evans (ENG)": {"KA": 91.0, "KAUSI 2025": 91.5, "COP": 33, "STD": 20},
    "Man Lok Leung (HKG)": {"KA": 85.5, "KAUSI 2025": 86.0, "COP": 29, "STD": 23},
    "Charlie Manby (ENG)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Matt Campbell (CAN)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 32, "STD": 21},
    "Adam Sevada (USA)": {"KA": 84.0, "KAUSI 2025": 84.5, "COP": 26, "STD": 25},
    "Cristo Reyes (ESP)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 33, "STD": 21},
    "Alan Soutar (SCO)": {"KA": 89.5, "KAUSI 2025": 90.0, "COP": 33, "STD": 21},
    "Teemu Harju (FIN)": {"KA": 87.0, "KAUSI 2025": 88.5, "COP": 25, "STD": 24}, # Tarkennettu
    "Darren Beveridge (SCO)": {"KA": 86.5, "KAUSI 2025": 87.0, "COP": 29, "STD": 23},
    "Madars Razma (LAT)": {"KA": 90.0, "KAUSI 2025": 90.5, "COP": 33, "STD": 21},
    "Jamai van den Herik (NED)": {"KA": 86.0, "KAUSI 2025": 86.0, "COP": 29, "STD": 23},
    "Mitsuhiko Tatsunami (JPN)": {"KA": 84.5, "KAUSI 2025": 85.0, "COP": 27, "STD": 24},
    "William O'Connor (IRE)": {"KA": 89.5, "KAUSI 2025": 90.0, "COP": 33, "STD": 21},
    "Krzysztof Kciuk (POL)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Noa-Lynn van Leuven (NED)": {"KA": 85.5, "KAUSI 2025": 86.0, "COP": 29, "STD": 23},
    "Kim Huybrechts (BEL)": {"KA": 90.5, "KAUSI 2025": 91.0, "COP": 33, "STD": 20},
    "Arno Merk (NED)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Adam Hunt (ENG)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Connor Scutt (ENG)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 31, "STD": 21},
    "Simon Whitlock (AUS)": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 35, "STD": 20},
    "Dominik Grüllich (GER)": {"KA": 85.5, "KAUSI 2025": 86.0, "COP": 28, "STD": 24},
    "Scott Williams (ENG)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 32, "STD": 21},
    "Paolo Nebrida (PHI)": {"KA": 84.0, "KAUSI 2025": 84.5, "COP": 26, "STD": 25},
    "Jurjen van der Velde (NED)": {"KA": 86.5, "KAUSI 2025": 87.0, "COP": 30, "STD": 22},
    "Nick Kenny (WAL)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 31, "STD": 22},
    "Justin Hood (ENG)": {"KA": 86.0, "KAUSI 2025": 86.5, "COP": 29, "STD": 23},
    "Jonny Tata (NZL)": {"KA": 85.0, "KAUSI 2025": 85.0, "COP": 27, "STD": 24},
    "Ryan Meikle (ENG)": {"KA": 88.5, "KAUSI 2025": 89.0, "COP": 31, "STD": 21},
    "Jesus Salate (ESP)": {"KA": 84.0, "KAUSI 2025": 84.5, "COP": 26, "STD": 25},
    "Gemma Hayter (ENG)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 28, "STD": 24},
    "Niko Springer (GER)": {"KA": 87.0, "KAUSI 2025": 87.5, "COP": 30, "STD": 22},
    "Joe Comito (USA)": {"KA": 85.5, "KAUSI 2025": 86.0, "COP": 28, "STD": 24},
    "Beau Greaves (ENG)": {"KA": 88.0, "KAUSI 2025": 88.5, "COP": 32, "STD": 21},
    "Callan Rydz (ENG)": {"KA": 89.0, "KAUSI 2025": 89.5, "COP": 32, "STD": 21},
    "Patrik Kovacs (HUN)": {"KA": 85.0, "KAUSI 2025": 85.5, "COP": 27, "STD": 24},
    
    "--- HARRASTAJAT ---": {"KA": 95.0, "KAUSI 2025": 95.0, "COP": 35, "STD": 18},
    "Epätasainen (Aloittelija)": {"KA": 80.0, "KAUSI 2025": 80.0, "COP": 28, "STD": 25},
    "Hyvä Harrastaja": {"KA": 90.0, "KAUSI 2025": 90.0, "COP": 33, "STD": 20}
}
CUSTOM_PRESET_FILE = "custom_presets.json"


# --- 3. Simulaatiofunktiot (Muuttumattomat) ---

def get_hit_score(segment):
    if segment in ["Bull", "B"]: return 50
    score_value = int(segment[1:]) if len(segment) > 1 else 0
    multiplier = SCORING_MAP.get(segment[0], 1)
    return score_value * multiplier

def simulate_score(average_score, std_dev):
    score = int(np.random.normal(average_score, std_dev))
    return max(0, min(180, score))

def attempt_checkout(current_score, cop):
    if current_score not in CHECKOUT_MAP or current_score <= 1:
        return current_score, False 

    if np.random.rand() < cop:
        return 0, True
    else:
        route = CHECKOUT_MAP.get(current_score, ["S20", "S20", "S20"]) 
        points_to_target = sum(get_hit_score(t) for t in route if not t.startswith('D'))
        score_taken = int(points_to_target * np.random.uniform(0.5, 0.9))
        new_score = current_score - score_taken
        if new_score < 2:
            return current_score, False
        return new_score, False

def simulate_leg(player_a_avg, player_a_cop, player_a_std, 
                 player_b_avg, player_b_cop, player_b_std, starts_a):
    score_a = 501
    score_b = 501
    turn_index = 0 if starts_a else 1 
    
    while score_a > 0 and score_b > 0:
        current_score = score_a if turn_index % 2 == 0 else score_b
        avg, cop, std = (player_a_avg, player_a_cop, player_a_std) if turn_index % 2 == 0 else (player_b_avg, player_b_cop, player_b_std)
            
        if current_score <= 170 and current_score in CHECKOUT_MAP:
            new_score, win = attempt_checkout(current_score, cop)
            if win: return "A" if turn_index % 2 == 0 else "B"
            current_score = new_score
        else:
            score = simulate_score(avg, std) 
            current_score -= score
            if current_score < 2: current_score += score
            
        if turn_index % 2 == 0:
            score_a = current_score
        else:
            score_b = current_score
                    
        turn_index += 1
    return "A" if score_a == 0 else "B" 


def simulate_match(params):
    p_a_avg, p_a_cop, p_a_std = params['P_A_AVG'], params['P_A_COP'], params['P_A_STD']
    p_b_avg, p_b_cop, p_b_std = params['P_B_AVG'], params['P_B_COP'], params['P_B_STD']
    match_type = params['MATCH_TYPE']
    
    match_wins_a = 0
    match_wins_b = 0
    
    if match_type == "SET":
        target_sets = (params['N_SETS'] // 2) + 1
        target_legs_per_set = 3 
        
        while match_wins_a < target_sets and match_wins_b < target_sets:
            set_wins_a = 0
            set_wins_b = 0
            starts_a = np.random.rand() < 0.5 
            
            while set_wins_a < target_legs_per_set and set_wins_b < target_legs_per_set:
                leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
                if leg_winner == "A": set_wins_a += 1
                else: set_wins_b += 1
                starts_a = not starts_a 
                
            if set_wins_a == target_legs_per_set: match_wins_a += 1
            else: match_wins_b += 1
                
        return "A" if match_wins_a == target_sets else "B"

    else: # LEG
        target_legs = (params['N_LEGS'] // 2) + 1
        starts_a = np.random.rand() < 0.5 
        
        while match_wins_a < target_legs and match_wins_b < target_legs:
            leg_winner = simulate_leg(p_a_avg, p_a_cop, p_a_std, p_b_avg, p_b_cop, p_b_std, starts_a)
            if leg_winner == "A": match_wins_a += 1
            else: match_wins_b += 1
            starts_a = not starts_a
            
        return "A" if match_wins_a == target_legs else "B"


# --- 4. Profiilien hallinta Session Statella (KÄYTÖSSÄ) ---

def load_custom_presets():
    """Lataa profiilit tiedostosta ja alustaa ne Session Stateen."""
    global DEFAULT_PRESETS, CUSTOM_PRESET_FILE 
    
    # 1. Tarkista, onko profiilit jo ladattu Session Stateen
    if 'PLAYER_PRESETS' in st.session_state:
        return 

    current_presets = DEFAULT_PRESETS.copy()
    
    # 2. Yritetään ladata mukautetut profiilit tiedostosta
    if os.path.exists(CUSTOM_PRESET_FILE):
        try:
            with open(CUSTOM_PRESET_FILE, 'r') as f:
                custom_data = json.load(f)
            current_presets.update(custom_data)
        except Exception:
            pass 
            
    # 3. Tallennetaan lopullinen sanakirja Session Stateen
    st.session_state['PLAYER_PRESETS'] = current_presets

def save_custom_presets():
    """Tallentaa vain käyttäjän luomat profiilit Session Statesta JSON-tiedostoon."""
    global DEFAULT_PRESETS, CUSTOM_PRESET_FILE
    
    all_presets = st.session_state.get('PLAYER_PRESETS', DEFAULT_PRESETS)
    
    custom_data = {
        k: v for k, v in all_presets.items() 
        if k not in DEFAULT_PRESETS and "---" not in k
    }
    try:
        with open(CUSTOM_PRESET_FILE, 'w') as f:
            json.dump(custom_data, f, indent=4)
        st.toast("Mukautetut profiilit tallennettu onnistuneesti!")
    except Exception as e:
        st.error(f"Mukautettujen profiilien tallentaminen epäonnistui: {e}")

def update_player_inputs(player_id):
    """Päivittää pelaajan syötekentät valitun profiilin perusteella Session Statesta."""
    
    player_presets = st.session_state['PLAYER_PRESETS']
    preset_key = st.session_state[f'preset_{player_id}']
    form_key = st.session_state[f'form_{player_id}']
    
    if "---" in preset_key:
        return
    
    data = player_presets.get(preset_key, player_presets["VALITSE PROFIILI"])
    
    st.session_state[f'cop_{player_id}'] = data.get("COP", 35)
    st.session_state[f'std_{player_id}'] = data.get("STD", 18.0)
    
    # HUOM: 'KAUSI' ja 'VIIMEISET 5' on muutettu muotoon 'KA' ja 'KAUSI 2025'
    new_avg = data.get(form_key, data.get("KA", 95.0))
    st.session_state[f'avg_{player_id}'] = f"{new_avg:.2f}"


# --- 5. Streamlit GUI & Logiikka (main-funktio) ---

def run_simulation(params, result_placeholder, progress_placeholder):
    """Suorittaa Monte Carlo -simulaation ja päivittää Streamlit-komponentteja (sisältää edistymispalkin)."""
    
    a_wins = 0
    b_wins = 0
    n = params['N_SIMULATIONS']
    
    progress_bar = progress_placeholder.progress(0, text="Käynnistetään simulaatio...")
    
    update_interval = max(1, n // 100) 
    
    for i in range(n):
        winner = simulate_match(params)
        
        if winner == "A":
            a_wins += 1
        else:
            b_wins += 1
        
        if (i + 1) % update_interval == 0 or (i + 1) == n:
            progress = (i + 1) / n
            progress_bar.progress(progress, text=f"Simuloidaan... {int(progress * 100)}%")

    prob_a = a_wins / n
    prob_b = b_wins / n
    
    p_a_name = st.session_state['preset_A'] if st.session_state['preset_A'] != "VALITSE PROFIILI" else "Pelaaja A"
    p_b_name = st.session_state['preset_B'] if st.session_state['preset_B'] != "VALITSE PROFIILI" else "Pelaaja B"

    progress_placeholder.empty() 
    result_placeholder.empty()
    with result_placeholder.container():
        st.subheader("✨ LOPULLINEN ENNUSTE ✨")
        st.info(f"Simulaatiot: **{n}** kierrosta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{p_a_name}**")
            st.metric(label="Voittotodennäköisyys", value=f"{prob_a:.2%}")
            st.markdown(f"Voittoja: **{a_wins}**")
        
        with col2:
            st.markdown(f"**{p_b_name}**")
            st.metric(label="Voittotodennäköisyys", value=f"{prob_b:.2%}")
            st.markdown(f"Voittoja: **{b_wins}**")
            
        st.markdown("---")
        if prob_a > prob_b:
            st.success(f"Todennäköisin voittaja: **{p_a_name}**")
        elif prob_b > prob_a:
            st.success(f"Todennäköisin voittaja: **{p_b_name}**")
        else:
            st.warning("Tasatilanne (50/50)")

def main():
    """Streamlit-sovelluksen pääfunktio."""
    
    # --- ALUSTUS TÄSSÄ ---
    
    load_custom_presets() 
    
    st.set_page_config(page_title="Darts-ennustin (Monte Carlo)", layout="wide")
    st.title("🎯 Darts-ennustin (Monte Carlo-simulaatio)")
    st.markdown("---")

    # 2. Session State - Alustus (Käyttää PLAYER_PRESETS Session Statea)
    if 'preset_A' not in st.session_state:
        default_data = st.session_state['PLAYER_PRESETS']["VALITSE PROFIILI"] 
        st.session_state['preset_A'] = "VALITSE PROFIILI"
        st.session_state['preset_B'] = "VALITSE PROFIILI"
        st.session_state['form_A'] = "KA"
        st.session_state['form_B'] = "KA"
        st.session_state['avg_A'] = f"{default_data['KA']:.2f}"
        st.session_state['cop_A'] = default_data['COP']
        st.session_state['std_A'] = default_data['STD']
        st.session_state['avg_B'] = f"{default_data['KA']:.2f}"
        st.session_state['cop_B'] = default_data['COP']
        st.session_state['std_B'] = default_data['STD']
        
    update_player_inputs('A') 
    update_player_inputs('B')

    # --- Pelaajien Syötteet ---
    st.header("1. Pelaajien Parametrit")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Pelaaja A")
        
        st.selectbox("Profiili (A)", options=list(st.session_state['PLAYER_PRESETS'].keys()), key='preset_A', on_change=lambda: update_player_inputs('A'))
        st.selectbox("3DA Muoto (A)", options=["KA", "KAUSI 2025"], key='form_A', on_change=lambda: update_player_inputs('A'))
        st.text_input("3DA (Kolmen tikan keskiarvo)", key='avg_A')
        st.number_input("COP (%) (Checkout-prosentti)", min_value=0, max_value=100, key='cop_A')
        st.number_input("STD DEV (Keskiarvon Keskihajonta)", key='std_A')
        
    with col_b:
        st.subheader("Pelaaja B")
        
        st.selectbox("Profiili (B)", options=list(st.session_state['PLAYER_PRESETS'].keys()), key='preset_B', on_change=lambda: update_player_inputs('B'))
        st.selectbox("3DA Muoto (B)", options=["KA", "KAUSI 2025"], key='form_B', on_change=lambda: update_player_inputs('B'))
        st.text_input("3DA (Kolmen tikan keskiarvo)", key='avg_B')
        st.number_input("COP (%) (Checkout-prosentti)", min_value=0, max_value=100, key='cop_B')
        st.number_input("STD DEV (Keskiarvon Keskihajonta)", key='std_B')
        
    st.markdown("---")

    # --- Ottelun Muoto & Simulaatio ---
    st.header("2. Ottelun Muoto ja Simulaatio")
    col_type, col_n, col_sim = st.columns([1, 1, 1])

    with col_type:
        match_type = st.radio("Ottelun tyyppi", options=["LEG", "SET"], key='match_type')

    with col_n:
        n_legs = None
        n_sets = None
        if match_type == "LEG":
            n_legs = st.number_input("Paras N Legistä", min_value=3, step=2, value=11, key='n_legs')
        else:
            n_sets = st.number_input("Paras N Setistä", min_value=3, step=2, value=5, key='n_sets')

    with col_sim:
        n_simulations = st.number_input("Simulaatioiden määrä", min_value=100, step=1000, value=10000, key='n_sims')

    st.markdown("---")
    
    progress_placeholder = st.empty() 
    result_placeholder = st.empty()

    # --- Käynnistysnappi ---
    if st.button("▶️ Aloita Simulaatio", type="primary"):
        try:
            params = {
                'P_A_AVG': float(st.session_state['avg_A'].replace(',', '.')),
                'P_A_COP': float(st.session_state['cop_A']) / 100.0,
                'P_A_STD': float(st.session_state['std_A']),
                'P_B_AVG': float(st.session_state['avg_B'].replace(',', '.')),
                'P_B_COP': float(st.session_state['cop_B']) / 100.0,
                'P_B_STD': float(st.session_state['std_B']),
                'N_SIMULATIONS': int(st.session_state['n_sims']),
                'MATCH_TYPE': match_type,
                'N_LEGS': n_legs,
                'N_SETS': n_sets
            }
            
            run_simulation(params, result_placeholder, progress_placeholder)

        except ValueError as e:
            st.error(f"Virhe syötteessä: Varmista, että kaikki numeeriset arvot ovat oikein. ({e})")
        except Exception as e:
            st.error(f"Odottamaton virhe: {e}")

if __name__ == "__main__":
    main()
