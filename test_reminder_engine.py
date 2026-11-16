"""
Unit tests for reminder_engine.py
Matches the 10 scenarios in Appendix 5 (T1-T10) and test run in Appendix 4 of the IPR.
"""

from datetime import datetime, date, timedelta
import pytest
from reminder_engine import ReminderEngine, Task, Occurrence, Status


def test_prompt_appears_on_time_not_before():
    """T1: Prompt checked one minute before and at its set time -> Shown at 12:30, not at 12:29"""
    task = Task(task_id=1, label="Have lunch", time_of_day="12:30")
    engine = ReminderEngine(tasks=[task])
    test_date = date(2026, 11, 16)
    engine.plan_day(test_date)

    # Check at 12:29 (one minute before)
    before_time = datetime(2026, 11, 16, 12, 29)
    showing = engine.poll(before_time)
    assert len(showing) == 0

    # Check at 12:30 (exact time)
    at_time = datetime(2026, 11, 16, 12, 30)
    showing = engine.poll(at_time)
    assert len(showing) == 1
    assert showing[0].task.label == "Have lunch"
    assert showing[0].status == Status.SHOWING


def test_task_skipped_on_unscheduled_day():
    """T2: Weekday-only task on a Sunday -> Not planned"""
    # days_mask 31 = 0b0011111 (Mon=0 to Fri=4, Saturday=5, Sunday=6 not set)
    task = Task(task_id=2, label="Weekday medicine", time_of_day="09:00", days_mask=31)
    engine = ReminderEngine(tasks=[task])

    # Sunday 22 Nov 2026
    sunday = date(2026, 11, 22)
    assert sunday.weekday() == 6

    occurrences = engine.plan_day(sunday)
    assert len(occurrences) == 0


def test_confirmation_closes_prompt():
    """T3: Person taps DONE -> Prompt closes and does not return"""
    task = Task(task_id=3, label="Drink water", time_of_day="10:00")
    engine = ReminderEngine(tasks=[task])
    engine.plan_day(date(2026, 11, 16))

    now = datetime(2026, 11, 16, 10, 0)
    showing = engine.poll(now)
    assert len(showing) == 1

    # Person taps DONE
    engine.confirm(showing[0], now=datetime(2026, 11, 16, 10, 1))

    # Next check 5 minutes later -> Prompt does not return
    later = datetime(2026, 11, 16, 10, 5)
    showing_again = engine.poll(later)
    assert len(showing_again) == 0


def test_snooze_brings_prompt_back_later():
    """T4: Person snoozes for 10 minutes -> Quiet for 10 minutes, then shown again"""
    task = Task(task_id=4, label="Take vitamins", time_of_day="14:00", snooze_minutes=10)
    engine = ReminderEngine(tasks=[task])
    engine.plan_day(date(2026, 11, 16))

    now = datetime(2026, 11, 16, 14, 0)
    showing = engine.poll(now)
    assert len(showing) == 1
    occ = showing[0]

    # Person snoozes at 14:01
    snoozed = engine.snooze(occ, now=datetime(2026, 11, 16, 14, 1))
    assert snoozed is True
    assert occ.status == Status.SNOOZED

    # Quiet during snooze window (e.g. 14:05)
    quiet_time = datetime(2026, 11, 16, 14, 5)
    assert len(engine.poll(quiet_time)) == 0

    # Prompt returns at 14:11 (10 min after snooze)
    return_time = datetime(2026, 11, 16, 14, 11)
    showing_again = engine.poll(return_time)
    assert len(showing_again) == 1
    assert showing_again[0].task.label == "Take vitamins"


def test_snooze_limit_is_enforced():
    """T5: Third snooze when the limit is 2 -> Refused; snooze button hidden"""
    task = Task(task_id=5, label="Physio exercises", time_of_day="11:00", max_snoozes=2, snooze_minutes=10)
    engine = ReminderEngine(tasks=[task])
    engine.plan_day(date(2026, 11, 16))

    now = datetime(2026, 11, 16, 11, 0)
    occ = engine.poll(now)[0]

    # Snooze 1
    assert engine.snooze(occ, datetime(2026, 11, 16, 11, 1)) is True
    assert occ.can_snooze is True

    # Snooze 2
    assert engine.snooze(occ, datetime(2026, 11, 16, 11, 12)) is True
    assert occ.can_snooze is False  # Limit reached (2/2)

    # Snooze 3 -> Refused!
    assert engine.snooze(occ, datetime(2026, 11, 16, 11, 23)) is False
    assert occ.snoozes == 2


