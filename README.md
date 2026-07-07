# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python3 main.py`:

```
Today's Schedule
------------------------------
Morning walk (30 min) [priority: high]
Feeding (10 min) [priority: high]
Litter box cleaning (5 min) [priority: medium]
Playtime (15 min) [priority: low]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Sorts tasks by priority (high → low) or by `preferred_time` (untimed tasks sorted last) |
| Filtering | `Scheduler.filter_tasks(completed=..., pet_name=...)` | Filters tasks across all pets by completion status, pet name, or both |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight check: groups pending tasks by exact `preferred_time` and returns a warning message for any time slot shared by 2+ tasks, across the same or different pets. Does not check for overlapping durations (see `reflection.md` for that tradeoff) |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a task via `Pet.complete_task()` marks it done and, if its `frequency` is `"daily"` or `"weekly"`, automatically appends a fresh incomplete copy for the next occurrence |
| Daily plan generation | `Scheduler.generate_daily_plan()`, `Scheduler.plan_by_pet()` | Builds a priority-ordered plan that backfills smaller lower-priority tasks into leftover time within a given time budget, and can group the result by pet |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
