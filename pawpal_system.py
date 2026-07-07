from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    owner: Owner
    tasks: list["CareTask"] = field(default_factory=list)


@dataclass
class CareTask:
    name: str
    category: str
    duration: int
    priority: str
    preferred_time: str = None
    recurring: bool = False


class TaskManager:
    def __init__(self):
        self.tasks: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        pass

    def edit_task(self, task_id: str, updates: dict) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def generate_plan(self, time_available: int) -> list[CareTask]:
        pass
