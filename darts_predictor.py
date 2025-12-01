import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from threading import Thread
import json
import os

# --- 1. Optimal Checkout Taulukko ---
# (Jätetty ennalleen)
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

# --- 2. Päivitetyt Pelaajaprofiilit (PDC Top 20) ---
DEFAULT_PRESETS = {
    "VALITSE PROFIILI": {"KAUSI": 95.0, "VIIMEISET 5": 95.0, "COP": 35, "STD": 18},
    "--- PDC TOP 20 (2024 Arviot) ---": {"KAUSI": 95.0, "VIIMEISET 5": 95.0, "COP": 35, "STD": 18},
    "Luke Littler (1)": {"KAUSI": 100.96, "VIIMEISET 5": 101.5, "COP": 41, "STD": 16},
    "Luke Humphries (2)": {"KAUSI": 98.50, "VIIMEISET 5": 99.0, "COP": 39, "STD": 17},
    "M. van Gerwen (3)": {"KAUSI": 97.28, "VIIMEISET 5": 98.96, "COP": 41, "STD": 18},
    "Josh Rock (4)": {"KAUSI": 98.10, "VIIMEISET 5": 98.5, "COP": 36, "STD": 18},
    "Stephen Bunting (5)": {"KAUSI": 98.04, "VIIMEISET 5": 97.8, "COP": 37, "STD": 18},
    "Gerwyn Price (6)": {"KAUSI": 97.75, "VIIMEISET 5": 97.3, "COP": 36, "STD": 19},
    "Gian van Veen (7)": {"KAUSI": 97.91, "VIIMEISET 5": 97.2, "COP": 33, "STD": 19},
    "Gary Anderson (8)": {"KAUSI": 97.41, "VIIMEISET 5": 97.8, "COP": 35, "STD": 17},
    "Chris Dobey (9)": {"KAUSI": 96.76, "VIIMEISET 5": 97.1, "COP": 34, "STD": 19},
    "Dirk van Duijvenbode (10)": {"KAUSI": 96.53, "VIIMEISET 5": 96.8, "COP": 34, "STD": 20},
    "Ross Smith (11)": {"KAUSI": 96.50, "VIIMEISET 5": 96.0, "COP": 33, "STD": 20},
    "Jonny Clayton (12)": {"KAUSI": 96.30, "VIIMEISET 5": 96.0, "COP": 34, "STD": 20},
    "Wessel Nijman (13)": {"KAUSI": 95.86, "VIIMEISET 5": 95.5, "COP": 32, "STD": 21},
    "Ryan Searle (14)": {"KAUSI": 95.76, "VIIMEISET 5": 96.0, "COP": 33, "STD": 20},
    "Rob Cross (15)": {"KAUSI": 95.75, "VIIMEISET 5": 96.5, "COP": 34, "STD": 20},
    "Nathan Aspinall (16)": {"KAUSI": 95.64, "VIIMEISET 5": 95.3, "COP": 34, "STD": 20},
    "Jermaine Wattimena (17)": {"KAUSI": 94.87, "VIIMEISET 5": 95.0, "COP": 32, "STD": 21},
    "Damon Heta (18)": {"KAUSI": 94.81, "VIIMEISET 5": 95.5, "COP": 35, "STD": 20},
    "James Wade (19)": {"KAUSI": 94.79, "VIIMEISET 5": 94.0, "COP": 38, "STD": 20},
    "Danny Noppert (20)": {"KAUSI": 94.79, "VIIMEISET 5": 95.0, "COP": 37, "STD": 20},
    "--- HARRASTAJAT ---": {"KAUSI": 95.0, "VIIMEISET 5": 95.0, "COP": 35, "STD": 18},
    "Epätasainen (Aloittelija)": {"KAUSI": 80.0, "VIIMEISET 5": 80.0, "COP": 28, "STD": 25},
    "Hyvä Harrastaja": {"KAUSI": 90.0, "VIIMEISET 5": 90.0, "COP": 33, "STD": 20}
}
PLAYER_PRESETS = DEFAULT_PRESETS.copy()
CUSTOM_PRESET_FILE = "custom_presets.json"


# --- 3. Simulaatiofunktiot (Jätetty ennalleen) ---
# (simulate_score, attempt_checkout, simulate_leg, simulate_match)
# ... (Koodi on sama kuin edellisessä vastauksessa)

