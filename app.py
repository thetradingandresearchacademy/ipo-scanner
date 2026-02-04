import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 🔱 TARA BRANDING & UI CONFIG ---
st.set_page_config(page_title="TARA IPO RADAR", layout="wide")

# High-Contrast Gold/White Theme with Centered Headers
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    
    /* Header Styling */
    .header-container { text-align: center; padding: 20px; }
    .main-title { color: #D4AF37 !important; font-weight: 800; text-transform: uppercase; font-size: 2.5rem; margin-bottom: 0; }
    .sub-title { color: #FFFFFF; font-size: 1.1rem; opacity: 0.8; letter-spacing: 2px; }
    
    /* Table & Footer */
    th { color: #D4AF37 !important; }
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0E1117; color: #666; 
              text-align: center; padding: 10px; font-size: 0.75rem; border-top: 1px solid #333; }
    
    /* Logo Positioning */
    .logo-img { position: absolute; top: -50px; left: 0px; width: 80px; }
    </style>
    """, unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/tradingandresearchacademy/logos/main/tara_logo.png" # Update with your actual URL
CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    # --- TOP UI AREA ---
    st.markdown(f"""
        <div class="header-container">
            <img src="{LOGO_URL}" class="logo-img">
            <h1 class="main-title">🔱 TARA PRO IPO RADAR</h1>
            <p class="sub-title">Powered by SwingLab</p>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(CSV_NAME):
        st.error(f"Universe CSV '{CSV_NAME}' not found. Please ensure it's in your GitHub repo.")
        return

    # 1. Load & Process Universe
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    # 6-Month Filter
    cutoff = datetime.now() - timedelta(days=180)
    active = df[df['DATE OF LISTING'] >= cutoff].copy()

    # 2. Analytics Summary
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Universe", len(active))
    c2.metric("SME Risk", len(active[active['SECURITY TYPE'] == 'SME']))
    c3.metric("Window", "180 Days")

    # 3. Quality Logic & Table Preparation
    results = []
    for _, row in active.iterrows():
        symbol = str(row['Symbol']).strip()
        age = (datetime.now() - row['DATE OF LISTING']).days
        
        # Scoring Logic
        stars = 3
        setup = "Consolidating"
        if 15 <= age <= 60:
            setup = "Primary Base (VCP)"
            stars = 5
        
        tv_url = f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        
        results.append({
            "Symbol": symbol,
            "Quality": "⭐" * stars,
            "Issue Price": row['ISSUE PRICE'],
            "Setup": setup,
            "Segment": "🚨 SME" if row['SECURITY TYPE'] == 'SME' else "Mainboard",
            "Age (Days)": age,
            "TV Link": tv_url
        })

    # 4. Interactive Table with Sorting
    res_df = pd.DataFrame(results)
    
    # Using st.column_config to make the Symbol a clickable link while keeping it sortable
    st.dataframe(
        res_df,
        column_config={
            "TV Link": st.column_config.LinkColumn("View Chart", display_text="Open TV"),
            "Issue Price": st.column_config.NumberColumn(format="₹%d"),
            "Symbol": st.column_config.TextColumn(help="Click header to sort")
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- SEBI SAFE FOOTER ---
    st.markdown("""
        <div class="footer">
            <b>DISCLAIMER:</b> Investment in securities market are subject to market risks. Read all the related documents carefully before investing. 
            Registration granted by SEBI, membership of BASL and certification from NISM in no way guarantee performance of the intermediary or provide any assurance of returns to investors. 
            The symbols and data provided are for educational purposes under the SwingLab Framework and not a recommendation.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
