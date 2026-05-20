import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "handtalk.db"


# -----------------------
# CONNECTION
# -----------------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# -----------------------
# CREATE DATABASE
# -----------------------
def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Translation Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            letter TEXT,
            confidence REAL,
            timestamp TEXT
        )
    """)

    # User Login Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Training Sessions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            total INTEGER,
            timestamp TEXT
        )
    """)

    # Per-Letter Accuracy Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS letter_accuracy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            letter TEXT,
            correct INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# -----------------------
# INSERT TRANSLATION
# -----------------------
def insert_translation(letter, confidence):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%H:%M:%S %p") # Change to standard timezone

        cursor.execute("""
            INSERT INTO translation (letter, confidence, timestamp)
            VALUES (?, ?, ?)
        """, (letter, float(confidence), timestamp)) # Float confidence so it fix the hash BLOB 

        conn.commit()
        conn.close()

        print(f"Saved: {letter} ({confidence:.2f}) at {timestamp}")

    except Exception as e:
        print("DB Error:", e)


# -----------------------
# REGISTER USER (HASHED)
# -----------------------
def register_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # hash password before saving (IMPORTANT)
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, hashed))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print("Register Error:", e)
        return False


# -----------------------
# LOGIN USER (HASHED CHECK)
# -----------------------
def login_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password FROM users
            WHERE username = ?
        """, (username,))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return False

        # compare entered password with stored hash
        stored_hash = result[0]

        # handle both bytes and string stored in db
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        return bcrypt.checkpw(password.encode("utf-8"), stored_hash)

    except Exception as e:
        print("Login Error:", e)
        return False


# -----------------------
# SAVE TRAINING SESSION
# -----------------------
def save_training_session(username, score, total):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p") # Change to standard timezone

        cursor.execute("""
            INSERT INTO training_sessions (username, score, total, timestamp)
            VALUES (?, ?, ?, ?)
        """, (username, score, total, timestamp))

        conn.commit()
        conn.close()

        print(f"✅ Session saved: {score}/{total} for {username}")

    except Exception as e:
        print("Session Save Error:", e)


# -----------------------
# UPDATE LETTER ACCURACY
# -----------------------
def update_letter_accuracy(username, letter, correct):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # check if record exists
        cursor.execute("""
            SELECT id, correct, attempts FROM letter_accuracy
            WHERE username = ? AND letter = ?
        """, (username, letter))

        row = cursor.fetchone()

        if row:
            # update existing record
            new_correct  = row[1] + (1 if correct else 0)
            new_attempts = row[2] + 1

            cursor.execute("""
                UPDATE letter_accuracy
                SET correct = ?, attempts = ?
                WHERE id = ?
            """, (new_correct, new_attempts, row[0]))

        else:
            # insert new record
            cursor.execute("""
                INSERT INTO letter_accuracy (username, letter, correct, attempts)
                VALUES (?, ?, ?, ?)
            """, (username, letter, 1 if correct else 0, 1))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Accuracy Update Error:", e)


# -----------------------
# GET TRAINING SESSIONS
# -----------------------
def get_training_sessions(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT score, total, timestamp FROM training_sessions
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (username,))

        rows = cursor.fetchall()
        conn.close()

        return rows

    except Exception as e:
        print("Fetch Sessions Error:", e)
        return []


# -----------------------
# GET LETTER ACCURACY
# -----------------------
def get_letter_accuracy(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT letter, correct, attempts FROM letter_accuracy
            WHERE username = ?
            ORDER BY letter ASC
        """, (username,))

        rows = cursor.fetchall()
        conn.close()

        return rows

    except Exception as e:
        print("Fetch Accuracy Error:", e)
        return []


# -----------------------
# RUN DATABASE CREATION
# -----------------------
if __name__ == "__main__":
    create_database()
    print("✅ Database created successfully")