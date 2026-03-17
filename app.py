import streamlit as st
import yfinance as yf
import pandas as pd

st.title("AI Stock Dashboard")

stock = st.text_input("Enter Stock Symbol", "RELIANCE.NS")

data = yf.download(stock, period="3mo")

st.line_chart(data["Close"])