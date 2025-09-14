import streamlit as st
import sqlite3, datetime
import pandas as pd

# ---------------- DB Setup -----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    # users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    # mood logs table
    c.execute('''CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mood TEXT,
        note TEXT,
        date TEXT DEFAULT (date('now'))
    )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- User Functions -----------------
def signup_user(name, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                  (name,email,password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id,name,email FROM users WHERE email=? AND password=?",(email,password))
    data = c.fetchone()
    conn.close()
    return data

# ---------------- Mood Functions -----------------
def add_mood(user_id, mood, note):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO moods (user_id, mood, note) VALUES (?,?,?)",(user_id,mood,note))
    conn.commit()
    conn.close()

def get_moods(user_id):
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query("SELECT date,mood,note FROM moods WHERE user_id=? ORDER BY date",
                           conn, params=(user_id,))
    conn.close()
    return df

# ---------------- UI -----------------
st.set_page_config(page_title="🧠 Mental Health Support", layout="wide")

st.title("🧠 Mental Health Support Platform")

if "user" not in st.session_state:
    st.session_state.user = None

# Sidebar login/signup
option = st.sidebar.radio("🔑 Choose Action", ["Login","Signup"])

if st.session_state.user is None:
    if option == "Signup":
        st.subheader("📝 Create account")
        name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign up"):
            if signup_user(name,email,password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Email already exists.")
    else:
        st.subheader("🔓 Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = login_user(email,password)
            if user:
                st.session_state.user = {"id":user[0],"name":user[1],"email":user[2]}
                st.success(f"Welcome {user[1]}!")
            else:
                st.error("Invalid credentials.")
else:
    # Logged-in dashboard
    user = st.session_state.user
    st.success(f"✅ Logged in as {user['name']}")

    col1, col2 = st.columns([2,3])
    with col1:
        st.image("https://images.unsplash.com/photo-1535223289827-42f1e9919769", use_container_width=True)
        st.write("💡 *Remember to take a break and breathe deeply.*")

        st.subheader("Log Your Mood")
        mood = st.selectbox("Mood 😊😔😡😴", ["Happy 😊","Sad 😔","Angry 😡","Tired 😴","Excited 🤩"])
        note = st.text_area("Write a note about your day")
        if st.button("Add Mood"):
            add_mood(user['id'], mood, note)
            st.success("Mood added!")

    with col2:
        st.subheader("📊 Your Mood Chart")
        df = get_moods(user['id'])
        if not df.empty:
            # Bar chart of mood counts
            mood_counts = df['mood'].value_counts()
            fig, ax = plt.subplots()
            mood_counts.plot(kind='bar', ax=ax)
            ax.set_title("Mood Frequency")
            st.pyplot(fig)

            st.subheader("📅 Mood History")
            st.dataframe(df)
        else:
            st.info("No mood data yet. Add your first mood!")

    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()
