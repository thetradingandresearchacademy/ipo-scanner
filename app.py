import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 🔱 TARA BRANDING (GOLD/WHITE/DARK) ---
st.set_page_config(page_title="TARA IPO Intelligence", layout="wide")

st.markdown("""<style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stTable { border: 1px solid #D4AF37; }
</style>""", unsafe_allow_html=True)

# --- AUTO-LOAD CSV ---
CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def get_ipo_universe():
    if os.path.exists(CSV_NAME):
        df = pd.read_csv(CSV_NAME)
        df.columns = df.columns.str.strip()
        return df
    return None

def main():
    st.title("🔱 TARA IPO PULSE")
    universe = get_ipo_universe()
    
    if universe is None:
        st.error(f"Universe File '{CSV_NAME}' not found. Please sync your GitHub repo.")
        return

    # Filter: Last 6 Months (The SwingLab Window)
    universe['DATE OF LISTING'] = pd.to_datetime(universe['DATE OF LISTING'], errors='coerce')
    six_months_ago = datetime.now() - timedelta(days=180)
    active_ipos = universe[universe['DATE OF LISTING'] >= six_months_ago].copy()
    
    # Cleaning Symbols for Google Finance
    active_ipos = active_ipos[active_ipos['SECURITY TYPE'].isin(['EQ', 'SME'])]
    
    st.subheader(f"Analyzing {len(active_ipos)} Active IPOs")

    # Display Table with Strategy Logic
    results = []
    for _, row in active_ipos.iterrows():
        symbol = row['Symbol']
        # Google Finance Link for Quick TA
        tv_link = f"https://www.tradingview.com/chart/?symbol=NSE%3A{symbol}"
        
        results.append({
            "Symbol": f"[{symbol}]({tv_link})",
            "Listing Date": row['DATE OF LISTING'].strftime('%d-%b-%Y'),
            "Type": row['SECURITY TYPE'],
            "Setup Check": "Waiting for Base...",
            "Rating": "⭐⭐⭐" # Placeholder for live logic
        })

    res_df = pd.DataFrame(results)
    st.write("### 🔱 Live Radar Table")
    st.write("Click on Symbol for TradingView Chart")
    st.table(res_df)

if __name__ == "__main__":
    main()
