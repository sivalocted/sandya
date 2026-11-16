"""
Background Scheduler Service (APScheduler).
Checks every minute (or 10 seconds in development) for due reminders and timeout windows.
Enforces Rule 2 (On-time prompt) and Rule 3 (Window timeout into Missed).
"""

import time as time_lib
from datetime import datetime, date, time, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import database
from reminder_engine import ReminderEngine, Task, Occurrence, Status

scheduler = BackgroundScheduler()


class EngineManager:
    def __init__(self):
        self.engine = ReminderEngine(tasks=[], escalate_after_misses=2)
        self.active_occurrences = {}  # occ_id -> Occurrence
        self.reload_tasks()

    def reload_tasks(self):
        tasks_data = database.get_active_tasks()
        tasks = []
        for r in tasks_data:
            t = Task(
                task_id=r["task_id"],
                label=r["label"],
                time_of_day=r["time_of_day"],
                days_mask=r["days_mask"],
                snooze_minutes=r["snooze_min"],
                max_snoozes=r["max_snoozes"],
                window_minutes=r["window_min"],
                alert_caregiver=bool(r["alert_caregiver"]),
                person_id=r["person_id"],
            )
            tasks.append(t)
        self.engine.tasks = tasks
        self.plan_today()

    def plan_today(self):
        today = date.today()
        weekday = today.weekday()
        conn = database.get_connection()
        c = conn.cursor()

        for t in self.engine.tasks:
            if t.is_scheduled_on(weekday):
                hour, minute = map(int, t.time_of_day.split(":"))
                due = datetime.combine(today, time(hour, minute))

                # Check if occurrence already exists in DB for today
                c.execute(
                    "SELECT occ_id, status, snoozes FROM OCCURRENCE WHERE task_id = ? AND date(due_at) = date(?)",
                    (t.task_id, due.strftime("%Y-%m-%d")),
                )
                row = c.fetchone()
                if not row:
                    c.execute(
                        "INSERT INTO OCCURRENCE (task_id, due_at, status, snoozes) VALUES (?, ?, 'pending', 0)",
                        (t.task_id, due.strftime("%Y-%m-%d %H:%M:%S")),
                    )
                    occ_id = c.lastrowid
                    occ = Occurrence(occ_id, t, due)
                    self.active_occurrences[occ_id] = occ
                    self.engine.occurrences.append(occ)
                else:
                    occ_id, status_str, snoozes = row
                    if occ_id not in self.active_occurrences:
                        occ = Occurrence(occ_id, t, due)
                        occ.status = Status(status_str)
                        occ.snoozes = snoozes
                        self.active_occurrences[occ_id] = occ
                        self.engine.occurrences.append(occ)
        conn.commit()
        conn.close()

    def check_schedule(self):
        """Called every 10 seconds by APScheduler."""
        now = datetime.now()
        conn = database.get_connection()
        c = conn.cursor()

        for occ in list(self.engine.occurrences):
            if occ.status in (Status.PENDING, Status.SNOOZED, Status.SHOWING):
                # Rule 3: Close unconfirmed prompt after window
                window_expiry = occ.due_at + timedelta(minutes=occ.task.window_minutes)
                if now >= window_expiry:
                    occ.status = Status.MISSED
                    self.engine._register_miss(occ, now)
                    c.execute("UPDATE OCCURRENCE SET status = 'missed' WHERE occ_id = ?", (occ.occ_id,))
                    c.execute(
                        "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
                        (occ.occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Window expired - Missed: {occ.task.label}"),
                    )
                    continue

                # Rule 2: Show prompt on time
                if now >= occ.next_prompt_at and occ.status != Status.SHOWING:
                    occ.status = Status.SHOWING
                    c.execute("UPDATE OCCURRENCE SET status = 'showing' WHERE occ_id = ?", (occ.occ_id,))
                    c.execute(
                        "INSERT INTO EVENT_LOG (occ_id, timestamp, action) VALUES (?, ?, ?)",
                        (occ.occ_id, now.strftime("%Y-%m-%d %H:%M:%S"), f"Prompt active on screen: {occ.task.label}"),
                    )

        conn.commit()
        conn.close()


manager = EngineManager()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(func=manager.check_schedule, trigger="interval", seconds=10, id="reminder_check")
        scheduler.start()
        print("APScheduler background service started (checking every 10 seconds).")
