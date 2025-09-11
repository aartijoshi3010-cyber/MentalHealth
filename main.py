import streamlit as st
from datetime import datetime

# -----------------------------------
# MySQL Database Connection
# -----------------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",        # Replace with your DB host
        user="root",             # Replace with your DB user
        password="yourpassword", # Replace with your DB password
        database="mindcare_db"   # Ensure this DB exists
    )

def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            name VARCHAR(100),
            password_hash VARCHAR(255)
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, name, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, name, password_hash) VALUES (%s, %s, %s)",
                   (username, name, hashed_pw))
    conn.commit()
    conn.close()
    return True, "Registration successful."

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        name, stored_hash = result
        if bcrypt.checkpw(password.encode(), stored_hash.encode() if isinstance(stored_hash, str) else stored_hash):
            return True, name
    return False, None

# -----------------------------------
# Streamlit UI Setup
# -----------------------------------
st.set_page_config(page_title="MindCare", layout="centered")

# Initialize DB
create_user_table()

# Auth State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.name = ""

auth_mode = st.sidebar.radio("Account", ["Login", "Signup", "Logout"])

if auth_mode == "Signup":
    st.sidebar.subheader("Create Account")
    new_name = st.sidebar.text_input("Your Name")
    new_username = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    if st.sidebar.button("Register"):
        if new_password != confirm_password:
            st.sidebar.error("Passwords don't match.")
        else:
            success, message = register_user(new_username, new_name, new_password)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)

elif auth_mode == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        success, name = authenticate_user(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.name = name
            st.success(f"Welcome, {name}!")
        else:
            st.sidebar.error("Invalid username or password.")

elif auth_mode == "Logout":
    st.session_state.authenticated = False
    st.session_state.name = ""
    st.sidebar.success("You are now logged out.")

# -----------------------------------
# Main App (Authenticated Users)
# -----------------------------------
if st.session_state.authenticated:
    st.title("🧠 MindCare")
    st.markdown("Welcome to your Mental Health Support System")
    st.markdown("---")

    menu = ["🏠 Home", "📝 Self-Assessment", "💬 Community Chat", "📚 Resources", "📞 Get Help"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # Home
    if choice == "🏠 Home":
        st.header("Welcome to MindCare")
        st.markdown("""
        - 🧪 Self-assess your mental well-being  
        - 💬 Chat anonymously  
        - 📚 Access resources  
        - 📞 Reach out for professional help
        """)
        st.image("https://i.imgur.com/G6m9W0Z.jpg", use_column_width=True)

    # Assessment
    elif choice == "📝 Self-Assessment":
        st.header("GAD-7 Anxiety Test")
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
            answer = st.radio(q, list(options.keys()), key=q)
            scores.append(options[answer])

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

    # Chat
    elif choice == "💬 Community Chat":
        st.header("💬 Community Chat (Anonymous)")

        if "chat" not in st.session_state:
            st.session_state.chat = []

        nickname = st.text_input("Your nickname (optional):", key="chatname")
        msg = st.text_area("Write your message:", key="chatmsg")

        if st.button("Send"):
            if msg.strip():
                sender = nickname if nickname.strip() else "Anonymous"
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.chat.append(f"[{timestamp}] {sender}: {msg.strip()}")
            else:
                st.warning("Message cannot be empty.")

        st.subheader("Chat History")
        for line in reversed(st.session_state.chat[-10:]):
            st.write(line)

    # Resources
    elif choice == "📚 Resources":
        st.header("📚 Helpful Resources")
        st.markdown("""
        - [Headspace](https://www.headspace.com/)
        - [7 Cups](https://www.7cups.com/)
        - [Mental Health Foundation](https://www.mentalhealth.org.uk/)
        - [WHO Mental Health](https://www.who.int/teams/mental-health-and-substance-use)
        """)
        st.image("https://i.imgur.com/rbBz8V0.png", use_column_width=True)

    # Get Help
    elif choice == "📞 Get Help":
        st.header("📞 Talk to a Professional")
        st.markdown("""
        - **India**: AASRA – 91-22-27546669  
        - **USA**: 1-800-662-HELP (SAMHSA)  
        - **UK**: Samaritans – 116 123  
        - **Global**: [https://findahelpline.com](https://findahelpline.com)

        📧 Email us: help@mindcare.org
        """)

else:
    st.warning("🔐 Please login or sign up from the sidebar to access MindCare.")
