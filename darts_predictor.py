import streamlit as st
import pandas as pd
import numpy as np
import os 

# --- 0. ENNUSTUSTEKSIN APUFUNKTIOT ---

def get_score_prediction_text(prob_win_a, match_format, legs_or_sets_to_win, player_a_name, player_b_name):
    """Generates a text-based score prediction based on win probability (Pelaaja A:n näkökulmasta)."""
    P = prob_win_a * 100
    W = legs_or_sets_to_win # Legs or Sets to win
    
    # 1. Määritellään LEG-muodon ennusteet
    if match_format.startswith('BO Leg'):
        W_loss_close = W - 1 # Lähin häviötulos (esim. BO25, 13-12)
        W_loss_mid = W - 2  # Keskihäviötulos (esim. BO25, 13-11)
        
        # Määritetään voiton kynnysarvot (A voittaa)
        if P > 80:
            win_msg = f"{player_a_name}n selkeä voitto."
            score_example = f"({W}-0, {W}-1 tai {W}-2 leg-tulos)."
        elif P > 65:
            win_msg = f"{player_a_name}n todennäköinen voitto."
            score_example = f"({W}-2, {W}-3 tai {W}-4 leg-tulos)."
        elif P > 50.5:
            win_msg = f"Tasainen {player_a_name}n voitto."
            score_example = f"({W}-{W_loss_mid} tai {W}-{W_loss_close} leg-tulos)."
        # Määritetään häviön kynnysarvot (B voittaa)
        elif P < 19.5:
            win_msg = f"{player_b_name}n selkeä voitto."
            score_example = f"(esim. 0-{W} tai 1-{W} leg-tulos)."
        elif P < 35:
            win_msg = f"{player_b_name}n todennäköinen voitto."
            score_example = f"(esim. 4-{W} tai 3-{W} leg-tulos)."
        else:
            win_msg = "Erittäin tasainen ottelu."
            score_example = f"({W_loss_close}-{W} tai {W}-{W_loss_close} leg-tulos)."

    # 2. Määritellään SET-muodon ennusteet (W = voittoon tarvittava settien määrä)
    else: # Set-malli
        S = W # Sets to win
        S_Loss_Tight = S - 1 # Tiukin mahdollinen häviö (esim. 7-6)
        S_Loss_Mid = S - 2   # Keskihäviö (esim. 7-5)

        if P > 80:
            win_msg = f"{player_a_name}n selkeä voitto."
            score_example = f"({S}-0 tai {S}-1 seteissä)."
        elif P > 65:
            win_msg = f"{player_a_name}n todennäköinen voitto."
            # Käytetään dynaamisia häviöasetuksia, esim. 7-2, 7-3, 7-4.
            score_example = f"({S}-2, {S}-3 tai {S}-4 seteissä)."
        elif P > 50.5:
            win_msg = f"Tasainen {player_a_name}n voitto."
            # TIUKIN MAHDOLLINEN VOITTO: S - (S-1)
            score_example = f"({S}-{S_Loss_Tight} seteissä)." 
        elif P < 19.5:
            win_msg = f"{player_b_name}n selkeä voitto."
            score_example = f"(esim. 0-{S} tai 1-{S} seteissä)."
        elif P < 35:
            win_msg = f"{player_b_name}n todennäköinen voitto."
            score_example = f"(esim. 4-{S} tai 3-{S} seteissä)."
        else:
            win_msg = "Erittäin tasainen ottelu."
            score_example = f"({S_Loss_Tight}-{S} tai {S}-{S_Loss_Tight} seteissä)."

    return f"{win_msg} {score_example}"

# --- 1. DATAN KÄSITTELY FUNKTIOT ---

