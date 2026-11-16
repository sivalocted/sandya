# Implementation Plan: Assistive Technology for Alzheimer's and Dementia

What we are going to build, based on the plan in the Interim Progress Report (IPR).

## 1. Already built ✅

| Part | What it does |
|---|---|
| **Reminder engine** (Python, `reminder_engine.py`) | The "brain": decides when to show a reminder, handles Done and Snooze, marks missed tasks, and alerts the caregiver after 2 misses in a row |
| **10 unit tests** (`test_reminder_engine.py`) | Prove each rule works, and all 10 pass |

## 2. To build next

| Priority | What we build | In simple words | When |
|---|---|---|---|
| **Must** | **SQLite database** (6 tables) | Where tasks, contacts and the history of what happened are saved | Week 5 (17–23 Nov) |
| **Must** | **Flask web app** | Connects the screens to the engine and the database | Week 5 |
| **Must** | **Screen A: Home** | Big date and time, "Next: Have your lunch", call buttons | Week 5 |
| **Must** | **Screen B: Reminder prompt** | Big green DONE button, plus "Remind me in 10 minutes" | Week 5 |
| **Must** | **Screen C: Caregiver setup** (with login) | The family member adds tasks, times, days and turns alerts on or off | Week 5 |
| **Must** | **Scheduler** (APScheduler) | Checks every minute: "Is a reminder due now?" | Week 5 |
| **Should** | **Read aloud (text-to-speech)** | The tablet speaks the reminder, using the browser's built-in voice (Web Speech API) | Week 5 |
| **Could** | **Voice commands** (speech-to-text) | The person says "done" instead of tapping | Only if time allows |
| **Could** | **Isolation Forest experiment** | Compare ML with simple rules on fake (simulated) data. It stays a test only and never sends real alerts. | Week 6, if time allows |
| **Won't** | **GPS / location alerts** | Left out of this project (needs a phone app, high privacy risk) | Not in this project |

### Database tables (from Appendix 3 of the IPR)

| Table | Holds |
|---|---|
| `CAREGIVER` | caregiver_id, name, email, password_hash |
| `PERSON` | person_id, caregiver_id, display_name, text_size, voice_on |
| `TASK` | task_id, person_id, label, time_of_day, days_mask, snooze_min, max_snoozes, window_min, alert_caregiver |
| `OCCURRENCE` | occ_id, task_id, due_at, status, snoozes |
| `EVENT_LOG` | log_id, occ_id, timestamp, action |
| `CONTACT` | contact_id, person_id, name, phone |

## 3. Week 6: testing (24–29 Nov)

- **Fix the clock-change bug**: a reminder at 01:30 on the night the clocks go forward (28 March 2027) would never show, so we store times in UTC.
- Run the edge-case tests T11–T18: midnight, two reminders at once, page refresh, a caregiver editing a reminder while it's showing.
- A **7-day simulation** on an accelerated clock: zero missed or duplicate reminders allowed.
- **Accessibility check** (WCAG 2.2 AA): text contrast of at least 4.5:1 and buttons of at least 48 px.

## 4. Build order

1. Database
2. Flask app and caregiver screen
3. Home and reminder screens
4. Scheduler
5. Read aloud
6. Tests
7. Optional extras

> **Rule:** we don't start the optional extras until all the **Must** items work and pass their tests.

## 5. Milestones

| Date | Milestone |
|---|---|
| 20 Nov 2026 | IPR due (check the real date on Canvas) |
| 23 Nov 2026 | Prototype demo-ready |
| 30 Nov 2026 | Final presentation (check the real date) |

## 6. 🇫🇷 En français

| Français | Prononciation | English |
|---|---|---|
| D'abord, nous construisons la base de données et les trois écrans. | dah-BOR, noo kohn-strwee-ZOHN lah BAHZ duh doh-NAY ay lay TRWAH-zay-KRAHN | First, we build the database and the three screens. |
| Ensuite, nous testons chaque règle. | ahn-SWEET, noo tess-TOHN SHAHK REH-gluh | Next, we test each rule. |
| La géolocalisation n'est pas incluse dans ce projet. | lah zhay-oh-loh-kah-lee-zah-SYOHN neh pah-zan-KLÜZ dahn suh pro-ZHAY | Geolocation is not included in this project. |

## 7. 📊 Data analyst link

The **`EVENT_LOG` table** works like a **fact table** in a data warehouse: every Done, Snooze or Miss becomes one row with a timestamp. Measures like the completion rate are simple aggregations on it:

```sql
SELECT
    SUM(CASE WHEN o.status = 'done' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS completion_rate
FROM OCCURRENCE o
WHERE o.status IN ('done', 'missed');
```
