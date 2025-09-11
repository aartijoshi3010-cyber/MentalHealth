import streamlit as st
import sqlite3

from datetime import datetime

# ------------------ CSS Styling ------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg,#a8edea,#fed6e3);
        color: #333333;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.6em 1.2em;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        transition: all .3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Database helpers ------------------
def init_db():
    conn = sqlite3.connect('mh_support.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(name, email, password):
    conn = sqlite3.connect('mh_support.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute('INSERT INTO users (name,email,password_hash,created_at) VALUES (?,?,?,?)',
              (name, email, hashed, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect('mh_support.db')
    c = conn.cursor()
    c.execute('SELECT id,name,email,password_hash,created_at FROM users WHERE email=?', (email,))
    row = c.fetchone()
    conn.close()
    return row

# ------------------ Auth helpers ------------------
def login(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    _, name, email, password_hash, created_at = user
    if bcrypt.checkpw(password.encode(), password_hash):
        return {'id': user[0], 'name': name, 'email': email, 'created_at': created_at}
    return None

# ------------------ Streamlit App ------------------
st.set_page_config(page_title="Mental Health Support System", page_icon="💚", layout="wide")
init_db()

if 'user' not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Sign Up"] if not st.session_state.user else ["Dashboard", "Logout"]
choice = st.sidebar.radio("📋 Menu", menu)

st.title("💚 Mental Health Support System")

# Center the form in columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.user:
        if choice == "Login":
            st.markdown("<div class='card'><h3>🔐 Login</h3>", unsafe_allow_html=True)
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = login(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown("</div>", unsafe_allow_html=True)

        elif choice == "Sign Up":
            st.markdown("<div class='card'><h3>📝 Create a New Account</h3>", unsafe_allow_html=True)
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                if not name or not email or not password:
                    st.error("Please fill all fields")
                else:
                    import sqlite3
                    try:
                        add_user(name, email, password)
                        st.success("🎉 Account created! Please log in.")
                    except sqlite3.IntegrityError:
                        st.error("An account with that email already exists.")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        if choice == "Dashboard":
            user = st.session_state.user
            st.markdown(
                f"""
                <div class='card'>
                <h3>👋 Hello, {user['name']}!</h3>
                <p><b>Email:</b> {user['email']}<br>
                <b>Member since:</b> {user['created_at']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.subheader("📝 Mood Log")
            mood = st.text_area("How are you feeling today?")
            if st.button("Save Mood"):
                st.info("Mood logging feature can be implemented here.")

            st.subheader("📚 Helpful Resources")
            st.markdown(
                """
                - [National Mental Health Helpline (India): 1800-599-0019](https://www.mohfw.gov.in)
                - [WHO Mental Health Resources](https://www.who.int/health-topics/mental-health)
                - [Calm App](https://www.calm.com/)
                """)
        elif choice == "Logout":
            st.session_state.user = None
            st.experimental_rerun()
