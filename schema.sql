-- Database Schema for Alzheimer's & Dementia Daily-Living Assistant
-- Derived from Appendix 3 (System architecture & data model)

CREATE TABLE IF NOT EXISTS CAREGIVER (
    caregiver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PERSON (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    caregiver_id INTEGER NOT NULL,
    display_name TEXT NOT NULL,
    text_size TEXT DEFAULT 'large',  -- 'normal', 'large', 'extra-large'
    voice_on BOOLEAN DEFAULT 1,
    FOREIGN KEY (caregiver_id) REFERENCES CAREGIVER(caregiver_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TASK (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    time_of_day TEXT NOT NULL,  -- 'HH:MM' stored in 24hr format
    days_mask INTEGER DEFAULT 127,  -- 7-bit mask (1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun)
    snooze_min INTEGER DEFAULT 10,
    max_snoozes INTEGER DEFAULT 2,
    window_min INTEGER DEFAULT 60,
    alert_caregiver BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (person_id) REFERENCES PERSON(person_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS OCCURRENCE (
    occ_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    due_at TIMESTAMP NOT NULL,  -- Stored in UTC ISO format to prevent DST bugs
    status TEXT NOT NULL CHECK (status IN ('pending', 'showing', 'snoozed', 'done', 'missed')),
    snoozes INTEGER DEFAULT 0,
    FOREIGN KEY (task_id) REFERENCES TASK(task_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS EVENT_LOG (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    occ_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,  -- 'created', 'shown', 'snoozed', 'done', 'missed', 'escalated'
    FOREIGN KEY (occ_id) REFERENCES OCCURRENCE(occ_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CONTACT (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    avatar_color TEXT DEFAULT '#4A90E2',
    FOREIGN KEY (person_id) REFERENCES PERSON(person_id) ON DELETE CASCADE
);
