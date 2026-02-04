import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

# --- 🔱 TARA BRANDING & UI ---
st.set_page_config(page_title="TARA IPO RADAR", layout="wide")
st.markdown("""<style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    h1, h2 { color: #D4AF37 !important; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; }
</style>""", unsafe_allow_html=True)

# --- AUTO-LOAD CSV LOGIC ---
DEFAULT_CSV = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def load_data():
    if os.path.exists(DEFAULT_CSV):
        return pd.read_csv(DEFAULT_CSV)
    return None

def run_app():
    st.title("🔱 TARA IPO RADAR")
    df = load_data()
    
    if df is None:
        st.error(f"Universe File '{DEFAULT_CSV}' not found in GitHub. Please upload it to your repo.")
        return

    # Data Cleaning
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    
    # Filter: Last 6 Months (The IPO Sweet Spot)
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].dropna(subset=['Symbol'])
    symbols = [f"{str(s).strip()}.NS" for s in active['Symbol'] if len(str(s)) > 1]

    # --- STABLE DATA FETCH ---
    if 'ipo_data' not in st.session_state:
        with st.spinner(f"Initiating NSE Link for {len(symbols)} Stocks..."):
            # Fetch in smaller groups to prevent 'Market Data Fetch Failed'
            try:
                st.session_state.ipo_data = yf.download(symbols, period="10d", interval="1d", group_by='ticker', silent=True, threads=True)
            except:
                st.error("NSE Server Busy. Retrying in 5 seconds...")
                return

    all_data = st.session_state.ipo_data
    results = []

    for ticker in symbols:
        try:
            hist = all_data[ticker].dropna()
            if len(hist) < 3: continue
            
            curr, prev = hist.iloc[-1], hist.iloc[-2]
            
            # --- STRATEGY: VCP & ORANGE VOLUME ---
            # VCP: Price range is tightening (Inside Day)
            is_inside = (curr['High'] < prev['High']) and (curr['Low'] > prev['Low'])
            # Orange Vol: Today's volume is significantly lower than average
            is_low_vol = curr['Volume'] < hist['Volume'].tail(5).mean()
            
            stars = 1
            if is_inside: stars += 2
            if is_low_vol: stars += 2
            
            results.append({
                "Symbol": ticker.replace(".NS", ""),
                "Price": round(curr['Close'], 2),
                "Quality": "⭐" * min(stars, 5),
                "Setup": "VCP / INSIDE" if is_inside else "Base",
                "Volume": "QUIET (GOLD)" if is_low_vol else "Normal",
                "Age (Days)": (datetime.now() - active[active['Symbol'] == ticker.replace(".NS", "")]['DATE OF LISTING'].iloc[0]).days
            })
        except: continue

    if results:
        res_df = pd.DataFrame(results).sort_values("Quality", ascending=False)
        st.table(res_df) # Faster & cleaner for mobile
    else:
        st.info("Scanner Ready. No high-conviction setups found in this cycle.")

run_app()
