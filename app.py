import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- UI CONFIG (WHITE/GOLD/DARK MODE) ---
st.set_page_config(page_title="TARA IPO PULSE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
    .stMetric { background-color: #1B1F27; border: 1px solid #D4AF37; padding: 15px; border-radius: 10px; }
    div[data-testid="metric-container"] label { color: #D4AF37 !important; font-weight: bold; text-transform: uppercase; }
    .star { color: #D4AF37; font-weight: bold; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stDataFrame { border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_market_data(tickers):
    # Fetching live data via yfinance (Server-side)
    return yf.download(tickers, period="10d", interval="1d", group_by='ticker', silent=True)

def run_tara_scanner(df):
    st.title("🔱 TARA IPO PULSE")
    st.subheader("Automated IPO Strategy Scanner | SwingLab Edition")
    
    # Pre-processing
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    active_universe = df[df['DATE OF LISTING'] >= (datetime.now() - timedelta(days=180))]
    symbols = [f"{s}.NS" for s in active_universe['Symbol'].dropna()]
    
    if not symbols:
        st.error("No active IPOs found in the last 6 months.")
        return

    data = get_market_data(symbols)
    results = []

    for ticker in symbols:
        try:
            hist = data[ticker]
            curr, prev = hist.iloc[-1], hist.iloc[-2]
            
            # --- STRATEGY LOGIC ---
            # 1. Inside Day (VCP)
            is_inside = (curr['High'] < prev['High']) and (curr['Low'] > prev['Low'])
            
            # 2. Orange Volume (Lowest in 5 days)
            is_low_vol = curr['Volume'] < hist['Volume'].tail(5).min() * 1.1
            
            # 3. RS Improvement (Outperforming Nifty - Placeholder logic)
            is_strong = curr['Close'] > prev['Close']
            
            # --- STAR RATING ---
            stars = 1 # Base
            if is_strong: stars += 1
            if is_inside: stars += 1
            if is_low_vol: stars += 1
            if curr['Close'] > hist['Close'].mean(): stars += 1 # Trend check
            
            # --- CATEGORY DETECTION ---
            category = "Scanning..."
            if is_inside and is_low_vol: category = "FLAG / VCP"
            elif curr['Close'] > hist['High'].max() * 0.98: category = "EARLY BOOM"
            
            results.append({
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr['Close'], 2),
                "Rating": "⭐" * stars,
                "Setup": category,
                "Volume Status": "QUIET (GOLD)" if is_low_vol else "Normal",
                "Action": "READY" if (is_inside and is_low_vol) else "Watch"
            })
        except: continue

    res_df = pd.DataFrame(results).sort_values(by="Rating", ascending=False)
    
    # UI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Scans", len(symbols))
    c2.metric("High Quality (4-5⭐)", len(res_df[res_df['Rating'].str.len() >= 4]))
    c3.metric("VCP Alerts", len(res_df[res_df['Volume Status'] == "QUIET (GOLD)"]))
    
    st.dataframe(res_df, use_container_width=True)

# Main App Flow
uploaded_file = st.sidebar.file_uploader("Upload IPO Universe (CSV)", type="csv")
if uploaded_file:
    run_tara_scanner(pd.read_csv(uploaded_file))
else:
    st.info("Please upload your weekly IPO CSV to start the scan.")
