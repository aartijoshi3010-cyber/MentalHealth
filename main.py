import streamlit as st
from datetime import datetime
from auth import init_db, register_user, authenticate_user, get_authenticator

# Initialize DB
init_db()

# Setup authenticator
authenticator = get_authenticator()

# Login / Signup UI
st.set_page_config(page_title="MindCare Auth", layout="centered")

# Sidebar or top for login/signup
st.sidebar.title("Account")

if 'login_mode' not in st.session_state:
    st.session_state.login_mode = 'login'  # or 'signup'

mode = st.sidebar.selectbox("Login or Signup", options=['Login', 'Signup'])

if mode == 'Signup':
    st.header("🆕 Signup")
    new_username = st.text_input("Username")
    new_name = st.text_input("Your Name")
    new_password = st.text_input("Password", type='password')
    new_password_confirm = st.text_input("Confirm Password", type='password')
    if st.button("Register"):
        if new_password != new_password_confirm:
            st.error("Passwords don't match")
        elif new_username == "" or new_name == "" or new_password == "":
            st.error("Please fill all fields")
        else:
            ok, msg = register_user(new_username, new_name, new_password)
            if ok:
                st.success(msg + ". Please login now.")
                st.session_state.login_mode = 'login'
            else:
                st.error(msg)
    st.stop()  # stop here so rest of app doesn’t render until login

else:  # Login mode
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        st.sidebar.success(f"Logged in as {name}")
    elif authentication_status == False:
        st.sidebar.error("Username/password is incorrect")
    else:
        st.sidebar.info("Please enter your credentials")
    if not authentication_status:
        st.stop()

# If reached here, user is authenticated
# Main app content

st.title("🧠 MindCare – Mental Health Support System")
st.write(f"Welcome, {name}!")

menu = ["Home", "Self-Assessment", "Community Chat", "Resources", "Get Help"]
choice = st.sidebar.selectbox("Navigate", menu)

if choice == "Home":
    st.header("Home")
    st.markdown("MindCare provides self assessment, community and resources...")

elif choice == "Self-Assessment":
    # Same GAD‑7 self assessment code here

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
        response = st.radio(q, list(options.keys()), key=q)
        scores.append(options[response])

    if st.button("Submit Assessment"):
        total = sum(scores)
        st.success(f"Your GAD-7 Score: {total}/21")
        # same scoring logic

elif choice == "Community Chat":
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    name_input = st.text_input("Enter a nickname (optional):", key="nickname_chat")
    msg = st.text_area("Your Message:", key="msg_chat")
    if st.button("Send"):
        if msg.strip():
            nickname = name_input if name_input.strip() else "Anonymous"
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(f"[{timestamp}] {nickname}: {msg.strip()}")
        else:
            st.warning("⚠️ Message cannot be empty.")
    st.markdown("---")
    st.subheader("Recent Messages")
    for m in reversed(st.session_state.chat_history[-10:]):
        st.write(m)

elif choice == "Resources":
    st.header("Resources")
    st.markdown("""
    - 🧘 [Headspace – Meditation & Sleep](https://www.headspace.com/)
    - 💬 [7 Cups – Free Chat with Listeners](https://www.7cups.com/)
    - 📖 [Mental Health Foundation](https://www.mentalhealth.org.uk/)
    - 🌐 [WHO Mental Health Info](https://www.who.int/teams/mental-health-and-substance-use)
    """)
elif choice == "Get Help":
    st.header("Get Help")
    st.markdown("""
    If you're in crisis or need professional help:
    - India: AASRA – 91‑22‑27546669  
    - USA: National Helpline – 1‑800‑662‑HELP  
    etc.
    """)



