import streamlit as st
from datetime import datetime

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="MindCare - Mental Health Platform", layout="centered")

# -------------------
# Header
# -------------------
st.title("🧠 MindCare")
st.subheader("A Mental Health Support Platform")
st.markdown("---")

# -------------------
# Sidebar Navigation
# -------------------
menu = ["🏠 Home", "📝 Self-Assessment", "💬 Community Chat", "📚 Resources", "📞 Get Help"]
choice = st.sidebar.selectbox("Navigation", menu)

# -------------------
# Home Page
# -------------------
if choice == "🏠 Home":
    st.header("Welcome to MindCare")
    st.markdown("""
        MindCare is a safe and anonymous platform to support your mental well-being.
        - Take a quick self-assessment
        - Connect with others through community chat
        - Access helpful resources
        - Reach out to professionals
    """)
    st.image("https://i.imgur.com/G6m9W0Z.jpg", use_column_width=True)

# -------------------
# Self-Assessment
# -------------------
elif choice == "📝 Self-Assessment":
    st.header("📝 Self-Assessment Tool")
    st.write("This is a basic GAD-7-style anxiety test. Rate how often you’ve been bothered by the following problems over the last 2 weeks:")

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
        total_score = sum(scores)

        st.success(f"Your GAD-7 Score: {total_score}/21")

        if total_score <= 4:
            st.info("Minimal anxiety. Continue healthy habits.")
        elif total_score <= 9:
            st.warning("Mild anxiety. Monitor and consider stress-relief techniques.")
        elif total_score <= 14:
            st.warning("Moderate anxiety. Consider speaking with a professional.")
        else:
            st.error("Severe anxiety. We recommend professional help.")

# -------------------
# Community Chat (Simulated)
# -------------------
elif choice == "💬 Community Chat":
    st.header("💬 Anonymous Community Chat")
    st.write("Share your thoughts, support others, or just talk. All messages are anonymous.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    name = st.text_input("Enter a nickname (optional):", "")
    msg = st.text_area("Your Message", "")

    if st.button("Send"):
        if msg.strip():
            nickname = name if name else "Anonymous"
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(f"[{timestamp}] {nickname}: {msg}")
        else:
            st.warning("Message cannot be empty.")

    st.markdown("---")
    st.subheader("Chat History")

    for message in reversed(st.session_state.chat_history[-10:]):
        st.write(message)

# -------------------
# Resources
# -------------------
elif choice == "📚 Resources":
    st.header("📚 Mental Health Resources")
    st.markdown("""
    - [🧘 Headspace (Meditation)](https://www.headspace.com/)
    - [🌐 7 Cups (Free support chat)](https://www.7cups.com/)
    - [📖 Mental Health Foundation](https://www.mentalhealth.org.uk/)
    - [📞 WHO Mental Health Support](https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response)
    """)

    st.image("https://i.imgur.com/rbBz8V0.png", caption="Take care of your mind 🧠", use_column_width=True)

# -------------------
# Get Help
# -------------------
elif choice == "📞 Get Help":
    st.header("📞 Talk to a Professional")
    st.markdown("""
    If you're in crisis or need professional help, please contact:

    - **India:** AASRA: 91-22-27546669 / 91-22-27546667  
    - **USA:** National Suicide Prevention Lifeline: 1-800-273-TALK (8255)  
    - **UK:** Samaritans: 116 123  
    - **Global:** [https://findahelpline.com](https://findahelpline.com)

    **Email a therapist:**  
    📧 contact@mindcare-support.org
    """)

    st.warning("⚠️ If you are in immediate danger, contact emergency services.")

---

