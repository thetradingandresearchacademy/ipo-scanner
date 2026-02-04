import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# --- 🔱 TARA BRANDING: HIGH-CONTRAST GOLD/WHITE ---
st.set_page_config(page_title="TARA PRO IPO RADAR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    div[data-testid="metric-container"] label { color: #D4AF37 !important; font-weight: bold; text-transform: uppercase; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800; text-transform: uppercase; }
    table { border: 1px solid #444; width: 100%; color: white; border-collapse: collapse; }
    th { color: #D4AF37 !important; border-bottom: 2px solid #D4AF37 !important; text-align: left; padding: 10px; }
    td { padding: 10px; border-bottom: 1px solid #333; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    .sme-badge { background-color: #721c24; color: #f8d7da; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🚀 RATE-PROOF NSE ENGINE ---
class TARAEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/"
        }
        self.session = requests.Session()
        self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)

    def fetch_quote(self, symbol):
        try:
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            resp = self.session.get(url, headers=self.headers, timeout=5)
            data = resp.json()
            return {
                "symbol": symbol,
                "LTP": data['priceInfo']['lastPrice'],
                "PrevClose": data['priceInfo']['close'] if data['priceInfo']['close'] != 0 else data['priceInfo']['previousClose'],
                "High": data['priceInfo']['intraDayHighLow']['max'],
                "Low": data['priceInfo']['intraDayHighLow']['min'],
                "Volume": data['priceInfo']['totalTradedVolume']
            }
        except: return None

# --- UI LOGIC ---
def run_app():
    st.title("🔱 TARA PRO IPO RADAR")
    
    CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"
    if not os.path.exists(CSV_NAME):
        st.error("Universe CSV not found in repository.")
        return

    # Load Universe
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    # 6-Month Focus
    active = df[df['DATE OF LISTING'] >= (datetime.now() - timedelta(days=180))].copy()
    symbols = active['Symbol'].dropna().unique()

    # Summary Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Universe", len(symbols))
    c2.metric("SME Risk Count", len(active[active['SECURITY TYPE'] == 'SME']))
    c3.metric("Data Source", "Direct NSE API")

    # Fast Multi-threaded Fetching
    engine = TARAEngine()
    results = []
    
    with st.spinner(f"🔱 TARA Intelligence scanning {len(symbols)} IPOs..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            raw_quotes = list(executor.map(engine.fetch_quote, symbols))

    # Quality Logic
    for quote in filter(None, raw_quotes):
        symbol = quote['symbol']
        row = active[active['Symbol'] == symbol].iloc[0]
        
        # Strategy Logic: VCP/Inside Day (Rough approximation via Day High/Low vs PrevClose)
        # Note: True VCP needs historical data; here we score based on Listing Strength & Vol
        roi = round(((quote['LTP'] - row['ISSUE PRICE']) / row['ISSUE PRICE']) * 100, 1)
        
        stars = 2
        if roi > 25: stars += 1
        if quote['LTP'] > quote['PrevClose']: stars += 1
        if quote['Volume'] > 100000: stars += 1

        # TradingView Link (Correct Format)
        tv_url = f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        
        results.append({
            "Symbol": f'<a href="{tv_url}" target="_blank">{symbol}</a>',
            "Rating": "⭐" * min(stars, 5),
            "LTP": f"₹{quote['LTP']}",
            "ROI%": f"{roi}%",
            "Setup": "Active" if quote['LTP'] > row['ISSUE PRICE'] else "Accumulation",
            "Risk": '<span class="sme-badge">🚨 SME</span>' if row['SECURITY TYPE'] == 'SME' else "Mainboard",
            "Age": (datetime.now() - row['DATE OF LISTING']).days
        })

    if results:
        res_df = pd.DataFrame(results).sort_values("ROI%", ascending=False)
        st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No live data returned. Check market hours.")

if __name__ == "__main__":
    run_app()
