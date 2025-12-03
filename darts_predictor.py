import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATAN KÄSITTELY FUNKTIOT ---

@st.cache_resource
def load_data(file_path):
    """
    Lataa pelaajadatan CSV-tiedostosta ja tekee tarvittavat esikäsittelyt.
    """
    try:
        # Ladataan data käyttäen pilkkua desimaalierottimena ja poistaen lainausmerkit
        # Tässä käytetään useimpien sarakkeiden tyypiksi string, jotta 'replace' toimii
        df = pd.read_csv(
            file_path, 
            sep=',', 
            decimal=',',  # Yritetään lukea desimaalit pilkulla
            thousands='.', # Jos tuhansissa käytetty pistettä (ei kovin yleinen, mutta varmuuden vuoksi)
            encoding='utf-8'
        )
        
        # Puhdistetaan Pelaajan Nimi -sarake ylimääräisistä numeroista ja pisteistä (esim. "1. Luke Littler (England)" -> "Luke Littler (England)")
        df['Pelaajan Nimi'] = df['Pelaajan Nimi'].str.replace(r'^\d+\.\s*', '', regex=True)
        
        # Määriteltävät sarakkeet, joissa on pilkku desimaalierottimena ja pitäisi olla floatteja
        float_cols = ['KAUSI 2025 (3DA)', 'COP (%)', 'STD (Hajonta)', 'TWS KA', 'RWS KA']
        
        for col in float_cols:
            if col in df.columns:
                # Muutetaan string-sarakkeet floateiksi: ensin poistetaan lainausmerkit, sitten vaihdetaan pilkku pisteeksi
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.', regex=False)
                # Lopuksi yritetään muuttaa floatiksi. Jos epäonnistuu (esim. tyhjä arvo), tulee NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Poistetaan NaN-arvot Pelaajan Nimi -sarakkeesta
        df = df.dropna(subset=['Pelaajan Nimi']).reset_index(drop=True)
        
        st.session_state['player_data'] = df
        st.session_state['all_players'] = df['Pelaajan Nimi'].tolist()
        return df
        
    except Exception as e:
        st.error(f"Virhe datan latauksessa: {e}")
        return pd.DataFrame()


def load_player_data(player_name):
    """Hakee pelaajan tilastot DataFrame-objektista."""
    df = st.session_state.get('player_data', pd.DataFrame())
    if player_name and not df.empty:
        # Haetaan rivi, joka vastaa pelaajan nimeä
        row = df[df['Pelaajan Nimi'] == player_name]
        if not row.empty:
            # Palautetaan rivi sanakirjana (ilman indeksiä)
            return row.iloc[0].to_dict()
    return {} 

def get_float_val(data, key, default_value):
    """Hakee arvon pelaajan tiedoista ja palauttaa float-luvun."""
    if data and key in data:
        value = data[key]
        # Pandas-datassa arvo on jo float (tai NaN), jos esikäsittely onnistui
        if pd.notna(value):
            return float(value)
            
    return float(default_value)


# --- 2. ENNUSTUSLASKENTA (PLACEHOLDER) ---

def calculate_win_probability(a_stats, b_stats):
    """
    Laske ottelun todennäköisyys annettujen tilastojen perusteella.
    TÄMÄ ON EHDOTTOMASTI KORVATTAVA OMALLA MALLI- TAI LASKENTALOGIIKALLASI!
    """
    # Esimerkki: Painotetaan kauden keskiarvoa (3DA) ja tarkistusprosenttia (COP)
    
    # Käytetään 3DA:ta ja COP:ta (HUOM: COP:n tulisi olla pienempi kuin 1.0)
    a_score = a_stats['KAUSI 2025 (3DA)'] + (a_stats['COP (%)'] * 10) 
    b_score = b_stats['KAUSI 2025 (3DA)'] + (b_stats['COP (%)'] * 10) 

    if a_score + b_score == 0:
        return 0.5 
        
    prob_a = a_score / (a_score + b_score)
    
    # STD (Hajonta) voisi vaikuttaa esimerkiksi todennäköisyyden tasoitukseen tai luotettavuuteen
    # Nyt jätetään yksinkertaisuuden vuoksi pois peruslaskennasta.

    return prob_a


# --- 3. STREAMLIT PÄÄFUNKTIO (PÄIVITETYT SYÖTEKENTÄT) ---

