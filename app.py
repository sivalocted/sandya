"""
Full-Stack Web Application for Alzheimer's & Dementia Daily Living Assistant.
Provides:
1. Recipient Tablet View (Screen A Home + Screen B Prompt with Voice & Chimes)
2. Caregiver Portal (Screen C Setup, Routine Management, Event Audit Log, Analytics)
3. 3-Screen Design Showcase (Figure A2.1 Live Interactive Architecture)
4. APScheduler Background Scheduling Service
"""

import os
import sqlite3
from datetime import datetime, date, time, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash

import database
from reminder_engine import ReminderEngine, Task, Occurrence, Status
from scheduler_service import manager, start_scheduler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = "dementia-assistant-secret-key-production-msc"

# Initialize database tables
try:
    database.init_db()
except Exception as e:
    print(f"Database init note: {e}")

# In persistent server environments, start background APScheduler
if not os.environ.get("VERCEL"):
    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler start note: {e}")


def get_part_of_day(hour: int) -> str:
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


# -------------------------------------------------------------
# UNIFIED APPLICATION: COMBINED ALL 3 SCREENS IN ONE INTERACTIVE WORKSPACE
# -------------------------------------------------------------
@app.route("/")
@app.route("/unified")
@app.route("/studio")
def index_unified():
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %B %Y")
    current_time = now.strftime("%H:%M")
    part_of_day = get_part_of_day(now.hour)

    tasks = database.get_active_tasks()
    event_logs = database.get_event_logs(limit=30)
    contacts = database.get_contacts()
    completion_rate = database.get_completion_rate()
    caregiver = database.get_caregiver()
    person = database.get_person()

    # Active prompt if any
    active_occ = None
    for occ in manager.engine.occurrences:
        if occ.status == Status.SHOWING:
            active_occ = occ
            break

    # Next upcoming task
    next_task = None
    future_occs = [
        o for o in manager.engine.occurrences
        if o.status in (Status.PENDING, Status.SNOOZED)
    ]
    if future_occs:
        future_occs.sort(key=lambda o: o.next_prompt_at)
        next_task = future_occs[0].task

    next_task_label = next_task.label if next_task else "Have your lunch"

    # Daily schedule for "My day" modal
    day_schedule = []
    for o in manager.engine.occurrences:
        day_schedule.append({
            "occ_id": o.occ_id,
            "time": o.task.time_of_day,
            "label": o.task.label,
            "status": o.status.value,
            "snoozes": o.snoozes,
        })
    day_schedule.sort(key=lambda x: x["time"])

    return render_template(
        "unified_app.html",
        tasks=tasks,
        event_logs=event_logs,
        contacts=contacts,
        completion_rate=completion_rate,
        alerts=manager.engine.caregiver_alerts,
        caregiver=caregiver,
        person=person,
        day_name=day_name,
        date_str=date_str,
        current_time=current_time,
        part_of_day=part_of_day,
        next_task_label=next_task_label,
        day_schedule=day_schedule,
        active_occ=active_occ,
    )


# -------------------------------------------------------------
# STANDALONE RECIPIENT TABLET VIEW: SCREEN A (HOME)
# -------------------------------------------------------------
@app.route("/home")
@app.route("/screen-a")
def home():
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %B %Y")
    current_time = now.strftime("%H:%M")
    part_of_day = get_part_of_day(now.hour)

    active_occ = None
    for occ in manager.engine.occurrences:
        if occ.status == Status.SHOWING:
            active_occ = occ
            break

    if active_occ and request.args.get("stay") != "1":
        return redirect(url_for("prompt", occ_id=active_occ.occ_id))

    next_task = None
    future_occs = [
        o for o in manager.engine.occurrences
        if o.status in (Status.PENDING, Status.SNOOZED)
    ]
    if future_occs:
        future_occs.sort(key=lambda o: o.next_prompt_at)
        next_task = future_occs[0].task

    next_task_label = next_task.label if next_task else "Have your lunch"

    day_schedule = []
    for o in manager.engine.occurrences:
        day_schedule.append({
            "occ_id": o.occ_id,
            "time": o.task.time_of_day,
            "label": o.task.label,
            "status": o.status.value,
            "snoozes": o.snoozes,
        })
    day_schedule.sort(key=lambda x: x["time"])

    contacts = database.get_contacts()

    return render_template(
        "home.html",
        day_name=day_name,
        date_str=date_str,
        current_time=current_time,
        part_of_day=part_of_day,
        next_task_label=next_task_label,
        day_schedule=day_schedule,
        contacts=contacts,
        active_occ=active_occ,
    )


