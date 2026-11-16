"""
Database management for Alzheimer's & Dementia Daily Living Assistant.
Implements the 6 tables specified in Appendix 3 of the IPR:
CAREGIVER, PERSON, TASK, OCCURRENCE, EVENT_LOG, CONTACT.
"""

import os
import sqlite3
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional

def get_db_path() -> str:
    if os.environ.get("VERCEL"):
        tmp_db = "/tmp/assistant.db"
        if not os.path.exists(tmp_db):
            base_db = os.path.join(os.path.dirname(__file__), "assistant.db")
            if os.path.exists(base_db):
                import shutil
                shutil.copy2(base_db, tmp_db)
        return tmp_db
    return os.path.join(os.path.dirname(__file__), "assistant.db")

DB_PATH = get_db_path()
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> None:
    if db_path is None:
        db_path = get_db_path()
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection(db_path)
    c = conn.cursor()
    with open(schema_path, "r", encoding="utf-8") as f:
        c.executescript(f.read())
    conn.commit()

    # Seed initial data if empty
    c.execute("SELECT COUNT(*) FROM CAREGIVER")
    if c.fetchone()[0] == 0:
        seed_data(conn)
    conn.close()


def seed_data(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    # 1. Caregiver: Sarah (daughter)
    c.execute(
        "INSERT INTO CAREGIVER (name, email, password_hash) VALUES (?, ?, ?)",
        ("Sarah Jenkins", "sarah@example.com", "pbkdf2:sha256:caregiver123"),
    )
    caregiver_id = c.lastrowid

    # 2. Person living with dementia: John (father)
    c.execute(
        "INSERT INTO PERSON (caregiver_id, display_name, text_size, voice_on) VALUES (?, ?, ?, ?)",
        (caregiver_id, "John", "large", 1),
    )
    person_id = c.lastrowid

    # 3. Tasks (Daily Routines)
    tasks = [
        (person_id, "Have morning tea & toast", "08:30", 127, 10, 2, 45, 0),
        (person_id, "Take morning blood pressure medication", "09:00", 127, 10, 2, 60, 1),
        (person_id, "Have your lunch", "12:30", 127, 10, 2, 60, 1),
        (person_id, "Afternoon walk in the garden", "15:30", 31, 15, 2, 60, 0),
        (person_id, "Take evening heart medicine", "20:00", 127, 10, 2, 60, 1),
    ]
    c.executemany(
        """INSERT INTO TASK 
        (person_id, label, time_of_day, days_mask, snooze_min, max_snoozes, window_min, alert_caregiver) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        tasks,
    )

    # 4. Contacts
    contacts = [
        (person_id, "Sarah (Daughter)", "07123 456789", "#2E7D32"),
        (person_id, "Dr. Evans (GP)", "01234 567890", "#1565C0"),
        (person_id, "Nurse Mark", "07987 654321", "#6A1B9A"),
    ]
    c.executemany(
        "INSERT INTO CONTACT (person_id, name, phone, avatar_color) VALUES (?, ?, ?, ?)",
        contacts,
    )

    # 5. Seed some initial completed occurrences & events for testing
    now = datetime.now()
    today_date = date.today()

    # Morning task completed
    c.execute("SELECT task_id FROM TASK WHERE label LIKE '%morning tea%' LIMIT 1")
    t1_row = c.fetchone()
    if t1_row:
        t1_id = t1_row[0]
        c.execute(
            "INSERT INTO OCCURRENCE (task_id, due_at, status, snoozes) VALUES (?, ?, 'done', 0)",
            (t1_id, f"{today_date} 08:30:00"),
        )
        occ1_id = c.lastrowid
        c.execute(
            "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
            (occ1_id, f"{today_date} 08:35:12", "Confirmed DONE: Have morning tea & toast"),
        )

    conn.commit()


# Helper query methods
def get_person(person_id: int = 1) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM PERSON WHERE person_id = ?", (person_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_caregiver(caregiver_id: int = 1) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM CAREGIVER WHERE caregiver_id = ?", (caregiver_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_tasks(person_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM TASK WHERE person_id = ? AND is_active = 1 ORDER BY time_of_day ASC", (person_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_contacts(person_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM CONTACT WHERE person_id = ?", (person_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_event_logs(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT e.log_id, e.timestamp, e.action, o.occ_id, t.label, t.time_of_day 
        FROM EVENT_LOG e 
        LEFT JOIN OCCURRENCE o ON e.occ_id = o.occ_id 
        LEFT JOIN TASK t ON o.task_id = t.task_id 
        ORDER BY e.log_id DESC LIMIT ?""",
        (limit,),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def log_event(occ_id: int, action: str) -> None:
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)", (occ_id, now_str, action))
    conn.commit()
    conn.close()


def get_completion_rate() -> float:
    """Calculates overall completion rate as specified in Section 7 of IPR plan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            SUM(CASE WHEN o.status = 'done' THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*), 0) AS rate
        FROM OCCURRENCE o
        WHERE o.status IN ('done', 'missed')
    """)
    res = c.fetchone()[0]
    conn.close()
    return round((res or 0.0) * 100, 1)
