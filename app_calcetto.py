import streamlit as st
import pandas as pd

# 1. Configurazione della pagina
st.set_page_config(page_title="Calcetto Stats", page_icon="⚽", layout="wide")

# Stile CSS personalizzato
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetric"] {
            background-color: #1A1F2B;
            border: 1px solid #2D3548;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            color: #FFFFFF;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1A1F2B;
            border-radius: 8px 8px 0px 0px;
            padding: 10px 20px;
            border: 1px solid #2D3548;
            border-bottom: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00E676 !important;
            color: #0E1117 !important;
            font-weight: bold;
        }

        /* Stile del Banner Ultima Partita */
        .match-banner {
            background: linear-gradient(135deg, #1A1F2B 0%, #232A3B 100%);
            border: 1px solid #00E676;
            border-radius: 14px;
            padding: 20px 25px;
            margin-bottom: 25px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
        }
        .match-date {
            text-align: center;
            color: #00E676;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .match-score {
            text-align: center;
            font-size: 2.6rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 15px;
        }
        .team-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #00E676;
            margin-bottom: 6px;
        }
        .player-list {
            font-size: 0.95rem;
            color: #E0E4EC;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)


# 2. Caricamento e pulizia dati
def load_data():
    df = pd.read_excel("archivio_calcetto.xlsx", sheet_name="LOG PARTITE")
    df = df.dropna(subset=['GIOCATORE']).copy()

    df['DATA'] = pd.to_datetime(df['DATA'])
    df['GIOCATORE'] = df['GIOCATORE'].astype(str).str.strip()
    df['SQUADRA'] = df['SQUADRA'].astype(str).str.strip().str.upper()

    cols_num = ['GOL SEGNATI', 'GOL FATTI SQUADRA', 'GOL SUBITI SQUADRA', 'VITTORIA']
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['SCARTO'] = df['GOL FATTI SQUADRA'] - df['GOL SUBITI SQUADRA']
    # Chiave univoca per identificare chi ha giocato nella stessa squadra
    df['MATCH_TEAM'] = df['DATA'].dt.strftime('%Y-%m-%d') + '-' + df['SQUADRA']
    return df


df_log = load_data()


# Calcolo tabella statistiche aggregate per giocatore
def calcola_statistiche(df):
    stats = df.groupby('GIOCATORE').agg(
        Presenze=('DATA', 'count'),
        Vittorie=('VITTORIA', 'sum'),
        Gol_Totali=('GOL SEGNATI', 'sum'),
        Scarto_Reti_Tot=('SCARTO', 'sum')
    ).reset_index()

    stats['% Vittorie'] = (stats['Vittorie'] / stats['Presenze'] * 100).round(1)
    stats['Media Gol'] = (stats['Gol_Totali'] / stats['Presenze']).round(2)
    stats['Scarto Medio'] = (stats['Scarto_Reti_Tot'] / stats['Presenze']).round(2)

    stats = stats.rename(columns={
        'GIOCATORE': 'Giocatore',
        'Gol_Totali': 'Gol Totali',
        'Scarto_Reti_Tot': 'Scarto Reti'
    })

    for col in ['Presenze', 'Vittorie', 'Gol Totali', 'Scarto Reti']:
        stats[col] = stats[col].astype(int)

    return stats


df_stats = calcola_statistiche(df_log)

# Sidebar con pulsante di aggiornamento rapido
st.sidebar.title("⚽ Calcetto Stats")
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Aggiorna Dati", use_container_width=True):
    st.rerun()
st.sidebar.caption(f"Partite in archivio: {df_log['DATA'].nunique()}")
st.sidebar.caption(f"Giocatori registrati: {df_log['GIOCATORE'].nunique()}")

# 3. HEADER + BANNER ULTIMA PARTITA
st.title("⚽ Statistiche Calcetto")

if not df_log.empty:
    ultima_data = df_log['DATA'].max()
    df_last = df_log[df_log['DATA'] == ultima_data]

    sq_a = df_last[df_last['SQUADRA'] == 'A']
    sq_b = df_last[df_last['SQUADRA'] == 'B']

    gol_a = int(sq_a['GOL FATTI SQUADRA'].iloc[0]) if not sq_a.empty else 0
    gol_b = int(sq_b['GOL FATTI SQUADRA'].iloc[0]) if not sq_b.empty else 0


    def formatta_giocatori(df_sq):
        righe = []
        for _, row in df_sq.iterrows():
            gol = int(row['GOL SEGNATI'])
            if gol > 0:
                righe.append(f"• {row['GIOCATORE']} <b>({gol} ⚽)</b>")
            else:
                righe.append(f"• {row['GIOCATORE']}")
        return "<br>".join(righe)


    lista_a = formatta_giocatori(sq_a)
    lista_b = formatta_giocatori(sq_b)
    data_str = ultima_data.strftime("%d/%m/%Y")

    st.markdown(f"""
        <div class="match-banner">
            <div class="match-date">Ultima Partita Giocata • {data_str}</div>
            <div class="match-score">SQUADRA A &nbsp; {gol_a} - {gol_b} &nbsp; SQUADRA B</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
                <div style="min-width: 200px;">
                    <div class="team-title">Formazione A</div>
                    <div class="player-list">{lista_a}</div>
                </div>
                <div style="min-width: 200px;">
                    <div class="team-title">Formazione B</div>
                    <div class="player-list">{lista_b}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 4. SEZIONI PRINCIPALI (TABS)
tab_classifiche, tab_giocatore, tab_affinita = st.tabs([
    "🏆 Classifiche",
    "👤 Scheda Giocatore",
    "🤝 Affinità di Coppia"
])

lista_giocatori = sorted(df_stats['Giocatore'].unique())

# --- TAB 1: CLASSIFICHE ---
with tab_classifiche:
    st.subheader("Classifica Generale")

    col_ord, col_dir = st.columns([2, 1])
    with col_ord:
        criterio = st.selectbox(
            "Ordina giocatori per:",
            ["Gol Totali", "Presenze", "Vittorie", "% Vittorie", "Media Gol", "Scarto Reti", "Scarto Medio"]
        )
    with col_dir:
        ordine = st.radio("Ordine:", ["Decrescente", "Crescente"], horizontal=True)

    ascendente = (ordine == "Crescente")
    df_ordinato = df_stats.sort_values(by=criterio, ascending=ascendente)

    st.dataframe(
        df_ordinato,
        use_container_width=True,
        hide_index=True,
        column_config={
            "% Vittorie": st.column_config.NumberColumn(format="%.1f%%"),
            "Media Gol": st.column_config.NumberColumn(format="%.2f"),
            "Scarto Medio": st.column_config.NumberColumn(format="%.2f"),
        }
    )

    st.markdown("---")
    st.subheader(f"Grafico: {criterio}")
    st.bar_chart(df_ordinato.set_index('Giocatore')[criterio], color="#00E676")

# --- TAB 2: SCHEDA GIOCATORE ---
with tab_giocatore:
    giocatore_sel = st.selectbox("Seleziona un giocatore:", lista_giocatori, key="scheda_sel")

    riga_g = df_stats[df_stats['Giocatore'] == giocatore_sel].iloc[0]

    st.markdown(f"### Profilo di **{giocatore_sel}**")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Presenze", f"{riga_g['Presenze']}")
    c2.metric("Vittorie", f"{riga_g['Vittorie']}", f"{riga_g['% Vittorie']}% Win Rate")
    c3.metric("Gol Totali", f"{riga_g['Gol Totali']}", f"{riga_g['Media Gol']} a partita")
    c4.metric("Scarto Reti", f"{riga_g['Scarto Reti']:+d}", f"{riga_g['Scarto Medio']:+.2f} medio")

    st.markdown("---")
    st.subheader("Storico Partite")

    storico = df_log[df_log['GIOCATORE'] == giocatore_sel].sort_values(by='DATA', ascending=False).copy()
    storico['Data'] = storico['DATA'].dt.strftime('%d/%m/%Y')
    storico['Risultato'] = storico['GOL FATTI SQUADRA'].astype(int).astype(str) + " - " + storico[
        'GOL SUBITI SQUADRA'].astype(int).astype(str)
    storico['Esito'] = storico.apply(
        lambda r: "✅ Vittoria" if r['GOL FATTI SQUADRA'] > r['GOL SUBITI SQUADRA'] else (
            "🤝 Pareggio" if r['GOL FATTI SQUADRA'] == r['GOL SUBITI SQUADRA'] else "❌ Sconfitta"),
        axis=1
    )

    colonne_vista = storico[['Data', 'SQUADRA', 'Risultato', 'GOL SEGNATI', 'Esito']].rename(columns={
        'SQUADRA': 'Squadra',
        'GOL SEGNATI': 'Gol Segnati'
    })
    colonne_vista['Gol Segnati'] = colonne_vista['Gol Segnati'].astype(int)

    st.dataframe(colonne_vista, use_container_width=True, hide_index=True)

# --- TAB 3: AFFINITÀ DI COPPIA ---
with tab_affinita:
    st.subheader("Confronto Diretto")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        g1 = st.selectbox("Giocatore 1:", lista_giocatori, index=0, key="aff_g1")
    with col_g2:
        default_g2 = 1 if len(lista_giocatori) > 1 else 0
        g2 = st.selectbox("Giocatore 2:", lista_giocatori, index=default_g2, key="aff_g2")

    if g1 == g2:
        st.warning("Seleziona due giocatori diversi per calcolare l'affinità di coppia.")
    else:
        match_g1 = set(df_log[df_log['GIOCATORE'] == g1]['MATCH_TEAM'])
        match_g2 = set(df_log[df_log['GIOCATORE'] == g2]['MATCH_TEAM'])
        match_comuni = match_g1.intersection(match_g2)

        if not match_comuni:
            st.info(f"**{g1}** e **{g2}** non hanno ancora giocato nella stessa squadra.")
        else:
            df_coppia = df_log[(df_log['GIOCATORE'] == g1) & (df_log['MATCH_TEAM'].isin(match_comuni))]
            partite_ins = len(df_coppia)
            vittorie_ins = int(df_coppia['VITTORIA'].sum())
            win_rate_ins = round((vittorie_ins / partite_ins) * 100, 1)
            scarto_ins = int(df_coppia['SCARTO'].sum())

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Partite Insieme", f"{partite_ins}")
            k2.metric("Vittorie Insieme", f"{vittorie_ins}")
            k3.metric("Win Rate Coppia", f"{win_rate_ins}%")
            k4.metric("Scarto Reti Insieme", f"{scarto_ins:+d}")

    st.markdown("---")
    st.subheader(f"Rendimento di {g1} con tutti i compagni")

    match_g1_all = set(df_log[df_log['GIOCATORE'] == g1]['MATCH_TEAM'])
    df_compagni = df_log[(df_log['MATCH_TEAM'].isin(match_g1_all)) & (df_log['GIOCATORE'] != g1)]

    if df_compagni.empty:
        st.info(f"Nessun compagno registrato per {g1}.")
    else:
        tab_compagni = df_compagni.groupby('GIOCATORE').agg(
            Partite_Insieme=('MATCH_TEAM', 'count'),
            Vittorie=('VITTORIA', 'sum'),
            Scarto_Reti=('SCARTO', 'sum')
        ).reset_index()

        tab_compagni['% Vittorie'] = (tab_compagni['Vittorie'] / tab_compagni['Partite_Insieme'] * 100).round(1)
        tab_compagni = tab_compagni.rename(columns={
            'GIOCATORE': 'Compagno',
            'Partite_Insieme': 'Partite Insieme',
            'Scarto_Reti': 'Scarto Reti'
        })

        for col in ['Partite Insieme', 'Vittorie', 'Scarto Reti']:
            tab_compagni[col] = tab_compagni[col].astype(int)

        tab_compagni = tab_compagni.sort_values(by=['% Vittorie', 'Partite Insieme'], ascending=[False, False])

        st.dataframe(
            tab_compagni,
            use_container_width=True,
            hide_index=True,
            column_config={
                "% Vittorie": st.column_config.NumberColumn(format="%.1f%%")
            }
        )