# PawPal+ Project Reflection

## 1. System Design

The design centers on three core actions a user performs:

1. **Enter/manage owner + pet info** — create a profile for the owner and their pet(s).
2. **Add/edit care tasks** — input tasks (walks, feeding, meds, grooming, etc.) with duration, priority, and constraints (time available, preferences).
3. **Generate and view a daily plan** — run the scheduling logic to produce a plan and display it with reasoning.

These actions map to four core classes.

**a. Initial design**

My initial UML draft (`diagrams/uml_draft.mmd`) had four classes:

- **`Owner`** — the pet owner's basic info (name, preferences).
- **`Pet`** — a pet's info (name, species/breed) linked back to an `Owner`, plus the pet's collection of `CareTask`s.
- **`CareTask`** — a single care task's data: name, category (walk/feeding/meds/grooming/enrichment), duration, priority, and constraints (preferred time, recurring, etc.).
- **`TaskManager`** — owned one-to-one by a `Pet`, responsible for CRUD on that pet's tasks (`add_task()`, `edit_task()`, `remove_task()`) and for handing them off to scheduling logic that generates a daily plan.

**b. Design changes**

Comparing the draft to `diagrams/uml_final.mmd` (matching the real `pawpal_system.py`), several things changed once I was actually implementing instead of designing on paper:

- `CareTask` became `Task`, and lost fields I never ended up needing (`category`, a `recurring` bool) in favor of a `frequency` string (`"daily"`/`"weekly"`/other) plus a `completed` flag — `frequency` doubled as both "is this recurring" and "how often," so the separate boolean was redundant.
- `Owner.preferences: dict` was dropped entirely — I never found a concrete use for a free-form preferences dict once `Task.preferred_time` and `priority` covered the actual scheduling inputs.
- `Pet.owner` (the back-reference) was dropped. Nothing in the scheduling logic ever needed to walk from a `Pet` back up to its `Owner`, so keeping it would have been an unused relationship purely for diagram symmetry.
- The biggest change: `TaskManager` (one per `Pet`, doing CRUD + planning) was replaced by a single `Scheduler` class that takes a whole `Owner` and operates across *all* of that owner's pets. This happened because the moment I implemented conflict detection and cross-pet daily planning, a per-pet manager couldn't see other pets' tasks to compare against — the natural owner of that logic is something that already has access to the whole `Owner.pets` list, not something scoped to one `Pet`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: **time available** (a hard budget passed into `generate_daily_plan()`), **priority** (`high`/`medium`/`low`, used to decide task order when the budget can't fit everything), and **preferred time** (used for chronological display and conflict detection, not for filling the time budget). I prioritized time and priority as the "must-have" constraints because the core scenario is "what fits today given limited time," and treated preferred-time conflict detection as a secondary but still important constraint, since pet care tasks (feeding, meds) often have real-world timing requirements where a scheduling collision is a genuine problem, not just a display inconvenience.

**b. Tradeoffs**

`Scheduler.detect_conflicts()` only checks for exact `preferred_time` matches (e.g. two tasks both set to `"12:30"`) rather than checking whether tasks' durations actually overlap. A 20-minute task starting at `12:30` and a 15-minute task starting at `12:40` would genuinely overlap in real time, but since their `preferred_time` values differ, my scheduler would miss that conflict. True overlap detection would require converting each task into a start/end interval and checking pairwise interval intersection, which is more code and harder to reason about for a small daily task list.

This tradeoff is reasonable for this scenario because pet care tasks are typically scheduled to round time slots (e.g. "8:00am walk," "6:00pm feeding") rather than back-to-back with tight margins, so exact-match conflicts are the far more common and higher-value case to catch. It keeps the conflict check simple (a single dictionary grouped by time) and avoids false positives from over-strict interval math on approximate preferred times. If this app needed precise back-to-back scheduling (e.g. multiple pet sitters on a tight route), true interval overlap detection would be worth the added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant (Claude Code) across nearly every phase: drafting the initial UML skeleton, implementing `pawpal_system.py`, writing the test suite, wiring `Scheduler` methods into the Streamlit UI, and re-syncing the UML diagram against the final code. The most effective feature was giving it direct read access to my actual source files (`pawpal_system.py`, `app.py`, `tests/test_pawpal.py`) instead of describing my code from memory — when I asked it to identify edge cases for the scheduler, it read the real implementation and caught concrete issues tied to specific lines (e.g., the string-based time comparison in `sort_by_time`), rather than giving generic "test null and negative inputs" advice. Running the actual test suite and `main.py` output and pasting it back into the assistant's context (rather than it guessing at output) was also key — it let me verify claims instead of trusting them.

