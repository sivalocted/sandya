"""
Reminder Engine - Core logic for Alzheimer's & Dementia daily living assistant.
Implements the 5 deterministic rules specified in the IPR (Sections 1.5, 2.1, Appendix 4).
"""

from datetime import datetime, date, time, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any


class Status(str, Enum):
    PENDING = "pending"
    SHOWING = "showing"
    SNOOZED = "snoozed"
    DONE = "done"
    MISSED = "missed"


class Task:
    def __init__(
        self,
        task_id: int,
        label: str,
        time_of_day: str,  # "HH:MM" e.g. "12:30"
        days_mask: int = 127,  # 7-bit mask: Mon=1, Tue=2, Wed=4, Thu=8, Fri=16, Sat=32, Sun=64 (127=all days, 31=Mon-Fri)
        snooze_minutes: int = 10,
        max_snoozes: int = 2,
        window_minutes: int = 60,
        alert_caregiver: bool = False,
        person_id: int = 1,
    ):
        self.task_id = task_id
        self.label = label
        self.time_of_day = time_of_day
        self.days_mask = days_mask
        self.snooze_minutes = snooze_minutes
        self.max_snoozes = max_snoozes
        self.window_minutes = window_minutes
        self.alert_caregiver = alert_caregiver
        self.person_id = person_id

    def is_scheduled_on(self, day_of_week: int) -> bool:
        """day_of_week: Monday=0, Tuesday=1, ..., Sunday=6"""
        return bool(self.days_mask & (1 << day_of_week))


class Occurrence:
    def __init__(self, occ_id: int, task: Task, due_at: datetime):
        self.occ_id = occ_id
        self.task = task
        self.due_at = due_at
        self.next_prompt_at = due_at
        self.status = Status.PENDING
        self.snoozes = 0
        self.event_log: List[Dict[str, Any]] = []
        self._note(due_at, "occurrence created")

    def _note(self, now: datetime, action: str) -> None:
        self.event_log.append({"timestamp": now, "action": action, "status": self.status})

    @property
    def can_snooze(self) -> bool:
        return self.snoozes < self.task.max_snoozes and self.status in (Status.SHOWING, Status.PENDING, Status.SNOOZED)


class ReminderEngine:
    def __init__(self, tasks: Optional[List[Task]] = None, escalate_after_misses: int = 2):
        self.tasks: List[Task] = tasks or []
        self.occurrences: List[Occurrence] = []
        self._miss_streak: Dict[int, int] = {}
        self.escalate_after_misses = escalate_after_misses
        self.caregiver_alerts: List[Dict[str, Any]] = []
        self._next_occ_id = 1

    # Rule 1: Plan the day based on recurrence and days mask
    def plan_day(self, target_date: date) -> List[Occurrence]:
        day_occurrences = []
        weekday = target_date.weekday()  # Mon=0 ... Sun=6
        for task in self.tasks:
            if task.is_scheduled_on(weekday):
                hour, minute = map(int, task.time_of_day.split(":"))
                due_at = datetime.combine(target_date, time(hour, minute))
                occ = Occurrence(self._next_occ_id, task, due_at)
                self._next_occ_id += 1
                self.occurrences.append(occ)
                day_occurrences.append(occ)
        return day_occurrences

    # Rule 2 & 3: Check/poll prompt on time; close unconfirmed prompt after window
    def poll(self, now: datetime) -> List[Occurrence]:
        showing: List[Occurrence] = []
        for occ in self.occurrences:
            if occ.status in (Status.PENDING, Status.SNOOZED, Status.SHOWING):
                # Rule 3: Close unconfirmed prompt after window
                window_expiry = occ.due_at + timedelta(minutes=occ.task.window_minutes)
                if now >= window_expiry:
                    occ.status = Status.MISSED
                    occ._note(now, "window expired - marked as missed")
                    self._register_miss(occ, now)
                    continue

                # Rule 2: Prompt appears on time, not before
                if now >= occ.next_prompt_at:
                    occ.status = Status.SHOWING
                    showing.append(occ)
        return showing

    # Confirmation: taps DONE
    def confirm(self, occ: Occurrence, now: datetime) -> None:
        occ.status = Status.DONE
        occ._note(now, "confirmed done")
        # Rule 5 complement: confirmation resets miss streak
        tid = occ.task.task_id
        self._miss_streak[tid] = 0

    # Rule 4: Snoozing allowed limited times, then refused / hidden
    def snooze(self, occ: Occurrence, now: datetime) -> bool:
        if occ.snoozes >= occ.task.max_snoozes:
            occ._note(now, "snooze refused (limit reached)")
            return False
        occ.snoozes += 1
        occ.status = Status.SNOOZED
        occ.next_prompt_at = now + timedelta(minutes=occ.task.snooze_minutes)
        occ._note(now, f"snoozed ({occ.snoozes}/{occ.task.max_snoozes})")
        return True

    # Rule 5: Only repeated misses on an opted-in task reach the caregiver
    def _register_miss(self, occ: Occurrence, now: datetime) -> None:
        tid = occ.task.task_id
        self._miss_streak[tid] = self._miss_streak.get(tid, 0) + 1
        if occ.task.alert_caregiver and self._miss_streak[tid] >= self.escalate_after_misses:
            self.caregiver_alerts.append({
                "timestamp": now,
                "task_id": tid,
                "label": occ.task.label,
                "consecutive_misses": self._miss_streak[tid],
                "message": f"Caregiver Alert: '{occ.task.label}' missed {self._miss_streak[tid]} times consecutively."
            })

    # Metric: Completion rate over finished occurrences
    def completion_rate(self) -> float:
        finished = [o for o in self.occurrences if o.status in (Status.DONE, Status.MISSED)]
        if not finished:
            return 0.0
        done_count = sum(1 for o in finished if o.status == Status.DONE)
        return done_count / len(finished)
