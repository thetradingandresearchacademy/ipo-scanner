import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

# --- 🔱 UI CONFIG ---
st.set_page_config(page_title="TARA IPO RADAR", layout="wide")
st.markdown("""<style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800; text-transform: uppercase; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    .stars { color: #D4AF37; font-size: 1.2rem; }
    .sme-tag { background-color: #721c24; color: #f8d7da; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
</style>""", unsafe_allow_html=True)

CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

# --- CACHED UNIVERSE PROCESSING ---
@st.cache_data(ttl=3600)
def get_clean_universe(file_name):
    if not os.path.exists(file_name): return None
    df = pd.read_csv(file_name)
    df.columns = df.columns.str.strip()
    # Filter for Equities & SMEs only to speed up fetch
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    # Focus on last 6 months
    cutoff = datetime.now() - timedelta(days=180)
    return df[df['DATE OF LISTING'] >= cutoff].dropna(subset=['Symbol'])

# --- HIGH-SPEED DATA FETCH ---
@st.cache_data(ttl=300) # Refresh data every 5 minutes
def fetch_market_data(symbols):
    # Use threads=True and batch download for max speed
    return yf.download(symbols, period="5d", interval="1d", group_by='ticker', silent=True, threads=True, timeout=15)

def main():
    st.title("🔱 TARA IPO Intelligence")
    
    active = get_clean_universe(CSV_NAME)
    if active is None:
        st.error(f"Universe file {CSV_NAME} not found. Ensure it is in your GitHub repo.")
        return

    # Prepare Symbol List
    symbols = [f"{str(s).strip()}.NS" for s in active['Symbol'] if len(str(s)) > 1]
    
    with st.spinner(f"🔱 TARA Engine: Scanning {len(symbols)} Stocks..."):
        all_data = fetch_market_data(symbols)
    
    results = []
    for _, row in active.iterrows():
        ticker = f"{row['Symbol']}.NS"
        try:
            # Extract data safely
            hist = all_data[ticker].dropna() if len(symbols) > 1 else all_data.dropna()
            if hist.empty: continue
            
            curr, prev = hist.iloc[-1], hist.iloc[-2]
            ltp = round(curr['Close'], 2)
            
            # --- TARA QUALITY SCORING ---
            roi = round(((ltp - row['ISSUE PRICE']) / row['ISSUE PRICE']) * 100, 1)
            age = (datetime.now() - row['DATE OF LISTING']).days
            
            # Setup Detection
            is_inside = (curr['High'] < prev['High']) and (curr['Low'] > prev['Low'])
            is_low_vol = curr['Volume'] < hist['Volume'].mean()
            
            stars = 2
            if roi > 20: stars += 1
            if is_inside: stars += 1
            if is_low_vol: stars += 1
            if row['SECURITY TYPE'] == 'SME' and row['ISSUE PRICE'] > 250: stars -= 1 # Risk penalty
            
            # TradingView Link
            tv_url = f"https://www.tradingview.com/symbols/NSE-{row['Symbol']}/"
            
            results.append({
                "Symbol": f'<a href="{tv_url}" target="_blank">{row["Symbol"]}</a>',
                "Rating": "⭐" * min(max(stars, 1), 5),
                "LTP": f"₹{ltp}",
                "ROI%": f"{roi}%",
                "Setup": "VCP/INSIDE" if is_inside else "Trend",
                "Risk": "🚨 SME" if row['SECURITY TYPE'] == 'SME' else "Mainboard",
                "Age": f"{age}d"
            })
        except: continue

    # --- UI RENDERING ---
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Rating", ascending=False)
        
        # Summary Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Universe", len(symbols))
        c2.metric("Top Rated (5⭐)", len(res_df[res_df['Rating'] == "⭐⭐⭐⭐⭐"]))
        c3.metric("Avg ROI", f"{round(pd.to_numeric(res_df['ROI%'].str.replace('%','')).mean(),1)}%")

        st.markdown("---")
        st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Scanner Active. Waiting for market hours or valid data.")

if __name__ == "__main__":
    main()
