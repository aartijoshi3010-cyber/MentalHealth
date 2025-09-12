# frontend.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# try importing plotly, but continue even if it's missing
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception as _e:
    px = None
    PLOTLY_AVAILABLE = False
    PLOTLY_IMPORT_ERROR = str(_e)

API_URL = "http://127.0.0.1:5000"  # change if backend runs elsewhere

st.set_page_config(page_title="🧠 Mental Health Support", page_icon="🧠", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
        body { background: linear-gradient(to bottom right, #E8F0FF, #F9F9F9); }
        .stButton>button { background-color: #4CAF50; color: white; padding: 0.5em 2em; border-radius: 12px; border: none; font-weight: bold; }
        .stButton>button:hover { background-color: #45a049; transform: scale(1.02); }
        .main-title { font-size: 2.2rem; text-align: center; color: #2E86C1; margin-bottom: 0.2rem; }
        .subtitle { text-align: center; font-size: 1rem; color: #555; margin-bottom: 1.2rem; }
        .card { padding: 1rem; border-radius: 12px; background: rgba(255,255,255,0.9); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🧠 Mental Health Support System</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Track your mood, reflect, and grow 🌱</div>", unsafe_allow_html=True)

# warn user if plotly is missing
if not PLOTLY_AVAILABLE:
    st.warning("Optional package `plotly` is not installed — interactive charts will fall back to simpler visuals. "
               "Install with `pip install plotly` if you want the fancier chart. "
               f"(Import error: {PLOTLY_IMPORT_ERROR})")

# Sidebar navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["🔐 Login", "📝 Sign Up", "📊 Mood Tracker"])

if "user" not in st.session_state:
    st.session_state.user = None

# Helper: perform safe requests with friendly messages
def safe_post(path, json):
    try:
        r = requests.post(f"{API_URL}{path}", json=json, timeout=6)
        return r
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None

def safe_get(path):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=6)
        return r
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None

# --- Sign Up ---
if menu == "📝 Sign Up":
    st.header("📝 Create a new account")
    with st.form(key="signup"):
        name = st.text_input("Full Name 👤")
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
        submitted = st.form_submit_button("Sign Up")
    if submitted:
        if not (name and email and password):
            st.warning("Please fill all fields")
        else:
            res = safe_post("/signup", json={"name": name, "email": email, "password": password})
            if res:
                if res.status_code == 201:
                    st.success("✅ Account created! You can now log in.")
                else:
                    try:
                        st.error("⚠️ " + res.json().get("error", "Sign up failed"))
                    except Exception:
                        st.error(f"Sign up failed (status {res.status_code})")

# --- Login ---
elif menu == "🔐 Login":
    st.header("🔐 Login to your account")
    with st.form(key="login"):
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        if not (email and password):
            st.warning("Please fill both email and password")
        else:
            res = safe_post("/login", json={"email": email, "password": password})
            if res:
                if res.status_code == 200:
                    st.session_state.user = res.json()
                    st.success(f"👋 Welcome back, {st.session_state.user['name']}!")
                else:
                    try:
                        st.error("⚠️ " + res.json().get("error", "Login failed"))
                    except Exception:
                        st.error(f"Login failed (status {res.status_code})")

# --- Mood Tracker ---
elif menu == "📊 Mood Tracker":
    if not st.session_state.user:
        st.warning("Please login first.")
    else:
        st.header("📖 Log your current mood")
        with st.form(key="mood"):
            mood = st.text_area("How are you feeling today? ✍️")
            submitted = st.form_submit_button("Save Mood")
        if submitted:
            if not mood.strip():
                st.warning("Please type something before saving.")
            else:
                res = safe_post("/mood", json={
                    "user_id": st.session_state.user["id"],
                    "mood_text": mood.strip()
                })
                if res and res.status_code == 201:
                    st.success("✅ Mood saved!")
                # else error messages already shown by safe_post/safe handling

        # Show history
        st.subheader("📈 Your Mood History")
        res = safe_get(f"/mood/{st.session_state.user['id']}")
        if res and res.status_code == 200:
            data = res.json()
            if data:
                df = pd.DataFrame(data)
                # parse time
                try:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                except Exception:
                    # fallback: treat as string
                    df['created_at'] = df['created_at'].astype(str)
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Aggregate counts per day (numeric trend that doesn't require sentiment)
                try:
                    df['date'] = pd.to_datetime(df['created_at']).dt.date
                    counts = df.groupby('date').size().reset_index(name='count')
                    counts = counts.sort_values('date')
                    counts['date_str'] = counts['date'].astype(str)
                except Exception:
                    counts = None

                if counts is not None and not counts.empty:
                    st.subheader("📊 Mood Entries Per Day")
                    if PLOTLY_AVAILABLE:
                        # interactive bar chart with plotly
                        fig = px.bar(counts, x='date_str', y='count',
                                     labels={'date_str':'Date','count':'Number of entries'},
                                     title='Mood entries per day')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # fallback simple chart
                        st.line_chart(counts.set_index('date')['count'])
                else:
                    st.info("Not enough data to show a trend chart.")
            else:
                st.info("No moods logged yet.")
