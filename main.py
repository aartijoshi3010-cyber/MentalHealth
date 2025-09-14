# app.py
import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from datetime import datetime, date

# ---------------------------
# Database helpers
# ---------------------------
DB_PATH = "mental_health.db"

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

def add_user(name: str, email: str, password_hashed: str):
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
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
    finally:
        conn.close()

def login_user(email: str, password_hashed: str):
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,name,email,created_at FROM users WHERE email=? AND password=?", (email, password_hashed))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'email': row[2], 'created_at': row[3]}
    return None

def save_mood(user_id: int, mood: str, notes: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO moods (user_id,mood,notes,created_at) VALUES (?,?,?,?)", (user_id, mood, notes, now))
    conn.commit()
    conn.close()

def get_moods(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT mood,notes,created_at FROM moods WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows  # list of tuples (mood, notes, created_at)

def add_habit(user_id: int, habit: str, habit_date: str, done: int = 0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO habits (user_id,habit,date,done) VALUES (?,?,?,?)", (user_id, habit, habit_date, done))
    conn.commit()
    conn.close()

def get_habits(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,habit,date,done FROM habits WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows  # list of tuples (id, habit, date, done)

def toggle_habit_done(habit_id: int, new_done: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE habits SET done=? WHERE id=?", (new_done, habit_id))
    conn.commit()
    conn.close()

# ---------------------------
# Utility
# ---------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------
# App UI
# ---------------------------
st.set_page_config(page_title="Mental Health Platform", page_icon="🧠", layout="wide")
init_db()

# ---- CSS styling (purple theme, light background) ----
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #ffffff, #f4f6ff);
}
header {visibility: hidden;}
div.stButton > button {
  background: linear-gradient(90deg,#6C63FF,#9A8CFF);
  color:white; border:none; padding:0.6rem 1rem; border-radius:10px; font-weight:700;
}
div.stButton > button:hover { transform: scale(1.03); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#6C63FF,#9A8CFF); color: white; }
section[data-testid="stSidebar"] * { color: white !important; }
.card { background: #ffffff; border-radius:12px; padding:14px; box-shadow: 0 6px 20px rgba(0,0,0,0.06); }
.mood-card { background:#fff; border-left:6px solid #6C63FF; padding:10px; border-radius:8px; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

# Title & subtitle
st.markdown("<h1 style='text-align:center; color:#3b2fdb;'>🧠 Mental Health Support Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#444;'>Private self-tracking & resources — sign up and get started.</p>", unsafe_allow_html=True)

# Sidebar menu
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    menu_options = ["Dashboard", "Resources", "Export Data", "Logout"]
else:
    menu_options = ["Home"]

choice = st.sidebar.selectbox("Menu", menu_options)

# Home: hero + signup/login on right
if choice == "Home":
    left, right = st.columns([2, 1])
    with left:
        st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1200&q=80", use_column_width=True)
        st.markdown("### A safe place to track moods, build habits and find resources.")
        st.markdown("**Features included:** mood logging (emoji), journal-style notes, habit tracker, charts, CSV export, resources & hotlines.")
    with right:
        # Use forms with distinct keys to avoid Streamlit rerun/button conflicts
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
                    hashed = hash_password(su_password)
                    ok, err = add_user(su_name, su_email, hashed)
                    if ok:
                        st.success("Account created! Now log in from the Login tab.")
                    else:
                        st.error(err)

        with st.form(key="login_form"):
            st.subheader("Login")
            li_email = st.text_input("Email", key="li_email")
            li_password = st.text_input("Password", type="password", key="li_pw")
            submit_login = st.form_submit_button("Login")
            if submit_login:
                if not li_email.strip() or not li_password:
                    st.error("Please provide both email and password.")
                else:
                    hashed = hash_password(li_password)
                    user = login_user(li_email, hashed)
                    if user:
                        # store as dict in session
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid email or password.")

# Dashboard: logged-in user features
elif choice == "Dashboard" and st.session_state.user:
    user = st.session_state.user
    st.markdown(f"### Hello, **{user['name']}** 👋")
    st.write(f"Member since: {user.get('created_at','-')}")

    # Layout: left for logging, right for quick stats
    left, right = st.columns([2, 1])

    # LEFT: Mood & Journal + Habit add
    with left:
        st.subheader("Log Mood / Journal")
        mood_options = ["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral","🤩 Excited","😴 Tired","😡 Angry"]
        with st.form(key="mood_form"):
            mood = st.selectbox("How are you feeling?", mood_options, key="mood_select")
            notes = st.text_area("Notes / Journal entry (optional)", key="mood_notes", height=120)
            saved = st.form_submit_button("Save Mood")
            if saved:
                if not mood:
                    st.warning("Select a mood first.")
                else:
                    save_mood(user['id'], mood, notes or "")
                    st.success("Mood saved ✅")

        st.markdown("---")
        st.subheader("Add Habit")
        with st.form(key="habit_form"):
            habit_name = st.text_input("Habit name (e.g., Meditate)", key="habit_name")
            habit_date = st.date_input("Date", value=date.today(), key="habit_date")
            add_habit_btn = st.form_submit_button("Add Habit")
            if add_habit_btn:
                if not habit_name.strip():
                    st.error("Please enter a habit name.")
                else:
                    add_habit(user['id'], habit_name.strip(), habit_date.isoformat(), 0)
                    st.success("Habit added ✅")

        st.markdown("---")
        st.subheader("Your Mood History")
        moods = get_moods(user['id'])
        if not moods:
            st.info("No moods logged yet — record your first mood above.")
        else:
            # show most recent first
            for mood_text, notes, created in reversed(moods):
                created_local = created
                st.markdown(f"<div class='mood-card'><b>{mood_text}</b>  •  <small>{created_local}</small><br><i>{notes}</i></div>", unsafe_allow_html=True)

    # RIGHT: Quick stats, habits
    with right:
        st.subheader("Quick Stats")
        moods = get_moods(user['id'])
        if moods:
            df = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
            df["Created"] = pd.to_datetime(df["Created"])
            # Frequency
            st.markdown("**Mood frequency**")
            freq = df["Mood"].value_counts()
            fig1, ax1 = plt.subplots(figsize=(3.2,2.2))
            freq.plot(kind="bar", ax=ax1, color="#6C63FF")
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
            ax1.set_ylabel("Count")
            ax1.set_xlabel("")
            st.pyplot(fig1, bbox_inches='tight')

            # Timeline (map moods to stable order)
            st.markdown("**Mood timeline**")
            mood_order = list(dict.fromkeys(df["Mood"].tolist()))  # preserve observed order
            # ensure consistent ordering across sessions: define canonical order mapping
            canonical = ["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral","🤩 Excited","😴 Tired","😡 Angry"]
            # create map using canonical order fallback to index in canonical
            mood_to_num = {m:i for i,m in enumerate(canonical)}
            df["MoodNum"] = df["Mood"].map(lambda x: mood_to_num.get(x, len(mood_to_num)))
            fig2, ax2 = plt.subplots(figsize=(3.6,2.2))
            ax2.plot(df["Created"], df["MoodNum"], marker="o", linestyle="-", color="#6C63FF")
            ax2.set_yticks(list(mood_to_num.values()))
            ax2.set_yticklabels(list(mood_to_num.keys()))
            ax2.set_xlabel("")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
            st.pyplot(fig2, bbox_inches='tight')
        else:
            st.info("No stats yet — log moods to see charts here.")

        st.markdown("---")
        st.subheader("Habits")
        habits = get_habits(user['id'])
        if not habits:
            st.info("No habits yet.")
        else:
            # Show habit table with toggle done
            hab_df = pd.DataFrame(habits, columns=["id","Habit","Date","Done"])
            # interactive toggles (careful: actions rerun app; we handle toggles)
            for idx, row in hab_df.iterrows():
                hid, hname, hdate, hdone = row["id"], row["Habit"], row["Date"], row["Done"]
                cols = st.columns([3,2,1])
                cols[0].markdown(f"**{hname}**  \n<small>{hdate}</small>", unsafe_allow_html=True)
                new_val = cols[2].checkbox("Done", value=bool(hdone), key=f"habit_{hid}")
                # If user changed checkbox, update DB
                if new_val != bool(hdone):
                    toggle_habit_done(hid, int(new_val))
                    st.experimental_rerun()

# Resources page & Export
elif choice == "Resources":
    st.title("📚 Resources & Support")
    st.markdown("**Coping strategies**")
    st.markdown("""
    - Practice deep breathing for 2–5 minutes  
    - Keep a short gratitude list each day  
    - Try a 5-minute walk outside  
    - Break big tasks into very small steps  
    """)
    st.markdown("**Emergency / crisis lines**")
    st.markdown("""
    - India (Aasra): 91-22-2754-6669 / 91-22-2754-9999  
    - USA: 988 (Suicide & Crisis Lifeline)  
    - UK: Samaritans 116 123  
    - If you are in immediate danger call your local emergency number.
    """)
    st.markdown("---")
    st.markdown("**Download your data**")
    if st.session_state.user:
        moods = get_moods(st.session_state.user['id'])
        if moods:
            df = pd.DataFrame(moods, columns=["Mood","Notes","Created"])
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download mood CSV", csv, "my_moods.csv", "text/csv")
        else:
            st.info("No mood data to download yet.")
    else:
        st.info("Log in to download your data.")

# Export Data quick link
elif choice == "Export Data":
    # (only appears for logged in user)
    if st.session_state.user:
        st.header("Export")
        moods = get_moods(st.session_state.user['id'])
        df = pd.DataFrame(moods, columns=["Mood","Notes","Created"]) if moods else pd.DataFrame()
        if not df.empty:
            csv = df.to_csv(index=False).encode()
            st.download_button("Download all moods CSV", csv, "moods.csv", "text/csv")
        else:
            st.info("No data available.")
    else:
        st.info("Login required.")

# Logout flow
elif choice == "Logout":
    st.session_state.user = None
    st.experimental_rerun()
