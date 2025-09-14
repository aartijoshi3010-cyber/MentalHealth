
    import streamlit as st
import sqlite3, datetime
import pandas as pd
t

# === CUSTOM CSS ===
st.markdown("""
<style>
/* Clean gradient background */
.stApp {
    background: linear-gradient(to right, #f8f9fa, #e0f7fa);
    font-family: 'Segoe UI', sans-serif;
}

/* Content container */
.block-container {
    background-color: rgba(255,255,255,0.85);
    border-radius: 12px;
    padding: 2rem;
}

/* Sidebar */
.css-1d391kg, .css-1v3fvcr {
    background-color: #3f51b5 !important;
}
.sidebar .sidebar-content {
    color: white;
}

/* Headers */
h1, h2, h3, h4 {
    color: #2c3e50 !important;
    font-weight: 700;
}

/* Buttons */
.stButton>button {
    background-color: #3f51b5;
    color: white;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    border: none;
}
.stButton>button:hover {
    background-color: #283593;
}

/* Input boxes */
.stTextInput>div>div>input {
    border-radius: 6px;
    border: 1px solid #3f51b5;
}

/* Mood card */
.mood-card {
    background-color: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# === DATABASE ===
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    conn.commit()
    conn.close()

init_db()

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

# === STREAMLIT UI ===
st.title("🧠 Mental Health Support Platform")

if "user" not in st.session_state:
    st.session_state.user = None

option = st.sidebar.selectbox("Choose Action", ["Login","Signup"])

if option == "Signup":
    st.subheader("Create account")
    name = st.text_input("Full name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign up"):
        if signup_user(name,email,password):
            st.success("Account created successfully! Please log in.")
        else:
            st.error("Email already exists.")
else:
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        user = login_user(email,password)
        if user:
            st.session_state.user = {"id":user[0],"name":user[1],"email":user[2]}
            st.success(f"Welcome {user[1]}!")
        else:
            st.error("Invalid credentials.")

if st.session_state.user:
    st.write(f"✅ Logged in as {st.session_state.user['name']}")

    # Mood tracker example graph
    st.subheader("📊 Your Mood Tracker")
    mood_data = pd.DataFrame({
        "Date": pd.date_range(end=datetime.datetime.today(), periods=7),
        "Mood Score": [5,6,7,8,6,7,9]
    })
    st.line_chart(mood_data.set_index("Date"))