def main():
    st.set_page_config(page_title="Darts Ennustaja", layout="wide")
    st.title("🎯 Darts-ottelun Tulosennustin")
    
    # Lataa data heti alussa
    data_file_path = "MM 25 csv - Voitko tehdä kaikista osallistujista docs listan... (1).csv"
    if 'player_data' not in st.session_state or st.session_state['player_data'].empty:
        load_data(data_file_path)

    all_players = st.session_state.get('all_players', ["Muokkaa itse"])
    
    if all_players == ["Muokkaa itse"]:
        st.warning("Pelaajadataa ei voitu ladata. Tarkista tiedostonimi ja muoto.")
        
    col1, col2 = st.columns(2)

    # --- Pelaaja A ---
    with col1:
        st.header("Pelaaja A")
        player_a_name = st.selectbox(
            "Valitse Pelaaja A", 
            all_players, 
            index=all_players.index("Luke Littler (England)") if "Luke Littler (England)" in all_players else 0, 
            key='a_name'
        )
        
        player_a_data = load_player_data(player_a_name)
        
        st.subheader("Keskiarvot ja Tehokkuus")
        
        # KAUSI 2025 (3DA)
        a_3da = st.number_input(
            "Kauden 3-darts Average (3DA)",
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_a_data, 'KAUSI 2025 (3DA)', 90.0),
            key='a_3da', format="%.2f"
        )
        
        # UUSI: COP (%)
        a_cop = st.number_input(
            "COP (Checkout %)",
            min_value=10.0, max_value=80.0, step=0.01,
            value=get_float_val(player_a_data, 'COP (%)', 35.0),
            key='a_cop', format="%.2f"
        )
        
        # UUSI: STD (Hajonta)
        a_std = st.number_input(
            "STD (Pist. heittojen hajonta)",
            min_value=10.0, max_value=30.0, step=0.01,
            value=get_float_val(player_a_data, 'STD (Hajonta)', 20.0),
            key='a_std', format="%.2f"
        )
        
        # TWS KA (Total Win/Score KA) - HEITTÄJÄN ALOITTAMA LEGI
        a_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_a_data, 'TWS KA', 90.0), 
            key='a_tws', format="%.2f"
        )
        
        # RWS KA (Receiver Win/Score KA) - VASTAANOTETTU LEGI
        a_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_a_data, 'RWS KA', 90.0), 
            key='a_rws', format="%.2f"
        )
        
        a_stats = {
            'TWS KA': a_tws, 'RWS KA': a_rws, 'KAUSI 2025 (3DA)': a_3da,
            'COP (%)': a_cop, 'STD (Hajonta)': a_std
        }


    # --- Pelaaja B ---
    with col2:
        st.header("Pelaaja B")
        player_b_name = st.selectbox(
            "Valitse Pelaaja B", 
            all_players, 
            index=all_players.index("Luke Humphries (England)") if "Luke Humphries (England)" in all_players else 0, 
            key='b_name'
        )
        
        player_b_data = load_player_data(player_b_name)
        
        st.subheader("Keskiarvot ja Tehokkuus")

        # KAUSI 2025 (3DA)
        b_3da = st.number_input(
            "Kauden 3-darts Average (3DA)",
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_b_data, 'KAUSI 2025 (3DA)', 90.0),
            key='b_3da', format="%.2f"
        )
        
        # UUSI: COP (%)
        b_cop = st.number_input(
            "COP (Checkout %)",
            min_value=10.0, max_value=80.0, step=0.01,
            value=get_float_val(player_b_data, 'COP (%)', 35.0),
            key='b_cop', format="%.2f"
        )
        
        # UUSI: STD (Hajonta)
        b_std = st.number_input(
            "STD (Pist. heittojen hajonta)",
            min_value=10.0, max_value=30.0, step=0.01,
            value=get_float_val(player_b_data, 'STD (Hajonta)', 20.0),
            key='b_std', format="%.2f"
        )
        
        # TWS KA (Total Win/Score KA) - HEITTÄJÄN ALOITTAMA LEGI
        b_tws = st.number_input(
            "TWS KA (Avg. Score / Leg Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_b_data, 'TWS KA', 90.0), 
            key='b_tws', format="%.2f"
        )
        
        # RWS KA (Receiver Win/Score KA) - VASTAANOTETTU LEGI
        b_rws = st.number_input(
            "RWS KA (Avg. Score / Leg Opponent Started)", 
            min_value=60.0, max_value=120.0, step=0.01,
            value=get_float_val(player_b_data, 'RWS KA', 90.0), 
            key='b_rws', format="%.2f"
        )

        b_stats = {
            'TWS KA': b_tws, 'RWS KA': b_rws, 'KAUSI 2025 (3DA)': b_3da,
            'COP (%)': b_cop, 'STD (Hajonta)': b_std
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