def get_hit_score(segment):
    """Palauttaa heiton pistearvon."""
    if segment in ["Bull", "B"]:
        return 50
    score_value = int(segment[1:]) if len(segment) > 1 else 0
    multiplier = SCORING_MAP.get(segment[0], 1)
    return score_value * multiplier

def simulate_score(average_score, std_dev):
    """Simuloi yhden kolmen tikan heittovuoron pistemäärän."""
    score = int(np.random.normal(average_score, std_dev))
    return max(0, min(180, score))

def attempt_checkout(current_score, cop):
    """Simuloi ulosheittoyrityksen."""
    
    if current_score not in CHECKOUT_MAP or current_score <= 1:
        return current_score, False 

    # cop on todennäköisyys osua koko ulosheittoon
    if np.random.rand() < cop:
        return 0, True

    # Epäonnistuminen: simuloidaan osittaista onnistumista
    route = CHECKOUT_MAP.get(current_score, ["S20", "S20", "S20"])  # Oletus jos ei optimaalista löydy
    # Laske koko reitin pisteet (sisältää myös doublen)
    points_to_target = sum(get_hit_score(t) for t in route)
    # Simuloi osittaista onnistumista reitistä (ei aina kaikkea osuta)
    score_taken = int(points_to_target * np.random.uniform(0.3, 0.85))
    new_score = current_score - score_taken

    # Jos bustaa (alle 2), pysytään nykyisessä pisteessä (realistinen käyttäytyminen)
    if new_score < 2:
        return current_score, False

    return new_score, False
        
def simulate_leg(player_a_avg, player_a_cop, player_a_std, 
                 player_b_avg, player_b_cop, player_b_std, starts_a):
    """Simuloi yhden 501-legin."""
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
    """Simuloi koko ottelun (useita lecejä tai settejä)."""  
    
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


# --- 4. Sovelluksen luokka ---

class DartsPredictorApp:
    def __init__(self, master):
        self.master = master
        master.title("Darts-ennustin (Monte Carlo)")
        
        # Päivitetty teema & fontit
        self.THEME_COLOR = "gray20"
        self.TEXT_COLOR = "white"
        self.ACCENT_COLOR = "firebrick3"
        self.DEFAULT_FONT = ('Arial', 11)
        self.HEADER_FONT = ('Arial', 13, 'bold')
        self.RESULT_FONT = ('Courier', 12, 'bold')
        
        self.apply_theme()
        
        self.load_custom_presets() 

        # Muuttujat
        self.p_a_avg = tk.StringVar()
        self.p_a_cop = tk.StringVar()
        self.p_a_std = tk.StringVar()
        self.p_b_avg = tk.StringVar()
        self.p_b_cop = tk.StringVar()
        self.p_b_std = tk.StringVar()
        
        # Preset-valitsimet
        self.preset_a = tk.StringVar(value="VALITSE PROFIILI")
        self.preset_b = tk.StringVar(value="VALITSE PROFIILI")
        self.form_a = tk.StringVar(value="KAUSI")
        self.form_b = tk.StringVar(value="KAUSI")

        self.preset_a_data = PLAYER_PRESETS["VALITSE PROFIILI"]
        self.preset_b_data = PLAYER_PRESETS["VALITSE PROFIILI"]
        
        self.n_simulations = tk.StringVar(value="10000")
        self.match_type = tk.StringVar(value="LEG")
        self.n_legs = tk.StringVar(value="11")
        self.n_sets = tk.StringVar(value="5")
        
        self.handle_preset_change("VALITSE PROFIILI", "A") 
        self.handle_preset_change("VALITSE PROFIILI", "B")
        
        self.create_player_frames()
        self.create_match_frame()
        self.create_control_frame()
        self.create_results_frame()
    
    # --- PROFIILIEN HALLINTA ---
    
