import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import re
import time
from streamlit.components.v1 import html
import yfinance as yf

# App-Konfiguration
st.set_page_config(
    page_title="Finanz Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modernes Farbschema: Grün, Braun, Beige, Weiß, Schwarz
st.markdown("""
<style>
    /* Globale Stile */
    .main {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #000000;
    }
    /* Header */
    .main-header {
        font-size: 3rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(45deg, #1DB954, #191414);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* Seitenüberschriften */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    /* Metrik-Karten */
    .metric-card {
        background-color: #191414;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid #2E2E2E;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(29, 185, 84, 0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #A0A0A0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .metric-change-positive {
        color: #1DB954;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .metric-change-negative {
        color: #E22134;
        font-weight: 700;
        font-size: 1.1rem;
    }
    /* Buttons */
    .stButton > button {
        background-color: #1DB954;
        color: #FFFFFF;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #1ED760;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    .secondary-button > button {
        background-color: transparent;
        color: #1DB954;
        border: 2px solid #1DB954;
    }
    .secondary-button > button:hover {
        background-color: rgba(29, 185, 84, 0.1);
    }
    .danger-button > button {
        background-color: transparent;
        color: #E22134;
        border: 2px solid #E22134;
    }
    .danger-button > button:hover {
        background-color: rgba(226, 33, 52, 0.1);
    }
    /* Sidebar */
    .css-1d391kg, .css-1oe5cao {
        background-color: #191414;
    }
    .sidebar-header {
        color: #1DB954 !important;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    /* Formulare */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #191414;
        color: #FFFFFF;
        border: 1px solid #2E2E2E;
        border-radius: 8px;
        padding: 0.75rem;
    }
    /* Dataframes */
    .dataframe {
        background-color: #191414;
        color: #FFFFFF;
    }
    /* Radio-Buttons in der Sidebar */
    .stRadio > div {
        flex-direction: column;
        gap: 0.5rem;
    }
    .stRadio > div > label {
        color: #FFFFFF !important;
        padding: 0.75rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
        background-color: #191414;
        border: 1px solid #2E2E2E;
    }
    .stRadio > div > label:hover {
        background-color: #2A2A2A;
        border-color: #1DB954;
    }
    .stRadio > div > label[data-testid="stRadioLabel"] > div:first-child {
        background-color: #191414;
    }
    .stRadio > div > label[data-testid="stRadioLabel"] > div:first-child > div {
        border-color: #1DB954;
    }
    .stRadio > div > label[data-testid="stRadioLabel"] > div:first-child > div > div {
        background-color: #1DB954;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #191414;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        gap: 8px;
        font-weight: 600;
        border: 1px solid #2E2E2E;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1DB954;
        color: #000000;
    }
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #191414;
        color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #2E2E2E;
        padding: 0.75rem 1rem;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover {
        background-color: #2A2A2A;
    }
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: #1DB954;
    }
    /* Code */
    .stCode {
        border-radius: 8px;
    }
    /* Info, Success, Warning Boxes */
    .stAlert {
        border-radius: 8px;
        background-color: #191414;
        border: 1px solid #2E2E2E;
    }
    /* Custom Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #1DB954, transparent);
        margin: 2rem 0;
    }
    /* Asset Card */
    .asset-card {
        background-color: #191414;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #2E2E2E;
        transition: all 0.3s ease;
    }
    .asset-card:hover {
        border-color: #1DB954;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(29, 185, 84, 0.1);
    }
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-value {
            font-size: 1.5rem;
        }
    }
    /* Loading Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .pulse {
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Titel der App
st.markdown('<h1 class="main-header">🌿 Finanz Portfolio Tracker</h1>', unsafe_allow_html=True)

# Portfolio-Daten initialisieren
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'last_price_update' not in st.session_state:
    st.session_state.last_price_update = None
if 'price_history' not in st.session_state:
    st.session_state.price_history = {}

# Beispiel-Daten für Demo-Zwecke
if not st.session_state.portfolio:
    st.session_state.portfolio = {
        "Vanguard FTSE All-World (VWRA)": {
            "symbol": "VWRA.AS",
            "quantity": 15.5,
            "purchase_price": 95.40,
            "purchase_date": "2023-05-15",
            "current_price": 102.30,
            "type": "ETF",
            "currency": "EUR",
            "sector": "Global"
        },
        "Bitcoin (BTC)": {
            "symbol": "BTC-USD",
            "quantity": 0.25,
            "purchase_price": 38500.00,
            "purchase_date": "2023-08-10",
            "current_price": 42000.00,
            "type": "Krypto",
            "currency": "USD",
            "sector": "Kryptowährung"
        },
        "Apple Inc. (AAPL)": {
            "symbol": "AAPL",
            "quantity": 5,
            "purchase_price": 170.50,
            "purchase_date": "2023-10-05",
            "current_price": 185.20,
            "type": "Aktie",
            "currency": "USD",
            "sector": "Technology"
        },
        "iShares Core S&P 500 (IVV)": {
            "symbol": "IVV",
            "quantity": 8,
            "purchase_price": 420.75,
            "purchase_date": "2023-03-22",
            "current_price": 455.30,
            "type": "ETF",
            "currency": "USD",
            "sector": "US Large Cap"
        },
        "Nestlé SA (NESN)": {
            "symbol": "NESN.SW",
            "quantity": 10,
            "purchase_price": 105.20,
            "purchase_date": "2023-07-18",
            "current_price": 112.50,
            "type": "Aktie",
            "currency": "CHF",
            "sector": "Consumer Goods"
        }
    }

# Funktion zum Abrufen aktueller Preise von Yahoo Finance
def update_prices_from_yahoo():
    """Aktualisiere Preise von Yahoo Finance"""
    if st.session_state.portfolio:
        with st.spinner("Aktualisiere Preise von Yahoo Finance..."):
            progress_bar = st.progress(0)
            assets = list(st.session_state.portfolio.keys())
            
            for i, asset_name in enumerate(assets):
                asset_data = st.session_state.portfolio[asset_name]
                symbol = asset_data['symbol']
                
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty and 'Close' in hist:
                        current_price = hist['Close'].iloc[-1]
                        st.session_state.portfolio[asset_name]['current_price'] = current_price
                        
                        # Preisverlauf speichern
                        if asset_name not in st.session_state.price_history:
                            st.session_state.price_history[asset_name] = []
                        
                        st.session_state.price_history[asset_name].append({
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'price': current_price
                        })
                    
                    # Fortschritt aktualisieren
                    progress_bar.progress((i + 1) / len(assets))
                    time.sleep(0.1)  # Kurze Pause um API nicht zu überlasten
                    
                except Exception as e:
                    st.error(f"Fehler beim Abrufen des Preises für {asset_name}: {str(e)}")
            
            st.session_state.last_price_update = datetime.now()
            st.success("Preise erfolgreich aktualisiert!")
            st.rerun()

# CSV-Upload und Verarbeitung für verschiedene Formate
def process_csv(uploaded_file):
    try:
        # CSV Datei lesen mit korrekter Kodierung
        content = uploaded_file.read().decode('utf-8-sig')
        df = pd.read_csv(io.StringIO(content), sep=';|,', engine='python')
        
        assets_added = 0
        for _, row in df.iterrows():
            try:
                # Verschiedene CSV-Formate unterstützen
                if 'Ticker' in df.columns and 'Quantity' in df.columns and 'Price' in df.columns:
                    # Standardformat
                    asset_name = row['Ticker']
                    symbol = row['Ticker']
                    quantity = float(row['Quantity'])
                    price = float(row['Price'])
                    asset_type = row.get('Type', 'Aktie')
                    currency = row.get('Currency', 'USD')
                    date = row.get('Date', datetime.now().strftime('%Y-%m-%d'))
                    sector = row.get('Sector', 'Allgemein')
                
                elif 'ACTIVITY TYPE' in df.columns and df['ACTIVITY TYPE'].str.contains('INVEST_ORDER_EXECUTED').any():
                    # Yuh-Format
                    if row['ACTIVITY TYPE'] != 'INVEST_ORDER_EXECUTED':
                        continue
                    
                    activity_name = str(row['ACTIVITY NAME'])
                    quantity_match = re.search(r'([\d,\.]+)x', activity_name)
                    name_match = re.search(r'x\s+(.+)', activity_name)
                    
                    if quantity_match and name_match:
                        quantity_str = quantity_match.group(1).replace(',', '')
                        quantity = float(quantity_str)
                        asset_name = name_match.group(1).strip()
                        symbol = row['ASSET'] if pd.notna(row['ASSET']) else asset_name
                        price = float(row['PRICE PER UNIT']) if pd.notna(row['PRICE PER UNIT']) else 0
                        currency = row['DEBIT CURRENCY'] if pd.notna(row['DEBIT CURRENCY']) else 'CHF'
                        date = row['DATE']
                        sector = 'Allgemein'
                        
                        # Asset-Typ bestimmen
                        asset_name_upper = asset_name.upper()
                        if any(x in asset_name_upper for x in ['VANGUARD', 'ISHARES', 'ETF', 'FONDS']):
                            asset_type = "ETF"
                        elif any(x in asset_name_upper for x in ['XBT', 'XRP', 'XLM', 'LNK', 'BTC', 'ETH']):
                            asset_type = "Krypto"
                        elif 'GOLD' in asset_name_upper or 'SILVER' in asset_name_upper:
                            asset_type = "Rohstoffe"
                        else:
                            asset_type = "Aktie"
                
                else:
                    # Einfaches Format: Name, Symbol, Quantity, Price
                    asset_name = row.iloc[0] if len(row) > 0 else "Unbekannt"
                    symbol = row.iloc[1] if len(row) > 1 else asset_name
                    quantity = float(row.iloc[2]) if len(row) > 2 else 0
                    price = float(row.iloc[3]) if len(row) > 3 else 0
                    asset_type = row.iloc[4] if len(row) > 4 else "Aktie"
                    currency = row.iloc[5] if len(row) > 5 else "USD"
                    date = row.iloc[6] if len(row) > 6 else datetime.now().strftime('%Y-%m-%d')
                    sector = row.iloc[7] if len(row) > 7 else "Allgemein"
                
                # Einzigartigen Schlüssel erstellen
                asset_key = f"{asset_name} ({symbol})"
                
                # Prüfen ob Asset bereits existiert und Menge addieren
                if asset_key in st.session_state.portfolio:
                    st.session_state.portfolio[asset_key]['quantity'] += quantity
                    # Durchschnittspreis berechnen
                    old_value = st.session_state.portfolio[asset_key]['quantity'] * st.session_state.portfolio[asset_key]['purchase_price']
                    new_value = quantity * price
                    total_quantity = st.session_state.portfolio[asset_key]['quantity']
                    st.session_state.portfolio[asset_key]['purchase_price'] = (old_value + new_value) / total_quantity
                else:
                    # Neues Asset hinzufügen
                    st.session_state.portfolio[asset_key] = {
                        "symbol": symbol,
                        "quantity": quantity,
                        "purchase_price": price,
                        "purchase_date": date,
                        "current_price": price,  # Startet mit Kaufpreis
                        "type": asset_type,
                        "currency": currency,
                        "sector": sector
                    }
                
                assets_added += 1
                    
            except Exception as e:
                st.warning(f"Konnte Transaktion nicht verarbeiten: {str(row)}. Fehler: {str(e)}")
                continue
        
        return assets_added
        
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der CSV-Datei: {str(e)}")
        return 0

# Funktion zum Exportieren des Portfolios als CSV
def export_portfolio():
    """Exportiere Portfolio als CSV"""
    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame.from_dict(st.session_state.portfolio, orient='index')
        return portfolio_df.to_csv(index=True)
    return None

# Navigation
st.sidebar.markdown('<p class="sidebar-header">🌿 Navigation</p>', unsafe_allow_html=True)
page = st.sidebar.radio("", ["Dashboard", "Asset hinzufügen", "CSV Import", "Portfolio Management", "Analysen", "Einstellungen"], label_visibility="collapsed")

# Preise aktualisieren Button in der Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Preise aktualisieren", use_container_width=True):
    update_prices_from_yahoo()

if st.session_state.last_price_update:
    st.sidebar.caption(f"Letzte Aktualisierung: {st.session_state.last_price_update.strftime('%d.%m.%Y %H:%M')}")

# Dashboard Seite
if page == "Dashboard":
    st.header("📊 Portfolio Übersicht")
    
    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame.from_dict(st.session_state.portfolio, orient='index')
        portfolio_df['Investiert'] = portfolio_df['quantity'] * portfolio_df['purchase_price']
        portfolio_df['Aktueller Wert'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['Gewinn/Verlust'] = portfolio_df['Aktueller Wert'] - portfolio_df['Investiert']
        portfolio_df['Gewinn/Verlust %'] = (portfolio_df['Gewinn/Verlust'] / portfolio_df['Investiert']) * 100
        
        total_invested = portfolio_df['Investiert'].sum()
        total_current = portfolio_df['Aktueller Wert'].sum()
        total_gain = total_current - total_invested
        gain_percentage = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        # Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Gesamt investiert</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">CHF {total_invested:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Aktueller Wert</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">CHF {total_current:,.2f}</p>', unsafe_allow_html=True)
            change_class = "metric-change-positive" if gain_percentage >= 0 else "metric-change-negative"
            st.markdown(f'<p class="{change_class}">{gain_percentage:+.2f}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Gesamtgewinn/verlust</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">CHF {total_gain:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-label">Anzahl Assets</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{len(portfolio_df)}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance Diagramme
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Asset-Verteilung nach Wert")
            if not portfolio_df.empty:
                fig = px.pie(portfolio_df, values='Aktueller Wert', names=portfolio_df.index, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Performance nach Asset")
            if not portfolio_df.empty:
                fig = px.bar(portfolio_df.sort_values('Gewinn/Verlust %', ascending=False), 
                             x=portfolio_df.index, y='Gewinn/Verlust %', 
                             title="Gewinn/Verlust in %",
                             color='Gewinn/Verlust %',
                             color_continuous_scale=['#E22134', '#1DB954'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    xaxis_title="Asset",
                    yaxis_title="Gewinn/Verlust %",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Detaillierte Asset-Tabelle
        st.subheader("Asset Details")
        display_df = portfolio_df[['symbol', 'quantity', 'purchase_price', 'current_price', 
                                  'Investiert', 'Aktueller Wert', 'Gewinn/Verlust', 'Gewinn/Verlust %']].copy()
        display_df.columns = ['Symbol', 'Menge', 'Kaufpreis', 'Aktueller Preis', 
                             'Investiert (CHF)', 'Aktueller Wert (CHF)', 'Gewinn/Verlust (CHF)', 'Gewinn/Verlust %']
        
        # Formatierung
        for col in ['Kaufpreis', 'Aktueller Preis', 'Investiert (CHF)', 'Aktueller Wert (CHF)', 'Gewinn/Verlust (CHF)']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f}")
        display_df['Gewinn/Verlust %'] = display_df['Gewinn/Verlust %'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
    else:
        st.info("❌ Noch keine Assets vorhanden. Gehen Sie zu 'CSV Import' oder 'Asset hinzufügen' um Investments hinzuzufügen.")

# Asset hinzufügen Seite
elif page == "Asset hinzufügen":
    st.header("➕ Neues Asset hinzufügen")
    
    with st.form("add_asset_form"):
        col1, col2 = st.columns(2)
        
        name = col1.text_input("Name des Assets (z.B. 'Vanguard ETF')", placeholder="Apple Inc.")
        symbol = col2.text_input("Symbol (z.B. 'AAPL')", placeholder="AAPL")
        
        col3, col4 = st.columns(2)
        quantity = col3.number_input("Menge", min_value=0.0001, format="%.4f", value=1.0, step=0.0001)
        price = col4.number_input("Kaufpreis pro Stück", min_value=0.01, format="%.2f", value=100.0, step=0.01)
        
        col5, col6 = st.columns(2)
        date = col5.date_input("Kaufdatum", value=datetime.now())
        asset_type = col6.selectbox("Typ", ["Aktie", "ETF", "Krypto", "Fonds", "Rohstoffe", "Anleihe", "Andere"])
        
        col7, col8 = st.columns(2)
        currency = col7.selectbox("Währung", ["CHF", "USD", "EUR", "GBP", "JPY", "CNY"])
        sector = col8.selectbox("Sektor", ["Technology", "Healthcare", "Financial", "Consumer", "Energy", "Industrial", "Other"])
        
        submitted = st.form_submit_button("Asset hinzufügen")
        
        if submitted:
            if not name or not symbol:
                st.error("Bitte geben Sie einen Namen und ein Symbol für das Asset ein!")
            else:
                # Aktuellen Preis setzen
                current_price = price
                
                asset_key = f"{name} ({symbol})"
                st.session_state.portfolio[asset_key] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": price,
                    "purchase_date": str(date),
                    "current_price": current_price,
                    "type": asset_type,
                    "currency": currency,
                    "sector": sector
                }
                st.success(f"✅ {asset_key} wurde erfolgreich hinzugefügt!")
                st.balloons()

# CSV Import Seite
elif page == "CSV Import":
    st.header("📤 CSV Datei importieren")
    
    tab1, tab2 = st.tabs(["Datei hochladen", "Vorlage herunterladen"])
    
    with tab1:
        st.info("""
        **Unterstützte Formate:** Yuh, Standard CSV oder benutzerdefinierte Formate
        **Erwartete Spalten:** Asset-Name, Symbol, Menge, Kaufpreis (optional: Typ, Währung, Datum, Sektor)
        """)
        
        uploaded_file = st.file_uploader("CSV Datei hochladen", type="csv")
        
        if uploaded_file is not None:
            with st.spinner("Verarbeite CSV-Datei..."):
                assets_added = process_csv(uploaded_file)
                
            if assets_added > 0:
                st.success(f"✅ {assets_added} Assets wurden erfolgreich importiert!")
                st.balloons()
                st.info("Wechseln Sie zum Dashboard um Ihre Portfolio-Übersicht zu sehen.")
            else:
                st.warning("Keine neuen Transaktionen in der CSV-Datei gefunden oder Format nicht erkannt.")
    
    with tab2:
        st.subheader("CSV-Vorlage")
        st.download_button(
            label="Vorlage herunterladen",
            data="Name,Symbol,Menge,Kaufpreis,Typ,Währung,Datum,Sektor\nApple Inc.,AAPL,10,150.50,Aktie,USD,2023-01-15,Technology\nVanguard S&P 500 ETF,VOO,5,350.75,ETF,USD,2023-02-20,US Large Cap",
            file_name="portfolio_vorlage.csv",
            mime="text/csv"
        )

# Portfolio Management Seite
elif page == "Portfolio Management":
    st.header("⚙️ Portfolio Management")
    
    if st.session_state.portfolio:
        # Export-Button
        csv_data = export_portfolio()
        if csv_data:
            st.download_button(
                label="📥 Portfolio exportieren",
                data=csv_data,
                file_name="portfolio_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.subheader("Aktuelle Assets")
        
        for asset_name, asset_data in list(st.session_state.portfolio.items()):
            with st.expander(f"{asset_name}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Symbol:** {asset_data['symbol']}")
                    st.write(f"**Menge:** {asset_data['quantity']}")
                    st.write(f"**Kaufpreis:** {asset_data['purchase_price']} {asset_data['currency']}")
                    st.write(f"**Sektor:** {asset_data.get('sector', 'Nicht angegeben')}")
                
                with col2:
                    st.write(f"**Aktueller Preis:** {asset_data['current_price']} {asset_data['currency']}")
                    st.write(f"**Kaufdatum:** {asset_data['purchase_date']}")
                    st.write(f"**Typ:** {asset_data['type']}")
                
                # Gewinn/Verlust berechnen
                invested = asset_data['quantity'] * asset_data['purchase_price']
                current = asset_data['quantity'] * asset_data['current_price']
                gain = current - invested
                gain_percent = (gain / invested) * 100 if invested > 0 else 0
                
                change_class = "metric-change-positive" if gain >= 0 else "metric-change-negative"
                st.markdown(f"**Gewinn/Verlust:** <span class='{change_class}'>{gain:,.2f} {asset_data['currency']} ({gain_percent:+.2f}%)</span>", unsafe_allow_html=True)
                
                # Bearbeiten und Löschen Buttons
                col3, col4 = st.columns(2)
                
                with col3:
                    if st.button(f"Bearbeiten", key=f"edit_{asset_name}"):
                        st.session_state.editing_asset = asset_name
                
                with col4:
                    if st.button(f"Löschen", key=f"delete_{asset_name}"):
                        del st.session_state.portfolio[asset_name]
                        if asset_name in st.session_state.price_history:
                            del st.session_state.price_history[asset_name]
                        st.success(f"✅ {asset_name} wurde gelöscht!")
                        st.rerun()
        
        # Asset Bearbeiten Formular
        if 'editing_asset' in st.session_state:
            st.subheader("Asset bearbeiten")
            asset_name = st.session_state.editing_asset
            asset_data = st.session_state.portfolio[asset_name]
            
            with st.form("edit_asset_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_quantity = st.number_input("Menge", value=asset_data['quantity'], min_value=0.0001, format="%.4f", step=0.0001)
                    new_price = st.number_input("Kaufpreis", value=asset_data['purchase_price'], min_value=0.01, format="%.2f", step=0.01)
                
                with col2:
                    new_current_price = st.number_input("Aktueller Preis", value=asset_data['current_price'], min_value=0.01, format="%.2f", step=0.01)
                    new_sector = st.text_input("Sektor", value=asset_data.get('sector', ''))
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.form_submit_button("Änderungen speichern"):
                        st.session_state.portfolio[asset_name]['quantity'] = new_quantity
                        st.session_state.portfolio[asset_name]['purchase_price'] = new_price
                        st.session_state.portfolio[asset_name]['current_price'] = new_current_price
                        st.session_state.portfolio[asset_name]['sector'] = new_sector
                        del st.session_state.editing_asset
                        st.success("✅ Asset wurde aktualisiert!")
                        st.rerun()
                
                with col4:
                    if st.form_submit_button("Abbrechen"):
                        del st.session_state.editing_asset
                        st.rerun()
    
    else:
        st.info("Keine Assets zum Verwalten vorhanden.")

# Analysen Seite
elif page == "Analysen":
    st.header("📈 Detaillierte Analysen")
    
    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame.from_dict(st.session_state.portfolio, orient='index')
        portfolio_df['Investiert'] = portfolio_df['quantity'] * portfolio_df['purchase_price']
        portfolio_df['Aktueller Wert'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['Gewinn/Verlust'] = portfolio_df['Aktueller Wert'] - portfolio_df['Investiert']
        
        # Performance nach Asset Typ
        st.subheader("Performance nach Asset Typ")
        type_performance = portfolio_df.groupby('type').agg({
            'Investiert': 'sum',
            'Aktueller Wert': 'sum',
            'Gewinn/Verlust': 'sum'
        }).reset_index()
        
        type_performance['Gewinn/Verlust %'] = (type_performance['Gewinn/Verlust'] / type_performance['Investiert']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not type_performance.empty:
                fig = px.bar(type_performance, x='type', y='Gewinn/Verlust', 
                             title="Gewinn/Verlust nach Typ (CHF)",
                             color='type', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not type_performance.empty:
                fig = px.pie(type_performance, values='Aktueller Wert', names='type', 
                             title="Verteilung nach Typ",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Performance nach Sektor
        if 'sector' in portfolio_df.columns:
            st.subheader("Performance nach Sektor")
            sector_performance = portfolio_df.groupby('sector').agg({
                'Investiert': 'sum',
                'Aktueller Wert': 'sum',
                'Gewinn/Verlust': 'sum'
            }).reset_index()
            
            sector_performance['Gewinn/Verlust %'] = (sector_performance['Gewinn/Verlust'] / sector_performance['Investiert']) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                if not sector_performance.empty:
                    fig = px.bar(sector_performance, x='sector', y='Gewinn/Verlust', 
                                 title="Gewinn/Verlust nach Sektor (CHF)",
                                 color='sector', color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#FFFFFF',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if not sector_performance.empty:
                    fig = px.pie(sector_performance, values='Aktueller Wert', names='sector', 
                                 title="Verteilung nach Sektor",
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#FFFFFF'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Top Performers
        st.subheader("Top Performers")
        if not portfolio_df.empty:
            top_performers = portfolio_df.nlargest(5, 'Gewinn/Verlust')
            fig = px.bar(top_performers, x=top_performers.index, y='Gewinn/Verlust',
                         title="Top 5 Assets nach Gewinn (CHF)",
                         color_discrete_sequence=['#1DB954'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Risikoanalyse
        st.subheader("Risikoanalyse")
        if not portfolio_df.empty:
            portfolio_df['Volatilität'] = np.random.uniform(5, 25, len(portfolio_df))  # Simulierte Daten
            fig = px.scatter(portfolio_df, x='Volatilität', y='Gewinn/Verlust %', 
                             size='Aktueller Wert', hover_name=portfolio_df.index,
                             title="Risiko vs. Ertrag",
                             color='Gewinn/Verlust %',
                             color_continuous_scale=['#E22134', '#1DB954'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Preisverlauf anzeigen
        if st.session_state.price_history:
            st.subheader("Preisverlauf")
            selected_asset = st.selectbox("Asset auswählen", options=list(st.session_state.price_history.keys()))
            
            if selected_asset and st.session_state.price_history[selected_asset]:
                history_df = pd.DataFrame(st.session_state.price_history[selected_asset])
                history_df['date'] = pd.to_datetime(history_df['date'])
                
                fig = px.line(history_df, x='date', y='price', 
                              title=f"Preisverlauf für {selected_asset}",
                              markers=True)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    xaxis_title="Datum",
                    yaxis_title="Preis"
                )
                st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Fügen Sie Assets hinzu, um detaillierte Analysen zu sehen.")

# Einstellungen Seite
else:
    st.header("⚙️ Einstellungen")
    
    st.subheader("Portfolio zurücksetzen")
    st.warning("Diese Aktion löscht alle Ihre Portfolio-Daten und kann nicht rückgängig gemacht werden.")
    
    if st.button("Portfolio zurücksetzen", type="secondary"):
        st.session_state.portfolio = {}
        st.session_state.price_history = {}
        st.session_state.last_price_update = None
        st.success("Portfolio wurde zurückgesetzt!")
        st.rerun()
    
    st.subheader("Daten-Backup")
    csv_data = export_portfolio()
    if csv_data:
        st.download_button(
            label="Backup erstellen",
            data=csv_data,
            file_name="portfolio_backup.csv",
            mime="text/csv"
        )
    
    st.subheader("Design-Einstellungen")
    theme = st.selectbox("Farbschema", ["Dunkel (Standard)", "Hell"])
    st.info("Das Farbschema wird nach einem Neuladen der Seite aktiv.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🌿 Finanz Portfolio Tracker v2.0 | Erstellt mit Streamlit")

# Auto-Update der Preise (alle 30 Minuten)
if st.session_state.portfolio and st.session_state.last_price_update:
    time_diff = datetime.now() - st.session_state.last_price_update
    if time_diff.total_seconds() > 1800:  # 30 Minuten
        with st.sidebar:
            with st.spinner("Preise werden aktualisiert..."):
                update_prices_from_yahoo()
