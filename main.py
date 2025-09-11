import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime

# ------------------------------------
# Page Configuration
# ------------------------------------
st.set_page_config(page_title="MindCare - Mental Health Support", layout="centered")

# ------------------------------------
# Database Setup
# ------------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, name, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.
