import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 🔱 TARA BRANDING & UI ---
st.set_page_config(page_title="TARA IPO ANALYTICS", layout="wide")

st.markdown("""<style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; text-transform: uppercase; font-weight: bold; }
    .stTable { border: 1px solid #444; color: white; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    .status-box { padding: 10px; border-radius: 5px; border: 1px solid #D4AF37; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

CSV_NAME = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"

def main():
    st.title("🔱 TARA IPO ANALYTICS DASHBOARD")
    
    if not os.path.exists(CSV_NAME):
        st.error(f"Universe File '{CSV_NAME}' not found in GitHub.")
        return

    # 1. Load & Clean
    df = pd.read_csv(CSV_NAME)
    df.columns = df.columns.str.strip()
    df = df[df['SECURITY TYPE'].isin(['EQ', 'SME'])].copy()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    df['ISSUE PRICE'] = pd.to_numeric(df['ISSUE PRICE'].str.replace(',', '').str.strip(), errors='coerce')

    # 2. Analytics Calculation
    cutoff_6m = datetime.now() - timedelta(days=180)
    recent = df[df['DATE OF LISTING'] >= cutoff_6m].copy()
    
    # Summary Metrics
    total_ipos = len(recent)
    mainboard_count = len(recent[recent['SECURITY TYPE'] == 'EQ'])
    sme_count = len(recent[recent['SECURITY TYPE'] == 'SME'])

    # --- TOP DASHBOARD ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Universe", f"{total_ipos} IPOs")
    c2.metric("Mainboard (EQ)", mainboard_count)
    c3.metric("SME Segment", sme_count)
    c4.metric("Market Sentiment", "Bullish" if total_ipos > 20 else "Neutral")

    st.markdown("---")

    # --- ANALYTICAL TABLE ---
    st.subheader("🔱 Quality Rating & Strategy Scanner")
    
    scan_results = []
    for _, row in recent.iterrows():
        symbol = str(row['Symbol']).strip()
        # FIXED TV LINK FORMAT
        tv_url = f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        
        # QUALITY SCORING LOGIC (Age + Type + Pricing)
        age_days = (datetime.now() - row['DATE OF LISTING']).days
        
        # Scoring Criteria
        stars = 3 # Base
        setup = "Early Base"
        
        if age_days < 15: 
            setup = "Discovery Phase"
            stars = 2
        elif 15 <= age_days <= 60:
            setup = "Primary Base (Minervini)"
            stars = 5
        elif age_days > 60:
            setup = "Secondary Base"
            stars = 4

        scan_results.append({
            "Symbol": f'<a href="{tv_url}" target="_blank">{symbol}</a>',
            "Listing Date": row['DATE OF LISTING'].strftime('%d-%b-%Y'),
            "Type": row['SECURITY TYPE'],
            "Issue Price": f"₹{row['ISSUE PRICE']}",
            "Setup Type": setup,
            "Quality Rating": "⭐" * stars,
            "Age (Days)": age_days
        })

    # Display as HTML for clickable links
    report_df = pd.DataFrame(scan_results).sort_values("Age (Days)")
    st.write(report_df.to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
