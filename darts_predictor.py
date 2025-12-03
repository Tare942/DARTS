import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATAN KÄSITTELY FUNKTIOT ---

@st.cache_resource
def load_data(file_path):
    """Lataa pelaajadatan CSV-tiedostosta ja tekee tarvittavat esikäsittelyt."""
    try:
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

# 🟢 UUSI: TAKAISINKUTSUFUNKTIO ARVOJEN PÄIVITYKSEEN 🟢
def set_player_stats(player_key):
    """
    Lataa valitun pelaajan tiedot ja asettaa ne suoraan Streamlitin sessiotilaan.
    Tämä päivittää number_input-kenttien arvot automaattisesti.
    """
    player_name = st.session_state[player_key]
    player_data = load_player_data(player_name)
    
    # Määritä syötekenttien avaimet ja oletusarvot (HUOM: number_input-kenttien uudet avaimet)
    stats_map = {
        'KAUSI 2025 (3DA)': (90.0, '3da'),
        'COP (%)': (35.0, 'COP_%'),
        'STD (Hajonta)': (20.0, 'STD_Hajonta'),
        'TWS KA': (90.0, 'TWS_KA'),
        'RWS KA': (90.0, 'RWS_KA'),
    }

    prefix = player_key.split('_')[0] # 'a' tai 'b'
    
    for stat_key, (default_val, suffix) in stats_map.items():
        # UUSI AVAIN MUOTO: 'a_3da', 'b_COP_%' jne.
        session_key = f"{prefix}_{suffix}"
        
        # Asetetaan arvo suoraan st.session_stateen
        st.session_state[session_key] = get_float_val(player_data, stat_key, default_val)


# --- 2. ENNUSTUSLASKENTA (PLACEHOLDER) ---

def calculate_win_probability(a_stats, b_stats):
    """Laske ottelun todennäköisyys annettujen tilastojen perusteella."""
    a_score = a_stats['KAUSI 2025 (3DA)'] + (a_stats['COP (%)'] * 10) 
    b_score = b_stats['KAUSI 2025 (3DA)'] + (b_stats['COP (%)'] * 10) 

    if a_score + b_score == 0:
        return 0.5 
        
    prob_a = a_score / (a_score + b_score)
    return prob_a


# --- 3. STREAMLIT PÄÄFUNKTIO ---

def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("🎯 Darts-ottelun Tulosennustin")
    
    data_file_path = "Voitko tehdä kaikista osallistujista docs listan... - Voitko tehdä kaikista osallistujista docs listan....csv"
    
    if 'player_data' not in st.session_state or st.session_state['player_data'].empty:
        load_data(data_file_path)

    all_players = st.session_state.get('all_players', ["Muokkaa itse"])
    
    if len(all_players) == 1 and all_players[0] == "Muokkaa itse":
        st.warning(f"Pelaajadataa ei voitu ladata tiedostosta: {data_file_path}. Tarkista tiedostonimi ja muoto.")
        
    # Ladataan alustavat arvot kerran, jos niitä ei ole asetettu
    if 'a_name' not in st.session_state:
        st.session_state['a_name'] = all_players[0] if all_players else "Muokkaa itse"
        set_player_stats('a_name')
    if 'b_name' not in st.session_state:
        st.session_state['b_name'] = all_players[1] if len(all_players) > 1 else all_players[0]
        set_player_stats('b_name')

    
    col1, col2 = st.columns(2)

    # --- Pelaaja A ---
    with col1:
        st.header("Pelaaja A")
        
        default_a_index = all_players.index(st.session_state['a_name']) if st.session_state['a_name'] in all_players else 0
        
        # 🟢 MUUTOS: Lisätty on_change ja args automaattista päivitystä varten
        player_a_name = st.selectbox(
            "Valitse Pelaaja A", 
            all_players, 
            index=default_a_index, 
            key='a_name', 
            on_change=set_player_stats,
            args=('a_name',)
        )
        
        st.subheader("Keskiarvot ja Tehokkuus")
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        a_3da = st.number_input(
            "Kauden 3-darts Average (3DA)",
            min_value=60.0, max_value=120.0, step=0.01,
            key='a_3da',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        a_cop = st.number_input(
            "COP (Checkout %)",
            min_value=10.0, max_value=80.0, step=0.01,
            key='a_COP_%',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        a_std = st.number_input(
            "STD (Pist. heittojen hajonta)",
            min_value=10.0, max_value=40.0, 
            step=0.01,
            key='a_STD_Hajonta',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        a_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            key='a_TWS_KA', 
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        a_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            key='a_RWS_KA', 
            format="%.2f"
        )
        
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
        
        # 🟢 MUUTOS: Lisätty on_change ja args automaattista päivitystä varten
        player_b_name = st.selectbox(
            "Valitse Pelaaja B", 
            all_players, 
            index=default_b_index, 
            key='b_name', 
            on_change=set_player_stats,
            args=('b_name',)
        )
        
        st.subheader("Keskiarvot ja Tehokkuus")

        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        b_3da = st.number_input(
            "Kauden 3-darts Average (3DA)",
            min_value=60.0, max_value=120.0, step=0.01,
            key='b_3da',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        b_cop = st.number_input(
            "COP (Checkout %)",
            min_value=10.0, max_value=80.0, step=0.01,
            key='b_COP_%',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        b_std = st.number_input(
            "STD (Pist. heittojen hajonta)",
            min_value=10.0, max_value=40.0, 
            step=0.01,
            key='b_STD_Hajonta',
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        b_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            key='b_TWS_KA', 
            format="%.2f"
        )
        
        # 🔴 MUUTOS: value-argumentti POISTETTU, key-arvo muutettu
        b_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            key='b_RWS_KA',
            format="%.2f"
        )

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
        prob_a = calculate_win_probability(a_stats, b_stats)
        prob_b = 1.0 - prob_a
        
        st.success("## 🏆 Ottelun Ennuste")
        
        col_prob_a, col_prob_b = st.columns(2)
        
        with col_prob_a:
            st.markdown(f"**{player_a_name}** voittotodennäköisyys:")
            st.metric(label="Todennäköisyys", value=f"{prob_a * 100:.1f} %")
            st.progress(prob_a)
            
        with col_prob_b:
            st.markdown(f"**{player_b_name}** voittotodennäköisyys:")
            st.metric(label="Todennäköisyys", value=f"{prob_b * 100:.1f} %")
            st.progress(prob_b)
        
        st.info("Muista korvata calculate_win_probability-funktio omalla varsinaisella ennustemallillasi.")


if __name__ == '__main__':
    main()
