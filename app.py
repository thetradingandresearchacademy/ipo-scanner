import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# --- 🔱 TARA BRANDING & UI (WHITE/GOLD/DARK) ---
st.set_page_config(page_title="TARA PRO RADAR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .stMetric { border: 1px solid #D4AF37 !important; background-color: #1B1F27; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800; text-transform: uppercase; }
    th { color: #D4AF37 !important; border-bottom: 2px solid #D4AF37 !important; }
    a { color: #D4AF37 !important; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🚀 DIRECT NSE ENGINE (FAST & RATE-PROOF) ---
class NSEFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
        self.session = requests.Session()
        # Initialize session to get cookies
        self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)

    def get_quote(self, symbol):
        try:
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            response = self.session.get(url, headers=self.headers, timeout=5)
            data = response.json()
            return {
                "price": data['priceInfo']['lastPrice'],
                "pChng": data['priceInfo']['pChange'],
                "volume": data['priceInfo']['totalTradedVolume']
            }
        except: return None

# --- UI APP ---
def main():
    st.title("🔱 TARA PRO IPO RADAR")
    st.info("Direct NSE Link established. Zero Yahoo-Finance lag.")

    CSV_FILE = "IPO-PastIssue-04-02-2025-to-04-02-2026.csv"
    
    if not os.path.exists(CSV_FILE):
        st.error(f"Universe file '{CSV_FILE}' not found. Please sync your GitHub.")
        return

    # Process Universe
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip()
    df['DATE OF LISTING'] = pd.to_datetime(df['DATE OF LISTING'], errors='coerce')
    active = df[df['DATE OF LISTING'] >= (datetime.now() - timedelta(days=180))]
    symbols = active['Symbol'].dropna().unique()

    fetcher = NSEFetcher()
    results = []

    # Display results table
    with st.status("🔱 TARA Engine scanning live market...", expanded=True) as status:
        for sym in symbols:
            quote = fetcher.get_quote(sym)
            if quote:
                # TARA Quality Logic (VCP & Momentum)
                stars = 3
                if quote['pChng'] > 0: stars += 1
                if quote['volume'] > 50000: stars += 1
                
                results.append({
                    "Symbol": sym,
                    "LTP": quote['price'],
                    "Chg%": f"{quote['pChng']:.2f}%",
                    "Rating": "⭐" * min(stars, 5),
                    "Volume": f"{quote['volume']:,}",
                    "Type": active[active['Symbol']==sym]['SECURITY TYPE'].values[0]
                })
        status.update(label="Scan Complete!", state="complete", expanded=False)

    if results:
        res_df = pd.DataFrame(results).sort_values("Chg%", ascending=False)
        st.write("### 🔱 Live Quality Scanner")
        st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # --- TRADINGVIEW PRO WIDGET ---
        st.divider()
        st.markdown("### 🔱 Instant TA Radar")
        selected_sym = st.selectbox("Select Symbol for Charting", res_df['Symbol'].tolist())
        
        # High-Contrast Gold/Dark TV Widget
        st.components.v1.html(f"""
            <div style="height:600px; border: 2px solid #D4AF37; border-radius: 10px; overflow: hidden;">
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                  "width": "100%",
                  "height": 600,
                  "symbol": "NSE:{selected_sym}",
                  "interval": "D",
                  "timezone": "Asia/Kolkata",
                  "theme": "dark",
                  "style": "1",
                  "locale": "en",
                  "enable_publishing": false,
                  "allow_symbol_change": true,
                  "container_id": "tv_chart"
                }});
                </script>
                <div id="tv_chart"></div>
            </div>
        """, height=620)

if __name__ == "__main__":
    main()