def load_custom_presets(self):
        """Lataa käyttäjän luomat profiilit tiedostosta."""
        global PLAYER_PRESETS
        if os.path.exists(CUSTOM_PRESET_FILE):
            try:
                with open(CUSTOM_PRESET_FILE, 'r') as f:
                    custom_data = json.load(f)
                PLAYER_PRESETS = DEFAULT_PRESETS.copy()
                PLAYER_PRESETS.update(custom_data)
            except Exception as e:
                messagebox.showerror("Virhe", f"Mukautettujen profiilien lataaminen epäonnistui: {e}")

    def save_custom_presets(self):
        """Tallentaa vain käyttäjän luomat profiilit JSON-tiedostoon."""
        custom_data = {
            k: v for k, v in PLAYER_PRESETS.items() 
            if k not in DEFAULT_PRESETS
        }
        try:
            with open(CUSTOM_PRESET_FILE, 'w') as f:
                json.dump(custom_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Virhe", f"Mukautettujen profiilien tallentaminen epäonnistui: {e}")


    def open_create_profile_dialog(self):
        """Avaa dialogi uuden pelaajaprofiilin luomista varten."""
        current_avg = self.p_a_avg.get().replace(',', '.') 
        current_cop = self.p_a_cop.get()
        current_std = self.p_a_std.get()
        
        dialog = tk.Toplevel(self.master, bg=self.THEME_COLOR)
        dialog.title("Luo Uusi Profiili")
        dialog.transient(self.master)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(padx=10, pady=10)

        name_var = tk.StringVar(value="UUSI PROFIILI")
        avg_var = tk.StringVar(value=current_avg)
        cop_var = tk.StringVar(value=current_cop)
        std_var = tk.StringVar(value=current_std)

        # Nimi
        ttk.Label(frame, text="Profiilin Nimi:", font=self.DEFAULT_FONT).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(frame, textvariable=name_var, width=20, font=self.DEFAULT_FONT).grid(row=0, column=1, padx=5, pady=5)
        
        # 3DA
        ttk.Label(frame, text="3DA (Kausi/Oletus):", font=self.DEFAULT_FONT).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(frame, textvariable=avg_var, width=20, font=self.DEFAULT_FONT).grid(row=1, column=1, padx=5, pady=5)

        # COP (%)
        ttk.Label(frame, text="COP (%):", font=self.DEFAULT_FONT).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(frame, textvariable=cop_var, width=20, font=self.DEFAULT_FONT).grid(row=2, column=1, padx=5, pady=5)

        # STD DEV
        ttk.Label(frame, text="STD DEV:", font=self.DEFAULT_FONT).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(frame, textvariable=std_var, width=20, font=self.DEFAULT_FONT).grid(row=3, column=1, padx=5, pady=5)
        
        # Tallenna/Peruuta
        save_button = ttk.Button(frame, text="Tallenna Profiili", 
                                 command=lambda: self.process_new_profile(dialog, name_var.get(), avg_var.get(), cop_var.get(), std_var.get()))
        save_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        dialog.wait_window() 

    def process_new_profile(self, dialog, name, avg_str, cop_str, std_str):
        """Validioi tiedot ja tallentaa uuden profiilin."""
        global PLAYER_PRESETS
        avg_str = avg_str.replace(',', '.')

        try:
            name = name.strip()
            if not name or len(name) < 3:
                 raise ValueError("Profiilin nimi on liian lyhyt.")
            if name in PLAYER_PRESETS:
                 raise ValueError(f"Nimi '{name}' on jo käytössä. Valitse toinen nimi.")

            avg = float(avg_str)
            cop = int(cop_str)
            std = float(std_str)
            
            new_profile = {
                "KAUSI": avg, 
                "VIIMEISET 5": avg, 
                "COP": cop, 
                "STD": std
            }

            PLAYER_PRESETS[name] = new_profile
            self.save_custom_presets() 
            self.update_preset_comboboxes()
            
            messagebox.showinfo("Onnistui", f"Profiili '{name}' tallennettu.")
            dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Virhe syötteessä", f"Tarkista syötearvot: {e}")
        except Exception as e:
            messagebox.showerror("Virhe", f"Odottamaton virhe tallennuksessa: {e}")

    def update_preset_comboboxes(self):
        """Päivittää molemmat preset-valikot uusilla arvoilla."""
        new_values = list(PLAYER_PRESETS.keys())
        self.preset_combobox_a['values'] = new_values
        self.preset_combobox_b['values'] = new_values

    # --- PÄIVITETYT GUI-elementit ---

    def apply_theme(self):
        """Asettaa tumman teeman ja suuremmat fontit."""
        s = ttk.Style()
        s.theme_use('clam')
        
        # Määritellään isommat fontit
        s.configure('TFrame', background=self.THEME_COLOR)
        s.configure('TLabel', background=self.THEME_COLOR, foreground=self.TEXT_COLOR, font=self.DEFAULT_FONT)
        s.configure('TEntry', fieldbackground="gray30", foreground=self.TEXT_COLOR, font=self.DEFAULT_FONT)
        s.configure('TButton', background=self.ACCENT_COLOR, foreground=self.TEXT_COLOR, font=self.DEFAULT_FONT)
        s.map('TButton', background=[('active', 'red4')])
        s.configure('TRadiobutton', background=self.THEME_COLOR, foreground=self.TEXT_COLOR, font=self.DEFAULT_FONT)
        s.configure('TLabelframe', background=self.THEME_COLOR, foreground=self.TEXT_COLOR, font=self.HEADER_FONT)
        s.configure('TLabelframe.Label', background=self.THEME_COLOR, foreground=self.TEXT_COLOR, font=self.HEADER_FONT)
        s.configure('TCombobox', fieldbackground="gray30", foreground=self.TEXT_COLOR, selectbackground=self.ACCENT_COLOR, selectforeground="white", font=self.DEFAULT_FONT)
        s.configure('Horizontal.TProgressbar', background=self.ACCENT_COLOR, troughcolor='gray35', bordercolor='gray25')
        
        self.master.configure(bg=self.THEME_COLOR)

    def handle_preset_change(self, preset_name, player):
        """Lataa valitun profiilin tiedot."""
        if "---" in preset_name: # Estä otsikoiden valinta
            return

        data = PLAYER_PRESETS.get(preset_name, {})
        
        if player == "A":
            self.p_a_cop.set(data.get("COP", "35"))
            self.p_a_std.set(data.get("STD", "18"))
            self.preset_a_data = data
            if "KAUSI" in data:
                 self.form_a.set("KAUSI") 
        else:
            self.p_a_cop.set(data.get("COP", "35"))
            self.p_b_std.set(data.get("STD", "18"))
            self.preset_b_data = data
            if "KAUSI" in data:
                 self.form_b.set("KAUSI") 

        self.update_3da_entry(player) 

    def update_3da_entry(self, player_id):
        """Päivittää 3DA-syötekentän valitun kauden/muodon perusteella."""
        if player_id == "A":
            data = self.preset_a_data
            form = self.form_a.get()
            target_var = self.p_a_avg
        else:
            data = self.preset_b_data
            form = self.form_b.get()
            target_var = self.p_b_avg

        new_avg = data.get(form, data.get("KAUSI", 95.0)) 
        target_var.set(f"{new_avg:.2f}")

    def create_player_frames(self):
        """Luo kehykset pelaajien syötteille ja preseteille."""
        p_frame = ttk.Frame(self.master, padding="10")
        p_frame.pack(fill='x', padx=10, pady=5)
        
        frame_a = ttk.LabelFrame(p_frame, text="Pelaaja A", padding="10")
        frame_a.pack(side="left", padx=10, fill='x', expand=True)
        self.create_player_controls(frame_a, "A")

        frame_b = ttk.LabelFrame(p_frame, text="Pelaaja B", padding="10")
        frame_b.pack(side="right", padx=10, fill='x', expand=True)
        self.create_player_controls(frame_b, "B")
        
        create_profile_btn = ttk.Button(self.master, text="➕ Luo/Tallenna Profiili", 
                                        command=self.open_create_profile_dialog)
        create_profile_btn.pack(pady=5, padx=10)


    def create_player_controls(self, parent_frame, player_id):
        """Luo kaikki syötekentät yhdelle pelaajalle."""
        
        if player_id == "A":
            avg_var, cop_var, std_var = self.p_a_avg, self.p_a_cop, self.p_a_std
            preset_var, form_var = self.preset_a, self.form_a
        else:
            avg_var, cop_var, std_var = self.p_b_avg, self.p_b_cop, self.p_b_std
            preset_var, form_var = self.preset_b, self.form_b

        # 1. Preset valikko
        ttk.Label(parent_frame, text="Profiili:", font=self.DEFAULT_FONT).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
preset_combobox = ttk.Combobox(parent_frame, textvariable=preset_var, values=list(PLAYER_PRESETS.keys()), state="readonly", width=25)
        preset_combobox.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        if player_id == "A":
            self.preset_combobox_a = preset_combobox
        else:
            self.preset_combobox_b = preset_combobox

        # 2. 3DA Muoto valikko (KAUSI / VIIMEISET 5)
        ttk.Label(parent_frame, text="3DA Muoto:", font=self.DEFAULT_FONT).grid(row=1, column=0, sticky='w', padx=5, pady=5) 
        form_combobox = ttk.Combobox(parent_frame, textvariable=form_var, values=["KAUSI", "VIIMEISET 5"], state="readonly", width=15)
        form_combobox.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        
        # Bindingit
        preset_combobox.bind("<<ComboboxSelected>>", lambda event: self.handle_preset_change(preset_var.get(), player_id))
        form_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_3da_entry(player_id))

        # Syötekentät
        self.create_player_inputs(parent_frame, "3DA:", avg_var, row=2)
        self.create_player_inputs(parent_frame, "COP (%):", cop_var, row=3)
        self.create_player_inputs(parent_frame, "STD DEV:", std_var, row=4)

    def create_player_inputs(self, parent_frame, label_text, variable, row):
        """Luo Label ja Entry elementit."""
        ttk.Label(parent_frame, text=label_text, font=self.DEFAULT_FONT).grid(row=row, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=variable, width=10, font=self.DEFAULT_FONT).grid(row=row, column=1, sticky='e', padx=5, pady=5)

    def create_match_frame(self):
        """Luo kehyksen ottelun muodon ja pituuden valinnalle."""
        m_frame = ttk.LabelFrame(self.master, text="Ottelun Muoto", padding="10")
        m_frame.pack(fill='x', padx=10, pady=5)
        
