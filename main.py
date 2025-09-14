import streamlit as st
import sqlite3, datetime
import pandas as pd


# === CUSTOM CSS ===
# you can change the URL to any unsplash image you like
login_bg_url = "https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=1400&q=80"

st.markdown(f"""
<style>
/* Default gradient for dashboard */
.stApp {{
    background: linear-gradient(to right, #f8f9fa, #e0f7fa);
    font-family: 'Segoe UI', sans-serif;
}}

/* When on login/signup (no user in session), show a background image */
[data-testid="stAppViewContainer"] {{
    background-image: url('{login_bg_url}');
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
}}

/* Semi-transparent content panel to improve readability */
.block-container {{
    background-color: rgba(255,255,255,0.8);
    border-radius: 12px;
    padding: 2rem;
}}

/* Sidebar */
.css-1d391kg, .css-1v3fvcr {{
    background-color: #3f51b5 !important;
}}
.sidebar .sidebar-content {{
    color: white;
}}

/* Headers */
h1, h2, h3, h4 {{
    color: #2c3e50 !important;
    font-weight: 700;
}}

/* Buttons */
.stButton>button {{
    background-color: #3f51b5;
    color: white;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    border: none;
}}
.stButton>button:hover {{
    background-color: #283593;
}}

/* Input boxes */
.stTextInput>div>div>input {{
    border-radius: 6px;
    border: 1px solid #3f51b5;
}}

/* Mood card */
.mood-card {{
    background-color: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}
</style>
""", unsafe_allow_html=True)
