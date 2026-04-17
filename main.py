import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Agent Builder - VIP", page_icon="👑")

# ========== DATABASE ==========
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 🔥 GLOBAL STORE FOR USED UTR NUMBERS 🔥
if "used_utr_numbers" not in st.session_state:
    st.session_state.used_utr_numbers = []

CREATOR_EMAIL = "ChandanYadavofficial74@gmail.com"
UPI_ID = "chandanyadavofficial74@okicici"

def get_user_data(email):
    if email not in st.session_state.users:
        st.session_state.users[email] = {
            "agents_used": 0,
            "is_premium": False,
            "expiry": None,
            "is_creator": (email == CREATOR_EMAIL),
            "transaction_id": None,
            "payment_verified": False
        }
        if email == CREATOR_EMAIL:
            st.session_state.users[email]["is_premium"] = True
            st.session_state.users[email]["is_creator"] = True
            st.session_state.users[email]["payment_verified"] = True
    return st.session_state.users[email]

def can_create_agent(email):
    user = get_user_data(email)
    if user["is_creator"]:
        return True, "creator"
    if user["is_premium"]:
        if user["expiry"] and datetime.now() > user["expiry"]:
            user["is_premium"] = False
            return False, "premium_expired"
        return True, "premium"
    if user["agents_used"] < 3:
        return True, "free"
    return False, "free_limit"

def increment_agent(email):
    user = get_user_data(email)
    if not user["is_premium"] and not user["is_creator"]:
        user["agents_used"] += 1

def activate_premium(email, days=30, transaction_id=None):
    user = get_user_data(email)
    user["is_premium"] = True
    user["expiry"] = datetime.now() + timedelta(days=days)
    user["payment_verified"] = True
    if transaction_id:
        user["transaction_id"] = transaction_id

def is_utr_used(utr_number):
    return utr_number in st.session_state.used_utr_numbers

def mark_utr_as_used(utr_number):
    st.session_state.used_utr_numbers.append(utr_number)

# ========== LOGIN ==========
st.sidebar.title("👤 Account")
email = st.sidebar.text_input("Email ID")

if email:
    user_data = get_user_data(email)
    st.sidebar.markdown("---")
    if user_data["is_creator"]:
        st.sidebar.success("👑 VIP CREATOR - Unlimited")
    elif user_data["is_premium"]:
        days_left = (user_data["expiry"] - datetime.now()).days
        st.sidebar.success(f"💎 Premium - {days_left} days left")
    else:
        agents_left = 3 - user_data["agents_used"]
        st.sidebar.warning(f"🆓 Free - {agents_left}/3 left")
else:
    st.sidebar.info("👆 Enter email")
    st.stop()

# ========== PREMIUM UPGRADE SECTION ==========
def show_upgrade():
    st.markdown("---")
    st.subheader("🚀 Upgrade to Premium - ₹99/month")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Free", "3 agents")
    with col2:
        st.metric("Premium", "Unlimited")
    with col3:
        st.metric("Price", "₹99/month")
    
    st.markdown(f"""
    ### 📱 Step 1: Pay ₹99 to this UPI ID
    ```
    {UPI_ID}
    ```
    """)
    st.caption("💡 UPI ID copy karne ke liye upar click karein")
    
    st.markdown("---")
    st.markdown("### 📝 Step 2: Enter Transaction ID after Payment")
    
    transaction_id = st.text_input("Transaction ID / UTR Number (Required):", placeholder="e.g., 1234567890")
    
    if st.button("✅ Verify Payment & Activate Premium", use_container_width=True):
        if not transaction_id:
            st.error("❌ Please enter Transaction ID / UTR Number first!")
        elif len(transaction_id) < 3:
            st.error("❌ Please enter a valid Transaction ID!")
        elif is_utr_used(transaction_id):
            st.error("❌ This Transaction ID has already been used!")
        else:
            mark_utr_as_used(transaction_id)
            activate_premium(email, transaction_id=transaction_id)
            st.balloons()
            st.success("🎉 PREMIUM ACTIVATED SUCCESSFULLY!")
            st.rerun()
    
    st.markdown("---")
    if st.button("🎁 Try 3 Days Free Trial", use_container_width=True):
        activate_premium(email, days=3)
        st.balloons()
        st.success("🎉 3-day free trial activated!")
        st.rerun()
    
    st.caption("🔒 One UTR number can be used only once.")