ttk.Radiobutton(m_frame, text="Paras N Legistä", variable=self.match_type, value="LEG", command=self.toggle_match_length).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Radiobutton(m_frame, text="Paras N Setistä", variable=self.match_type, value="SET", command=self.toggle_match_length).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        
ttk.Label(m_frame, text="N (Leg):", font=self.DEFAULT_FONT).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_legs = ttk.Entry(m_frame, textvariable=self.n_legs, width=5, font=self.DEFAULT_FONT)
        self.entry_legs.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
ttk.Label(m_frame, text="N (Set):", font=self.DEFAULT_FONT).grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_sets = ttk.Entry(m_frame, textvariable=self.n_sets, width=5, font=self.DEFAULT_FONT)
        self.entry_sets.grid(row=1, column=3, sticky='w', padx=5, pady=5)
        
    def toggle_match_length(self):
        """Vaihtaa näkyvissä olevan pituus-kentän ottelun muodon mukaan."""
        is_set = self.match_type.get() == "SET"
        
        # Tarkista, että kentät ovat olemassa ennen niiden käsittelyä
        if hasattr(self, 'entry_legs') and hasattr(self, 'entry_sets'):
            self.entry_legs.state(['disabled'] if is_set else ['!disabled'])
            self.entry_sets.state(['!disabled'] if is_set else ['disabled'])

    def create_control_frame(self):
        """Luo kehyksen simulaation ohjaukselle ja edistymispalkille."""
        c_frame = ttk.Frame(self.master, padding="10")
        c_frame.pack(fill='x', padx=10, pady=5)
        
