import streamlit as st
import requests
from groq import Groq
from datetime import datetime
import json
import os

# --- KEYS ---
SERPER_API_KEY = "32804b2829a40c8dadd2062d02ee7263618db626"
MEMORY_FILE = "bot_memory.json"

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Awais Personal Agent", layout="wide")

# --- MEMORY FUNCTIONS (Save/Load) ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are Awais bhai's personal AI Agent. Talk like a loyal assistant in Roman Urdu/Hindi. Remember his preferences. NO INTRODUCTIONS."}]

def save_memory(messages):
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f)

# Memory Load karna
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Search Function
def get_live_market(query):
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        res = requests.post(url, headers=headers, json={"q": f"{query} live price today"}, timeout=10)
        return " | ".join([r.get('snippet', '') for r in res.json().get('organic', [])[:3]])
    except: return "Data nahi mil raha."

st.title("🤖 Personal Agent (With Permanent Memory)")

# Display Chat
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

# User Input
if prompt := st.chat_input("Hukum karein Awais bhai..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        is_market_query = any(word in prompt.lower() for word in ["gold", "btc", "market", "price", "crypto", "oil"])
        live_data = get_live_market(prompt) if is_market_query else ""

        current_context = f"User: Awais bhai. Live Market: {live_data}. Remember past context."

        try:
            # Memory ke saath response generate karna
            response = client.chat.completions.create(
                messages=st.session_state.messages + [{"role": "system", "content": current_context}],
                model="llama-3.3-70b-versatile",
                temperature=0.6
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            
            # Har message ke baad file mein save karna
            save_memory(st.session_state.messages)
        except:
            st.error("Engine failure!")

# Sidebar mein Reset ka option (Memory saaf karne ke liye)
if st.sidebar.button("🗑️ Clear Permanent Memory"):
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    st.session_state.messages = [{"role": "system", "content": "You are Awais bhai's personal AI Agent. Talk like a loyal assistant in Roman Urdu/Hindi. NO INTRODUCTIONS."}]
    st.rerun()
    