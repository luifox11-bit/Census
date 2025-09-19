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
    layout="wide"
)

# Farbschema: Grün, Braun, Beige, Weiß, Schwarz
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57; /* Grün */
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .secondary-header {
        color: #8B4513; /* Braun */
        font-weight: 600;
    }
    .metric-card {
        background-color: #F5F5DC; /* Beige */
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #2E8B57;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #3CB371;
        color: white;
    }
    .delete-button {
        background-color: #8B4513 !important;
    }
    .sidebar .sidebar-content {
        background-color: #F5F5DC;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Titel der App
st.markdown('<h1 class="main-header">🌿 Finanz Portfolio Tracker</h1>', unsafe_allow_html=True)

# Portfolio-Daten initialisieren (leer beginnen)
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# CSV-Upload und Verarbeitung
def process_yuh_csv(uploaded_file):
    try:
        # CSV Datei lesen
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')
        
        # Transaktionen filtern (nur Käufe)
        buy_transactions = df[df['ACTIVITY TYPE'] == 'INVEST_ORDER_EXECUTED']
        
        assets_added = 0
        for _, transaction in buy_transactions.iterrows():
            activity_name = transaction['ACTIVITY NAME']
            
            # Asset-Informationen extrahieren
            match = re.search(r'([\d,.]+)x\s+(.+)', str(activity_name))
            if match:
                quantity = float(match.group(1).replace(',', ''))
                asset_name = match.group(2).strip()
                
                # Preis und Symbol extrahieren
                price_per_unit = transaction['PRICE PER UNIT']
                asset_symbol = transaction['ASSET']
                
                # Währung bestimmen
                currency = 'CHF' if transaction['DEBIT CURRENCY'] == 'CHF' else 'USD'
                
                # Asset zum Portfolio hinzufügen
                asset_key = f"{asset_name} ({asset_symbol})"
                if asset_key not in st.session_state.portfolio:
                    st.session_state.portfolio[asset_key] = {
                        "symbol": asset_symbol,
                        "quantity": quantity,
                        "purchase_price": price_per_unit,
                        "purchase_date": transaction['DATE'],
                        "current_price": price_per_unit * 1.05,  # 5% Gewinn simulieren
                        "type": "ETF" if "Vanguard" in asset_name else "Crypto" if "Bitcoin" in asset_name or "XBT" in asset_symbol else "Stock",
                        "currency": currency
                    }
                    assets_added += 1
        
        return assets_added
        
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der CSV-Datei: {e}")
        return 0

# Navigation
st.sidebar.markdown('<p class="secondary-header">Navigation</p>', unsafe_allow_html=True)
page = st.sidebar.radio("", ["Dashboard", "Asset hinzufügen", "CSV Import", "Portfolio Management", "Analysen"])

# Dashboard Seite
if page == "Dashboard":
    st.header("📊 Dashboard Übersicht")
    
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
            st.metric("Gesamt investiert", f"CHF {total_invested:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Aktueller Wert", f"CHF {total_current:,.2f}", 
                      f"{gain_percentage:+.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Gesamtgewinn/verlust", f"CHF {total_gain:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance Diagramme
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Asset-Verteilung")
            fig = px.pie(portfolio_df, values='Aktueller Wert', names=portfolio_df.index, 
                         color_discrete_sequence=['#2E8B57', '#8B4513', '#F5F5DC', '#3CB371', '#A0522D'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Performance nach Asset")
            fig = px.bar(portfolio_df, x=portfolio_df.index, y='Gewinn/Verlust %', 
                         title="Gewinn/Verlust in %",
                         color_discrete_sequence=['#2E8B57' if x >= 0 else '#8B4513' for x in portfolio_df['Gewinn/Verlust %']])
            fig.update_layout(xaxis_title="Asset", yaxis_title="Gewinn/Verlust %")
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
        
        st.dataframe(display_df, use_container_width=True)
        
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
        asset_type = col6.selectbox("Typ", ["Aktie", "ETF", "Krypto", "Fonds", "Rohstoffe"])
        
        currency = st.selectbox("Währung", ["CHF", "USD", "EUR"])
        
        submitted = st.form_submit_button("Asset hinzufügen")
        
        if submitted:
            if not name:
                st.error("Bitte geben Sie einen Namen für das Asset ein!")
            else:
                # Aktuellen Preis simulieren
                current_price = price * 1.05  # 5% Gewinn simulieren
                
                st.session_state.portfolio[name] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": price,
                    "purchase_date": str(date),
                    "current_price": current_price,
                    "type": asset_type,
                    "currency": currency
                }
                st.success(f"✅ {name} wurde erfolgreich hinzugefügt!")
                st.balloons()

# CSV Import Seite
elif page == "CSV Import":
    st.header("📤 CSV Datei importieren")
    
    st.info("""
    **Unterstütztes Format:** Yuh CSV Export (wie bereitgestellt)
    **So geht's:**
    1. Laden Sie Ihre CSV-Datei von Yuh herunter
    2. Laden Sie sie hier hoch
    3. Die App erkennt automatisch alle Kauf-Transaktionen
    """)
    
    uploaded_file = st.file_uploader("CSV Datei hochladen", type="csv")
    
    if uploaded_file is not None:
        assets_added = process_yuh_csv(uploaded_file)
        if assets_added > 0:
            st.success(f"✅ {assets_added} Assets wurden erfolgreich importiert!")
            st.balloons()
        else:
            st.warning("Keine neuen Assets in der CSV-Datei gefunden.")

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
                
                # Bearbeiten und Löschen Buttons
                col3, col4 = st.columns(2)
                
                with col3:
                    if st.button(f"Bearbeiten", key=f"edit_{asset_name}"):
                        st.session_state.editing_asset = asset_name
                
                with col4:
                    if st.button(f"Löschen", key=f"delete_{asset_name}", type="secondary"):
                        del st.session_state.portfolio[asset_name]
                        st.success(f"✅ {asset_name} wurde gelöscht!")
                        st.rerun()
        
        # Asset Bearbeiten Formular
        if 'editing_asset' in st.session_state:
            st.subheader("Asset bearbeiten")
            asset_name = st.session_state.editing_asset
            asset_data = st.session_state.portfolio[asset_name]
            
            with st.form("edit_asset_form"):
                new_name = st.text_input("Name", value=asset_name)
                new_quantity = st.number_input("Menge", value=asset_data['quantity'])
                new_price = st.number_input("Kaufpreis", value=asset_data['purchase_price'])
                
                if st.form_submit_button("Änderungen speichern"):
                    # Altes Asset löschen und neues hinzufügen
                    del st.session_state.portfolio[asset_name]
                    st.session_state.portfolio[new_name] = {
                        "symbol": asset_data['symbol'],
                        "quantity": new_quantity,
                        "purchase_price": new_price,
                        "purchase_date": asset_data['purchase_date'],
                        "current_price": new_price * 1.05,
                        "type": asset_data['type'],
                        "currency": asset_data['currency']
                    }
                    del st.session_state.editing_asset
                    st.success("✅ Asset wurde aktualisiert!")
                    st.rerun()
                
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
            fig = px.bar(type_performance, x='type', y='Gewinn/Verlust', 
                         title="Gewinn/Verlust nach Typ (CHF)",
                         color='type', color_discrete_sequence=['#2E8B57', '#8B4513', '#F5F5DC', '#3CB371'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(type_performance, values='Aktueller Wert', names='type', 
                         title="Verteilung nach Typ",
                         color_discrete_sequence=['#2E8B57', '#8B4513', '#F5F5DC', '#3CB371'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Performers
        st.subheader("Top Performers")
        top_performers = portfolio_df.nlargest(5, 'Gewinn/Verlust')
        fig = px.bar(top_performers, x=top_performers.index, y='Gewinn/Verlust',
                     title="Top 5 Assets nach Gewinn (CHF)",
                     color_discrete_sequence=['#2E8B57'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Risikoanalyse
        st.subheader("Risikoanalyse")
        portfolio_df['Volatilität'] = np.random.uniform(5, 25, len(portfolio_df))  # Simulierte Daten
        fig = px.scatter(portfolio_df, x='Volatilität', y='Gewinn/Verlust %', 
                         size='Aktueller Wert', hover_name=portfolio_df.index,
                         title="Risiko vs. Ertrag",
                         color_discrete_sequence=['#8B4513'])
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Fügen Sie Assets hinzu, um detaillierte Analysen zu sehen.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🌿 Finanz Portfolio Tracker | Erstellt mit Streamlit")
