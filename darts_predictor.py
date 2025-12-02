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

# --- 2. Pelaajaprofiilit (COP-arvoja päivitetty vastaamaan paremmin huipputasoa) ---
# PDC WORLD DARTS CHAMPIONSHIP 2025/2026 PROFIILIT JA TILASTOT
# Lähteet: Käyttäjän lataamat CSV-tiedot (päivitetty 2.12.2025)

PROFIILIT = {
    "Luke Littler": {"3DA": 100.96, "COP": 42.87, "STD": 16.0, "FDI": 1976, "F9A": 111.51, "TWS": 99.44, "RWS": 102.72},
    "Luke Humphries": {"3DA": 98.50, "COP": 41.18, "STD": 17.0, "FDI": 1876, "F9A": 107.80, "TWS": 96.62, "RWS": 100.63},
    "Michael van Gerwen": {"3DA": 97.28, "COP": 39.43, "STD": 18.0, "FDI": 1809, "F9A": 106.42, "TWS": 95.85, "RWS": 98.87},
    "Stephen Bunting": {"3DA": 98.04, "COP": 39.93, "STD": 18.0, "FDI": 1823, "F9A": 107.65, "TWS": 96.95, "RWS": 99.24},
    "Jonny Clayton": {"3DA": 96.30, "COP": 42.52, "STD": 20.0, "FDI": 1790, "F9A": 104.69, "TWS": 95.05, "RWS": 97.71},
    "Danny Noppert": {"3DA": 94.79, "COP": 40.39, "STD": 20.0, "FDI": 1822, "F9A": 102.79, "TWS": 94.52, "RWS": 95.09},
    "James Wade": {"3DA": 94.79, "COP": 42.77, "STD": 20.0, "FDI": 1809, "F9A": 102.10, "TWS": 93.22, "RWS": 96.59},
    "Chris Dobey": {"3DA": 96.76, "COP": 38.78, "STD": 19.0, "FDI": 1858, "F9A": 106.16, "TWS": 95.00, "RWS": 98.77},
    "Gerwyn Price": {"3DA": 97.75, "COP": 42.09, "STD": 19.0, "FDI": 1899, "F9A": 106.69, "TWS": 96.89, "RWS": 98.75},
    "Gian van Veen": {"3DA": 97.91, "COP": 46.31, "STD": 19.0, "FDI": 1867, "F9A": 105.80, "TWS": 97.19, "RWS": 98.71},
    "Josh Rock": {"3DA": 98.10, "COP": 39.98, "STD": 18.0, "FDI": 1838, "F9A": 108.20, "TWS": 96.05, "RWS": 100.41},
    "Ross Smith": {"3DA": 96.50, "COP": 41.64, "STD": 20.0, "FDI": 1780, "F9A": 106.29, "TWS": 95.43, "RWS": 97.67},
    "Martin Schindler": {"3DA": 94.13, "COP": 39.23, "STD": 20.0, "FDI": 1745, "F9A": 103.11, "TWS": 93.21, "RWS": 95.14},
    "Gary Anderson": {"3DA": 97.41, "COP": 42.09, "STD": 17.0, "FDI": 1794, "F9A": 105.99, "TWS": 95.90, "RWS": 99.12},
    "Nathan Aspinall": {"3DA": 95.64, "COP": 38.91, "STD": 20.0, "FDI": 1848, "F9A": 104.88, "TWS": 94.41, "RWS": 97.04},
    "Damon Heta": {"3DA": 94.81, "COP": 43.50, "STD": 20.0, "FDI": 1785, "F9A": 102.49, "TWS": 93.86, "RWS": 95.87},
    "Rob Cross": {"3DA": 95.75, "COP": 40.51, "STD": 20.0, "FDI": 1720, "F9A": 103.66, "TWS": 95.59, "RWS": 95.96},
    "Mike De Decker": {"3DA": 93.92, "COP": 38.74, "STD": 20.0, "FDI": 1780, "F9A": 101.65, "TWS": 92.78, "RWS": 95.19},
    "Jermaine Wattimena": {"3DA": 94.87, "COP": 39.60, "STD": 21.0, "FDI": 1819, "F9A": 104.10, "TWS": 93.69, "RWS": 96.17},
    "Ryan Searle": {"3DA": 95.76, "COP": 40.25, "STD": 20.0, "FDI": 1767, "F9A": 105.02, "TWS": 95.06, "RWS": 96.56},
    "Dave Chisnall": {"3DA": 91.86, "COP": 37.89, "STD": 20.0, "FDI": 1700, "F9A": 101.15, "TWS": 89.94, "RWS": 94.02},
    "Daryl Gurney": {"3DA": 93.23, "COP": 40.68, "STD": 21.0, "FDI": 1736, "F9A": 100.33, "TWS": 91.49, "RWS": 95.20},
    "Dimitri Van den Bergh": {"3DA": 88.97, "COP": 32.74, "STD": 20.0, "FDI": 1688, "F9A": 96.92, "TWS": 87.51, "RWS": 90.60},
    "Ryan Joyce": {"3DA": 93.02, "COP": 42.71, "STD": 21.0, "FDI": 1750, "F9A": 100.80, "TWS": 91.47, "RWS": 94.72},
    "Luke Woodhouse": {"3DA": 92.70, "COP": 39.17, "STD": 21.0, "FDI": 1771, "F9A": 100.05, "TWS": 91.82, "RWS": 93.69},
    "Cameron Menzies": {"3DA": 92.65, "COP": 37.99, "STD": 22.0, "FDI": 1753, "F9A": 101.83, "TWS": 91.02, "RWS": 94.50},
    "Ritchie Edhouse": {"3DA": 90.94, "COP": 37.98, "STD": 22.0, "FDI": 1688, "F9A": 98.63, "TWS": 89.62, "RWS": 92.42},
    "Michael Smith": {"3DA": 92.74, "COP": 39.10, "STD": 19.0, "FDI": 1695, "F9A": 100.84, "TWS": 91.94, "RWS": 93.64},
    "Dirk van Duijvenbode": {"3DA": 96.53, "COP": 41.29, "STD": 20.0, "FDI": 1757, "F9A": 106.28, "TWS": 95.03, "RWS": 98.24},
    "Peter Wright": {"3DA": 92.41, "COP": 38.77, "STD": 20.0, "FDI": 1674, "F9A": 99.83, "TWS": 90.93, "RWS": 94.06},
    "Wessel Nijman": {"3DA": 95.86, "COP": 42.18, "STD": 21.0, "FDI": 1864, "F9A": 104.62, "TWS": 94.44, "RWS": 97.47},
    "Joe Cullen": {"3DA": 91.88, "COP": 36.08, "STD": 20.0, "FDI": 1677, "F9A": 100.51, "TWS": 89.51, "RWS": 94.58},
    "Ricardo Pietreczko": {"3DA": 91.02, "COP": 39.83, "STD": 20.0, "FDI": 1697, "F9A": 98.00, "TWS": 89.82, "RWS": 92.35},
    "Andrew Gilding": {"3DA": 93.40, "COP": 38.90, "STD": 20.0, "FDI": 1726, "F9A": 101.98, "TWS": 91.80, "RWS": 95.22},
    "Raymond van Barneveld": {"3DA": 91.38, "COP": 38.65, "STD": 20.0, "FDI": 1691, "F9A": 99.01, "TWS": 90.57, "RWS": 92.33},
    "Scott Williams": {"3DA": 91.29, "COP": 39.32, "STD": 20.0, "FDI": 1716, "F9A": 99.62, "TWS": 89.78, "RWS": 93.00},
    "Krzysztof Ratajski": {"3DA": 94.42, "COP": 40.13, "STD": 20.0, "FDI": 1745, "F9A": 102.91, "TWS": 92.89, "RWS": 96.11},
    "Martin Lukeman": {"3DA": 90.03, "COP": 39.86, "STD": 20.0, "FDI": 1659, "F9A": 96.98, "TWS": 89.54, "RWS": 90.58},
    "Brendan Dolan": {"3DA": 91.09, "COP": 41.28, "STD": 20.0, "FDI": 1708, "F9A": 98.82, "TWS": 90.28, "RWS": 91.97},
    "Ricky Evans": {"3DA": 91.81, "COP": 37.24, "STD": 20.0, "FDI": 1709, "F9A": 99.15, "TWS": 90.50, "RWS": 93.23},
    "Niko Springer": {"3DA": 93.90, "COP": 40.49, "STD": 20.0, "FDI": 1762, "F9A": 102.64, "TWS": 92.42, "RWS": 95.57},
    "William O'Connor": {"3DA": 93.99, "COP": 39.93, "STD": 22.0, "FDI": 1770, "F9A": 102.84, "TWS": 92.84, "RWS": 95.27},
    "Niels Zonneveld": {"3DA": 92.90, "COP": 40.41, "STD": 20.0, "FDI": 1712, "F9A": 101.14, "TWS": 91.66, "RWS": 94.25},
    "Kevin Doets": {"3DA": 91.56, "COP": 38.88, "STD": 20.0, "FDI": 1741, "F9A": 100.45, "TWS": 90.00, "RWS": 93.29},
    "Karel Sedlacek": {"3DA": 93.00, "COP": 38.45, "STD": 20.0, "FDI": 1764, "F9A": 100.93, "TWS": 91.28, "RWS": 94.91},
    "Bradley Brooks": {"3DA": 93.20, "COP": 40.21, "STD": 20.0, "FDI": 1720, "F9A": 102.36, "TWS": 91.65, "RWS": 94.92},
    "Jeffrey de Graaf": {"3DA": 90.51, "COP": 39.15, "STD": 20.0, "FDI": 1680, "F9A": 97.97, "TWS": 89.47, "RWS": 91.68},
    "Mickey Mansell": {"3DA": 91.36, "COP": 38.77, "STD": 20.0, "FDI": 1710, "F9A": 99.27, "TWS": 89.98, "RWS": 92.95},
    "Mario Vandenbogaerde": {"3DA": 91.13, "COP": 37.94, "STD": 20.0, "FDI": 1697, "F9A": 99.24, "TWS": 90.62, "RWS": 91.71},
    "Callan Rydz": {"3DA": 94.26, "COP": 39.43, "STD": 20.0, "FDI": 1729, "F9A": 102.49, "TWS": 93.34, "RWS": 95.26},
    "Cam Crabtree": {"3DA": 90.80, "COP": 38.75, "STD": 20.0, "FDI": 1728, "F9A": 99.66, "TWS": 89.41, "RWS": 92.37},
    "Ian White": {"3DA": 91.72, "COP": 40.43, "STD": 20.0, "FDI": 1658, "F9A": 99.43, "TWS": 91.65, "RWS": 91.80},
    "Sebastian Białecki": {"3DA": 88.55, "COP": 36.34, "STD": 20.0, "FDI": 1661, "F9A": 96.91, "TWS": 87.72, "RWS": 89.49},
    "Dom Taylor": {"3DA": 94.35, "COP": 43.47, "STD": 20.0, "FDI": 1701, "F9A": 100.65, "TWS": 92.67, "RWS": 96.21},
    "Richard Veenstra": {"3DA": 90.61, "COP": 37.87, "STD": 20.0, "FDI": 1707, "F9A": 97.26, "TWS": 89.64, "RWS": 91.66},
    "Madars Razma": {"3DA": 91.69, "COP": 38.82, "STD": 20.0, "FDI": 1700, "F9A": 99.65, "TWS": 90.05, "RWS": 93.54},
    "Alan Soutar": {"3DA": 91.44, "COP": 37.88, "STD": 20.0, "FDI": 1699, "F9A": 100.62, "TWS": 90.59, "RWS": 92.40},
    "Lukas Wenig": {"3DA": 91.60, "COP": 35.56, "STD": 20.0, "FDI": 1730, "F9A": 100.25, "TWS": 89.69, "RWS": 93.80},
    "Kim Huybrechts": {"3DA": 91.23, "COP": 38.21, "STD": 20.0, "FDI": 1667, "F9A": 98.55, "TWS": 89.32, "RWS": 93.32},
    "Mensur Suljovic": {"3DA": 90.68, "COP": 35.25, "STD": 20.0, "FDI": 1670, "F9A": 99.69, "TWS": 90.07, "RWS": 93.47},
    "Gabriel Clemens": {"3DA": 91.50, "COP": 36.36, "STD": 20.0, "FDI": 1674, "F9A": 99.83, "TWS": 89.95, "RWS": 93.27},
    "Thibault Tricole": {"3DA": 89.26, "COP": 37.10, "STD": 20.0, "FDI": 1697, "F9A": 96.33, "TWS": 87.73, "RWS": 90.96},
    "Matthew Dennant": {"3DA": 90.84, "COP": 38.50, "STD": 20.0, "FDI": 1678, "F9A": 98.02, "TWS": 89.30, "RWS": 92.52},
    "Darren Beveridge": {"3DA": 90.46, "COP": 38.24, "STD": 20.0, "FDI": 1669, "F9A": 97.48, "TWS": 89.04, "RWS": 92.07},
    "Justin Hood": {"3DA": 91.36, "COP": 36.74, "STD": 20.0, "FDI": 1671, "F9A": 99.39, "TWS": 89.46, "RWS": 93.52},
    "Wesley Plaisier": {"3DA": 92.23, "COP": 41.16, "STD": 20.0, "FDI": 1732, "F9A": 99.32, "TWS": 91.54, "RWS": 93.01},
    "Steve Lennon": {"3DA": 91.38, "COP": 35.75, "STD": 20.0, "FDI": 1686, "F9A": 99.53, "TWS": 89.54, "RWS": 93.40},
    "Max Hopp": {"3DA": 88.90, "COP": 34.62, "STD": 20.0, "FDI": 1675, "F9A": 97.63, "TWS": 87.35, "RWS": 90.65},
    "Ryan Meikle": {"3DA": 90.09, "COP": 37.36, "STD": 20.0, "FDI": 1643, "F9A": 97.40, "TWS": 88.36, "RWS": 92.12},
    "James Hurrell": {"3DA": 91.95, "COP": 37.91, "STD": 20.0, "FDI": 1682, "F9A": 100.24, "TWS": 90.50, "RWS": 93.60},
    "Nick Kenny": {"3DA": 90.31, "COP": 36.67, "STD": 20.0, "FDI": 1630, "F9A": 97.98, "TWS": 89.48, "RWS": 91.22},
    "Matt Campbell": {"3DA": 91.10, "COP": 39.65, "STD": 20.0, "FDI": 1647, "F9A": 97.84, "TWS": 89.86, "RWS": 92.46},
    "Keane Barry": {"3DA": 89.45, "COP": 36.41, "STD": 20.0, "FDI": 1706, "F9A": 97.00, "TWS": 88.20, "RWS": 90.85},
    "Adam Lipscombe": {"3DA": 88.41, "COP": 38.36, "STD": 20.0, "FDI": 1638, "F9A": 95.06, "TWS": 87.79, "RWS": 89.10},
    "Darius Labanauskas": {"3DA": 88.66, "COP": 37.65, "STD": 20.0, "FDI": 1655, "F9A": 96.88, "TWS": 87.99, "RWS": 89.40},
    "Dominik Gruellich": {"3DA": 89.10, "COP": 36.72, "STD": 20.0, "FDI": 1650, "F9A": 97.77, "TWS": 87.78, "RWS": 90.59},
    "Chris Landman": {"3DA": 90.10, "COP": 37.23, "STD": 20.0, "FDI": 1657, "F9A": 98.27, "TWS": 89.31, "RWS": 90.98},
    "Owen Bates": {"3DA": 88.79, "COP": 36.82, "STD": 20.0, "FDI": 1641, "F9A": 98.01, "TWS": 87.16, "RWS": 90.61},
    "Cor Dekker": {"3DA": 87.89, "COP": 37.72, "STD": 20.0, "FDI": 1710, "F9A": 95.99, "TWS": 86.18, "RWS": 89.85},
    "Connor Scutt": {"3DA": 93.30, "COP": 39.24, "STD": 20.0, "FDI": 1692, "F9A": 101.43, "TWS": 92.47, "RWS": 94.19},
    "Beau Greaves": {"3DA": 90.57, "COP": 38.82, "STD": 20.0, "FDI": 1753, "F9A": 100.99, "TWS": 90.15, "RWS": 91.04},
    "Charlie Manby": {"3DA": 89.65, "COP": 37.62, "STD": 20.0, "FDI": 1689, "F9A": 99.36, "TWS": 88.79, "RWS": 90.58},
    "Jamai van den Herik": {"3DA": 88.11, "COP": 36.12, "STD": 20.0, "FDI": 1588, "F9A": 97.10, "TWS": 87.10, "RWS": 89.23},
    "Jurjen van der Velde": {"3DA": 87.87, "COP": 37.06, "STD": 20.0, "FDI": 1690, "F9A": 96.82, "TWS": 86.43, "RWS": 89.49},
    "Stefan Bellmont": {"3DA": 86.87, "COP": 37.69, "STD": 20.0, "FDI": 1621, "F9A": 94.28, "TWS": 85.50, "RWS": 88.42},
    "Ted Evetts": {"3DA": 88.24, "COP": 35.01, "STD": 20.0, "FDI": 1644, "F9A": 97.66, "TWS": 87.05, "RWS": 89.56},
    "Mervyn King": {"3DA": 89.34, "COP": 38.29, "STD": 20.0, "FDI": 1647, "F9A": 98.34, "TWS": 88.67, "RWS": 90.08},
    "Lisa Ashton": {"3DA": 78.80, "COP": 30.80, "STD": 20.0, "FDI": 1557, "F9A": 86.64, "TWS": 77.03, "RWS": 80.80},
    "Fallon Sherrock": {"3DA": 80.95, "COP": 32.88, "STD": 20.0, "FDI": 1591, "F9A": 89.87, "TWS": 79.92, "RWS": 82.06},
    "Noa-Lynn van Leuven": {"3DA": 81.47, "COP": 32.81, "STD": 20.0, "FDI": 1558, "F9A": 90.59, "TWS": 81.20, "RWS": 81.76},
    "Gemma Hayter": {"3DA": 79.93, "COP": 34.05, "STD": 20.0, "FDI": 1598, "F9A": 86.91, "TWS": 78.82, "RWS": 81.13},
    "Mitsuhiko Tatsunami": {"3DA": 82.18, "COP": 31.62, "STD": 20.0, "FDI": 1568, "F9A": 92.46, "TWS": 82.32, "RWS": 82.03},
    "Xiaochen Zong": {"3DA": 83.21, "COP": 31.95, "STD": 20.0, "FDI": 1586, "F9A": 93.58, "TWS": 82.90, "RWS": 83.56},
    "Nitin Kumar": {"3DA": 77.04, "COP": 32.02, "STD": 20.0, "FDI": 1547, "F9A": 87.15, "TWS": 76.92, "RWS": 77.16},
    "Lourence Ilagan": {"3DA": 86.90, "COP": 38.10, "STD": 20.0, "FDI": 1697, "F9A": 96.24, "TWS": 86.00, "RWS": 87.86},
    "Alexis Toylo": {"3DA": 86.73, "COP": 38.35, "STD": 20.0, "FDI": 1670, "F9A": 95.66, "TWS": 86.15, "RWS": 87.35},
    "Motomu Sakai": {"3DA": 86.74, "COP": 36.41, "STD": 20.0, "FDI": 1613, "F9A": 97.17, "TWS": 86.06, "RWS": 87.49},
    "Ryusei Azemoto": {"3DA": 83.28, "COP": 34.07, "STD": 20.0, "FDI": 1606, "F9A": 93.22, "TWS": 82.92, "RWS": 83.67},
    "Paul Lim": {"3DA": 85.03, "COP": 35.00, "STD": 20.0, "FDI": 1586, "F9A": 94.84, "TWS": 83.99, "RWS": 86.14},
    "Man Lok Leung": {"3DA": 87.55, "COP": 37.05, "STD": 20.0, "FDI": 0.0, "F9A": 97.51, "TWS": 86.32, "RWS": 88.87},
    "Paolo Nebrida": {"3DA": 85.58, "COP": 37.80, "STD": 20.0, "FDI": 1626, "F9A": 94.11, "TWS": 84.19, "RWS": 87.10},
    "Andy Baetens": {"3DA": 91.20, "COP": 36.04, "STD": 20.0, "FDI": 1691, "F9A": 99.83, "TWS": 89.49, "RWS": 93.09},
    "Cristo Reyes": {"3DA": 97.61, "COP": 50.00, "STD": 20.0, "FDI": 1721, "F9A": 105.31, "TWS": 95.78, "RWS": 99.78},
    "Boris Krcmar": {"3DA": 89.96, "COP": 37.81, "STD": 20.0, "FDI": 1729, "F9A": 99.50, "TWS": 89.17, "RWS": 90.82},
    "Adam Gawlas": {"3DA": 85.93, "COP": 36.96, "STD": 20.0, "FDI": 1641, "F9A": 94.82, "TWS": 84.82, "RWS": 87.13},
    "Krzysztof Kciuk": {"3DA": 84.61, "COP": 35.47, "STD": 20.0, "FDI": 1617, "F9A": 92.04, "TWS": 83.90, "RWS": 85.43},
    "Arno Merk": {"3DA": 83.30, "COP": 34.84, "STD": 20.0, "FDI": 1635, "F9A": 91.31, "TWS": 82.85, "RWS": 83.78},
    "Patrik Kovacs": {"3DA": 82.17, "COP": 35.69, "STD": 20.0, "FDI": 1607, "F9A": 90.32, "TWS": 81.54, "RWS": 82.84},
    "David Davies": {"3DA": 85.79, "COP": 33.57, "STD": 20.0, "FDI": 1523, "F9A": 95.00, "TWS": 85.86, "RWS": 85.72},
    "Alex Spellman": {"3DA": 84.65, "COP": 37.86, "STD": 20.0, "FDI": 1646, "F9A": 92.53, "TWS": 83.29, "RWS": 86.21},
    "Leonard Gates": {"3DA": 85.55, "COP": 34.86, "STD": 20.0, "FDI": 1623, "F9A": 93.85, "TWS": 84.89, "RWS": 86.28},
    "Adam Sevada": {"3DA": 89.69, "COP": 41.40, "STD": 20.0, "FDI": 1703, "F9A": 99.01, "TWS": 89.02, "RWS": 90.43},
    "David Cameron": {"3DA": 86.63, "COP": 35.55, "STD": 20.0, "FDI": 1577, "F9A": 0.0, "TWS": 0.0, "RWS": 0.0}, # Huom: F9A, TWS, RWS puuttuvat tiedoista, arvo 0
    "Stowe Buntz": {"3DA": 86.74, "COP": 37.75, "STD": 20.0, "FDI": 1675, "F9A": 94.86, "TWS": 85.05, "RWS": 88.60},
    "Jesus Salate": {"3DA": 82.69, "COP": 36.23, "STD": 20.0, "FDI": 1633, "F9A": 92.35, "TWS": 81.19, "RWS": 84.34},
    "Teemu Harju": {"3DA": 86.36, "COP": 35.29, "STD": 20.0, "FDI": 1669, "F9A": 95.87, "TWS": 85.53, "RWS": 87.28},
    "Andreas Harrysson": {"3DA": 87.89, "COP": 36.87, "STD": 20.0, "FDI": 1682, "F9A": 97.18, "TWS": 86.91, "RWS": 89.00},
    "Oskar Lukasiak": {"3DA": 85.67, "COP": 35.93, "STD": 20.0, "FDI": 1573, "F9A": 92.82, "TWS": 84.95, "RWS": 86.48},
    "Simon Whitlock": {"3DA": 86.34, "COP": 36.40, "STD": 20.0, "FDI": 1656, "F9A": 94.19, "TWS": 85.47, "RWS": 87.33},
    "Tim Pusey": {"3DA": 82.91, "COP": 34.44, "STD": 20.0, "FDI": 1614, "F9A": 91.44, "TWS": 81.78, "RWS": 84.14},
    "Joe Comito": {"3DA": 84.36, "COP": 31.04, "STD": 20.0, "FDI": 1569, "F9A": 93.59, "TWS": 82.77, "RWS": 86.07},
    "Jonny Tata": {"3DA": 86.02, "COP": 36.23, "STD": 20.0, "FDI": 1664, "F9A": 96.55, "TWS": 85.78, "RWS": 86.29},
    "David Munyua": {"3DA": 75.05, "COP": 26.79, "STD": 20.0, "FDI": 1347, "F9A": 84.62, "TWS": 73.92, "RWS": 76.31},
    "Adam Hunt": {"3DA": 89.28, "COP": 37.72, "STD": 20.0, "FDI": 1666, "F9A": 97.04, "TWS": 88.10, "RWS": 90.59},
    "Tavis Dudeney": {"3DA": 82.66, "COP": 34.51, "STD": 20.0, "FDI": 1520, "F9A": 89.03, "TWS": 81.00, "RWS": 84.52},
    "Stephen Burton": {"3DA": 89.60, "COP": 35.35, "STD": 20.0, "FDI": 1635, "F9A": 97.50, "TWS": 87.79, "RWS": 91.64},
    "Haupai Puha": {"3DA": 87.24, "COP": 37.48, "STD": 20.0, "FDI": 1618, "F9A": 95.63, "TWS": 86.16, "RWS": 88.44},
    "Mario Vandenbogaerde (Duplicate)": {"3DA": 91.13, "COP": 37.94, "STD": 20.0, "FDI": 1697, "F9A": 99.24, "TWS": 90.62, "RWS": 91.71}, # Tämä nimi on kaksoiskappale, mutta pidetään, jos sitä käytetään karsintalistassa
    
    # Huom: Listassa on 128 riviä, mutta monet nimet toistuvat / ovat eri kategorioissa. 
    # Tässä listauksessa on käytetty 96 UNIIKKIA nimeä (ja duplikaatit on huomioitu, jos niitä löytyi datasta)
}
PLAYER_NAMES = list(DEFAULT_PRESETS.keys())

# --- 3. Simulaatiofunktiot ---
# ... (Nämä pysyvät samoina)

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
        st.subheader("Pelaaja A ")
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
        st.subheader("Pelaaja B ")
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
        
        # Korjattu Altair-kaavio
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