# -------------------------------------------------------------
# SCREEN B: REMINDER PROMPT
# -------------------------------------------------------------
@app.route("/prompt")
@app.route("/prompt/<int:occ_id>")
@app.route("/screen-b")
def prompt(occ_id=None):
    occ = None
    if occ_id:
        occ = manager.active_occurrences.get(occ_id)

    if not occ:
        # Get first showing or create test occurrence
        for o in manager.engine.occurrences:
            if o.status == Status.SHOWING:
                occ = o
                break

    if not occ:
        # Create a test occurrence for demo
        today = date.today()
        task = Task(task_id=101, label="Have your lunch", time_of_day="12:30", alert_caregiver=True)
        occ = Occurrence(999, task, datetime.now())
        occ.status = Status.SHOWING
        manager.active_occurrences[999] = occ
        manager.engine.occurrences.append(occ)

    return render_template(
        "prompt.html",
        occ=occ,
        prompt_time=occ.task.time_of_day,
        prompt_task=occ.task.label,
        can_snooze=occ.can_snooze,
        snooze_count=occ.snoozes,
        max_snoozes=occ.task.max_snoozes,
    )


# -------------------------------------------------------------
# CAREGIVER PORTAL: SETUP, ROUTINE CRUD, AUDIT LOG, ANALYTICS
# -------------------------------------------------------------
@app.route("/caregiver")
@app.route("/screen-c")
def caregiver_portal():
    tasks = database.get_active_tasks()
    event_logs = database.get_event_logs(limit=25)
    contacts = database.get_contacts()
    completion_rate = database.get_completion_rate()
    caregiver = database.get_caregiver()
    person = database.get_person()

    return render_template(
        "caregiver.html",
        tasks=tasks,
        event_logs=event_logs,
        contacts=contacts,
        completion_rate=completion_rate,
        alerts=manager.engine.caregiver_alerts,
        caregiver=caregiver,
        person=person,
    )


