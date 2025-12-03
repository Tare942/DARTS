import streamlit as st
import pandas as pd
import numpy as np

# --- 1. Datanlatausfunktio (Päivitetty käsittelemään float-arvoja ja desimaalipilkkua) ---

def load_player_data(player_name):
    """
    Lataa pelaajan tilastot. Tässä esimerkissä palautetaan mallidata.
    Sinun TÄYTYY korvata tämä omalla oikealla datanlatauslogiikallasi
    (esim. pandas.read_csv ja pelaajan nimellä suodattaminen).
    
    Aiemman virheen perusteella datassa on jo korkeita (avg) lukuja, esim.
    TWS KA: "111,51" ja RWS KA: "99,44".
    """
    # HUOM: Nämä arvot on poimittu lähettämästäsi CSV-tiedostosta Luke Littlerille
    if player_name == "Luke Littler":
        return {
            'TWS KA': "111,51",
            'RWS KA': "99,44",
            # Lisää muut tarvittavat sarakkeet tähän
            'KAUSI 2025 (3DA)': "100,96" 
        }
    if player_name == "Luke Humphries":
        return {
            'TWS KA': "107,8",
            'RWS KA': "96,62",
            'KAUSI 2025 (3DA)': "98,5"
        }
    return {} # Palauta tyhjä, jos pelaajaa ei löydy

def get_float_val(data, key, default_value):
    """
    Hakee arvon pelaajan tiedoista, käsittelee pilkun desimaalierottimena
    ja palauttaa float-luvun.
    """
    if data and key in data:
        value = data[key]
        try:
            # Korvataan pilkku pisteellä ja muunnetaan floatiksi
            if isinstance(value, str):
                return float(value.replace(',', '.'))
            return float(value)
        except (ValueError, TypeError):
            # Jos muunnos epäonnistuu, käytetään oletusarvoa
            pass 
            
    # Jos dataa ei ole tai keyta ei löydy, käytetään oletusarvoa
    return float(default_value)

# --- 2. Ennustuslaskenta (Placeholder) ---

def calculate_win_probability(a_stats, b_stats):
    """
    Laske ottelun todennäköisyys annettujen tilastojen perusteella.
    TÄMÄ ON EHDOTTOMASTI KORVATTAVA OMALLA MALLI- TAI LASKENTALOGIIKALLASI!
    """
    # Esimerkki: Simppeli keskiarvojen vertailu
    a_avg_score = (a_stats['TWS KA'] + a_stats['RWS KA']) / 2
    b_avg_score = (b_stats['TWS KA'] + b_stats['RWS KA']) / 2
    
    # Esimerkki yksinkertaisesta todennäköisyysmallista (ei todellinen darts-malli!)
    if a_avg_score + b_avg_score == 0:
        return 0.5 # Estä nollalla jakaminen
        
    prob_a = a_avg_score / (a_avg_score + b_avg_score)
    return prob_a


# --- 3. Streamlit Pääfunktio (Päivitetyt Syötekentät) ---

# Oletettu tiedosto: /mount/src/darts/darts_predictor.py
def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("Darts-ottelun Tulosennustin")
    
    # Tässä pitäisi olla oikea datanlataus, esim. kaikkien pelaajien lista CSV:stä
    all_players = ["Luke Littler", "Luke Humphries", "Muokkaa itse"]
    
    col1, col2 = st.columns(2)

    # --- Pelaaja A ---
    with col1:
        st.header("Pelaaja A")
        player_a_name = st.selectbox("Valitse Pelaaja A", all_players, index=0, key='a_name')
        
        # Ladataan tilastot (käytä oikeaa datanlatausta!)
        player_a_data = load_player_data(player_a_name)
        
        st.subheader("Pistekeskiarvot / Leg")
        
        # Etsi vanha rivi 330-339 ja korvaa se:
        # TWS KA (Total Win/Score KA) - HEITTÄJÄN ALOITTAMA LEGI (UUSI)
        a_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, 
            max_value=120.0, 
            step=0.01,
            value=get_float_val(player_a_data, 'TWS KA', 90.0), 
            key='a_tws',
            format="%.2f"
        )
        
        # Etsi vanha rivi 340 ja korvaa se:
        # RWS KA (Receiver Win/Score KA) - VASTAANOTETTU LEGI (UUSI)
        a_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, 
            max_value=120.0, 
            step=0.01,
            value=get_float_val(player_a_data, 'RWS KA', 90.0), 
            key='a_rws',
            format="%.2f"
        )
        
        # Muut tilastot (esim. KAUSI 2025 (3DA))
        a_3da = st.number_input(
            "Kauden 3-darts Average",
            min_value=60.0,
            max_value=120.0,
            step=0.01,
            value=get_float_val(player_a_data, 'KAUSI 2025 (3DA)', 90.0),
            key='a_3da',
            format="%.2f"
        )
        
        # Kootaan tilastot ennustetta varten
        a_stats = {'TWS KA': a_tws, 'RWS KA': a_rws, 'KAUSI 2025 (3DA)': a_3da}


    # --- Pelaaja B ---
    with col2:
        st.header("Pelaaja B")
        player_b_name = st.selectbox("Valitse Pelaaja B", all_players, index=1, key='b_name')
        
        # Ladataan tilastot (käytä oikeaa datanlatausta!)
        player_b_data = load_player_data(player_b_name)
        
        st.subheader("Pistekeskiarvot / Leg")
        
        # TWS KA (Total Win/Score KA) - HEITTÄJÄN ALOITTAMA LEGI (UUSI)
        b_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, 
            max_value=120.0, 
            step=0.01,
            value=get_float_val(player_b_data, 'TWS KA', 90.0), 
            key='b_tws',
            format="%.2f"
        )
        
        # RWS KA (Receiver Win/Score KA) - VASTAANOTETTU LEGI (UUSI)
        b_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, 
            max_value=120.0, 
            step=0.01,
            value=get_float_val(player_b_data, 'RWS KA', 90.0), 
            key='b_rws',
            format="%.2f"
        )
        
        # Muut tilastot (esim. KAUSI 2025 (3DA))
        b_3da = st.number_input(
            "Kauden 3-darts Average",
            min_value=60.0,
            max_value=120.0,
            step=0.01,
            value=get_float_val(player_b_data, 'KAUSI 2025 (3DA)', 90.0),
            key='b_3da',
            format="%.2f"
        )

        # Kootaan tilastot ennustetta varten
        b_stats = {'TWS KA': b_tws, 'RWS KA': b_rws, 'KAUSI 2025 (3DA)': b_3da}

    st.markdown("---")
    
    # --- Ennusteen esittäminen ---
    if st.button("Laske Voittotodennäköisyys"):
        prob_a = calculate_win_probability(a_stats, b_stats)
        prob_b = 1.0 - prob_a
        
        st.success("## 🎯 Ottelun Ennuste")
        
        st.markdown(f"**{player_a_name}** voittotodennäköisyys: **{prob_a * 100:.1f} %**")
        st.progress(prob_a)
        st.markdown(f"**{player_b_name}** voittotodennäköisyys: **{prob_b * 100:.1f} %**")
        st.progress(prob_b)
        
        st.info("Muista korvata calculate_win_probability-funktio omalla varsinaisella ennustemallillasi.")


if __name__ == '__main__':
    main()
    # TÄMÄ ON RIVI 478 (OLETETTU)
