import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- UI CONFIG ---
st.set_page_config(page_title="TARA IPO PULSE", layout="wide")

# High-Contrast Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { background-color: #1B1F27; border: 1px solid #D4AF37; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_data_safe(tickers):
    try:
        # Fetch data with a timeout to prevent app hanging
        return yf.download(tickers, period="10d", interval="1d", group_by='ticker', silent=True, timeout=20)
    except Exception as e:
        st.error(f"Market Data Timeout: {e}")
        return None

def run_scanner(df):
    st.title("🔱 TARA IPO PULSE")
    
    # Data Cleaning
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    # Filter 6 months
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].copy()
    
    if active.empty:
        st.warning("No IPOs found in the 180-day window.")
        return

    symbols = [f"{str(s).strip()}.NS" for s in active['Symbol'].dropna() if s != "-"]
    
    with st.spinner('Syncing with NSE Data...'):
        all_data = get_data_safe(symbols)
    
    if all_data is None or all_data.empty:
        st.error("Could not retrieve live prices. Please check your internet or Ticker list.")
        return

    results = []
    for ticker in symbols:
        try:
            # Check if ticker exists in downloaded data
            if ticker not in all_data.columns.get_level_values(0): continue
            
            hist = all_data[ticker].dropna()
            if len(hist) < 2: continue
            
            curr, prev = hist.iloc[-1], hist.iloc[-2]
            
            # --- STRATEGY: INSIDE DAY + ORANGE VOLUME ---
            is_inside = (curr['High'] < prev['High']) and (curr['Low'] > prev['Low'])
            # Video Strategy: Lowest volume in last 5 days
            is_low_vol = curr['Volume'] <= hist['Volume'].tail(5).min() * 1.05
            
            stars = 1
            if is_inside: stars += 2
            if is_low_vol: stars += 2
            if curr['Close'] > prev['Close']: stars += 1

            results.append({
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr['Close'], 2),
                "Rating": "⭐" * min(stars, 5),
                "Setup": "VCP / INSIDE" if is_inside else "Consolidating",
                "Volume": "QUIET (GOLD)" if is_low_vol else "Normal",
                "ListingDate": active[active['Symbol'] == ticker.replace(".NS", "")]['DATE OF LISTING'].iloc[0].strftime('%Y-%m-%d')
            })
        except: continue

    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by="Rating", ascending=False)
        st.table(res_df) # Table is more stable than dataframe for mobile
    else:
        st.info("No active setups detected today. Keep the 'Five Star Patience'.")

# Main
uploaded_file = st.sidebar.file_uploader("Upload IPO CSV", type="csv")
if uploaded_file:
    run_scanner(pd.read_csv(uploaded_file))
else:
    st.info("🔱 Awaiting 'IPO Universe' CSV upload...")
