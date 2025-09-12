from flask import Flask, request, jsonify
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)

DB = "mh_support.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
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

init_db()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password_hash,created_at) VALUES (?,?,?,?)",
                  (name, email, hash_password(password), datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id,name,email,password_hash FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row and hash_password(password) == row[3]:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/mood", methods=["POST"])
def save_mood():
    data = request.get_json()
    user_id = data.get("user_id")
    mood_text = data.get("mood_text")
    if not user_id or not mood_text:
        return jsonify({"error": "Missing fields"}), 400
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO moods (user_id,mood_text,created_at) VALUES (?,?,?)",
              (user_id, mood_text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Mood saved"}), 201

@app.route("/mood/<int:user_id>", methods=["GET"])
def get_moods(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT mood_text, created_at FROM moods WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    moods = [{"mood_text": r[0], "created_at": r[1]} for r in rows]
    return jsonify(moods), 200

if __name__ == "__main__":
    app.run(debug=True)