@st.cache_resource
def load_data(file_path):
    """Lataa pelaajadatan CSV-tiedostosta ja tekee tarvittavat esikäsittelyt."""
    
    try:
        df = pd.read_csv(file_path, sep=',') 
        
        if 'Pelaajan Nimi' in df.columns:
            # Puhdistetaan pelaajanimistä mahdolliset järjestysnumerot (esim. "1. ")
            df['Pelaajan Nimi'] = df['Pelaajan Nimi'].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)

        # FDI sisällytetty numeerisiin sarakkeisiin
        float_cols = ['KAUSI 2025 (3DA)', 'COP (%)', 'STD (Hajonta)', 'FDI', 'TWS KA', 'RWS KA']
        
        for col in float_cols:
            if col in df.columns:
                # Korvataan lainausmerkit ja pilkut pisteiksi desimaalien takia
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['Pelaajan Nimi']).reset_index(drop=True)
        
        st.session_state['player_data'] = df
        st.session_state['all_players'] = df['Pelaajan Nimi'].tolist()
        st.success(f"Data ladattu onnistuneesti! ({len(df)} pelaajaa)")
        return df
        
    except FileNotFoundError:
        st.error(f"❌ Virhe: Tiedostoa '{file_path}' ei löydy. Tarkista tiedoston nimi ja polku.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Virhe datan käsittelyssä. Tarkista, että tiedosto on oikeassa CSV-muodossa (erotin: pilkku, desimaali: pilkku/piste): {e}")
        return pd.DataFrame()


def load_player_data(player_name):
    """Hakee pelaajan tilastot DataFrame-objektista."""
    df = st.session_state.get('player_data', pd.DataFrame())
    if player_name and not df.empty:
        row = df[df['Pelaajan Nimi'] == player_name]
        if not row.empty:
            return row.iloc[0].to_dict()
    return {} 

def get_float_val(data, key, default_value):
    """Hakee arvon pelaajan tiedoista ja palauttaa float-luvun."""
    if data and key in data:
        value = data[key]
        if pd.notna(value):
            return float(value)
            
    return float(default_value)


def set_player_stats(player_key):
    """Takaisinkutsufunktio, joka lataa valitun pelaajan tiedot ja asettaa ne Streamlitin sessiotilaan."""
    player_name = st.session_state[player_key]
    player_data = load_player_data(player_name)
    
    stats_map = {
        'KAUSI 2025 (3DA)': (90.0, '3da'),
        'COP (%)': (35.0, 'COP_%'),
        'STD (Hajonta)': (20.0, 'STD_Hajonta'),
        'FDI': (1500.0, 'FDI'), 
        'TWS KA': (90.0, 'TWS_KA'),
        'RWS KA': (90.0, 'RWS_KA'),
    }

    prefix = player_key.split('_')[0]
    
    for stat_key, (default_val, suffix) in stats_map.items():
        session_key = f"{prefix}_{suffix}"
        st.session_state[session_key] = get_float_val(player_data, stat_key, default_val)


# --- 2. ENNUSTUSMALLI (MONTE CARLO) ---

def calculate_leg_win_probability(attacker_stats, defender_stats, type='TWS'):
    """
    Laskee Legivoiton Todennäköisyyden (LWP) suhteellisen vahvuuden perusteella.
    Käyttää päivitettyä FDI-painotusta (0.005) ja aloittajan etua (1.08).
    """
    
    # 🟢 VAHVUUSMUUTTUJIEN MÄÄRITTELY (Painotukset)
    WEIGHT_SCORING = 1.0  
    WEIGHT_COP = 0.075     
    WEIGHT_3DA = 0.03    
    WEIGHT_FDI = 0.25    # PÄIVITETTY: Käyttäjän pyytämä FDI-painotus
    
    # PÄIVITETTY: Aloittajan etu kerroin
    TWS_ADVANTAGE_MULTIPLIER = 1.44 
    
    # 1. Määritellään hyökkääjän ja vastustajan legin pisteytysvoima TWS/RWS roolin mukaan
    if type == 'TWS': # Pelaaja A aloittaa legin
        attacker_score = attacker_stats['TWS KA'] * WEIGHT_SCORING * TWS_ADVANTAGE_MULTIPLIER
        defender_score = defender_stats['RWS KA'] * WEIGHT_SCORING
    else: # type == 'RWS' (Pelaaja B aloittaa legin)
        attacker_score = attacker_stats['RWS KA'] * WEIGHT_SCORING
        defender_score = defender_stats['TWS KA'] * WEIGHT_SCORING * TWS_ADVANTAGE_MULTIPLIER

    # 2. Lisätään hienosäätö COP, 3DA ja FDI perusteella
    
    # Hyökkääjän FDI-kontribuutio
    fdi_contribution_a = attacker_stats.get('FDI', 0) * WEIGHT_FDI
    attacker_boost = (attacker_stats['COP (%)'] * WEIGHT_COP) + \
                     (attacker_stats['KAUSI 2025 (3DA)'] * WEIGHT_3DA) + \
                     fdi_contribution_a
    
    # Vastustajan FDI-kontribuutio
    fdi_contribution_b = defender_stats.get('FDI', 0) * WEIGHT_FDI
    defender_boost = (defender_stats['COP (%)'] * WEIGHT_COP) + \
                     (defender_stats['KAUSI 2025 (3DA)'] * WEIGHT_3DA) + \
                     fdi_contribution_b
    
    total_attacker_strength = attacker_score + attacker_boost
    total_defender_strength = defender_score + defender_boost
    
    total_strength = total_attacker_strength + total_defender_strength
    if total_strength <= 0:
        return 0.5
        
    prob_win = total_attacker_strength / total_strength
    
    return prob_win


