import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import re

# App-Konfiguration
st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        color: #1DB954; /* Spotify Grün */
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
        background-color: #191414; /* Dunkles Braun-Schwarz */
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid #2E2E2E;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 1rem;
        color: #A0A0A0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-change-positive {
        color: #1DB954;
        font-weight: 700;
    }
    .metric-change-negative {
        color: #E22134;
        font-weight: 700;
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
    }
    .stRadio > div > label:hover {
        background-color: #2A2A2A;
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
    }
    /* Custom Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #1DB954, transparent);
        margin: 2rem 0;
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
</style>
""", unsafe_allow_html=True)

# Titel der App
st.markdown('<h1 class="main-header">🌿 Finanz Portfolio Tracker</h1>', unsafe_allow_html=True)

# Portfolio-Daten initialisieren (leer beginnen)
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# Beispiel-Daten für Demo-Zwecke
if not st.session_state.portfolio:
    st.session_state.portfolio = {
        "Vanguard FTSE All-World (VWRA)": {
            "symbol": "VWRA",
            "quantity": 15.5,
            "purchase_price": 95.40,
            "purchase_date": "2023-05-15",
            "current_price": 102.30,
            "type": "ETF",
            "currency": "USD"
        },
        "Bitcoin (BTC)": {
            "symbol": "BTC",
            "quantity": 0.25,
            "purchase_price": 38500.00,
            "purchase_date": "2023-08-10",
            "current_price": 42000.00,
            "type": "Krypto",
            "currency": "USD"
        },
        "Apple Inc. (AAPL)": {
            "symbol": "AAPL",
            "quantity": 5,
            "purchase_price": 170.50,
            "purchase_date": "2023-10-05",
            "current_price": 185.20,
            "type": "Aktie",
            "currency": "USD"
        },
        "iShares Core S&P 500 (IVV)": {
            "symbol": "IVV",
            "quantity": 8,
            "purchase_price": 420.75,
            "purchase_date": "2023-03-22",
            "current_price": 455.30,
            "type": "ETF",
            "currency": "USD"
        }
    }

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
                        "current_price": price * np.random.uniform(0.95, 1.15),  # Etwas Variation
                        "type": asset_type,
                        "currency": currency
                    }
                
                assets_added += 1
                    
            except Exception as e:
                st.warning(f"Konnte Transaktion nicht verarbeiten: {str(row)}")
                continue
        
        return assets_added
        
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der CSV-Datei: {str(e)}")
        return 0

# Navigation
st.sidebar.markdown('<p class="sidebar-header">🌿 Navigation</p>', unsafe_allow_html=True)
page = st.sidebar.radio("", ["Dashboard", "Asset hinzufügen", "CSV Import", "Portfolio Management", "Analysen"], label_visibility="collapsed")

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
        col1, col2, col3 = st.columns(3)
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
        
        # Performance Diagramme
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Asset-Verteilung")
            if not portfolio_df.empty:
                fig = px.pie(portfolio_df, values='Aktueller Wert', names=portfolio_df.index, 
                             color_discrete_sequence=['#1DB954', '#191414', '#F5F5DC', '#3CB371', '#A0522D'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Performance nach Asset")
            if not portfolio_df.empty:
                fig = px.bar(portfolio_df, x=portfolio_df.index, y='Gewinn/Verlust %', 
                             title="Gewinn/Verlust in %",
                             color='Gewinn/Verlust %',
                             color_continuous_scale=['#E22134', '#1DB954'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    xaxis_title="Asset",
                    yaxis_title="Gewinn/Verlust %"
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
        
        name = col1.text_input("Name des Assets (z.B. 'Vanguard ETF')")
        symbol = col2.text_input("Symbol (z.B. 'VWCE.DE')")
        
        col3, col4 = st.columns(2)
        quantity = col3.number_input("Menge", min_value=0.0, format="%.4f", value=1.0)
        price = col4.number_input("Kaufpreis pro Stück", min_value=0.0, format="%.2f", value=100.0)
        
        col5, col6 = st.columns(2)
        date = col5.date_input("Kaufdatum", value=datetime.now())
        asset_type = col6.selectbox("Typ", ["Aktie", "ETF", "Krypto", "Fonds", "Rohstoffe", "Andere"])
        
        currency = st.selectbox("Währung", ["CHF", "USD", "EUR", "GBP", "JPY"])
        
        submitted = st.form_submit_button("Asset hinzufügen")
        
        if submitted:
            if not name:
                st.error("Bitte geben Sie einen Namen für das Asset ein!")
            else:
                # Aktuellen Preis simulieren
                current_price = price * np.random.uniform(0.9, 1.2)
                
                asset_key = f"{name} ({symbol})" if symbol else name
                st.session_state.portfolio[asset_key] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": price,
                    "purchase_date": str(date),
                    "current_price": current_price,
                    "type": asset_type,
                    "currency": currency
                }
                st.success(f"✅ {asset_key} wurde erfolgreich hinzugefügt!")
                st.balloons()

# CSV Import Seite
elif page == "CSV Import":
    st.header("📤 CSV Datei importieren")
    
    st.info("""
    **Unterstützte Formate:** Yuh, Standard CSV oder benutzerdefinierte Formate
    **Erwartete Spalten:** Asset-Name, Symbol, Menge, Kaufpreis (optional: Typ, Währung, Datum)
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

# Portfolio Management Seite
elif page == "Portfolio Management":
    st.header("⚙️ Portfolio Management")
    
    if st.session_state.portfolio:
        st.subheader("Aktuelle Assets")
        
        for asset_name, asset_data in list(st.session_state.portfolio.items()):
            with st.expander(f"{asset_name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Symbol:** {asset_data['symbol']}")
                    st.write(f"**Menge:** {asset_data['quantity']}")
                    st.write(f"**Kaufpreis:** {asset_data['purchase_price']} {asset_data['currency']}")
                
                with col2:
                    st.write(f"**Aktueller Preis:** {asset_data['current_price']} {asset_data['currency']}")
                    st.write(f"**Kaufdatum:** {asset_data['purchase_date']}")
                    st.write(f"**Typ:** {asset_data['type']}")
                
                # Gewinn/Verlust berechnen
                invested = asset_data['quantity'] * asset_data['purchase_price']
                current = asset_data['quantity'] * asset_data['current_price']
                gain = current - invested
                gain_percent = (gain / invested) * 100 if invested > 0 else 0
                
                st.write(f"**Gewinn/Verlust:** {gain:,.2f} {asset_data['currency']} ({gain_percent:+.2f}%)")
                
                # Bearbeiten und Löschen Buttons
                col3, col4 = st.columns(2)
                
                with col3:
                    if st.button(f"Bearbeiten", key=f"edit_{asset_name}"):
                        st.session_state.editing_asset = asset_name
                
                with col4:
                    if st.button(f"Löschen", key=f"delete_{asset_name}"):
                        del st.session_state.portfolio[asset_name]
                        st.success(f"✅ {asset_name} wurde gelöscht!")
                        st.rerun()
        
        # Asset Bearbeiten Formular
        if 'editing_asset' in st.session_state:
            st.subheader("Asset bearbeiten")
            asset_name = st.session_state.editing_asset
            asset_data = st.session_state.portfolio[asset_name]
            
            with st.form("edit_asset_form"):
                new_quantity = st.number_input("Menge", value=asset_data['quantity'], min_value=0.0, format="%.4f")
                new_price = st.number_input("Kaufpreis", value=asset_data['purchase_price'], min_value=0.0, format="%.2f")
                new_current_price = st.number_input("Aktueller Preis", value=asset_data['current_price'], min_value=0.0, format="%.2f")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Änderungen speichern"):
                        st.session_state.portfolio[asset_name]['quantity'] = new_quantity
                        st.session_state.portfolio[asset_name]['purchase_price'] = new_price
                        st.session_state.portfolio[asset_name]['current_price'] = new_current_price
                        del st.session_state.editing_asset
                        st.success("✅ Asset wurde aktualisiert!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Abbrechen"):
                        del st.session_state.editing_asset
                        st.rerun()
    
    else:
        st.info("Keine Assets zum Verwalten vorhanden.")

# Analysen Seite
else:
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
                             color='type', color_discrete_sequence=['#1DB954', '#191414', '#F5F5DC', '#3CB371'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not type_performance.empty:
                fig = px.pie(type_performance, values='Aktueller Wert', names='type', 
                             title="Verteilung nach Typ",
                             color_discrete_sequence=['#1DB954', '#191414', '#F5F5DC', '#3CB371'])
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
                font_color='#FFFFFF'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Risikoanalyse
        st.subheader("Risikoanalyse")
        if not portfolio_df.empty:
            portfolio_df['Volatilität'] = np.random.uniform(5, 25, len(portfolio_df))  # Simulierte Daten
            fig = px.scatter(portfolio_df, x='Volatilität', y='Gewinn/Verlust %', 
                             size='Aktueller Wert', hover_name=portfolio_df.index,
                             title="Risiko vs. Ertrag",
                             color_discrete_sequence=['#1DB954'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF'
            )
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Fügen Sie Assets hinzu, um detaillierte Analysen zu sehen.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🌿 Finanz Portfolio Tracker | Erstellt mit Streamlit")
