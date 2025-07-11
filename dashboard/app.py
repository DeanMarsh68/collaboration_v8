import streamlit as st
import pandas as pd
import plotly.express as px
from collaboration.config import START_BANKROLL

st.set_page_config("collaboration_v8", layout="wide")

@st.cache(ttl=30)
def load_ledger():
    return pd.read_csv("ledger.csv", parse_dates=["date"])

ledger           = load_ledger()
ledger["type"]   = ledger.market.apply(lambda m: "Double" if m.startswith("DOUBLE_") else "Single")

col1, col2, col3 = st.columns(3)
col1.metric("ROI",      f"{ledger['return'].sum()/START_BANKROLL:.2%}")
col2.metric("Hit Rate", f"{ledger.win.mean():.2%}")
col3.metric("Sharpe(50)", f"{ledger['return'].rolling(50).mean().iloc[-1]/ledger['return'].rolling(50).std().iloc[-1]:.2f}")

st.subheader("ROI: Singles vs Doubles")
st.bar_chart(ledger.groupby("type")["return"].sum() / START_BANKROLL)

st.subheader("Bankroll Over Time")
fig = px.line(ledger, x="date", y="bankroll", color="type")
st.plotly_chart(fig, use_container_width=True)
