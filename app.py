import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 🔱 TARA BRANDING: GOLD/WHITE/DARK ---
st.set_page_config(page_title="TARA PRO IPO RADAR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; border: 1px solid #444; }
    th { color: #D4AF37 !important; border-bottom: 2px solid #D4AF37 !important; text-align: left; padding: 12px; }
    td { padding: 12px; border-bottom: 1px solid #333; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    .sme-risk { color: #FF4B4B; font-weight: bold; font-size: 0.85rem; border: 1px solid #FF4B4B; padding: 2px 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    st.title("🔱 TARA PRO IPO RADAR")
    
    if not os.path.exists(CSV_NAME):
        st.error(f"Universe CSV '{CSV_NAME}' not found. Please upload it to your GitHub.")
        return

    # 1. Process Universe
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')
    
    # 6-Month Focused Window
    active = df[df['DATE OF LISTING'] >= (datetime.now() - timedelta(days=180))].copy()
    
    # 2. Analytics Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("Universe", len(active))
    c2.metric("SME Segment", len(active[active['SECURITY TYPE'] == 'SME']))
    c3.metric("Engine", "TARA Multi-Cloud")

    st.divider()
    st.subheader("🔱 Quality Setup Scanner")

    # 3. Strategy Table
    results = []
    for _, row in active.iterrows():
        symbol = str(row['Symbol']).strip()
        age = (datetime.now() - row['DATE OF LISTING']).days
        
        # FIXED TV & GOOGLE LINKS
        tv_url = f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        
        # Risk & Quality Scoring
        risk = "Mainboard"
        stars = 3
        
        if row['SECURITY TYPE'] == 'SME':
            risk = '<span class="sme-risk">🚨 HIGH RISK (SME)</span>'
            if row['ISSUE PRICE'] > 200: stars -= 1
            
        # Strategy Logic based on Age (Primary Base Detection)
        setup = "Discovery"
        if 15 <= age <= 60:
            setup = "Primary Base (VCP)"
            stars = 5
        elif age > 60:
            setup = "Consolidation"
            stars = 4

        results.append({
            "Symbol": f'<a href="{tv_url}" target="_blank">{symbol}</a>',
            "Rating": "⭐" * stars,
            "Issue Price": f"₹{row['ISSUE PRICE']}",
            "Setup Type": setup,
            "Risk Filter": risk,
            "Age": f"{age}d"
        })

    if results:
        res_df = pd.DataFrame(results).sort_values("Age")
        st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # 4. TA Radar Widget
        st.divider()
        st.markdown("### 🔱 Deep TA Radar")
        selected = st.selectbox("Select Symbol for Charting", [r['Symbol'].split('>')[1].split('<')[0] for r in results])
        st.components.v1.html(f"""
            <div style="height:500px; border:1px solid #D4AF37;">
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                  "width": "100%", "height": 500, "symbol": "NSE:{selected}",
                  "interval": "D", "theme": "dark", "style": "1", "locale": "en",
                  "container_id": "tv_chart"
                }});
                </script>
                <div id="tv_chart"></div>
            </div>
        """, height=520)

if __name__ == "__main__":
    main()
