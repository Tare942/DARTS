# ... (CHECKOUT_MAP, SCORING_MAP, DEFAULT_PRESETS,
#      get_hit_score, simulate_score, attempt_checkout,
#      simulate_leg, simulate_match, load_custom_presets, save_custom_presets functions remain unchanged)

# --- 5. Streamlit GUI & Logiikka ---

def update_player_inputs(player_id):
    """Päivittää pelaajan syötekentät valitun profiilin perusteella."""
    
    preset_key = st.session_state[f'preset_{player_id}']
    form_key = st.session_state[f'form_{player_id}']
    
    if "---" in preset_key:
        return

    # HUOM: PLAYER_PRESETS täytyy olla globaali tai ladattu main:issa
    global PLAYER_PRESETS 
    data = PLAYER_PRESETS.get(preset_key, PLAYER_PRESETS["VALITSE PROFIILI"])
    
    # Päivitä COP ja STD suoraan
    st.session_state[f'cop_{player_id}'] = data.get("COP", 35)
    st.session_state[f'std_{player_id}'] = data.get("STD", 18.0)
    
    # Päivitä 3DA (KAUSI/VIIMEISET 5)
    new_avg = data.get(form_key, data.get("KAUSI", 95.0))
    st.session_state[f'avg_{player_id}'] = f"{new_avg:.2f}"

def run_simulation(params, result_placeholder, progress_placeholder):
    """Suorittaa Monte Carlo -simulaation ja päivittää Streamlit-komponentteja."""
    
    a_wins = 0
    b_wins = 0
    n = params['N_SIMULATIONS']
    
    # Luo edistymispalkki placeholderiin
    progress_bar = progress_placeholder.progress(0, text="Käynnistetään simulaatio...")
    
    # Päivitysväli (päivitä noin 100 kertaa)
    update_interval = max(1, n // 100) 
    
    for i in range(n):
        winner = simulate_match(params)
        
        if winner == "A":
            a_wins += 1
        else:
            b_wins += 1
        
        # Päivitä edistyminen vain tarvittaessa
        if (i + 1) % update_interval == 0 or (i + 1) == n:
            progress = (i + 1) / n
            progress_bar.progress(progress, text=f"Simuloidaan... {int(progress * 100)}%")

    prob_a = a_wins / n
    prob_b = b_wins / n
    
    p_a_name = st.session_state['preset_A'] if st.session_state['preset_A'] != "VALITSE PROFIILI" else "Pelaaja A"
    p_b_name = st.session_state['preset_B'] if st.session_state['preset_B'] != "VALITSE PROFIILI" else "Pelaaja B"

    # Näytä tulokset
    result_placeholder.empty()
    with result_placeholder.container():
        st.subheader("✨ LOPULLINEN ENNUSTE ✨")
        st.info(f"Simulaatiot: **{n}** kierrosta")
        
        col1, col2 = st.columns(2)
        
        # Käytä absoluuttisia lukuja ja prosentteja selkeämmin
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
    load_custom_presets()
    st.set_page_config(page_title="Darts-ennustin (Monte Carlo)", layout="wide")
    st.title("🎯 Darts-ennustin (Monte Carlo-simulaatio)")
    st.markdown("---")

    # --- Session State (Tilanhallinta) ---
    if 'preset_A' not in st.session_state:
        st.session_state['preset_A'] = "VALITSE PROFIILI"
        st.session_state['preset_B'] = "VALITSE PROFIILI"
        st.session_state['form_A'] = "KAUSI"
        st.session_state['form_B'] = "KAUSI"
        st.session_state['avg_A'] = "95.00"
        st.session_state['cop_A'] = 35
        st.session_state['std_A'] = 18.0
        st.session_state['avg_B'] = "95.00"
        st.session_state['cop_B'] = 35
        st.session_state['std_B'] = 18.0
        
    update_player_inputs('A') 
    update_player_inputs('B')

    # --- Pelaajien Syötteet (käyttää st.session_statea) ---
    st.header("1. Pelaajien Parametrit")
    col_a, col_b = st.columns(2)

    # Pelaaja A
    with col_a:
        st.subheader("Pelaaja A")
        
        st.selectbox("Profiili (A)", options=list(PLAYER_PRESETS.keys()), key='preset_A', on_change=lambda: update_player_inputs('A'))
        st.selectbox("3DA Muoto (A)", options=["KAUSI", "VIIMEISET 5"], key='form_A', on_change=lambda: update_player_inputs('A'))
        st.text_input("3DA (Kolmen tikan keskiarvo)", key='avg_A')
        st.number_input("COP (%) (Checkout-prosentti)", min_value=0, max_value=100, key='cop_A')
        st.number_input("STD DEV (Keskiarvon Keskihajonta)", key='std_A')
        
    # Pelaaja B
    with col_b:
        st.subheader("Pelaaja B")
        
        st.selectbox("Profiili (B)", options=list(PLAYER_PRESETS.keys()), key='preset_B', on_change=lambda: update_player_inputs('B'))
        st.selectbox("3DA Muoto (B)", options=["KAUSI", "VIIMEISET 5"], key='form_B', on_change=lambda: update_player_inputs('B'))
        st.text_input("3DA (Kolmen tikan keskiarvo)", key='avg_B')
        st.number_input("COP (%) (Checkout-prosentti)", min_value=0, max_value=100, key='cop_B')
        st.number_input("STD DEV (Keskiarvon Keskihajonta)", key='std_B')
        
    st.markdown("---")

    # --- Ottelun Muoto & Simulaatio ---
    st.header("2. Ottelun Muoto ja Simulaatio")
    col_type, col_n, col_sim = st.columns([1, 1, 1])

    # Ottelun tyyppi
    with col_type:
        match_type = st.radio("Ottelun tyyppi", options=["LEG", "SET"], key='match_type')

    # Legien/Settien määrä
    with col_n:
        n_legs = None
        n_sets = None
        if match_type == "LEG":
            n_legs = st.number_input("Paras N Legistä", min_value=3, step=2, value=11, key='n_legs')
        else:
            n_sets = st.number_input("Paras N Setistä", min_value=3, step=2, value=5, key='n_sets')

    # Simulaatioiden määrä
    with col_sim:
        n_simulations = st.number_input("Simulaatioiden määrä", min_value=100, step=1000, value=10000, key='n_sims')

    st.markdown("---")
    
    # Placeholder edistymispalkille (Progress Bar)
    progress_placeholder = st.empty() 
    # Placeholder tuloksille
    result_placeholder = st.empty()

    # --- Käynnistysnappi ---
    if st.button("▶️ Aloita Simulaatio", type="primary"):
        try:
            # Parametrien kokoaminen ja validointi
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
            
            # Suorita simulaatio
            run_simulation(params, result_placeholder, progress_placeholder)

        except ValueError as e:
            st.error(f"Virhe syötteessä: Varmista, että kaikki numeeriset arvot ovat oikein. ({e})")
        except Exception as e:
            st.error(f"Odottamaton virhe: {e}")

if __name__ == "__main__":
    main()