The most helpful prompts were narrow and outcome-specific ("draft test functions for these edge cases," "does this diagram still match this file," "render it") rather than open-ended ("review my code"). Asking it to run the code and show me real output, not just describe what it expected to happen, consistently surfaced things I would have missed, like the greedy backfill's non-optimal packing behavior.

**b. Judgment and verification**

One clear example: when I asked for a test confirming that completing an already-completed recurring task shouldn't spawn a duplicate, the assistant wrote the test with that assumption baked in — asserting `len(pet.tasks) == 3`. When we ran it, it failed with `4`, because `complete_task()` has no guard against re-completing an already-done task. Rather than "fixing" the test to force the assumption to pass (which would have hidden a real gap), I had it rewrite the test to document the actual behavior (`test_complete_task_called_again_on_already_completed_task_still_spawns`) and flag it as a candidate bug in the README's confidence-level notes instead. That's the pattern I used throughout: treat a failing assertion as a signal to re-examine the assumption, not the test — verify against the real, running code before accepting any suggested behavior as correct.

**c. Working across separate phases**

Scoping each request to one deliverable — "just focus on tests," then UML sync, then README sections, then the UI wiring — kept each round of work self-contained and easy to verify in isolation (run pytest, render the diagram, load the app) before moving to the next. It also meant each phase's output stayed traceable to a concrete artifact (a test file, a `.mmd`/`.png` pair, a README section) instead of one large diffuse change touching everything at once, which made it much easier to spot when something (like the stale UML diagram or the stale sample output in the README) had drifted from the actual code.

---

## 4. Testing and Verification

**a. What you tested**

`tests/test_pawpal.py` covers five behavior groups: **sorting** (priority order, chronological order by `preferred_time`, unknown-priority fallback, untimed tasks sorting last, stable ordering for ties), **recurrence** (`daily`/`weekly` completion spawning a fresh occurrence, non-recurring frequencies not spawning one, and what happens when a task is completed twice), **conflict detection** (same time across pets, same time within one pet, 3-way conflicts, and that completed/untimed tasks are correctly ignored), **daily plan generation** (zero/negative time budgets, exact-duration fits, and priority ordering under a tight budget), and **filtering/grouping** (`filter_tasks` and `plan_by_pet` with unknown pet names and with duplicate, value-equal tasks across pets). These mattered because they're exactly the behaviors the scenario depends on — a scheduler that sorts wrong, silently fails to recur, or misses a real double-booking would produce a plan the user can't trust, and the boundary cases (0 minutes, ties, duplicates) are where those categories of bugs tend to hide.

**b. Confidence**

I'm confident (documented as 4/5 stars in the README) that the core sorting, recurrence, and conflict-detection logic behaves correctly for the common cases — all 24 tests pass, and I verified them by running `main.py` and reading the real output rather than trusting assertions in isolation. I'm holding back a star for two known gaps the tests surfaced rather than hid: `sort_by_time` compares `preferred_time` as a raw string, so unpadded hours like `"9:00"` sort after `"10:00"`; and `complete_task()` has no guard against being called twice on the same task, so it will double-spawn a recurring occurrence. With more time I'd test: overlapping-duration conflicts (not just exact `preferred_time` matches, per the tradeoff in Section 2), what happens when a `Task` is added to two different `Pet`s' lists simultaneously (given `Task` equality is value-based, not identity-based), and Streamlit-session-state edge cases like re-running "Generate schedule" after removing a pet mid-session.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the conflict-detection and recurrence logic — both stayed simple (a dict grouped by time slot; a frequency check plus one new `Task` copy) while still handling the realistic cases the scenario cares about, and the test suite gave me confidence that simplicity wasn't hiding a correctness gap.

**b. What you would improve**

If I had another iteration, I'd wire recurrence into the Streamlit UI (there's currently no "complete task" button, so that behavior is only demonstrated via `main.py`), and I'd upgrade `detect_conflicts()` from exact-time matching to real start/end interval overlap now that the scenario has proven out — the simple version was the right starting tradeoff, but the UI makes double-booking visible enough that catching near-miss overlaps would add real value.

**c. Key takeaway**

The biggest lesson was that a design only becomes trustworthy once it's been run and observed, not just reasoned about — both the UML diagram and the README's sample output had quietly drifted from the real code, and a test I wrote from an assumption (`complete_task` twice) turned out to be wrong until I actually ran it. Treating "run it and look at the output" as a non-negotiable step, for both my own code and AI-suggested code, caught more real issues than any amount of re-reading the code would have.
