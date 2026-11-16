"""
Database initialisation script for the Alzheimer's & Dementia Assistant.
Creates the 6 tables and populates sample data for testing.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "assistant.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db(db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Insert sample data if empty
    cursor.execute("SELECT COUNT(*) FROM CAREGIVER")
    if cursor.fetchone()[0] == 0:
        # Caregiver: Sarah (daughter)
        cursor.execute(
            "INSERT INTO CAREGIVER (name, email, password_hash) VALUES (?, ?, ?)",
            ("Sarah", "sarah@example.com", "pbkdf2:sha256:dummyhashforprototype"),
        )
        caregiver_id = cursor.lastrowid

        # Person living with dementia: John (father)
        cursor.execute(
            "INSERT INTO PERSON (caregiver_id, display_name, text_size, voice_on) VALUES (?, ?, ?, ?)",
            (caregiver_id, "John", "large", 1),
        )
        person_id = cursor.lastrowid

        # Sample Daily Tasks
        tasks = [
            (person_id, "Have morning tea & toast", "08:30", 127, 10, 2, 45, 0),
            (person_id, "Take morning blood pressure medication", "09:00", 127, 10, 2, 60, 1),
            (person_id, "Have your lunch", "12:30", 127, 10, 2, 60, 1),
            (person_id, "Afternoon walk in the garden", "15:30", 31, 15, 2, 60, 0),
            (person_id, "Take evening tablet", "20:00", 127, 10, 2, 60, 1),
        ]
        cursor.executemany(
            """INSERT INTO TASK 
            (person_id, label, time_of_day, days_mask, snooze_min, max_snoozes, window_min, alert_caregiver) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tasks,
        )

        # Quick Contacts for Screen A
        contacts = [
            (person_id, "Call Sarah (Daughter)", "07123 456789", "#2E7D32"),
            (person_id, "Call Dr. Evans (GP)", "01234 567890", "#1565C0"),
        ]
        cursor.executemany(
            "INSERT INTO CONTACT (person_id, name, phone, avatar_color) VALUES (?, ?, ?, ?)",
            contacts,
        )

        conn.commit()
        print(f"Initialized database with seed data at: {db_path}")
    else:
        print(f"Database already initialized at: {db_path}")

    conn.close()


if __name__ == "__main__":
    init_db()