# ========== CHECK LIMIT ==========
can_create, reason = can_create_agent(email)
if not can_create:
    if reason == "free_limit":
        st.error("❌ Free limit reached! (3/3 agents used)")
    elif reason == "premium_expired":
        st.error("❌ Premium expired! Please renew.")
    show_upgrade()
    st.stop()

# ========== MAIN APP ==========
st.title("👑 AI Agent Builder")

if user_data["is_creator"]:
    st.markdown("🎖️ **VIP CREATOR** — Unlimited agents for life!")
elif user_data["is_premium"]:
    days_left = (user_data["expiry"] - datetime.now()).days
    st.markdown(f"💎 **Premium Active** — Unlimited! ({days_left} days left)")
else:
    agents_left = 3 - user_data["agents_used"]
    st.markdown(f"🆓 **Free Tier** — {agents_left}/3 agents left")

st.markdown("### ✨ Kuch bhi likho — AI agent ban jayega 5 second mein!")

# ========== AGENT FORM ==========
topic = st.text_area(
    "📝 Describe your agent:",
    height=100,
    placeholder="Example: Stock market advisor, Fitness trainer, Customer support"
)

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 Language:", ["Hinglish", "Hindi", "English"])
with col2:
    personality = st.selectbox("🎭 Personality:", ["Professional", "Friendly", "Funny"])

st.markdown("🔑 **Get free API key:** https://aistudio.google.com/apikey")
api_key = st.text_input("Google API Key", type="password")

# ========== GENERATE BUTTON ==========
if st.button("🚀 GENERATE AI AGENT 🚀", use_container_width=True):
    if not api_key:
        st.error("❌ Please enter API key!")
    elif not topic:
        st.error("❌ Please describe your agent!")
    else:
        if not user_data["is_premium"] and not user_data["is_creator"]:
            increment_agent(email)
        
        with st.spinner("🤖 Creating your AI agent..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                
                prompt = f"""You are an AI agent.
Topic: {topic}
Personality: {personality}
Language: {language}

Introduce yourself in 2-3 lines. Be engaging."""
                
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(url, json=payload, timeout=30)
                data = response.json()
                
                if "candidates" in data:
                    agent_intro = data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    st.balloons()
                    st.success("✅ AI Agent Created!")
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 15px;">
                        <h3>🤖 Your AI Agent</h3>
                        <p>{agent_intro}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Live chat
                    st.subheader("💬 Chat with your agent")
                    user_msg = st.text_input("Ask something:", placeholder="Namaste! Kaise ho?")
                    
                    if user_msg:
                        with st.spinner("Agent is thinking..."):
                            chat_prompt = f"Topic: {topic}. Personality: {personality}. Language: {language}. User: {user_msg}. Reply briefly."
                            chat_payload = {"contents": [{"parts": [{"text": chat_prompt}]}]}
                            chat_response = requests.post(url, json=chat_payload, timeout=30)
                            chat_data = chat_response.json()
                            if "candidates" in chat_data:
                                st.success(f"🤖 **Agent:** {chat_data['candidates'][0]['content']['parts'][0]['text']}")
                    
                    # Download code (premium/creator only)
                    if user_data["is_premium"] or user_data["is_creator"]:
                        code = f'''# 🤖 AI Agent Code - {topic}

import requests

API_KEY = "YOUR_GEMINI_API_KEY"
TOPIC = "{topic}"
PERSONALITY = "{personality}"
LANGUAGE = "{language}"

def chat_with_agent(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={{API_KEY}}"
    prompt = f"Topic: {{TOPIC}}. Personality: {{PERSONALITY}}. Language: {{LANGUAGE}}. User: {{user_message}}"
    payload = {{"contents": [{{"parts": [{{"text": prompt}}]}}]}}
    response = requests.post(url, json=payload)
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

print(chat_with_agent("Namaste"))
'''
                        st.download_button("📥 Download Agent Code", code, "my_agent.py", use_container_width=True)
                    else:
                        st.info("🔒 **Upgrade to premium to download code!**")
                        
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    st.error(f"Error: {error_msg}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ========== SHOW UPGRADE SECTION FOR FREE USERS ==========
if not user_data["is_premium"] and not user_data["is_creator"]:
    show_upgrade()

st.caption("👑 Creator: Unlimited | 💎 Premium: ₹99/month | 🆓 Free: 3 agents")
