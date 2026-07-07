from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    description: str
    duration: int
    priority: str = "medium"
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False


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

    def generate_daily_plan(self, time_available: int) -> list[Task]:
        """Build a priority-ordered task plan that fits within the available time."""
        plan = []
        remaining_time = time_available
        for task in self.sort_by_priority(self.get_all_pending_tasks()):
            if task.duration <= remaining_time:
                plan.append(task)
                remaining_time -= task.duration
        return plan
