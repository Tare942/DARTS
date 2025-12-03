import streamlit as st
import pandas as pd
import numpy as np
import os 

# --- 1. DATAN KÄSITTELY FUNKTIOT ---

@st.cache_resource
def load_data(file_path):
    """Lataa pelaajadatan CSV-tiedostosta ja tekee tarvittavat esikäsittelyt."""
    
    try:
        # Yritetään lukea data
        df = pd.read_csv(file_path, sep=',') 
        
        if 'Pelaajan Nimi' in df.columns:
            # Puhdistetaan pelaajanimistä mahdolliset järjestysnumerot (esim. "1. ")
            df['Pelaajan Nimi'] = df['Pelaajan Nimi'].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)

        float_cols = ['KAUSI 2025 (3DA)', 'COP (%)', 'STD (Hajonta)', 'TWS KA', 'RWS KA']
        
        for col in float_cols:
            if col in df.columns:
                # Korvataan lainausmerkit ja pilkut pisteiksi desimaalien takia
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Poistetaan rivit, joissa ei ole pelaajan nimeä
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
    Laskee Legivoiton Todennäköisyyden (LWP) suhteellisen vahvuuden perusteella 
    käyttäen annettuja painotuksia.
    """
    
    # 🟢 VAHVUUSMUUTTUJIEN MÄÄRITTELY (Painotukset)
    WEIGHT_SCORING = 1.0  
    WEIGHT_COP = 0.05     
    WEIGHT_3DA = 0.001    
    
    # 1. Määritellään hyökkääjän ja vastustajan legin pisteytysvoima
    if type == 'TWS':
        attacker_score = attacker_stats['TWS KA'] * WEIGHT_SCORING
        defender_score = defender_stats['RWS KA'] * WEIGHT_SCORING
    else:
        attacker_score = attacker_stats['RWS KA'] * WEIGHT_SCORING
        defender_score = defender_stats['TWS KA'] * WEIGHT_SCORING

    # 2. Lisätään hienosäätö COP ja 3DA perusteella
    attacker_boost = (attacker_stats['COP (%)'] * WEIGHT_COP) + (attacker_stats['KAUSI 2025 (3DA)'] * WEIGHT_3DA)
    defender_boost = (defender_stats['COP (%)'] * WEIGHT_COP) + (defender_stats['KAUSI 2025 (3DA)'] * WEIGHT_3DA)
    
    total_attacker_strength = attacker_score + attacker_boost
    total_defender_strength = defender_score + defender_boost
    
    total_strength = total_attacker_strength + total_defender_strength
    if total_strength <= 0:
        return 0.5
        
    prob_win = total_attacker_strength / total_strength
    
    return prob_win


def simulate_game(a_stats, b_stats, match_format, start_player, iterations=50000):
    """
    Simuloi koko ottelu Monte Carlo -tekniikalla, käyttäen uutta LWP-mallia.
    """
    
    twp_a = calculate_leg_win_probability(a_stats, b_stats, type='TWS') 
    rwp_a = calculate_leg_win_probability(a_stats, b_stats, type='RWS') 
    
    a_match_wins = 0
    
    if match_format == 'BO Leg (esim. BO9, 5 legiä voittoon)':
        legs_to_win = st.session_state['legs_to_win']
        
        for _ in range(iterations):
            current_start_player = start_player
            a_legs = 0
            b_legs = 0
            leg_count = 0
            
            while a_legs < legs_to_win and b_legs < legs_to_win:
                
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
                
    elif match_format == 'Set-malli (esim. BO5 set, setti on BO3 leg)':
        sets_to_win = st.session_state['sets_to_win']
        
        for _ in range(iterations):
            current_start_player = start_player
            a_sets = 0
            b_sets = 0
            set_count = 0
            
            while a_sets < sets_to_win and b_sets < sets_to_win:
                
                # Simulaatio Yhdestä Setistä (BO5 Leg, 3 legiä voittoon)
                a_legs = 0
                b_legs = 0
                leg_count_in_set = 0
                
                # Ehto: Tarvitaan 3 legiä setin voittoon (a_legs < 3 ja b_legs < 3)
                while a_legs < 3 and b_legs < 3: 
                    
                    leg_starter_a = (current_start_player == 1 and leg_count_in_set % 2 == 0) or \
                                    (current_start_player == -1 and leg_count_in_set % 2 != 0)
                    
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
                    
                current_start_player *= -1
                set_count += 1

            if a_sets > b_sets:
                a_match_wins += 1

    return a_match_wins / iterations


# --- 3. STREAMLIT PÄÄFUNKTIO ---

def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("🎯 Darts-ottelun Ennustaja (Monte Carlo Simulaatio)")
    
    # 💾 Datan lataus
    st.markdown("### 💾 Datan lataus")
    
    # Oletustiedostopolku on nyt "MM 25.csv"
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
    
    def get_initial_player_name(key, all_players):
        if key not in st.session_state or st.session_state[key] not in all_players:
            return all_players[0] if all_players else "Muokkaa itse"
        return st.session_state[key]
        
    if 'a_name' not in st.session_state or st.session_state['a_name'] not in all_players:
        st.session_state['a_name'] = get_initial_player_name('a_name', all_players)
        set_player_stats('a_name')
        
    if 'b_name' not in st.session_state or st.session_state['b_name'] not in all_players:
        default_b_name = all_players[1] if len(all_players) > 1 else all_players[0]
        st.session_state['b_name'] = get_initial_player_name('b_name', all_players)
        if st.session_state['a_name'] == st.session_state['b_name'] and len(all_players) > 1:
             st.session_state['b_name'] = all_players[1]
        set_player_stats('b_name')
        
    # Asetukset
    if 'match_format' not in st.session_state:
        st.session_state['match_format'] = 'BO Leg (esim. BO9, 5 legiä voittoon)'
    if 'legs_to_win' not in st.session_state:
        st.session_state['legs_to_win'] = 5
    if 'sets_to_win' not in st.session_state:
        st.session_state['sets_to_win'] = 3
    if 'start_player' not in st.session_state:
        st.session_state['start_player'] = 'Pelaaja A'

    
    col_settings1, col_settings2, col_settings3 = st.columns(3)

    with col_settings1:
        match_format = st.selectbox(
            "Ottelun Formaatti",
            ['BO Leg (esim. BO9, 5 legiä voittoon)', 'Set-malli (esim. BO5 set, setti on BO5 leg)'], # Päivitetty teksti
            key='match_format'
        )

    with col_settings2:
        if match_format == 'BO Leg (esim. BO9, 5 legiä voittoon)':
            legs_to_win = st.number_input(
                "Legiä voittoon (esim. BO9 -> 5)",
                min_value=1, max_value=25, step=1, key='legs_to_win'
            )
            st.caption(f"Simuloidaan Best of {legs_to_win * 2 - 1} legiä.")
        else:
            sets_to_win = st.number_input(
                "Settiä voittoon (esim. BO5 -> 3)",
                min_value=1, max_value=15, step=1, key='sets_to_win'
            )
            # Päivitetty kuvateksti vastaamaan BO5 Legiä
            st.caption(f"Simuloidaan Best of {sets_to_win * 2 - 1} settiä (setti on **BO5 leg**, eli **3 legiä voittoon**).")
            
        
    with col_settings3:
        start_player_name = st.selectbox(
            "Kuka Aloittaa Ottelun?",
            ['Pelaaja A', 'Pelaaja B'],
            key='start_player'
        )
    
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
            default_a_index = all_players.index(st.session_state['a_name'])
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
        
        a_stats = {
            'TWS KA': st.session_state['a_TWS_KA'], 
            'RWS KA': st.session_state['a_RWS_KA'], 
            'KAUSI 2025 (3DA)': st.session_state['a_3da'],
            'COP (%)': st.session_state['a_COP_%'], 
            'STD (Hajonta)': st.session_state['a_STD_Hajonta']
        }


    # --- Pelaaja B ---
    with col2:
        st.header("Pelaaja B")
        
        try:
            default_b_index = all_players.index(st.session_state['b_name'])
        except ValueError:
             default_b_index = 0
             
        if default_b_index == all_players.index(st.session_state['a_name']) and len(all_players) > 1:
            default_b_index = (default_b_index + 1) % len(all_players)

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

        b_stats = {
            'TWS KA': st.session_state['b_TWS_KA'], 
            'RWS KA': st.session_state['b_RWS_KA'], 
            'KAUSI 2025 (3DA)': st.session_state['b_3da'],
            'COP (%)': st.session_state['b_COP_%'], 
            'STD (Hajonta)': st.session_state['b_STD_Hajonta']
        }

    st.markdown("---")
    
    # --- Ennusteen esittäminen ---
    if st.button("Laske Voittotodennäköisyys"):
        
        start_player_val = 1 if start_player_name == 'Pelaaja A' else -1
        
        prob_a = simulate_game(a_stats, b_stats, match_format, start_player_val, iterations=N_ITERATIONS)
        prob_b = 1.0 - prob_a
        
        st.success(f"## 🏆 Ottelun Ennuste ({N_ITERATIONS} Simulaatiota)")
        st.info(f"Ottelun aloittaa: **{start_player_name}** | Formaatti: **{match_format}**")
        
        col_prob_a, col_prob_b = st.columns(2)
        
        with col_prob_a:
            st.markdown(f"**{player_a_name}** voittotodennäköisyys:")
            st.metric(label="Todennäköisyys", value=f"{prob_a * 100:.1f} %")
            st.progress(prob_a)
            
        with col_prob_b:
            st.markdown(f"**{player_b_name}** voittotodennäköisyys:")
            st.metric(label="Todennäköisyys", value=f"{prob_b * 100:.1f} %")
            st.progress(prob_b)


if __name__ == '__main__':
    main()
