# PawPal+ Project Reflection

## 1. System Design

The design centers on three core actions a user performs:

1. **Enter/manage owner + pet info** — create a profile for the owner and their pet(s).
2. **Add/edit care tasks** — input tasks (walks, feeding, meds, grooming, etc.) with duration, priority, and constraints (time available, preferences).
3. **Generate and view a daily plan** — run the scheduling logic to produce a plan and display it with reasoning.

These actions map to four core classes:



**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- **`Owner`** — the pet owner's basic info (name, preferences).
- **`Pet`** — a pet's info (name, species/breed) linked to an `Owner`, and the pet's collection of `CareTask`s.
- **`CareTask`** — a single care task's data: name, category (walk/feeding/meds/grooming/enrichment), duration, priority, and constraints (preferred time, recurring, etc.).
- **`TaskManager`** — manages a pet's tasks (`add_task()`, `edit_task()`, `remove_task()`) and hands them off, with constraints applied, to the scheduling logic that generates the daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts()` only checks for exact `preferred_time` matches (e.g. two tasks both set to `"12:30"`) rather than checking whether tasks' durations actually overlap. A 20-minute task starting at `12:30` and a 15-minute task starting at `12:40` would genuinely overlap in real time, but since their `preferred_time` values differ, my scheduler would miss that conflict. True overlap detection would require converting each task into a start/end interval and checking pairwise interval intersection, which is more code and harder to reason about for a small daily task list.

This tradeoff is reasonable for this scenario because pet care tasks are typically scheduled to round time slots (e.g. "8:00am walk," "6:00pm feeding") rather than back-to-back with tight margins, so exact-match conflicts are the far more common and higher-value case to catch. It keeps the conflict check simple (a single dictionary grouped by time) and avoids false positives from over-strict interval math on approximate preferred times. If this app needed precise back-to-back scheduling (e.g. multiple pet sitters on a tight route), true interval overlap detection would be worth the added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
