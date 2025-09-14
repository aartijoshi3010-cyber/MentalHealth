
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt

# ============= Database Setup ==============
def init_db():
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 email TEXT UNIQUE,
                 password TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS moods (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 mood TEXT,
                 notes TEXT
                 )""")
    conn.commit()
    conn.close()

def add_user(name, email, password):
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                  (name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email, password))
    user = c.fetchone()
    conn.close()
    return user

def save_mood(user_id, mood, notes):
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    c.execute("INSERT INTO moods (user_id,mood,notes) VALUES (?,?,?)",
              (user_id, mood, notes))
    conn.commit()
    conn.close()

def get_user_moods(user_id):
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    c.execute("SELECT mood,notes FROM moods WHERE user_id=?", (user_id,))
    moods = c.fetchall()
    conn.close()
    return moods

# ============= UI Setup ==============
st.set_page_config(page_title="Mental Health Support System",
                   page_icon="🧠",
                   layout="wide")

# ---- Custom CSS (light background, no green) ----
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #ffffff, #f2f6ff);
        }
        /* Buttons */
        div.stButton > button {
            background-color: #6C63FF;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease-in-out;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #5548c8;
            transform: scale(1.05);
        }
        /* Inputs */
        input, textarea, select {
            border-radius: 6px !important;
            border: 1px solid #6C63FF !important;
        }
        h1, h2, h3 {
            color: #6C63FF;
        }
        .mood-card {
            background-color: #ffffff;
            border-left: 6px solid #6C63FF;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Home", "Dashboard", "Logout"] if st.session_state.user else ["Home"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    # Hero section: left image, right sign-up/login
    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.image("https://images.unsplash.com/photo-1606761560599-712f06a4c09b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
                 caption="", use_column_width=True)
        st.markdown("<h2>Track Your Moods & Wellbeing</h2>", unsafe_allow_html=True)
        st.write("A simple, private place to note your feelings each day.")
    with right_col:
        tab1, tab2 = st.tabs(["Sign Up", "Login"])

        with tab1:
            st.subheader("Create a new account")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                hashed_pw = hashlib.sha256(pw.encode()).hexdigest()
                if add_user(name, email, hashed_pw):
                    st.success("✅ Account created! You can login now.")
                else:
                    st.error("⚠️ Email already exists.")

        with tab2:
            st.subheader("Login to your account")
            email2 = st.text_input("Email", key="login_email")
            pw2 = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login"):
                hashed_pw = hashlib.sha256(pw2.encode()).hexdigest()
                user = login_user(email2, hashed_pw)
                if user:
                    st.session_state.user = user
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password.")

elif choice == "Dashboard" and st.session_state.user:
    st.success(f"Welcome, {st.session_state.user[1]} 👋")

    mood_options = [
        "😃 Happy",
        "😢 Sad",
        "😰 Anxious",
        "😐 Neutral",
        "🤩 Excited",
        "😴 Tired",
        "😡 Angry"
    ]

    mood = st.selectbox("How are you feeling today?", mood_options)
    notes = st.text_area("Any notes you want to add?")
    if st.button("Save Mood"):
        save_mood(st.session_state.user[0], mood, notes)
        st.success("Mood saved successfully! ✅")

    st.write("### Your Past Moods")
    moods = get_user_moods(st.session_state.user[0])
    for m, n in moods[::-1]:
        st.markdown(f"<div class='mood-card'><b>{m}</b><br><b>Notes:</b> {n}</div>",
                    unsafe_allow_html=True)

    # Chart of mood counts
    if moods:
        df = pd.DataFrame(moods, columns=["Mood", "Notes"])
        mood_counts = df["Mood"].value_counts()
        st.write("### Mood Frequency Chart")
        fig, ax = plt.subplots()
        mood_counts.plot(kind="bar", ax=ax)
        ax.set_ylabel("Count")
        ax.set_xlabel("Mood")
        ax.set_title("Your Mood History")
        st.pyplot(fig)

elif choice == "Logout":
    st.session_state.user = None
    st.experimental_rerun()
