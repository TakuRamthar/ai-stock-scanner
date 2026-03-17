import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 🔥 PAGE CONFIG
st.set_page_config(
    page_title="AI Stock Scanner Pro",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 AI Stock Scanner Pro (India)")

# 🔥 STOCK LIST (Expanded)
stocks = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "ITC.NS","LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS",
    "BHARTIARTL.NS","ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS",
    "KOTAKBANK.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS"
]

results = []

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

# 🤖 AI TREND FUNCTION
def ai_prediction(data):
    short_ma = data["Close"].rolling(5).mean().iloc[-1]
    long_ma = data["Close"].rolling(20).mean().iloc[-1]
    rsi = data["RSI"].iloc[-1]

    if short_ma > long_ma and rsi < 65:
        return "📈 Strong Uptrend"
    elif short_ma > long_ma:
        return "⚠️ Mild Uptrend"
    else:
        return "📉 Weak Trend"

# 🔄 SCAN WITH SPINNER (UI FIX)
with st.spinner("🔍 Scanning market for opportunities..."):

    for stock in stocks:
        try:
            data = yf.download(stock, period="3mo", progress=False)

            if data.empty:
                continue

            # Fix multi-index issue
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

            # 🎯 SMART SIGNAL (RELAXED LOGIC)
            if (
                latest_close >= 0.98 * latest_high and
                latest_volume > 1.2 * avg_volume and
                latest_rsi < 65
            ):
                signal = "🚀 Strong Buy"

            elif (
                latest_close >= 0.95 * latest_high and
                latest_rsi < 70
            ):
                signal = "⚡ Watchlist"

            else:
                signal = "📊 Trending"

            prediction = ai_prediction(data)

            results.append({
                "Stock": stock,
                "Price": round(latest_close, 2),
                "RSI": round(latest_rsi, 1),
                "Volume": int(latest_volume),
                "Signal": signal,
                "AI View": prediction
            })

        except:
            continue

# ✅ SCAN COMPLETE MESSAGE
st.success(f"✅ Scan Complete: {len(results)} stocks analyzed")

# 📊 DATAFRAME
df = pd.DataFrame(results)

# 🔥 SORT (BEST FIRST)
df = df.sort_values(by="RSI")

# 📊 METRICS
col1, col2 = st.columns(2)
col1.metric("📊 Stocks Scanned", len(stocks))
col2.metric("🎯 Opportunities Found", len(df[df["Signal"] != "📊 Trending"]))

# 📊 LAYOUT
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Market Opportunities")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("📈 Stock Chart")

    selected_stock = st.selectbox("Select Stock", df["Stock"])

    chart_data = yf.download(selected_stock, period="3mo")

    if hasattr(chart_data.columns, "levels"):
        chart_data.columns = chart_data.columns.get_level_values(0)

    chart_data = chart_data.reset_index()

    fig = px.line(chart_data, x="Date", y="Close", title=selected_stock)
    st.plotly_chart(fig, use_container_width=True)
