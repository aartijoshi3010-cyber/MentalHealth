import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:5000"  # change to your backend URL if deployed

st.set_page_config(page_title="🧠 Mental Health Support", page_icon="🧠", layout="wide")

# --- Inject custom CSS ---
st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom right, #E8F0FF, #F9F9F9);
            font-family: 'Helvetica', sans-serif;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5em 2em;
            border-radius: 12px;
            border: none;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }
        .main-title {
            font-size: 2.5rem;
            text-align: center;
            color: #2E86C1;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            font-size: 1rem;
            color: #555;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Page title ---
st.markdown("<div class='main-title'>🧠 Mental Health Support System</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Track your mood, reflect, and grow 🌱</div>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", ["🔐 Login", "📝 Sign Up", "📊 Mood Tracker"])

if "user" not in st.session_state:
    st.session_state.user = None

# --- Sign Up ---
if menu == "📝 Sign Up":
    st.header("📝 Create a new account")
    with st.form(key="signup"):
        name = st.text_input("Full Name 👤")
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
        submitted = st.form_submit_button("Sign Up")
    if submitted:
        if name and email and password:
            res = requests.post(f"{API_URL}/signup", json={
                "name": name, "email": email, "password": password
            })
            if res.status_code == 201:
                st.success("✅ Account created! You can now log in.")
            else:
                st.error("⚠️ " + res.json().get("error", "Sign up failed"))
        else:
            st.warning("Please fill all fields")

# --- Login ---
elif menu == "🔐 Login":
    st.header("🔐 Login to your account")
    with st.form(key="login"):
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        res = requests.post(f"{API_URL}/login", json={
            "email": email, "password": password
        })
        if res.status_code == 200:
            st.session_state.user = res.json()
            st.success(f"👋 Welcome back, {st.session_state.user['name']}!")
        else:
            st.error("⚠️ " + res.json().get("error", "Login failed"))

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
            res = requests.post(f"{API_URL}/mood", json={
                "user_id": st.session_state.user["id"],
                "mood_text": mood
            })
            if res.status_code == 201:
                st.success("✅ Mood saved!")
            else:
                st.error("Error saving mood")

        st.subheader("📈 Your Mood History")
        res = requests.get(f"{API_URL}/mood/{st.session_state.user['id']}")
        if res.status_code == 200:
            moods = pd.DataFrame(res.json())
            if not moods.empty:
                # Show table
                st.dataframe(moods, use_container_width=True)
                # Show chart
                fig = px.scatter(moods, x="created_at", y="mood_text",
                                 title="Mood Over Time 🕒",
                                 color_discrete_sequence=["#4CAF50"])
                fig.update_traces(marker=dict(size=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No moods logged yet.")