ttk.Label(c_frame, text="Simulaatioiden määrä:", font=self.DEFAULT_FONT).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(c_frame, textvariable=self.n_simulations, width=10, font=self.DEFAULT_FONT).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        self.start_button = ttk.Button(c_frame, text="Aloita Simulaatio", command=self.start_simulation)
        self.start_button.grid(row=0, column=2, padx=20, sticky='e')
        
        # Edistymispalkki
        self.progress_bar = ttk.Progressbar(c_frame, orient='horizontal', length=300, mode='determinate', style='Horizontal.TProgressbar')
        self.progress_bar.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')

    def create_results_frame(self):
        """Luo kehyksen tulosten näyttämiselle."""
        r_frame = ttk.LabelFrame(self.master, text="Tulokset", padding="10")
        r_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.status_label = ttk.Label(r_frame, text="Valmis. Odota parametreja...", foreground="yellow", font=self.DEFAULT_FONT)
        self.status_label.pack(pady=5)
        
        self.result_text = tk.Text(r_frame, height=10, bg="gray15", fg="white", borderwidth=0, relief="flat", font=self.RESULT_FONT)
        self.result_text.pack(fill='both', expand=True)

    def start_simulation(self):
        """Käynnistää simulaation uudessa säikeessä."""
        try:
            p_a_avg_str = self.p_a_avg.get().replace(',', '.')
            p_b_avg_str = self.p_b_avg.get().replace(',', '.')
            n_sims = int(self.n_simulations.get())

            params = {
                'P_A_AVG': float(p_a_avg_str),
                'P_A_COP': float(self.p_a_cop.get()) / 100.0,
                'P_A_STD': float(self.p_a_std.get()),
                'P_B_AVG': float(p_b_avg_str),
                'P_B_COP': float(self.p_b_cop.get()) / 100.0,
                'P_B_STD': float(self.p_b_std.get()),
                'N_SIMULATIONS': n_sims,
                'MATCH_TYPE': self.match_type.get(),
                'N_LEGS': int(self.n_legs.get()) if self.match_type.get() == "LEG" else None,
                'N_SETS': int(self.n_sets.get()) if self.match_type.get() == "SET" else None
            }
            
            if params['MATCH_TYPE'] == "LEG" and params['N_LEGS'] % 2 == 0:
                raise ValueError("Legien määrän (N) täytyy olla pariton.")
            if params['MATCH_TYPE'] == "SET" and params['N_SETS'] % 2 == 0:
                raise ValueError("Settien määrän (N) täytyy olla pariton.")

            self.start_button.config(text="Simuloidaan...", state="disabled")
            self.status_label.config(text=f"Simulaatio käynnissä ({n_sims} kierrosta)...", foreground="cyan")
            self.result_text.delete(1.0, tk.END)
            
            # Aseta edistymispalkin maksimi ja arvo nollaan
            self.progress_bar['maximum'] = n_sims
            self.progress_bar['value'] = 0

            self.sim_thread = Thread(target=self.run_monte_carlo, args=(params,))
            self.sim_thread.start()

        except ValueError as e:
            messagebox.showerror("Virhe syötteessä", f"Tarkista syötearvot:\n{e}")
        except Exception as e:
            messagebox.showerror("Odottamaton virhe", str(e))

    def run_monte_carlo(self, params):
        """Suorittaa Monte Carlo -simulaation ja päivittää edistymispalkkia."""
        a_wins = 0
        b_wins = 0
        n = params['N_SIMULATIONS']
        
        # Päivitys joka 1000. iteraatio tai useammin, jos iteraatioita on vähemmän.
        UPDATE_INTERVAL = max(1, n // 200) 
        
        for i in range(n):
            winner = simulate_match(params)
            
            if winner == "A":
                a_wins += 1
            else:
                b_wins += 1
            
            # Päivitä edistymispalkki
            if (i + 1) % UPDATE_INTERVAL == 0:
                # after-kutsu varmistaa, että GUI-päivitys tapahtuu pääsäikeessä
                self.master.after(0, lambda current_i=i: self.progress_bar.config(value=current_i + 1))
        
        # Varmista, että palkki on täynnä lopussa
        self.master.after(0, lambda: self.progress_bar.config(value=n))
        
        self.master.after(0, lambda: self.show_results(a_wins, b_wins, n))

    def show_results(self, a_wins, b_wins, n):
        """Näyttää tulokset ja palauttaa GUI:n alkutilaan."""
        prob_a = a_wins / n
        prob_b = b_wins / n
        
        # Haetaan valitut pelaajat
        p_a_name = self.preset_a.get() if self.preset_a.get() != "VALITSE PROFIILI" else "Pelaaja A"
        p_b_name = self.preset_b.get() if self.preset_b.get() != "VALITSE PROFIILI" else "Pelaaja B"

        # Päätellään todennäköisin voittaja tai tasapeli
        if prob_a > prob_b:
            likely = 'A'
        elif prob_b > prob_a:
            likely = 'B'
        else:
            likely = 'Tasapeli'

        result_str = (
            f"✨ LOPULLINEN ENNUSTE ({n} simulaatiota) ✨\n"
            f"----------------------------------------------------------------------\n"
            f"{p_a_name:<30} | {p_b_name}\n"
            f"Voittotodennäköisyys: {prob_a:<20.2%} | {prob_b:.2%}\n"
            f"Voittoja: {a_wins:<30} | {b_wins}\n" 
            f"----------------------------------------------------------------------\n"
            f"Todennäköisin voittaja: {likely}"
        )
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_str)
        
        self.start_button.config(text="Aloita Simulaatio", state="normal")
        self.status_label.config(text="Simulaatio valmis.", foreground="lime green")


if __name__ == "__main__":
    root = tk.Tk()
    app = DartsPredictorApp(root)
    root.mainloop()