@app.route("/caregiver/tasks/add", methods=["POST"])
def add_routine():
    label = request.form.get("label", "").strip()
    time_of_day = request.form.get("time_of_day", "12:00").strip()
    snooze_min = int(request.form.get("snooze_min", 10))
    max_snoozes = int(request.form.get("max_snoozes", 2))
    window_min = int(request.form.get("window_min", 60))
    alert_optin = 1 if request.form.get("alert_caregiver") in ("1", "on", "true") else 0

    days_str = request.form.get("days", "Every day")
    days_mask = 127
    if "weekday" in days_str.lower():
        days_mask = 31
    elif "weekend" in days_str.lower():
        days_mask = 96

    if label:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO TASK 
            (person_id, label, time_of_day, days_mask, snooze_min, max_snoozes, window_min, alert_caregiver) 
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)""",
            (label, time_of_day, days_mask, snooze_min, max_snoozes, window_min, alert_optin),
        )
        task_id = c.lastrowid

        # Schedule occurrence for today
        hour, minute = map(int, time_of_day.split(":"))
        due = datetime.combine(date.today(), time(hour, minute))
        c.execute(
            "INSERT INTO OCCURRENCE (task_id, due_at, status, snoozes) VALUES (?, ?, 'pending', 0)",
            (task_id, due.strftime("%Y-%m-%d %H:%M:%S")),
        )
        occ_id = c.lastrowid
        c.execute(
            "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
            (occ_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Caregiver created routine: '{label}' at {time_of_day}"),
        )
        conn.commit()
        conn.close()

        # Reload live scheduler
        manager.reload_tasks()

    return redirect(url_for("caregiver_portal"))


@app.route("/caregiver/tasks/delete/<int:task_id>", methods=["POST"])
def delete_routine(task_id):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("UPDATE TASK SET is_active = 0 WHERE task_id = ?", (task_id,))
    c.execute(
        "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (1, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Caregiver removed task ID {task_id}"),
    )
    conn.commit()
    conn.close()
    manager.reload_tasks()
    return redirect(url_for("caregiver_portal"))


@app.route("/caregiver/contacts/add", methods=["POST"])
def add_contact():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    color = request.form.get("color", "#2563EB")
    if name and phone:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO CONTACT (person_id, name, phone, avatar_color) VALUES (1, ?, ?, ?)", (name, phone, color))
        conn.commit()
        conn.close()
    return redirect(url_for("caregiver_portal"))


@app.route("/caregiver/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM CONTACT WHERE contact_id = ?", (contact_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("caregiver_portal"))


# -------------------------------------------------------------
# 3-SCREEN SHOWCASE (Figure A2.1 Wireframe Architecture)
# -------------------------------------------------------------
@app.route("/all-screens")
@app.route("/showcase")
def all_screens():
    return render_template("all_screens.html")


# -------------------------------------------------------------
# INTERACTIVE API: CONFIRM, SNOOZE, POLL, DEMO TRIGGERS
# -------------------------------------------------------------
@app.route("/api/status")
def api_status():
    now = datetime.now()
    active_prompt = None
    for occ in manager.engine.occurrences:
        if occ.status == Status.SHOWING:
            active_prompt = {
                "occ_id": occ.occ_id,
                "label": occ.task.label,
                "time": occ.task.time_of_day,
                "can_snooze": occ.can_snooze,
                "snoozes": occ.snoozes,
            }
            break

    return jsonify({
        "current_time": now.strftime("%H:%M"),
        "date_str": now.strftime("%d %B %Y"),
        "day_name": now.strftime("%A"),
        "part_of_day": get_part_of_day(now.hour),
        "active_prompt": active_prompt,
        "completion_rate": database.get_completion_rate(),
        "alerts_count": len(manager.engine.caregiver_alerts),
    })


@app.route("/api/confirm/<int:occ_id>", methods=["POST"])
def api_confirm(occ_id):
    now = datetime.now()
    occ = manager.active_occurrences.get(occ_id)
    if not occ:
        for o in manager.engine.occurrences:
            if o.occ_id == occ_id or o.status == Status.SHOWING:
                occ = o
                break

    if occ:
        manager.engine.confirm(occ, now)
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("UPDATE OCCURRENCE SET status = 'done' WHERE occ_id = ?", (occ.occ_id,))
        c.execute(
            "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
            (occ.occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Confirmed DONE: {occ.task.label}"),
        )
        conn.commit()
        conn.close()

    return jsonify({"success": True, "message": f"Task confirmed done!"})


@app.route("/api/snooze/<int:occ_id>", methods=["POST"])
def api_snooze(occ_id):
    now = datetime.now()
    occ = manager.active_occurrences.get(occ_id)
    if not occ:
        for o in manager.engine.occurrences:
            if o.occ_id == occ_id or o.status == Status.SHOWING:
                occ = o
                break

    if occ:
        snoozed = manager.engine.snooze(occ, now)
        if snoozed:
            conn = database.get_connection()
            c = conn.cursor()
            c.execute("UPDATE OCCURRENCE SET status = 'snoozed', snoozes = ? WHERE occ_id = ?", (occ.snoozes, occ.occ_id))
            c.execute(
                "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
                (occ.occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Snoozed ({occ.snoozes}/{occ.task.max_snoozes}): {occ.task.label}"),
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True, "snoozes": occ.snoozes, "can_snooze": occ.can_snooze})
        else:
            return jsonify({"success": False, "message": "Snooze limit reached"})

    return jsonify({"success": False, "message": "Occurrence not found"})


@app.route("/api/trigger-test-prompt", methods=["POST"])
def trigger_test_prompt():
    label = request.form.get("label", "Have your lunch")
    now = datetime.now()
    conn = database.get_connection()
    c = conn.cursor()

    # Find task or create
    c.execute("SELECT task_id FROM TASK WHERE label LIKE ? AND is_active = 1 LIMIT 1", (f"%{label}%",))
    row = c.fetchone()
    if row:
        task_id = row[0]
        c.execute("SELECT * FROM TASK WHERE task_id = ?", (task_id,))
        t_data = dict(c.fetchone())
        task = Task(
            task_id=t_data["task_id"],
            label=t_data["label"],
            time_of_day=now.strftime("%H:%M"),
            snooze_minutes=t_data["snooze_min"],
            max_snoozes=t_data["max_snoozes"],
            window_minutes=t_data["window_min"],
            alert_caregiver=bool(t_data["alert_caregiver"]),
        )
    else:
        task = Task(task_id=999, label=label, time_of_day=now.strftime("%H:%M"), alert_caregiver=True)
        task_id = 999

    c.execute(
        "INSERT INTO OCCURRENCE (task_id, due_at, status, snoozes) VALUES (?, ?, 'showing', 0)",
        (task_id, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    occ_id = c.lastrowid
    c.execute(
        "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
        (occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Prompt triggered: {label}"),
    )
    conn.commit()
    conn.close()

    occ = Occurrence(occ_id, task, now)
    occ.status = Status.SHOWING
    manager.active_occurrences[occ_id] = occ
    manager.engine.occurrences.append(occ)

    return jsonify({"success": True, "occ_id": occ_id, "label": label})


@app.route("/api/simulate-miss", methods=["POST"])
def simulate_miss():
    now = datetime.now()
    task = Task(task_id=500, label="Blood pressure medication", time_of_day="09:00", alert_caregiver=True)
    occ = Occurrence(manager.engine._next_occ_id, task, now)
    manager.engine._next_occ_id += 1
    occ.status = Status.MISSED
    manager.engine.occurrences.append(occ)
    manager.engine._register_miss(occ, now)

    conn = database.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO OCCURRENCE (task_id, due_at, status, snoozes) VALUES (?, ?, 'missed', 0)",
        (500, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    occ_id = c.lastrowid
    c.execute(
        "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
        (occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Simulated Miss: {task.label}"),
    )
    conn.commit()
    conn.close()

    streak = manager.engine._miss_streak.get(500, 0)
    msg = f"Miss recorded for '{task.label}'. Consecutive misses: {streak}."
    if streak >= 2:
        msg += " ⚠️ CAREGIVER ESCALATION ALERT DISPATCHED!"
    return jsonify({"success": True, "message": msg, "streak": streak, "alerts": manager.engine.caregiver_alerts})


@app.route("/api/reset-data", methods=["POST"])
def reset_data():
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS EVENT_LOG")
    c.execute("DROP TABLE IF EXISTS OCCURRENCE")
    c.execute("DROP TABLE IF EXISTS TASK")
    c.execute("DROP TABLE IF EXISTS CONTACT")
    c.execute("DROP TABLE IF EXISTS PERSON")
    c.execute("DROP TABLE IF EXISTS CAREGIVER")
    conn.commit()
    conn.close()

    database.init_db()
    manager.active_occurrences.clear()
    manager.engine.occurrences.clear()
    manager.engine._miss_streak.clear()
    manager.engine.caregiver_alerts.clear()
    manager.reload_tasks()

    return jsonify({"success": True, "message": "Database successfully reset to initial seed state!"})


if __name__ == "__main__":
    print("Starting Live Full-Stack Daily Living Assistant on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
