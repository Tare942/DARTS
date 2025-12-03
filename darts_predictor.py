import streamlit as st
import pandas as pd
import numpy as np
# from scipy.stats import poisson <--- POISTETTU TÄSTÄ

# --- 1. DATAN KÄSITTELY FUNKTIOT ---

@st.cache_resource
def load_data(file_path):
    """Lataa pelaajadatan CSV-tiedostosta ja tekee tarvittavat esikäsittelyt."""
    try:
        # Tässä käytetään tiedostonimeä, joka on ollut käytössä aiemmin (huomioi pitkä nimi)
        df = pd.read_csv(file_path, sep=',') 
        
        if 'Pelaajan Nimi' in df.columns:
            df['Pelaajan Nimi'] = df['Pelaajan Nimi'].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)

        float_cols = ['KAUSI 2025 (3DA)', 'COP (%)', 'STD (Hajonta)', 'TWS KA', 'RWS KA']
        
        for col in float_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['Pelaajan Nimi']).reset_index(drop=True)
        
        st.session_state['player_data'] = df
        st.session_state['all_players'] = df['Pelaajan Nimi'].tolist()
        return df
        
    except Exception as e:
        st.error(f"Virhe datan latauksessa (Tarkista tiedostonimi ja muoto): {e}")
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


# --- 2. ENNUSTUSMALLI (MONTE CARLO) ILMAN SCIPY:Ä ---

def calculate_leg_win_probability(stat_A, stat_B):
    """
    Laskee legin voittotodennäköisyyden (LWP) suhteellisen vahvuuden perusteella.
    
    Käytetään Logit-pohjaista/Elo-tyylistä lähestymistapaa, joka on karkeasti 
    vastine Poisson-mallille ilman scipyä. 
    """
    
    # 1. Määritellään pelaajan kokonaisvahvuus (Strength Score)
    # Painotukset (voit hienosäätää näitä arvoja)
    WEIGHT_3DA = 0.5
    WEIGHT_COP = 0.5 
    
    # Huomioidaan vain pelaajan omat hyökkäysarvot tässä kohtaa suhteellisen vahvuuden laskemiseen.
    # TWS KA on tärkein mittari legin voitossa.
    
    strength_A = (stat_A['TWS KA'] * 1.0) + (stat_A['COP (%)'] * WEIGHT_COP) + (stat_A['KAUSI 2025 (3DA)'] * WEIGHT_3DA)
    strength_B = (stat_B['TWS KA'] * 1.0) + (stat_B['COP (%)'] * WEIGHT_COP) + (stat_B['KAUSI 2025 (3DA)'] * WEIGHT_3DA)

    # 2. Muutetaan vahvuusarvot todennäköisyydeksi (Logit/Sigmoid-funktio)
    # Käytetään yksinkertaista suhteellista jakoa, joka toimii samalla periaatteella kuin Elo-ero.
    
    total_strength = strength_A + strength_B
    if total_strength == 0:
        return 0.5
        
    prob_A = strength_A / total_strength
    
    return prob_A # Tämä on Leg Win Probability (LWP)


