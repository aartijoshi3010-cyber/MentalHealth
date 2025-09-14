
       import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "mental_health.db"

# ---------- DATABASE ----------
def init_db(reset=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if reset:  # drop and recreate each time
        c.execute("DROP TABLE IF EXISTS users")

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(name, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name,email,password,created_at) VALUES (?,?,?,?)",
        (name, email, hash_password(password), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id,name,email,created_at FROM users WHERE email=? AND password=?",
        (email, hash_password(password)),
    )
    user = c.fetchone()
    conn.close()
    return user

# ---------- UI ----------
st.set_page_config(page_title="Mental Health Support", layout="wide")

# Always reset table at start (while developing)
init_db(reset=True)

st.title("💚 Mental Health Support Platform")

# Two columns layout
col1, col2 = st.columns(2)

with col1:
    st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528", caption="Take care of your mind", use_column_width=True)
    st.markdown("""
    ### 🧠 Features
    - Mood tracking 📈
    - Journaling 📝
    - Self-care tips 🌱
    - Anonymous community support 🤝
    """)

with col2:
    st.subheader("Sign Up / Login")

    tabs = st.tabs(["📝 Sign Up", "🔑 Login"])

    with tabs[0]:
        su_name = st.text_input("Full Name")
        su_email = st.text_input("Email")
        su_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            try:
                add_user(su_name, su_email, su_password)
                st.success("✅ Account created! You can now login.")
            except sqlite3.IntegrityError:
                st.error("That email is already registered.")

    with tabs[1]:
        li_email = st.text_input("Email", key="li_email")
        li_password = st.text_input("Password", type="password", key="li_password")
        if st.button("Login"):
            user = login_user(li_email, li_password)
            if user:
                st.success(f"Welcome back {user[1]}! 🎉")
                st.write("Account created on:", user[3])
            else:
                st.error("Invalid email or password.")
