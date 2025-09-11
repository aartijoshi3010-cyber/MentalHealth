import streamlit as st
from datetime import datetime


# -----------------------------
# MySQL Database Connection Info
# -----------------------------
def get_connection():
    return mysq.connect(
        host="localhost",          # change as needed
        user="root",               # your DB user
        password="yourpassword",   # your DB user password
        database="mindcare_db"     # your DB name
    )

# Ensure table exists
def create_user_table():
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Register new user
def register_user(username, name, password):
    conn = get_connection()
    cursor = conn.cursor()
    # check if username already exists
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, "Username already exists."
    # hash password (bytes --> hash bytes --> decode to string for storage)
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_str = hashed_bytes.decode('utf-8')  # store as string
    cursor.execute(
        "INSERT INTO users (username, name, password_hash) VALUES (%s, %s, %s)",
        (username, name, hashed_str)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Registration successful."

# Authenticate login
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        name, stored_hash = result
        # stored_hash is a string, so encode to bytes
        try:
            stored_hash_bytes = stored_hash.encode('utf-8')
        except Exception as e:
            # fallback if already bytes or something else
            stored_hash_bytes = stored_hash if isinstance(stored_hash, (bytes, bytearray)) else stored_hash.encode('utf-8')
        # check password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash_bytes):
            return True, name
    return False, None

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="MindCare", layout="centered")

# initialize table
create_user_table()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.name = ""

# Sidebar for auth
auth_mode = st.sidebar.radio("Account", ["Login", "Signup", "Logout"])

if auth_mode == "Signup":
    st.sidebar.subheader("Create Account")
    new_name = st.sidebar.text_input("Your Name")
    new_username = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    if st.sidebar.button("Register"):
        if not (new_name and new_username and new_password and confirm_password):
            st.sidebar.error("Please fill in all fields.")
        elif new_password != confirm_password:
            st.sidebar.error("Passwords do not match.")
        else:
            success, message = register_user(new_username, new_name, new_password)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
    st.stop()  # stop so the rest of the app doesn’t load for signup view

elif auth_mode == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        success, name = authenticate_user(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.name = name
            st.success(f"Welcome {name}!")
        else:
            st.sidebar.error("Invalid username or password.")
    st.stop()  # stop until login is done

elif auth_mode == "Logout":
    st.session_state.authenticated = False
    st.session_state.name = ""
    st.sidebar.success("Logged out successfully.")
    st.stop()  # stop so that page reloads without authenticated content

# If here, user is authenticated
st.title("🧠 MindCare – Mental Health Support System")
st.write(f"Logged in as: {st.session_state.name}")
st.markdown("---")

menu = ["Home", "Self‑Assessment", "Community Chat", "Resources", "Get Help"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.header("Home")
    st.markdown("""
    MindCare is your mental health support system offering:
    - Self‑assessment (GAD‑7)
    - Anonymous community chat
    - Trusted mental health resources
    - Professional help contacts
    """)

elif choice == "Self‑Assessment":
    st.header("GAD‑7 Self‑Assessment")
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
        st.success(f"Your GAD‑7 Score: {total}/21")
        if total <= 4:
            st.info("Minimal Anxiety")
        elif total <= 9:
            st.warning("Mild Anxiety")
        elif total <= 14:
            st.warning("Moderate Anxiety – consider speaking to someone")
        else:
            st.error("Severe Anxiety – please consult a professional")

elif choice == "Community Chat":
    st.header("Anonymous Community Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    nickname = st.text_input("Nickname (optional):")
    msg = st.text_area("Your message:")
    if st.button("Send"):
        if msg.strip():
            nick = nickname.strip() if nickname.strip() else "Anonymous"
            ts = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(f"[{ts}] {nick}: {msg.strip()}")
        else:
            st.warning("Message cannot be empty.")
    st.subheader("Recent Messages")
    for m in reversed(st.session_state.chat_history[-10:]):
        st.write(m)

elif choice == "Resources":
    st.header("Resources")
    st.markdown("""
    - [Headspace](https://www.headspace.com/)
    - [7 Cups](https://www.7cups.com/)
    - [Mental Health Foundation](https://www.mentalhealth.org.uk/)
    - [WHO Mental Health](https://www.who.int/teams/mental-health-and-substance-use)
    """)

elif choice == "Get Help":
    st.header("Get Help")
    st.markdown("""
    If you need urgent help:
    - **India:** AASRA – 91‑22‑27546669  
    - **USA:** National Helpline – 1‑800‑662‑HELP  
    - **UK:** Samaritans – 116 123  
    - **Global:** findahelpline.com
    """)

