import streamlit as st
import pandas as pd
from datetime import date
from streamlit_autorefresh import st_autorefresh
from growwapi import GrowwAPI
st.set_page_config(page_title="Sensex Options Tracker", layout="wide")
st.title("📊 SENSEX LIVE OPTIONS TRACKER")
st.caption("Groww API | CE + PE | 15-second refresh")
# Refresh
st_autorefresh(interval=15000, key="refresh")
# Settings
expiry = st.sidebar.date_input("SENSEX Expiry", value=date.today())
token = st.sidebar.text_input("Groww API Access Token", type="password")
if not token:
   st.warning("Groww API token required. Add it in Streamlit Secrets after deployment.")
st.info("No live market data is being displayed yet.")
   st.stop()
try:
   groww = GrowwAPI(token)
   chain = groww.get_option_chain(
       exchange=groww.EXCHANGE_BSE,
       underlying="SENSEX",
       expiry_date=expiry.strftime("%Y-%m-%d")
   )
   spot = chain.get("underlying_ltp")
   strikes = chain.get("strikes", {})
   st.metric("SENSEX Spot", f"₹{spot:,.2f}" if spot else "N/A")
   rows = []
   for strike, sides in strikes.items():
       for side in ["CE", "PE"]:
           option = sides.get(side, {})
           greeks = option.get("greeks", {})
           rows.append({
               "Strike": strike,
               "Type": side,
               "LTP": option.get("ltp"),
               "OI": option.get("open_interest"),
               "Volume": option.get("volume"),
               "Delta": greeks.get("delta"),
               "Gamma": greeks.get("gamma"),
               "Theta": greeks.get("theta"),
               "Vega": greeks.get("vega"),
               "IV": greeks.get("iv")
           })
   df = pd.DataFrame(rows)
   ce, pe = st.tabs(["CALL OPTIONS (CE)", "PUT OPTIONS (PE)"])
   with ce:
       st.dataframe(
           df[df["Type"] == "CE"],
           use_container_width=True,
           hide_index=True
       )
   with pe:
       st.dataframe(
           df[df["Type"] == "PE"],
           use_container_width=True,
           hide_index=True
       )
   st.caption("Data refreshes every 15 seconds while this page is open.")
   st.caption("Use your own risk controls. This dashboard does not guarantee entry signals.")
except Exception as e:
   st.error(f"Groww API error: {e}")
st.info("Check API access, expiry date and SENSEX contract availability.")
