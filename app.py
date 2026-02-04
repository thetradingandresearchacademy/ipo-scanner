import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. UI SETUP (Gold/Dark Theme) ---
st.set_page_config(page_title="TARA IPO PULSE", layout="wide")
st.markdown("""<style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stTable { border: 1px solid #D4AF37; }
</style>""", unsafe_allow_html=True)

# --- 2. CORE SCANNER ENGINE ---
def run_stable_scan(df):
    st.title("🔱 TARA IPO PULSE")
    
    # Clean Column Names (Remove hidden spaces)
    df.columns = df.columns.str.strip()
    
    # Filter only Equities and SMEs (Exclude Debt/NCDs)
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])]
    
    # Process Dates
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].dropna(subset=['Symbol'])
    
    if active.empty:
        st.warning("No IPOs found in the 6-month window. Check CSV dates.")
        return

    # Prepare Symbols (Filter out non-string/empty symbols)
    symbols = [f"{str(s).strip()}.NS" for s in active['Symbol'] if len(str(s)) > 1]
    
    with st.spinner(f"Scanning {len(symbols)} Stocks..."):
        try:
            # Batch download to save time and prevent timeout
            all_data = yf.download(symbols, period="10d", interval="1d", group_by='ticker', silent=True, timeout=30)
        except Exception as e:
            st.error("Market data fetch failed. Try again in 1 minute.")
            return

    results = []
    for ticker in symbols:
        try:
            # Handle both Single and Multi-Index dataframes from yfinance
            hist = all_data[ticker].dropna() if len(symbols) > 1 else all_data.dropna()
            if len(hist) < 3: continue
            
            curr, prev = hist.iloc[-1], hist.iloc[-2]
            
            # --- STRATEGY: VCP + ORANGE VOLUME ---
            is_inside = (curr['High'] < prev['High']) and (curr['Low'] > prev['Low'])
            is_low_vol = curr['Volume'] < hist['Volume'].tail(5).mean()
            
            # Scoring
            stars = 1
            if is_inside: stars += 2
            if is_low_vol: stars += 2
            
            results.append({
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr['Close'], 2),
                "Rating": "⭐" * min(stars, 5),
                "Setup": "VCP / INSIDE" if is_inside else "Base",
                "Volume": "QUIET (GOLD)" if is_low_vol else "Normal",
                "Days Listed": (datetime.now() - active[active['Symbol'] == ticker.replace(".NS", "")]['DATE OF LISTING'].iloc[0]).days
            })
        except: continue

    if results:
        res_df = pd.DataFrame(results).sort_values("Rating", ascending=False)
        st.dataframe(res_df, use_container_width=True, hide_index=True)
    else:
        st.info("Scanner Ready. No VCP setups detected in current session.")

# --- 3. UPLOADER ---
uploaded_file = st.sidebar.file_uploader("Upload IPO CSV", type="csv")
if uploaded_file:
    try:
        input_df = pd.read_csv(uploaded_file)
        run_stable_scan(input_df)
    except Exception as e:
        st.error(f"Error reading CSV: {e}. Check if file matches IPO Universe format.")
else:
    st.info("🔱 Awaiting 'IPO Universe' CSV upload in sidebar...")