def simulate_game(a_stats, b_stats, match_format, start_player, iterations=50000):
    """
    Simuloi koko ottelu Monte Carlo -tekniikalla.
    start_player: 1 jos A aloittaa, -1 jos B aloittaa.
    """
    
    # Probabilities for A winning the leg:
    twp_a = calculate_leg_win_probability(a_stats, b_stats, type='TWS') # A starts leg (TWS)
    rwp_a = calculate_leg_win_probability(a_stats, b_stats, type='RWS') # B starts leg (RWS)
    
    a_match_wins = 0
    
    if match_format == 'BO Leg (esim. BO9, 5 legiä voittoon)':
        legs_to_win = st.session_state['legs_to_win']
        
        for _ in range(iterations):
            current_start_player = start_player
            a_legs = 0
            b_legs = 0
            leg_count = 0
            
            while a_legs < legs_to_win and b_legs < legs_to_win:
                
                # Leg format: Starter alternates every leg (based on match start)
                leg_starter_a = (current_start_player == 1 and leg_count % 2 == 0) or \
                                (current_start_player == -1 and leg_count % 2 != 0)
                
                if leg_starter_a:
                    prob_a_win = twp_a
                else:
                    prob_a_win = rwp_a
                
                if np.random.rand() < prob_a_win:
                    a_legs += 1
                else:
                    b_legs += 1
                
                leg_count += 1
                
            if a_legs > b_legs:
                a_match_wins += 1
                
    elif match_format == 'Set-malli (esim. BO5 set, setti on BO5 leg)':
        sets_to_win = st.session_state['sets_to_win']
        
        for _ in range(iterations):
            current_start_player = start_player # Match starter
            a_sets = 0
            b_sets = 0
            
            while a_sets < sets_to_win and b_sets < sets_to_win:
                
                # Simulaatio Yhdestä Setistä (BO5 Leg, 3 legiä voittoon)
                a_legs = 0
                b_legs = 0
                leg_count_in_set = 0
                
                set_starter_a = (current_start_player == 1) # Tarkista, kuka aloittaa setin
                
                while a_legs < 3 and b_legs < 3: 
                    
                    # Logiikka legien aloittajan vuorotteluun setin sisällä
                    if set_starter_a:
                        # Jos A aloittaa setin, A aloittaa parilliset legity (0, 2, 4)
                        leg_starter_a = (leg_count_in_set % 2 == 0)
                    else:
                        # Jos B aloittaa setin, B aloittaa parilliset legity, eli A aloittaa parittomat
                        leg_starter_a = (leg_count_in_set % 2 != 0)

                    # TWS/RWS roolin asetus
                    if leg_starter_a:
                        prob_a_win = twp_a
                    else:
                        prob_a_win = rwp_a
                        
                    if np.random.rand() < prob_a_win:
                        a_legs += 1
                    else:
                        b_legs += 1
                        
                    leg_count_in_set += 1
                    
                if a_legs > b_legs:
                    a_sets += 1
                else:
                    b_sets += 1
                    
                # Vuorotellaan seuraavan setin aloittaja (Match starter vaihtuu)
                current_start_player *= -1 

            if a_sets > b_sets:
                a_match_wins += 1

    return a_match_wins / iterations


