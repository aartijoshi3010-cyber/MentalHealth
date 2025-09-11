import streamlit as st
import sqlite3
from datetime import datetime
from sqlite3 import IntegrityError
import pandas as pd

# ---------- Fancy CSS ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        height: 100%;
        background: linear-gradient(-45deg, #a8edea, #fed6e3, #f6d365, #fda085);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #333333;
    }
    @keyframes gradientBG {
      0%{background-position:0% 50%}
      50%{background-position:100% 50%}
      100%{background-position:0% 50%}
    }
    .glass {
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.6);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
        animation: fadeIn .8s ease;
        margin-bottom: 20px;
    }
    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(10px);}
      to {opacity: 1; transform: translateY(0);}
    }
    .stButton>button {
        background: linear-gradient(90deg,#4facfe,#00f2fe);
        color: white;
        padding: 0.8em 1.4em;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        transition: all .3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg,#00f2fe,#4facfe);
    }
    input, textarea {
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Database helpers ----------
def init_db():
    """Create the users and moods table if they don't exist."""
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
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

def login(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    _, name, email, password_hash, created_at = user
    if bcrypt.checkpw(password.encode(), password_hash):
        return {'id': user[0], 'name': name, 'email': email, 'created_at': created_at}
    return None

def save_mood(user_id, mood_text):
    conn = sqlite3.connect('mh_support.db')
    c = conn.cursor()
    c.execute('INSERT INTO moods (user_id, mood_text, created_at) VALUES (?,?,?)',
              (user_id, mood_text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_moods(user_id):
    conn = sqlite3.connect('mh_support.db')
    c = conn.cursor()
    c.execute('SELECT mood_text, created_at FROM moods WHERE user_id=? ORDER BY created_at ASC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- App ----------
st.set_page_config(page_title="Mental Health Support System", page_icon="💚", layout="wide")
init_db()  # always ensure table exists

if 'user' not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Sign Up"] if not st.session_state.user else ["Dashboard", "Logout"]
choice = st.sidebar.radio("📋 Menu", menu)

st.markdown("<h1 style='text-align:center;'>💚 Mental Health Support System</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.user:
        if choice == "Login":
            st.markdown("<div class='glass'><h3>🔐 Login</h3>", unsafe_allow_html=True)
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    user = login(email, password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid email or password.")
                except Exception as e:
                    st.error(f"⚠️ Login error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        elif choice == "Sign Up":
            st.markdown("<div class='glass'><h3>📝 Create Account</h3>", unsafe_allow_html=True)
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                if not name or not email or not password:
                    st.error("Please fill all fields")
                else:
                    try:
                        add_user(name, email, password)
                        st.success("🎉 Account created! Please log in.")
                    except IntegrityError:
                        st.error("An account with that email already exists.")
                    except Exception as e:
                        st.error(f"⚠️ Sign-up error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        if choice == "Dashboard":
            user = st.session_state.user
            st.markdown(
                f"""
                <div class='glass'>
                <h3>👋 Hello, {user['name']}!</h3>
                <p><b>Email:</b> {user['email']}<br>
                <b>Member since:</b> {user['created_at']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Mood Log
            st.markdown("<div class='glass'><h3>📝 Mood Log</h3>", unsafe_allow_html=True)
            mood = st.text_area("How are you feeling today?")
            if st.button("Save Mood"):
                if mood.strip():
                    save_mood(user['id'], mood.strip())
                    st.success("Your mood has been saved 💚")
                else:
                    st.warning("Please write something before saving.")
            st.markdown("</div>", unsafe_allow_html=True)

            # Mood History + Trend Chart
            moods = get_moods(user['id'])
            if moods:
                # DataFrame for plotting
                df = pd.DataFrame(moods, columns=['mood_text', 'created_at'])
                df['created_at'] = pd.to_datetime(df['created_at'])
                # sentiment polarity
                df['sentiment'] = df['mood_text'].apply(lambda x: TextBlob(x).sentiment.polarity)

                st.markdown("<div class='glass'><h3>📜 My Mood History</h3>", unsafe_allow_html=True)
                for _, row in df[::-1].iterrows():
                    st.markdown(f"**{row['created_at'].strftime('%Y-%m-%d %H:%M')}** — {row['mood_text']}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='glass'><h3>📈 Mood Trend</h3>", unsafe_allow_html=True)
                st.line_chart(df.set_index('created_at')['sentiment'])
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No moods saved yet.")

            # Resources
            st.markdown("<div class='glass'><h3>📚 Helpful Resources</h3>", unsafe_allow_html=True)
            st.markdown(
                """
                - 🌐 [National Mental Health Helpline (India): 1800-599-0019](https://www.mohfw.gov.in)  
                - 🌐 [WHO Mental Health Resources](https://www.who.int/health-topics/mental-health)  
                - 🌐 [Calm App](https://www.calm.com/)  
                """)
            st.markdown("</div>", unsafe_allow_html=True)

        elif choice == "Logout":
            st.session_state.user = None
            st.experimental_rerun()
