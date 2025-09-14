
# app.py
import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from datetime import datetime, date
from typing import Optional, Tuple

DB_PATH = "mental_health.db"

# -----------------------------
# Database helpers
# -----------------------------
def get_conn():
    # allow usage across Streamlit reruns/threads safely
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
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

def normalize_email(email: str) -> str:
    return email.strip().lower()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(name: str, email: str, password_hashed: str) -> Tuple[bool, Optional[str]]:
    email = normalize_email(email)
    try:
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (name,email,password,created_at) VALUES (?,?,?,?)",
                (name.strip(), email, password_hashed, datetime.utcnow().isoformat())
            )
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."
    except Exception as e:
        return False, str(e)

def login_user(email: str, password_hashed: str) -> Optional[dict]:
    email = normalize_email(email)
    try:
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id,name,email,created_at FROM users WHERE email=? AND password=?", (email, password_hashed))
            row = c.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2], 'created_at': row[3]}
        return None
    except Exception:
        return None

def save_mood(user_id: int, mood: str, notes: str):
    with get_conn() as conn:
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute("INSERT INTO moods (user_id,mood,notes,created_at) VALUES (?,?,?,?)", (user_id, mood, notes, now))
        conn.commit()

def get_moods(user_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT mood,notes,created_at FROM moods WHERE user_id=? ORDER BY created_at ASC", (user_id,))
        return c.fetchall()

def add_habit(user_id: int, habit: str, habit_date: str, done: int = 0):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO habits (user_id,habit,date,done) VALUES (?,?,?,?)", (user_id, habit, habit_date, done))
        conn.commit()

def get_habits(user_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id,habit,date,done FROM habits WHERE user_id=? ORDER BY date DESC", (user_id,))
        return c.fetchall()

def set_habit_done(habit_id: int, done: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE habits SET done=? WHERE id=?", (done, habit_id))
        conn.commit()

# -----------------------------
# App initialization
# -----------------------------
st.set_page_config(page_title="Mental Health Platform", page_icon="🧠", layout="wide")
init_db()

# small debug info (uncomment to help debug)
# with get_conn() as conn:
#     tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
# st.sidebar.write("DB tables:", tables)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #ffffff, #f4f6ff); }
header {visibility: hidden;}
div.stButton > button {
  background: linear-gradient(90deg,#6C63FF,#9A8CFF);
  color:white; border:none; padding:0.6rem 1rem; border-radius:10px; font-weight:700;
}
div.stButton > button:hover { transform: scale(1.03); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#6C63FF,#9A8CFF); color: white; }
section[data-testid="stSidebar"] * { color: white !important; }
.mood-card { background:#fff; border-left:6px solid #6C63FF; padding:10px; border-radius:8px; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#3b2fdb;'>🧠 Mental Health Support Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#444;'>Privacy-first tracker — sign up and get started.</p>", unsafe_allow_html=True)

# initialize session user
if "user" not in st.session_state:
    st.session_state.user = None

# Sidebar menu
if st.session_state.user:
    menu_options = ["Dashboard", "Resources", "Export Data", "Logout"]
else:
    menu_options = ["Home"]

choice = st.sidebar.selectbox("Menu", menu_options)

# -----------------------------
# HOME (Signup + Login)
# -----------------------------
if choice == "Home":
    left, right = st.columns([2, 1])
    with left:
        st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80", use_column_width=True)
        st.markdown("### A private place to log moods, build habits and find resources.")
        st.markdown("Features: mood logging (emoji), journal notes, habit tracking, charts, CSV export, resources & hotlines.")
    with right:
        # SIGNUP form (unique keys)
        with st.form(key="signup_form"):
            st.subheader("Create account")
            su_name = st.text_input("Full name", key="su_name")
            su_email = st.text_input("Email", key="su_email")
            su_password = st.text_input("Password", type="password", key="su_pw")
            submit_signup = st.form_submit_button("Sign up")
            if submit_signup:
                if not su_name.strip() or not su_email.strip() or not su_password:
                    st.error("Please fill all fields.")
                else:
                    ok, err = add_user(su_name, su_email, hash_password(su_password))
                    if ok:
                        st.success("Account created — please login below.")
                    else:
                        st.error(err)

        # LOGIN form (unique keys)
        with st.form(key="login_form"):
            st.subheader("Login")
            li_email = st.text_input("Email", key="li_email")
            li_password = st.text_input("Password", type="password", key="li_pw")
            submit_login = st.form_submit_button("Login")
            if submit_login:
                if not li_email.strip() or not li_password:
                    st.error("Please enter both email and password.")
                else:
                    user = login_user(li_email, hash_password(li_password))
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid email or password.")

# -----------------------------
# DASHBOARD (logged-in)
# -----------------------------
elif choice == "Dashboard" and st.session_state.user:
    user = st.session_state.user
    st.markdown(f"### Hello, **{user['name']}** 👋")
    st.write(f"Member since: {user.get('created_at','-')}")

    left, right = st.columns([2, 1])
    # Left: mood & habit forms
    with left:
        st.subheader("Log Mood & Journal")
        mood_options = ["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral","🤩 Excited","😴 Tired","😡 Angry"]
        with st.form(key="mood_form"):
            mood = st.selectbox("How are you feeling?", mood_options, key="mood_select")
            notes = st.text_area("Notes / Journal (optional)", key="mood_notes", height=120)
            submit_mood = st.form_submit_button("Save Mood")
            if submit_mood:
                if mood:
                    save_mood(user['id'], mood, notes or "")
                    st.success("Mood saved ✅")
                else:
                    st.warning("Choose a mood first.")

        st.markdown("---")
        st.subheader("Add Habit")
        with st.form(key="habit_form"):
            habit_name = st.text_input("Habit name (e.g., Meditate)", key="habit_name")
            habit_date = st.date_input("Date", value=date.today(), key="habit_date")
            submit_habit = st.form_submit_button("Add Habit")
            if submit_habit:
                if habit_name.strip():
                    add_habit(user['id'], habit_name.strip(), habit_date.isoformat(), 0)
                    st.success("Habit added ✅")
                else:
                    st.error("Enter a habit name.")

        st.markdown("---")
        st.subheader("Your Mood History")
        moods = get_moods(user['id'])
        if not moods:
            st.info("No moods yet — log your first mood above.")
        else:
            for mood_text, notes_text, created in reversed(moods):
                try:
                    dt_display = datetime.fromisoformat(created).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    dt_display = created
                st.markdown(f"<div class='mood-card'><b>{mood_text}</b>  •  <small>{dt_display}</small><br><i>{notes_text}</i></div>", unsafe_allow_html=True)

    # Right: stats & habits
    with right:
        st.subheader("Quick Stats")
        moods = get_moods(user['id'])
        if moods:
            df_moods = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
            df_moods["Created"] = pd.to_datetime(df_moods["Created"], errors="coerce")

            st.markdown("**Mood frequency**")
            freq = df_moods["Mood"].value_counts()
            fig1, ax1 = plt.subplots(figsize=(3.2,2.2))
            freq.plot(kind="bar", ax=ax1, color="#6C63FF")
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
            ax1.set_ylabel("Count")
            ax1.set_xlabel("")
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)

            st.markdown("**Mood timeline**")
            canonical = ["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral","🤩 Excited","😴 Tired","😡 Angry"]
            mood_to_num = {m:i for i,m in enumerate(canonical)}
            df_moods["MoodNum"] = df_moods["Mood"].map(lambda x: mood_to_num.get(x, len(mood_to_num)))
            fig2, ax2 = plt.subplots(figsize=(3.6,2.2))
            ax2.plot(df_moods["Created"], df_moods["MoodNum"], marker="o", linestyle="-", color="#6C63FF")
            ax2.set_yticks(list(mood_to_num.values()))
            ax2.set_yticklabels(list(mood_to_num.keys()))
            ax2.set_xlabel("")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
        else:
            st.info("No stats yet — log moods to see charts here.")

        st.markdown("---")
        st.subheader("Habits")
        habits = get_habits(user['id'])
        if not habits:
            st.info("No habits yet.")
        else:
            for habit_row in habits:
                hid, hname, hdate, hdone = habit_row
                cols = st.columns([3,1])
                cols[0].markdown(f"**{hname}**  \n<small>{hdate}</small>", unsafe_allow_html=True)
                cb_key = f"habit_cb_{hid}"
                checked = cols[1].checkbox("Done", value=bool(hdone), key=cb_key)
                if checked != bool(hdone):
                    set_habit_done(hid, int(checked))
                    st.experimental_rerun()

# -----------------------------
# Resources
# -----------------------------
elif choice == "Resources":
    st.title("📚 Resources & Support")
    st.markdown("### Coping strategies")
    st.markdown("""
    - Practice deep breathing for 2–5 minutes  
    - Keep a short gratitude list each day  
    - Try a 5-minute walk outside  
    - Break big tasks into very small steps  
    """)
    st.markdown("### Emergency / crisis lines")
    st.markdown("""
    - India (Aasra): 91-22-2754-6669 / 91-22-2754-9999  
    - USA: 988 (Suicide & Crisis Lifeline)  
    - UK: Samaritans 116 123  
    - If you are in immediate danger call your local emergency number.
    """)
    st.markdown("---")
    st.markdown("### Download your mood data")
    if st.session_state.user:
        moods = get_moods(st.session_state.user['id'])
        if moods:
            df_export = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Download mood CSV", csv, "my_moods.csv", "text/csv")
        else:
            st.info("No mood data to download yet.")
    else:
        st.info("Log in to download your data.")

# -----------------------------
# Export Data (alternate)
# -----------------------------
elif choice == "Export Data":
    if st.session_state.user:
        st.header("Export Data")
        moods = get_moods(st.session_state.user['id'])
        if moods:
            df_export = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Download all moods CSV", csv, "moods.csv", "text/csv")
        else:
            st.info("No data available.")
    else:
        st.info("Login required.")

# -----------------------------
# Logout
# -----------------------------
elif choice == "Logout":
    st.session_state.user = None
    st.success("Logged out.")
    st.experimental_rerun()