# --- 3. STREAMLIT PÄÄFUNKTIO ---

def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("🎯 Darts-ottelun Ennustaja (Monte Carlo Simulaatio)")
    
    # 💾 Datan lataus
    st.markdown("### 💾 Datan lataus")
    
    # Oletettu tiedostonimi saatavilla olevasta datasta
    default_file_path = "MM 25.csv"
    
    data_file_path = st.text_input(
        "Syötä pelaajadataa sisältävän CSV-tiedoston nimi tai polku:",
        value=default_file_path,
        key='data_file_path_input'
    )
    
    # Latausnappi
    if st.button("Lataa Data Uudelleen"):
        if 'player_data' in st.session_state:
            del st.session_state['player_data']
        st.cache_resource.clear()
        st.rerun() 
        
    # Ladataan data, jos se puuttuu
    if 'player_data' not in st.session_state or st.session_state['player_data'].empty:
        df = load_data(data_file_path)
        if df.empty:
            return 
    
    # --- UI JATKUU VAIN, JOS DATA ON LADATTU ---
    st.markdown("---")
    st.markdown("### Ottelumuoto ja Simulaation Asetukset")
    
    all_players = st.session_state.get('all_players', ["Muokkaa itse"])
    
    # Initial player state setup (ensures stats are loaded when players are selected)
    def get_initial_player_name(key, all_players):
        if key not in st.session_state or st.session_state[key] not in all_players:
            # Yritetään hakea nimi ilman numeroa (esim. "Luke Littler") jos listassa on "1. Luke Littler"
            clean_name = st.session_state.get(key, all_players[0] if all_players else "Muokkaa itse").split('. ', 1)[-1]
            if clean_name in all_players:
                return clean_name
            return all_players[0] if all_players else "Muokkaa itse"
        return st.session_state[key]
        
    if 'a_name' not in st.session_state or st.session_state['a_name'] not in all_players:
        st.session_state['a_name'] = get_initial_player_name('a_name', all_players)
        set_player_stats('a_name')
        
    if 'b_name' not in st.session_state or st.session_state['b_name'] not in all_players:
        st.session_state['b_name'] = get_initial_player_name('b_name', all_players)
        if st.session_state['a_name'] == st.session_state['b_name'] and len(all_players) > 1:
             # Asetetaan Pelaaja B oletuksena toiseksi pelaajaksi jos A ja B ovat samat
             st.session_state['b_name'] = all_players[1] if len(all_players) > 1 else st.session_state['a_name']
        set_player_stats('b_name')
        
    # Otteluformaatin asetukset
    if 'match_format' not in st.session_state:
        st.session_state['match_format'] = 'BO Leg (esim. BO9, 5 legiä voittoon)'
    if 'legs_to_win' not in st.session_state:
        st.session_state['legs_to_win'] = 5
    if 'sets_to_win' not in st.session_state:
        st.session_state['sets_to_win'] = 3

    
    col_settings1, col_settings2 = st.columns(2) 

    with col_settings1:
        match_format = st.selectbox(
            "Ottelun Formaatti",
            ['BO Leg (esim. BO9, 5 legiä voittoon)', 'Set-malli (esim. BO5 set, setti on BO5 leg)'], 
            key='match_format'
        )

    with col_settings2:
        if match_format == 'BO Leg (esim. BO9, 5 legiä voittoon)':
            legs_to_win = st.number_input(
                "Legiä voittoon (esim. BO9 -> 5)",
                min_value=1, max_value=50, step=1, key='legs_to_win'
            )
            st.caption(f"Simuloidaan Best of {legs_to_win * 2 - 1} legiä.")
        else:
            sets_to_win = st.number_input(
                "Settiä voittoon (esim. BO5 -> 3)",
                min_value=1, max_value=15, step=1, key='sets_to_win'
            )
            st.caption(f"Simuloidaan Best of {sets_to_win * 2 - 1} settiä (setti on **BO5 leg**, eli **3 legiä voittoon**).")
            
        
    # Simulaatioiden määrä 50 000
    N_ITERATIONS = st.number_input(
        "Simulaatioiden Määrä (N)",
        min_value=100, max_value=100000, step=500, value=50000 
    )

    st.markdown("---")
    
    col1, col2 = st.columns(2)

    # --- Pelaaja A ---
    with col1:
        st.header("Pelaaja A")
        
        try:
            # Haetaan indeksi ilman numeroa, jos listassa on numeroita
            clean_name_a = st.session_state['a_name'].split('. ', 1)[-1]
            default_a_index = all_players.index(next((p for p in all_players if clean_name_a in p), st.session_state['a_name']))
        except ValueError:
             default_a_index = 0

        player_a_name = st.selectbox(
            "Valitse Pelaaja A", 
            all_players, 
            index=default_a_index, 
            key='a_name', 
            on_change=set_player_stats,
            args=('a_name',)
        )
        
        st.subheader("Tilastot")
        
        st.number_input("Kauden 3-darts Average (3DA)", min_value=60.0, max_value=120.0, step=0.01, key='a_3da', format="%.2f")
        st.number_input("COP (Checkout %)", min_value=10.0, max_value=80.0, step=0.01, key='a_COP_%', format="%.2f")
        st.number_input("STD (Hajonta)", min_value=10.0, max_value=40.0, step=0.01, key='a_STD_Hajonta', format="%.2f")
        st.number_input("TWS KA (Avg. Score / Leg Started)", min_value=60.0, max_value=120.0, step=0.01, key='a_TWS_KA', format="%.2f")
        st.number_input("RWS KA (Avg. Score / Leg Opponent Started)", min_value=60.0, max_value=120.0, step=0.01, key='a_RWS_KA', format="%.2f")
        st.number_input("FDI (Elo-vastine)", min_value=1000.0, max_value=3000.0, step=1.0, key='a_FDI', format="%.1f")
        
        a_stats = {
            'TWS KA': st.session_state['a_TWS_KA'], 
            'RWS KA': st.session_state['a_RWS_KA'], 
            'KAUSI 2025 (3DA)': st.session_state['a_3da'],
            'COP (%)': st.session_state['a_COP_%'], 
            'STD (Hajonta)': st.session_state['a_STD_Hajonta'],
            'FDI': st.session_state['a_FDI']
        }


    # --- Pelaaja B ---
    with col2:
        st.header("Pelaaja B")
        
        try:
            clean_name_b = st.session_state['b_name'].split('. ', 1)[-1]
            default_b_index = all_players.index(next((p for p in all_players if clean_name_b in p), st.session_state['b_name']))
        except ValueError:
             default_b_index = 0
             
        # Ongelmallinen lohko poistettu.

        player_b_name = st.selectbox(
            "Valitse Pelaaja B", 
            all_players, 
            index=default_b_index, 
            key='b_name', 
            on_change=set_player_stats,
            args=('b_name',)
        )
        
        st.subheader("Tilastot")

        st.number_input("Kauden 3-darts Average (3DA)", min_value=60.0, max_value=120.0, step=0.01, key='b_3da', format="%.2f")
        st.number_input("COP (Checkout %)", min_value=10.0, max_value=80.0, step=0.01, key='b_COP_%', format="%.2f")
        st.number_input("STD (Hajonta)", min_value=10.0, max_value=40.0, step=0.01, key='b_STD_Hajonta', format="%.2f")
        st.number_input("TWS KA (Avg. Score / Leg Started)", min_value=60.0, max_value=120.0, step=0.01, key='b_TWS_KA', format="%.2f")
        st.number_input("RWS KA (Avg. Score / Leg Opponent Started)", min_value=60.0, max_value=120.0, step=0.01, key='b_RWS_KA', format="%.2f")
        st.number_input("FDI (Elo-vastine)", min_value=1000.0, max_value=3000.0, step=1.0, key='b_FDI', format="%.1f")

        b_stats = {
            'TWS KA': st.session_state['b_TWS_KA'], 
            'RWS KA': st.session_state['b_RWS_KA'], 
            'KAUSI 2025 (3DA)': st.session_state['b_3da'],
            'COP (%)': st.session_state['b_COP_%'], 
            'STD (Hajonta)': st.session_state['b_STD_Hajonta'],
            'FDI': st.session_state['b_FDI']
        }

    st.markdown("---")
    
    # --- Ennusteen esittäminen ---
    if st.button("Laske Voittotodennäköisyys"):
        
        # Määritetään voittoon tarvittava määrä ennustetekstiä varten
        if st.session_state['match_format'] == 'BO Leg (esim. BO9, 5 legiä voittoon)':
            W = st.session_state['legs_to_win']
        else:
            W = st.session_state['sets_to_win']
            
        st.success(f"## 🏆 Ottelun Ennuste ({N_ITERATIONS} Simulaatiota) | Formaatti: **{st.session_state['match_format']}**")
        
        st.markdown("---")
        
        # --- Simulaatio 1: Pelaaja A Aloittaa Ottelun ---
        st.markdown(f"### 🥇 Skenaario 1: **{player_a_name}** Aloittaa Ottelun")
        
        prob_a_start_A = simulate_game(a_stats, b_stats, st.session_state['match_format'], 1, iterations=N_ITERATIONS)
        prob_b_start_A = 1.0 - prob_a_start_A
        
        col_a1, col_b1 = st.columns(2)
        
        with col_a1:
            st.metric(label=f"**{player_a_name}** voitto", value=f"{prob_a_start_A * 100:.1f} %")
        with col_b1:
            st.metric(label=f"**{player_b_name}** voitto", value=f"{prob_b_start_A * 100:.1f} %")
            
        score_text_start_A = get_score_prediction_text(prob_a_start_A, st.session_state['match_format'], W, player_a_name, player_b_name)
        st.info(f"**Tulosennuste:** {score_text_start_A}")
        st.progress(prob_a_start_A)

        st.markdown("---")

        # --- Simulaatio 2: Pelaaja B Aloittaa Ottelun ---
        st.markdown(f"### 🥈 Skenaario 2: **{player_b_name}** Aloittaa Ottelun")

        prob_a_start_B = simulate_game(a_stats, b_stats, st.session_state['match_format'], -1, iterations=N_ITERATIONS)
        prob_b_start_B = 1.0 - prob_a_start_B
        
        col_a2, col_b2 = st.columns(2)
        
        with col_a2:
            st.metric(label=f"**{player_a_name}** voitto", value=f"{prob_a_start_B * 100:.1f} %")
        with col_b2:
            st.metric(label=f"**{player_b_name}** voitto", value=f"{prob_b_start_B * 100:.1f} %")
            
        score_text_start_B = get_score_prediction_text(prob_a_start_B, st.session_state['match_format'], W, player_a_name, player_b_name)
        st.info(f"**Tulosennuste:** {score_text_start_B}")
        st.progress(prob_a_start_B)

        st.markdown("---")
        
        # Näytetään legivoiton todennäköisyydet (lisätietona)
        twp_a = calculate_leg_win_probability(a_stats, b_stats, type='TWS') 
        rwp_a = calculate_leg_win_probability(a_stats, b_stats, type='RWS') 
        
        st.markdown("### 🎯 Legivoiton Todennäköisyydet")
        st.caption(f"Legien LWP lasketaan käyttäen **FDI-painoa 0.02** ja **aloittajan etua 1.27**.")
        col_leg_1, col_leg_2 = st.columns(2)
        
        with col_leg_1:
            st.info(f"**{player_a_name}** aloittaa Legin (TWS): **{twp_a * 100:.1f} %**")
        with col_leg_2:
            st.info(f"**{player_a_name}** vastaanottaa Legin (RWS): **{rwp_a * 100:.1f} %**")

if __name__ == '__main__':
    main()