def simulate_game(a_stats, b_stats, match_format, start_player, iterations=2500):
    """
    Simuloi koko ottelu Monte Carlo -tekniikalla
    """
    
    # 1. Laske legivoiton todennäköisyys (LWP) aloittajasta riippuen
    # TWP_A (A voittaa kun A aloittaa)
    twp_a = calculate_leg_win_probability(a_stats, b_stats) 
    
    # RWP_A (A voittaa kun B aloittaa)
    # Käytetään tässä B:n RWS KA:ta A:n TWS KA:n sijaan, kun B aloittaa
    twp_b = calculate_leg_win_probability(b_stats, a_stats) # B:n legivoitto kun B aloittaa
    rwp_a = 1.0 - twp_b # A:n legivoitto kun B aloittaa
    
    # HUOMIO: Käytetään nyt todellisia TWS/RWS KA arvoja, jos ne ovat erillisiä!
    # Tämä tekee mallista entistä tarkemman.
    
    # Legivoitto, kun A aloittaa (LWP_A_TWS)
    twp_a = a_stats['TWS KA'] / (a_stats['TWS KA'] + b_stats['RWS KA'])
    # Legivoitto, kun B aloittaa (LWP_A_RWS)
    rwp_a = a_stats['RWS KA'] / (a_stats['RWS KA'] + b_stats['TWS KA'])
    
    a_match_wins = 0
    
    if match_format == 'BO Leg (esim. BO9, 5 legiä voittoon)':
        legs_to_win = st.session_state['legs_to_win']
        
        for _ in range(iterations):
            current_start_player = start_player
            a_legs = 0
            b_legs = 0
            leg_count = 0
            
            while a_legs < legs_to_win and b_legs < legs_to_win:
                
                # Legi-aloittaja vaihtuu joka kierroksella
                # Jos start_player=1 (A aloittaa) -> leg 0: A, leg 1: B, leg 2: A...
                leg_starter_a = (current_start_player == 1 and leg_count % 2 == 0) or \
                                (current_start_player == -1 and leg_count % 2 != 0)
                
                if leg_starter_a:
                    # A aloittaa: A käyttää TWS KA, B käyttää RWS KA
                    prob_a_win = twp_a
                else:
                    # B aloittaa: B käyttää TWS KA, A käyttää RWS KA
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
                
                # Simulaatio Yhdestä Setistä (BO3 Leg, 2 legiä voittoon)
                a_legs = 0
                b_legs = 0
                leg_count_in_set = 0
                
                while a_legs < 2 and b_legs < 2:
                    
                    # Legi-aloittaja vaihtuu joka legillä
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
                    
                # PDC:n formaatissa setin aloittaja vaihtuu
                # Vaihda aloitusvuoro jokaisen setin jälkeen
                current_start_player *= -1
                set_count += 1

            if a_sets > b_sets:
                a_match_wins += 1

    return a_match_wins / iterations


# --- 3. STREAMLIT PÄÄFUNKTIO ---

def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("🎯 Darts-ottelun Ennustaja (Monte Carlo Simulaatio)")
    st.markdown("### Ottelumuoto ja Simulaation Asetukset")
    
    data_file_path = "MM 25 csv.csv"
    
    if 'player_data' not in st.session_state or st.session_state['player_data'].empty:
        load_data(data_file_path)

    all_players = st.session_state.get('all_players', ["Muokkaa itse"])
        
    # Ladataan alustavat arvot kerran, jos niitä ei ole asetettu
    if 'a_name' not in st.session_state:
        st.session_state['a_name'] = all_players[0] if all_players else "Muokkaa itse"
        set_player_stats('a_name')
    if 'b_name' not in st.session_state:
        default_b_name = all_players[1] if len(all_players) > 1 else all_players[0]
        st.session_state['b_name'] = default_b_name
        set_player_stats('b_name')
        
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
            ['BO Leg (esim. BO9, 5 legiä voittoon)', 'Set-malli (esim. BO5 set, setti on BO3 leg)'],
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
            st.caption(f"Simuloidaan Best of {sets_to_win * 2 - 1} settiä (setti on BO3 leg).")
            
        
    with col_settings3:
        start_player_name = st.selectbox(
            "Kuka Aloittaa Ottelun?",
            ['Pelaaja A', 'Pelaaja B'],
            key='start_player'
        )
    
    N_ITERATIONS = st.number_input(
        "Simulaatioiden Määrä (N)",
        min_value=100, max_value=10000, step=500, value=2500
    )

    st.markdown("---")
    
    col1, col2 = st.columns(2)

    # --- Pelaaja A ---
    with col1:
        st.header("Pelaaja A")
        
        default_a_index = all_players.index(st.session_state['a_name']) if st.session_state['a_name'] in all_players else 0
        
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
        
        default_b_index = all_players.index(st.session_state['b_name']) if st.session_state['b_name'] in all_players else 0
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
        
        # Muutetaan aloittaja numeeriseksi arvoksi (A: 1, B: -1)
        start_player_val = 1 if start_player_name == 'Pelaaja A' else -1
        
        # Simuloidaan ottelu
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
