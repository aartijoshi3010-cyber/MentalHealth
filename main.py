import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from datetime import datetime

# ========== DB Setup ==========
def init_db():
    conn = sqlite3.connect("mental_health.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS moods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mood TEXT,
        notes TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        habit TEXT,
        date TEXT,
        done INTEGER
    )""")
    conn.commit()
    conn.close()

def add_user(name,email,password):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",(name,email,password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email,password):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password))
    u=c.fetchone()
    conn.close()
    return u

def save_mood(user_id,mood,notes):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO moods (user_id,mood,notes,created_at) VALUES (?,?,?,?)",(user_id,mood,notes,now))
    conn.commit()
    conn.close()

def get_moods(user_id):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    c.execute("SELECT mood,notes,created_at FROM moods WHERE user_id=?",(user_id,))
    data=c.fetchall()
    conn.close()
    return data

def add_habit(user_id,habit,date,done):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    c.execute("INSERT INTO habits (user_id,habit,date,done) VALUES (?,?,?,?)",(user_id,habit,date,done))
    conn.commit()
    conn.close()

def get_habits(user_id):
    conn=sqlite3.connect("mental_health.db")
    c=conn.cursor()
    c.execute("SELECT habit,date,done FROM habits WHERE user_id=?",(user_id,))
    rows=c.fetchall()
    conn.close()
    return rows

# ========== UI Setup ==========
st.set_page_config(page_title="Mental Health Platform",page_icon="🧠",layout="wide")

st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #ffffff, #f5f7ff);
}
div.stButton > button {
  background-color:#6C63FF;
  color:white;
  border:none;
  padding:0.5rem 1rem;
  border-radius:8px;
  font-weight:bold;
}
</style>
""",unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state.user=None

menu=["Home","Dashboard","Resources","Logout"] if st.session_state.user else ["Home"]
choice=st.sidebar.selectbox("Menu",menu)

if choice=="Home":
    col1,col2=st.columns([1,1])
    with col1:
        st.image("https://images.unsplash.com/photo-1606761560599-712f06a4c09b?auto=format&fit=crop&w=800&q=60",use_column_width=True)
        st.markdown("<h2>Track Your Moods & Wellbeing</h2>",unsafe_allow_html=True)
        st.write("Private space to log moods, habits, and get support tips.")
    with col2:
        tabs=st.tabs(["Sign Up","Login"])
        with tabs[0]:
            st.subheader("Create account")
            n=st.text_input("Full Name")
            e=st.text_input("Email")
            p=st.text_input("Password",type="password")
            if st.button("Sign Up"):
                hashed=hashlib.sha256(p.encode()).hexdigest()
                if add_user(n,e,hashed):
                    st.success("Account created! Login now.")
                else:
                    st.error("Email already exists.")
        with tabs[1]:
            st.subheader("Login")
            e2=st.text_input("Email",key="login_email")
            p2=st.text_input("Password",type="password",key="login_pw")
            if st.button("Login"):
                hashed=hashlib.sha256(p2.encode()).hexdigest()
                u=login_user(e2,hashed)
                if u:
                    st.session_state.user=u
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials.")

elif choice=="Dashboard" and st.session_state.user:
    st.success(f"Welcome {st.session_state.user[1]} 👋")
    mood_options=["😃 Happy","😢 Sad","😰 Anxious","😐 Neutral","🤩 Excited","😴 Tired","😡 Angry"]
    mood=st.selectbox("How are you feeling today?",mood_options)
    notes=st.text_area("Notes about your day")
    if st.button("Save Mood"):
        save_mood(st.session_state.user[0],mood,notes)
        st.success("Mood saved!")

    st.write("### Add a Habit")
    habit=st.text_input("Habit (e.g., Meditate, Exercise)")
    date=datetime.now().strftime("%Y-%m-%d")
    if st.button("Add Habit"):
        add_habit(st.session_state.user[0],habit,date,1)
        st.success("Habit saved!")

    st.write("### Your Mood History")
    moods=get_moods(st.session_state.user[0])
    for m,n,t in moods[::-1]:
        st.markdown(f"**{t}** — {m} — _{n}_")

    if moods:
        df=pd.DataFrame(moods,columns=["Mood","Notes","Created"])
        df["Created"]=pd.to_datetime(df["Created"])

        st.write("#### Download your data")
        csv=df.to_csv(index=False).encode()
        st.download_button("Download CSV",csv,"moods.csv","text/csv")

        st.write("#### Mood Frequency")
        mood_counts=df["Mood"].value_counts()
        fig,ax=plt.subplots()
        mood_counts.plot(kind="bar",ax=ax,color="#6C63FF")
        ax.set_ylabel("Count"); ax.set_xlabel("Mood"); plt.xticks(rotation=45)
        st.pyplot(fig)

        st.write("#### Mood Timeline")
        mood_map={m:i for i,m in enumerate(df["Mood"].unique())}
        df["MoodNum"]=df["Mood"].map(mood_map)
        fig2,ax2=plt.subplots()
        ax2.plot(df["Created"],df["MoodNum"],marker="o")
        ax2.set_yticks(list(mood_map.values()))
        ax2.set_yticklabels(list(mood_map.keys()))
        ax2.set_title("Mood over time")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.write("### Your Habits")
    habits=get_habits(st.session_state.user[0])
    if habits:
        dfh=pd.DataFrame(habits,columns=["Habit","Date","Done"])
        st.dataframe(dfh)

elif choice=="Resources":
    st.title("🛟 Resources & Support")
    st.write("Here are some helpful tips and hotlines:")
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Coping Tips")
        st.markdown("- Practice deep breathing\n- Keep a gratitude journal\n- Exercise or go for a walk\n- Stay connected with friends")
    with col2:
        st.subheader("Emergency Contacts")
        st.markdown("🇮🇳 India: **9152987821** (Snehi Helpline)\n\n🇺🇸 USA: **988** Suicide & Crisis Lifeline\n\n🇬🇧 UK: **116123** Samaritans")

elif choice=="Logout":
    st.session_state.user=None
    st.experimental_rerun()
