import streamlit as st
import sqlite3
import hashlib

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
                   layout="centered")

# ---- Custom CSS ----
st.markdown("""
    <style>
        /* Global background */
        .stApp {
            background: linear-gradient(135deg, #f9f9f9, #e6f7ff);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #4CAF50;
            color: white;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Buttons */
        div.stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease-in-out;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }

        /* Inputs */
        input, textarea, select {
            border-radius: 6px !important;
            border: 1px solid #4CAF50 !important;
        }

        /* Headings */
        h1, h2, h3, h4 {
            color: #4CAF50;
        }

        /* Mood cards */
        .mood-card {
            background-color: #ffffff;
            border-left: 6px solid #4CAF50;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center;'>🧠 Mental Health Support System</h1>",
    unsafe_allow_html=True
)

init_db()

# Session state to store user
if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Home", "Sign Up", "Login"]
if st.session_state.user:
    menu = ["Dashboard", "Logout"]

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.write("Welcome! Please sign up or login to track your moods.")

elif choice == "Sign Up":
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

elif choice == "Login":
    st.subheader("Login to your account")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        hashed_pw = hashlib.sha256(pw.encode()).hexdigest()
        user = login_user(email, hashed_pw)
        if user:
            st.session_state.user = user
           
        else:
            st.error("Invalid email or password.")

elif choice == "Dashboard" and st.session_state.user:
    st.success(f"Welcome, {st.session_state.user[1]} 👋")

    # Moods with emojis
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
        st.markdown(
            f"<div class='mood-card'><b>{m}</b><br><b>Notes:</b> {n}</div>",
            unsafe_allow_html=True)

elif choice == "Logout":
    st.session_state.user = None
    
