
import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from datetime import datetime, date

DB_PATH = "mental_health.db"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit TEXT,
            date TEXT,
            done INTEGER
        )
    """)
    conn.commit()
    conn.close()

# call it immediately so tables exist:
init_db()

# quick debug: show tables so you can confirm in Streamlit
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
st.sidebar.write("Debug DB tables:", tables)  # shows [('users',),('moods',),('habits',)]

# ---------- Helpers ----------
def normalize_email(email: str) -> str:
    return email.strip().lower()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(name, email, password_hashed):
    email = normalize_email(email)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password,created_at) VALUES (?,?,?,?)",
                  (name.strip(), email, password_hashed, datetime.utcnow().isoformat()))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(email, password_hashed):
    email = normalize_email(email)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,name,email,created_at FROM users WHERE email=? AND password=?", (email, password_hashed))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'email': row[2], 'created_at': row[3]}
    return None

def save_mood(user_id, mood, notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO moods (user_id,mood,notes,created_at) VALUES (?,?,?,?)",
              (user_id, mood, notes, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_moods(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT mood,notes,created_at FROM moods WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- UI ----------
st.set_page_config(page_title="Mental Health", page_icon="🧠")

if "user" not in st.session_state:
    st.session_state.user = None

st.title("🧠 Mental Health Platform")

if st.session_state.user is None:
    st.subheader("Sign Up")
    name = st.text_input("Name")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Create account"):
        if name and email and pw:
            ok, err = add_user(name, email, hash_password(pw))
            if ok:
                st.success("Account created! Please log in.")
            else:
                st.error(err)
        else:
            st.error("Fill all fields.")

    st.subheader("Login")
    lemail = st.text_input("Login Email")
    lpw = st.text_input("Login Password", type="password")
    if st.button("Login"):
        user = login_user(lemail, hash_password(lpw))
        if user:
            st.session_state.user = user
            st.success(f"Welcome {user['name']}")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
else:
    st.success(f"Logged in as {st.session_state.user['name']}")
    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

    st.subheader("Log your mood")
    mood = st.selectbox("How are you feeling?", ["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral"])
    notes = st.text_area("Notes")
    if st.button("Save mood"):
        save_mood(st.session_state.user['id'], mood, notes)
        st.success("Saved mood")

    st.subheader("Your moods")
    moods = get_moods(st.session_state.user['id'])
    if moods:
        df = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
        st.dataframe(df)
        fig, ax = plt.subplots()
        df["Mood"].value_counts().plot(kind="bar", ax=ax, color="#6C63FF")
        st.pyplot(fig)
    else:
        st.info("No moods yet.")
