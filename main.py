import streamlit as st
import sqlite3

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
    cursor.execute("INSERT INTO users (username, name, password_hash) VALUES (?, ?, ?)",
                   (username, name, hashed_pw))
    conn.commit()
    conn.close()
    return True, "User registered successfully."

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        name, hashed_pw = user
        if bcrypt.checkpw(password.encode(), hashed_pw):
            return True, name
    return False, None

# Initialize DB
init_db()

# ------------------------------------
# Login/Signup
# ------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.name = ""

auth_tab = st.sidebar.radio("Account", ["Login", "Signup", "Logout"])

if auth_tab == "Signup":
    st.sidebar.subheader("Create a New Account")
    new_name = st.sidebar.text_input("Full Name")
    new_username = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    if st.sidebar.button("Register"):
        if new_password != confirm_password:
            st.sidebar.error("Passwords do not match.")
        elif new_name and new_username and new_password:
            success, message = register_user(new_username, new_name, new_password)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
        else:
            st.sidebar.warning("Please fill in all fields.")

elif auth_tab == "Login":
    st.sidebar.subheader("Login to Your Account")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        success, name = authenticate_user(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.name = name
            st.success(f"Welcome, {name}!")
        else:
            st.sidebar.error("Invalid credentials.")

elif auth_tab == "Logout":
    st.session_state.authenticated = False
    st.session_state.name = ""
    st.sidebar.success("Logged out successfully.")

# ------------------------------------
# Main App Content (after login)
# ------------------------------------
if st.session_state.authenticated:

    st.title("🧠 MindCare")
    st.subheader("Welcome to your Mental Health Support System")
    st.markdown("---")

    # Sidebar Navigation
    menu = ["🏠 Home", "📝 Self-Assessment", "💬 Community Chat", "📚 Resources", "📞 Get Help"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # Home Page
    if choice == "🏠 Home":
        st.header("🏠 Welcome to MindCare")
        st.markdown("""
        MindCare is a mental health support platform offering:
        - ✅ Anxiety self-assessment (GAD-7)
        - 💬 Anonymous community chat
        - 📚 Trusted mental health resources
        - 📞 Emergency help contacts
        """)
        st.image("https://i.imgur.com/G6m9W0Z.jpg", use_column_width=True)

    # Self-Assessment Page
    elif choice == "📝 Self-Assessment":
        st.header("📝 GAD-7 Anxiety Self-Assessment")
        questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ]
        options = {
            "Not at all": 0,
            "Several days": 1,
            "More than half the days": 2,
            "Nearly every day": 3
        }

        scores = []
        for q in questions:
            ans = st.radio(q, list(options.keys()), key=q)
            scores.append(options[ans])

        if st.button("Submit Assessment"):
            total = sum(scores)
            st.success(f"Your GAD-7 Score: {total}/21")
            if total <= 4:
                st.info("🟢 Minimal Anxiety")
            elif total <= 9:
                st.warning("🟡 Mild Anxiety")
            elif total <= 14:
                st.warning("🟠 Moderate Anxiety – Consider reaching out.")
            else:
                st.error("🔴 Severe Anxiety – Seek professional help.")

    # Community Chat Page
    elif choice == "💬 Community Chat":
        st.header("💬 Anonymous Community Chat")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        nickname = st.text_input("Enter a nickname (optional):")
        msg = st.text_area("Your message")

        if st.button("Send"):
            if msg.strip():
                name = nickname if nickname.strip() else "Anonymous"
                time = datetime.now().strftime("%H:%M")
                message = f"[{time}] {name}: {msg.strip()}"
                st.session_state.chat_history.append(message)
            else:
                st.warning("Message cannot be empty.")

        st.subheader("Recent Messages")
        for m in reversed(st.session_state.chat_history[-10:]):
            st.write(m)

    # Resources Page
    elif choice == "📚 Resources":
        st.header("📚 Mental Health Resources")
        st.markdown("""
        - 🧘 [Headspace – Meditation & Sleep](https://www.headspace.com/)
        - 💬 [7 Cups – Free Chat with Listeners](https://www.7cups.com/)
        - 📖 [Mental Health Foundation](https://www.mentalhealth.org.uk/)
        - 🌐 [WHO Mental Health Info](https://www.who.int/teams/mental-health-and-substance-use)
        """)
        st.image("https://i.imgur.com/rbBz8V0.png", caption="You are not alone 🧠", use_column_width=True)

    # Get Help Page
    elif choice == "📞 Get Help":
        st.header("📞 Talk to a Professional")
        st.markdown("""
        If you're in crisis or need professional support:

        - **India:** AASRA – 91-22-27546669  
        - **USA:** National Helpline – 1-800-662-HELP  
        - **UK:** Samaritans – 116 123  
        - **Global Help:** [https://findahelpline.com](https://findahelpline.com)

        📧 Email support: help@mindcare.org

        ⚠️ *If you are in immediate danger, call emergency services.*
        """)

else:
    st.warning("🔐 Please login or sign up from the sidebar to access MindCare.")

