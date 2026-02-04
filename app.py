import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ---  UI CONFIG: PRECISION BRANDING ---
st.set_page_config(page_title="TARA PRO IPO RADAR", layout="wide")

st.markdown("""
    <style>
    /* Global Dark/Gold Theme */
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Top Left Logo Fix */
    .logo-container { position: absolute; top: -50px; left: 0; z-index: 1000; }
    .logo-img { width: 100px; height: auto; }
    
    /* Centered Headings */
    .title-area { text-align: center; margin-top: -20px; margin-bottom: 20px; width: 100%; }
    .main-title { color: #D4AF37 !important; font-weight: 900; font-size: 2.8rem; letter-spacing: 2px; margin: 0; }
    .sub-title { color: #FFFFFF; font-size: 1.1rem; opacity: 0.8; letter-spacing: 4px; font-weight: 300; }
    
    /* Table & Metric Styling */
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 10px; border-radius: 8px; }
    th { color: #D4AF37 !important; font-weight: bold !important; text-transform: uppercase; }
    
    /* Footer */
    .footer { text-align: center; color: #555; font-size: 0.75rem; border-top: 1px solid #333; padding-top: 20px; margin-top: 30px; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Update this URL with your raw GitHub logo link
LOGO_URL = "https://raw.githubusercontent.com/tradingandresearchacademy/logos/main/tara_logo.png"
CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    # --- 1. BRANDING AREA (LOGO TOP LEFT, HEADINGS CENTERED) ---
    col_logo, col_title, col_empty = st.columns([1, 4, 1])
    
    with col_logo:
        # Logo placed at top left
        st.image(LOGO_URL, width=110)
        
    with col_title:
        # Centered Headings
        st.markdown(f"""
            <div class="title-area">
                <h1 class="main-title"> IPO LENS FROM TARA</h1>
                <p class="sub-title">POWERED BY SWINGLAB</p>
            </div>
        """, unsafe_allow_html=True)

    if not os.path.exists(CSV_NAME):
        st.error(f"Critical Error: {CSV_NAME} not found. Ensure file is in GitHub root.")
        return

    # --- 2. DATA PROCESSING ---
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    # 180 Days Active Window
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].copy()

    # --- 3. ANALYTICS METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Active", len(active))
    m2.metric("SME Segment", len(active[active['SECURITY TYPE'] == 'SME']))
    m3.metric("Mainboard", len(active[active['SECURITY TYPE'] == 'EQ']))
    m4.metric("Window", "6 Months")

    st.divider()

    # --- 4. QUALITY SCANNER TABLE (WITH FULL SORTING) ---
    results = []
    for _, row in active.iterrows():
        symbol = str(row['Symbol']).strip()
        age = (datetime.now() - row['DATE OF LISTING']).days
        
        # Strategy Detection
        stars = 3
        setup = "Consolidating"
        if 15 <= age <= 60:
            setup = "Primary Base (VCP)"
            stars = 5
        elif age > 60:
            setup = "Secondary Base"
            stars = 4
        
        results.append({
            "Symbol": symbol,
            "Quality": "⭐" * stars,
            "Issue Price": row['ISSUE PRICE'],
            "Setup Type": setup,
            "Risk Filter": "🚨 SME" if row['SECURITY TYPE'] == 'SME' else "Mainboard",
            "Days Listed": age,
            "Chart": f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        })

    res_df = pd.DataFrame(results)

    # Interactive Table with Auto-Sort Enabled
    st.dataframe(
        res_df,
        column_config={
            "Chart": st.column_config.LinkColumn("View", display_text="Open TV"),
            "Issue Price": st.column_config.NumberColumn(format="₹%d"),
            "Symbol": st.column_config.TextColumn(help="Click header to sort"),
            "Quality": st.column_config.TextColumn(width="medium")
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- 5. SEBI SAFE FOOTER ---
    st.markdown("""
        <div class="footer">
            <b>SEBI SAFE DISCLAIMER:</b> Investment in securities market are subject to market risks. Read all the related documents carefully before investing. 
            Registration granted by SEBI, membership of BASL and certification from NISM in no way guarantee performance of the intermediary or provide any assurance of returns to investors. 
            The setups identified under the SwingLab Framework are for educational purposes and do not constitute financial advice.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
