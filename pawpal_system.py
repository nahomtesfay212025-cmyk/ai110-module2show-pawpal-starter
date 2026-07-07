from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    description: str
    duration: int
    priority: str = "medium"
    frequency: str = "daily"
    completed: bool = False
    preferred_time: str = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def next_occurrence(self) -> "Task":
        """Return a fresh, incomplete copy of this task for its next daily/weekly occurrence."""
        return Task(
            description=self.description,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            preferred_time=self.preferred_time,
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def complete_task(self, task: Task) -> None:
        """Mark a task complete, auto-scheduling its next occurrence if it recurs daily/weekly."""
        task.mark_complete()
        if task.frequency in ("daily", "weekly"):
            self.add_task(task.next_occurrence())


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list of pets."""
        self.pets.remove(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks this scheduler manages."""
        self.owner = owner

    def get_all_pending_tasks(self) -> list[Task]:
        """Return every incomplete task across all of the owner's pets."""
        tasks = []
        for pet in self.owner.pets:
            tasks.extend(pet.pending_tasks())
        return tasks

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> list[Task]:
        """Return tasks across all pets, optionally filtered by completion status and/or pet name."""
        tasks = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                tasks.append(task)
        return tasks

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted by preferred_time, with untimed tasks last."""
        return sorted(tasks, key=lambda t: t.preferred_time or "99:99")

    def generate_daily_plan(self, time_available: int) -> list[Task]:
        """Build a priority-ordered task plan, backfilling smaller tasks to use leftover time."""
        plan = []
        remaining_time = time_available
        for task in self.sort_by_priority(self.get_all_pending_tasks()):
            if task.duration <= remaining_time:
                plan.append(task)
                remaining_time -= task.duration
        return plan

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for any pending tasks sharing the same preferred_time."""
        warnings = []
        by_time: dict[str, list[tuple[str, Task]]] = {}
        for pet in self.owner.pets:
            for task in pet.pending_tasks():
                if not task.preferred_time:
                    continue
                by_time.setdefault(task.preferred_time, []).append((pet.name, task))

        for time_slot, entries in by_time.items():
            if len(entries) < 2:
                continue
            names = ", ".join(f"{pet_name}'s {task.description}" for pet_name, task in entries)
            warnings.append(f"Conflict at {time_slot}: {names}")
        return warnings

    def plan_by_pet(self, time_available: int) -> dict[str, list[Task]]:
        """Group the generated daily plan's tasks by the pet they belong to."""
        plan = self.generate_daily_plan(time_available)
        grouped: dict[str, list[Task]] = {pet.name: [] for pet in self.owner.pets}
        for pet in self.owner.pets:
            grouped[pet.name] = [t for t in pet.tasks if t in plan]
        return grouped
