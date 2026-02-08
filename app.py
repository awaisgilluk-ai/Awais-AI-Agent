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

@st.cache_resource
def init_clients():
    return Groq(api_key=GROQ_API_KEY), Exa(api_key=EXA_API_KEY), ccxt.binance()

client, exa, binance = init_clients()

def get_technical_report(symbol, is_crypto=True):
    try:
        if is_crypto:
            # Har Crypto Token ke liye Binance Live
            bars = binance.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            src = f"Binance Live ({symbol})"
        else:
            # Har Stock/Gold/Forex ke liye Yahoo Live
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d", interval="1h")
            df.columns = [c.lower() for c in df.columns]
            src = f"Yahoo Finance ({symbol})"

        if df.empty: return None

        df['rsi'] = ta.rsi(df['close'], length=14)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        ma_20 = ta.sma(df['close'], length=20).iloc[-1]
        
        price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        atr = df['atr'].iloc[-1]
        
        return {
            "source": src, "price": round(price, 4), "rsi": round(rsi, 2), 
            "trend": "BULLISH" if price > ma_20 else "BEARISH",
            "sl": round(price - (atr * 2), 4), "tp": round(price + (atr * 3), 4)
        }
    except: return None

def get_fundamental_report(query):
    try:
        search_response = exa.search_and_contents(query, num_results=2, use_autoprompt=True, text={"max_characters": 500})
        return "\n".join([f"- {r.text[:300]}" for r in search_response.results])
    except: return "No live news found."

# --- UI ---
st.set_page_config(page_title="Awais Universal AI", layout="wide")

if "messages" not in st.session_state:
    # Saved Instructions [cite: 2026-02-08]
    st.session_state.messages = [{"role": "system", "content": "You are the UNIVERSAL COMMANDER. 1. If user says 'hay', reply 'data analysis' [cite: 2026-02-08]. 2. Reply 'Walaikum Assalam' to Salam. 3. Always provide 4-Filter Analysis for ANY asset (Crypto or Stock). Roman Urdu."}]

st.title("🛡️ Awais Universal AI Agent")

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("BNB, Gold, ya Tesla... kuch bhi puchen"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        p_low = prompt.lower()
        
        if p_low == "hay":
            ans = "data analysis"
        else:
            with st.spinner('Poori market scan kar raha hoon...'):
                greeting = "Walaikum Assalam Awais bhai! " if "salam" in p_low or "assalam" in p_low else ""
                
                # --- AUTO-DETECTION ENGINE ---
                target_symbol = ""
                is_crypto = False
                
                # Check for Crypto (Simple detection)
                tokens = ["btc", "eth", "bnb", "sol", "xrp", "ada", "doge", "matic", "link", "dot"]
                for t in tokens:
                    if t in p_low:
                        target_symbol = f"{t.upper()}/USDT"
                        is_crypto = True
                        break
                
                # If not crypto, check for Stocks or Gold
                if not target_symbol:
                    if "gold" in p_low: target_symbol = "GC=F"
                    elif "apple" in p_low: target_symbol = "AAPL"
                    elif "tesla" in p_low: target_symbol = "TSLA"
                    elif "nvdia" in p_low: target_symbol = "NVDA"
                    else: target_symbol = "BTC/USDT"; is_crypto = True # Default
                
                tech = get_technical_report(target_symbol, is_crypto)
                funda = get_fundamental_report(prompt)
                
                army_briefing = f"ASSET: {target_symbol}\nDATA: {tech}\nNEWS: {funda}\n\nTask: Commander, perform a professional 4-Filter analysis."

                response = client.chat.completions.create(
                    messages=st.session_state.messages + [{"role": "system", "content": army_briefing}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2
                )
                ans = greeting + response.choices[0].message.content

        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
