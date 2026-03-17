import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("🚀 AI Stock Scanner Pro (India)")

# 🔥 Expanded stock list (mini NIFTY set)
stocks = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "ITC.NS","LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS",
    "BHARTIARTL.NS","ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS",
    "KOTAKBANK.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS"
]

results = []

st.write("🔍 Scanning market...")

# 🔥 RSI FUNCTION
def calculate_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# 🔁 SCAN LOOP
for stock in stocks:
    try:
        data = yf.download(stock, period="3mo", progress=False)

        if data.empty:
            continue

        # Fix columns
        if hasattr(data.columns, "levels"):
            data.columns = data.columns.get_level_values(0)

        data["Close"] = data["Close"].astype(float)
        data["Volume"] = data["Volume"].astype(float)

        # Indicators
        data["20D_High"] = data["Close"].rolling(20).max()
        data["Avg_Volume"] = data["Volume"].rolling(20).mean()
        data["RSI"] = calculate_rsi(data)

        latest_close = data["Close"].iloc[-1]
        latest_high = data["20D_High"].iloc[-1]
        latest_volume = data["Volume"].iloc[-1]
        avg_volume = data["Avg_Volume"].iloc[-1]
        latest_rsi = data["RSI"].iloc[-1]

        # 🎯 SMART SIGNAL
        if (
            latest_close >= latest_high and
            latest_volume > 1.5 * avg_volume and
            latest_rsi < 70
        ):
            signal = "🚀 Strong Buy"
        elif latest_close >= 0.95 * latest_high and latest_rsi < 65:
            signal = "⚡ Watchlist"
        else:
            signal = None

        if signal:
            results.append({
                "Stock": stock,
                "Price": round(latest_close, 2),
                "RSI": round(latest_rsi, 1),
                "Volume": int(latest_volume),
                "Signal": signal
            })

    except:
        continue

# 📊 SHOW RESULTS
st.subheader("📊 Opportunities")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df)

    # 🔥 SELECT STOCK FOR CHART
    selected_stock = st.selectbox("📈 View Chart", df["Stock"])

    chart_data = yf.download(selected_stock, period="3mo")

    if hasattr(chart_data.columns, "levels"):
        chart_data.columns = chart_data.columns.get_level_values(0)

    chart_data = chart_data.reset_index()

    fig = px.line(chart_data, x="Date", y="Close", title=selected_stock)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No strong opportunities found today.")
