import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# ---  UI CONFIG: MAX DENSITY & GOLD/WHITE ---
st.set_page_config(page_title="TARA PRO IPO RADAR", layout="wide")

# Precision CSS to eliminate empty spaces
st.markdown("""
    <style>
    /* Force Wide Layout & Minimal Padding */
    [data-testid="block-container"] { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Top Row Layout */
    .header-row { display: flex; align-items: flex-start; width: 100%; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px; }
    .logo-container { flex: 0 0 120px; text-align: left; }
    .center-branding { flex: 1; text-align: center; }
    .timestamp-box { flex: 0 0 120px; text-align: right; color: #D4AF37; font-size: 0.75rem; font-family: monospace; }
    
    .main-title { color: #D4AF37 !important; font-weight: 900; font-size: 2.2rem; margin: 0; line-height: 1; text-transform: uppercase; }
    .sub-title { color: #FFFFFF; font-size: 0.8rem; opacity: 0.7; letter-spacing: 5px; margin: 0; }
    
    /* Max Table Space */
    .stDataFrame { height: 75vh !important; border: 1px solid #D4AF37; }
    th { color: #D4AF37 !important; text-transform: uppercase; font-size: 0.85rem !important; }
    
    /* Footer Styling */
    .footer { text-align: center; color: #444; font-size: 0.7rem; border-top: 1px solid #222; padding: 10px 0; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Branding Variables
LOGO_URL = "https://raw.githubusercontent.com/tradingandresearchacademy/logos/main/tara_logo.png"
CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    # --- 1. COMPACT BRANDING HEADER ---
    last_sync = datetime.now().strftime("%H:%M:%S")
    
    st.markdown(f"""
        <div class="header-row">
            <div class="logo-container">
                <img src="{LOGO_URL}" width="90" onerror="this.style.display='none'">
            </div>
            <div class="center-branding">
                <h1 class="main-title"> IPO LENS FROM THE TRADING & RESEARCH ACADEMY - TARA </h1>
                <p class="sub-title">POWERED BY SWINGLAB</p>
            </div>
            <div class="timestamp-box">
                LAST SYNC<br><b>{last_sync}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(CSV_NAME):
        st.error(f"Universe CSV Missing.")
        return

    # --- 2. ENGINE ---
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].copy()

    # --- 3. SLIM METRIC BAR ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Universe", len(active))
    c2.metric("SME Risk", len(active[active['SECURITY TYPE'] == 'SME']))
    c3.metric("Primary Base", len(active[(datetime.now() - active['DATE OF LISTING']).dt.days.between(15,60)]))
    c4.metric("Window", "180D")

    # --- 4. THE SCANNER (FULL SCREEN HEIGHT) ---
    results = []
    for _, row in active.iterrows():
        symbol = str(row['Symbol']).strip()
        age = (datetime.now() - row['DATE OF LISTING']).days
        
        # Strategy Logic
        stars = 3
        setup = "Consolidating"
        if 15 <= age <= 60:
            setup = "PRIMARY BASE (VCP)"
            stars = 5
        elif age > 60:
            setup = "SECONDARY BASE"
            stars = 4
        
        results.append({
            "Symbol": symbol,
            "Quality": "⭐" * stars,
            "Setup Type": setup,
            "Age": age,
            "Risk": "🚨 SME" if row['SECURITY TYPE'] == 'SME' else "Mainboard",
            "Issue Price": row['ISSUE PRICE'],
            "Analysis": f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        })

    res_df = pd.DataFrame(results)

    # st.dataframe with height to fill the bottom space
    st.dataframe(
        res_df,
        column_config={
            "Analysis": st.column_config.LinkColumn("Chart", display_text="Open TV"),
            "Issue Price": st.column_config.NumberColumn(format="₹%d"),
            "Age": st.column_config.NumberColumn("Days Ago", format="%d"),
            "Symbol": st.column_config.TextColumn(help="Click to sort Universe")
        },
        use_container_width=True,
        hide_index=True,
        height=600 # Increased height to utilize bottom space
    )

    # --- 5. COMPLIANCE FOOTER ---
    st.markdown("""
        <div class="footer">
            <b>SEBI SAFE:</b> Investment in securities market are subject to market risks. Read all documents carefully. 
            Registration granted by SEBI, BASL and NISM does not guarantee performance. 
            SwingLab Framework is for educational intent. All symbols/setups are case-studies, not recommendations.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
