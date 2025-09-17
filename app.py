import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# App-Konfiguration
st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📊",
    layout="wide"
)

# CSS für mobiles Design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Mock-Daten
def initialize_portfolio():
    return {
        "Vanguard FTSE All-World UCITS ETF": {
            "symbol": "VWCE.DE",
            "quantity": 0.7926,
            "purchase_price": 126.16,
            "purchase_date": "2025-08-08",
            "current_price": 132.47,
            "type": "ETF",
            "currency": "CHF"
        }
    }

# Portfolio-Daten laden
def load_portfolio_data():
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = initialize_portfolio()
    return st.session_state.portfolio

# Haupt-App
def main():
    st.markdown('<h1 class="main-header">📊 Portfolio Tracker</h1>', unsafe_allow_html=True)
    
    # Navigation für Mobile optimiert
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Seiten", ["Dashboard", "Asset hinzufügen", "Analysen"])
    
    portfolio = load_portfolio_data()
    
    if page == "Dashboard":
        show_dashboard(portfolio)
    elif page == "Asset hinzufügen":
        show_add_asset(portfolio)
    elif page == "Analysen":
        show_analytics(portfolio)

def show_dashboard(portfolio):
    st.header("Portfolio Übersicht")
    
    if portfolio:
        portfolio_df = pd.DataFrame.from_dict(portfolio, orient='index')
        portfolio_df['Investiert'] = portfolio_df['quantity'] * portfolio_df['purchase_price']
        portfolio_df['Aktueller Wert'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['Gewinn/Verlust'] = portfolio_df['Aktueller Wert'] - portfolio_df['Investiert']
        
        total_invested = portfolio_df['Investiert'].sum()
        total_current = portfolio_df['Aktueller Wert'].sum()
        total_gain = total_current - total_invested
        
        # Metriken in Spalten für Mobile optimiert
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Investiert", f"CHF {total_invested:,.2f}")
        with col2:
            st.metric("Aktuell", f"CHF {total_current:,.2f}")
        
        st.metric("Gewinn/Verlust", f"CHF {total_gain:,.2f}")
        
        # Asset-Tabelle
        st.subheader("Assets")
        for asset, data in portfolio.items():
            with st.expander(asset):
                st.write(f"Symbol: {data['symbol']}")
                st.write(f"Menge: {data['quantity']}")
                st.write(f"Kaufpreis: {data['purchase_price']} {data['currency']}")
                st.write(f"Aktueller Preis: {data['current_price']} {data['currency']}")
                st.write(f"Kaufdatum: {data['purchase_date']}")
    else:
        st.info("Fügen Sie Ihr erstes Asset hinzu!")

def show_add_asset(portfolio):
    st.header("Asset hinzufügen")
    
    with st.form("add_asset"):
        name = st.text_input("Name")
        symbol = st.text_input("Symbol")
        quantity = st.number_input("Menge", min_value=0.0, format="%.4f")
        price = st.number_input("Kaufpreis", min_value=0.0, format="%.2f")
        date = st.date_input("Kaufdatum")
        asset_type = st.selectbox("Typ", ["Aktie", "ETF", "Krypto"])
        
        if st.form_submit_button("Hinzufügen"):
            portfolio[name] = {
                "symbol": symbol,
                "quantity": quantity,
                "purchase_price": price,
                "purchase_date": str(date),
                "current_price": price * 1.05,  # Simulierter aktueller Preis
                "type": asset_type,
                "currency": "CHF"
            }
            st.success(f"{name} hinzugefügt!")

def show_analytics(portfolio):
    st.header("Analysen")
    
    if portfolio:
        # Einfache Kreisdiagramm für mobile Darstellung
        portfolio_df = pd.DataFrame.from_dict(portfolio, orient='index')
        portfolio_df['Wert'] = portfolio_df['quantity'] * portfolio_df['current_price']
        
        fig = px.pie(portfolio_df, values='Wert', names=portfolio_df.index, 
                     title="Portfolioverteilung")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Fügen Sie Assets hinzu, um Analysen zu sehen")

if __name__ == "__main__":
    main()