def test_unconfirmed_prompt_becomes_missed_after_window():
    """T6: No response for 60 minutes -> Recorded as missed"""
    task = Task(task_id=6, label="Call daughter", time_of_day="15:00", window_minutes=60)
    engine = ReminderEngine(tasks=[task])
    engine.plan_day(date(2026, 11, 16))

    start = datetime(2026, 11, 16, 15, 0)
    engine.poll(start)

    # 60 minutes later with no response
    after_window = datetime(2026, 11, 16, 16, 0)
    engine.poll(after_window)

    occ = engine.occurrences[0]
    assert occ.status == Status.MISSED


def test_no_caregiver_alert_without_opt_in():
    """T7: Two misses, alerts not opted in -> No caregiver alert"""
    task = Task(task_id=7, label="Check mail", time_of_day="09:00", alert_caregiver=False, window_minutes=30)
    engine = ReminderEngine(tasks=[task], escalate_after_misses=2)

    # Day 1 miss
    engine.plan_day(date(2026, 11, 16))
    engine.poll(datetime(2026, 11, 16, 9, 0))
    engine.poll(datetime(2026, 11, 16, 9, 31))  # missed

    # Day 2 miss
    engine.plan_day(date(2026, 11, 17))
    engine.poll(datetime(2026, 11, 17, 9, 0))
    engine.poll(datetime(2026, 11, 17, 9, 31))  # missed

    assert len(engine.caregiver_alerts) == 0


def test_caregiver_alert_only_after_repeated_misses():
    """T8: Two misses in a row, opted in -> Exactly one caregiver alert"""
    task = Task(task_id=8, label="Blood pressure pill", time_of_day="08:00", alert_caregiver=True, window_minutes=30)
    engine = ReminderEngine(tasks=[task], escalate_after_misses=2)

    # Miss 1: No alert yet
    engine.plan_day(date(2026, 11, 16))
    engine.poll(datetime(2026, 11, 16, 8, 0))
    engine.poll(datetime(2026, 11, 16, 8, 31))
    assert len(engine.caregiver_alerts) == 0

    # Miss 2: Consecutive miss -> Alert triggered!
    engine.plan_day(date(2026, 11, 17))
    engine.poll(datetime(2026, 11, 17, 8, 0))
    engine.poll(datetime(2026, 11, 17, 8, 31))
    assert len(engine.caregiver_alerts) == 1
    assert engine.caregiver_alerts[0]["task_id"] == 8
    assert engine.caregiver_alerts[0]["consecutive_misses"] == 2


def test_confirmation_resets_miss_streak():
    """T9: Miss, then done, then miss -> No alert (streak reset)"""
    task = Task(task_id=9, label="Heart medication", time_of_day="08:00", alert_caregiver=True, window_minutes=30)
    engine = ReminderEngine(tasks=[task], escalate_after_misses=2)

    # Day 1: Miss
    engine.plan_day(date(2026, 11, 16))
    engine.poll(datetime(2026, 11, 16, 8, 0))
    engine.poll(datetime(2026, 11, 16, 8, 31))
    assert engine._miss_streak[9] == 1

    # Day 2: Done (confirmed) -> Resets streak to 0
    engine.plan_day(date(2026, 11, 17))
    showing = engine.poll(datetime(2026, 11, 17, 8, 0))
    engine.confirm(showing[0], datetime(2026, 11, 17, 8, 5))
    assert engine._miss_streak[9] == 0

    # Day 3: Miss again -> Streak is 1, so no alert
    engine.plan_day(date(2026, 11, 18))
    engine.poll(datetime(2026, 11, 18, 8, 0))
    engine.poll(datetime(2026, 11, 18, 8, 31))
    assert engine._miss_streak[9] == 1
    assert len(engine.caregiver_alerts) == 0


def test_completion_rate():
    """T10: One done and one missed task -> Completion rate 50%"""
    t1 = Task(task_id=10, label="Lunch", time_of_day="12:00", window_minutes=30)
    t2 = Task(task_id=11, label="Walk", time_of_day="16:00", window_minutes=30)
    engine = ReminderEngine(tasks=[t1, t2])
    engine.plan_day(date(2026, 11, 16))

    # Task 1 is confirmed done
    s1 = engine.poll(datetime(2026, 11, 16, 12, 0))
    engine.confirm(s1[0], datetime(2026, 11, 16, 12, 10))

    # Task 2 is missed
    engine.poll(datetime(2026, 11, 16, 16, 0))
    engine.poll(datetime(2026, 11, 16, 16, 31))

    # Completion rate: 1 done / 2 finished = 0.50 (50%)
    assert engine.completion_rate() == 0.50
