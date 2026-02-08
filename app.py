import streamlit as st
import yfinance as yf
import ccxt
import pandas as pd
import pandas_ta as ta
from groq import Groq
from exa_py import Exa

# --- KEYS ---
GROQ_API_KEY = "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"
EXA_API_KEY = "Cb2283a3-9698-4634-ae9e-9bbb6da887d0"

# Connection caching (Only for speed, not for data)
@st.cache_resource
def init_clients():
    return Groq(api_key=GROQ_API_KEY), Exa(api_key=EXA_API_KEY), ccxt.binance()

client, exa, binance = init_clients()

# --- AGENT 1: TECHNICAL ANALYST (LIVE DATA ONLY) ---
def get_technical_report(symbol, source="binance"):
    try:
        if source == "binance":
            bars = binance.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            source_name = "Binance (Live)"
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d", interval="1h")
            df.columns = [c.lower() for c in df.columns]
            source_name = "Yahoo Finance (Live)"

        # Indicators
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        ma_20 = ta.sma(df['close'], length=20).iloc[-1]
        
        price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        atr = df['atr'].iloc[-1]
        trend = "BULLISH" if price > ma_20 else "BEARISH"
        
        sl = price - (atr * 2)
        tp = price + (atr * 3)
        
        return f"Source: {source_name} | Price: {price:.2f} | RSI: {rsi:.2f} | Trend: {trend} | SL: {sl:.2f} | TP: {tp:.2f}"
    except: return "Technical Analysis Fail: Market data not reachable."

# --- AGENT 2: FUNDAMENTAL RESEARCHER ---
def get_fundamental_report(query):
    try:
        search_response = exa.search_and_contents(
            query, num_results=2, use_autoprompt=True, text={"max_characters": 500}
        )
        return "\n".join([f"News: {r.text[:300]}" for r in search_response.results])
    except: return "No fundamental news found at the moment."

# --- UI SETUP ---
st.set_page_config(page_title="Awais AI Army", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are the COMMANDER. Always mention data sources (Binance/Yahoo). Apply the 4-filters: Trend, RSI, News, and Risk Management. Give analysis like a pro trader in Roman Urdu."}]

st.title("🎖️ Awais AI Army (Expert Mode)")

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("BTC ya Gold ka analysis puchen..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('Analyzing ...'):
            # Logic to pick the right target
            p_low = prompt.lower()
            if "btc" in p_low or "bitcoin" in p_low:
                target, source = "BTC/USDT", "binance"
            else:
                target, source = "GC=F", "yahoo"
            
            # Agents briefing
            tech_data = get_technical_report(target, source)
            fund_data = get_fundamental_report(prompt)
            
            army_context = f"REPORTS RECEIVED:\n1. {tech_data}\n2. {fund_data}\n\nTask: Compare and give an expert action plan."

            response = client.chat.completions.create(
                messages=st.session_state.messages + [{"role": "system", "content": army_context}],
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
