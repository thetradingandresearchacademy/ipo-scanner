import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 🔱 UI CONFIG: TIGHT & HIGH-CONTRAST ---
st.set_page_config(page_title="TARA PRO IPO RADAR", layout="wide")

# Compressed CSS for Zero Vertical Waste
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    [data-testid="block-container"] { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Header Container - Zero Waste */
    .brand-header { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 10px; gap: 20px; }
    .logo-box img { width: 60px; height: auto; }
    .title-box { text-align: center; }
    .main-title { color: #D4AF37 !important; font-weight: 800; font-size: 2rem; margin: 0; line-height: 1; }
    .sub-title { color: #FFFFFF; font-size: 0.9rem; opacity: 0.7; letter-spacing: 3px; margin: 0; }
    
    /* Metric & Table Styling */
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 10px !important; border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #D4AF37 !important; }
    
    /* Footer */
    .footer { width: 100%; color: #666; text-align: center; padding: 15px; font-size: 0.7rem; border-top: 1px solid #333; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Logo Placeholder - Use your actual GitHub link or Academy URL
LOGO_URL = "https://raw.githubusercontent.com/tradingandresearchacademy/logos/main/tara_logo.png"
CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    # --- 1. SLIM BRANDING ROW ---
    st.markdown(f"""
        <div class="brand-header">
            <div class="logo-box">
                <img src="{LOGO_URL}" onerror="this.src='https://via.placeholder.com/60/D4AF37/000000?text=TARA'">
            </div>
            <div class="title-box">
                <h1 class="main-title"IPO LENS FROM THE TRADING & RESEARCH ACADEMY (TARA) </h1>
                <p class="sub-title">POWERED BY SWINGLAB</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(CSV_NAME):
        st.error(f"Universe CSV Missing.")
        return

    # --- 2. FAST DATA ENGINE ---
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].copy()

    # --- 3. ANALYTICS METRICS (COMPACT) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Universe", len(active))
    c2.metric("SME Risk", len(active[active['SECURITY TYPE'] == 'SME']))
    c3.metric("Window", "180 Days")
    c4.metric("Status", "Ready")

    # --- 4. QUALITY SCANNER TABLE ---
    results = []
    for _, row in active.iterrows():
        symbol = str(row['Symbol']).strip()
        age = (datetime.now() - row['DATE OF LISTING']).days
        
        stars = 3
        setup = "Discovery"
        if 15 <= age <= 60:
            setup = "Primary Base (VCP)"
            stars = 5
        elif age > 60:
            setup = "Consolidation"
            stars = 4
        
        results.append({
            "Symbol": symbol,
            "Quality": "⭐" * stars,
            "Issue Price": row['ISSUE PRICE'],
            "Setup Type": setup,
            "Risk Filter": "🚨 SME" if row['SECURITY TYPE'] == 'SME' else "Mainboard",
            "Age (Days)": age,
            "TV Chart": f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        })

    res_df = pd.DataFrame(results)

    # Full Width Interactive Table with Sort Enabled
    st.dataframe(
        res_df,
        column_config={
            "TV Chart": st.column_config.LinkColumn("View", display_text="Open"),
            "Issue Price": st.column_config.NumberColumn(format="₹%d"),
            "Symbol": st.column_config.TextColumn(help="Click to sort"),
            "Quality": st.column_config.TextColumn(width="medium")
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- 5. SEBI SAFE FOOTER ---
    st.markdown("""
        <div class="footer">
            <b>DISCLAIMER:</b> Investment in securities market are subject to market risks. Read all the related documents carefully before investing. 
            Registration granted by SEBI, membership of BASL and certification from NISM in no way guarantee performance of the intermediary or provide any assurance of returns to investors. 
            The symbols/setups provided under the SwingLab Framework are for educational purposes and not buy/sell recommendations.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
