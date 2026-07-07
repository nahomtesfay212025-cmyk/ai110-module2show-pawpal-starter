from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Alex")

    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby")

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    # Tasks added out of order (mixed times, priorities, completion status)
    biscuit.add_task(
        Task(description="Feeding", duration=10, priority="high", preferred_time="18:00")
    )
    biscuit.add_task(
        Task(
            description="Morning walk",
            duration=30,
            priority="high",
            preferred_time="08:00",
            completed=True,
        )
    )
    whiskers.add_task(Task(description="Playtime", duration=15, priority="low", preferred_time="12:30"))
    whiskers.add_task(
        Task(
            description="Litter box cleaning",
            duration=5,
            priority="medium",
            preferred_time="07:00",
        )
    )

    # Two tasks scheduled at the same time (different pets) to trigger a conflict.
    biscuit.add_task(
        Task(description="Vet checkup", duration=20, priority="high", preferred_time="12:30")
    )

    scheduler = Scheduler(owner)

    print("All tasks sorted by time")
    print("-" * 30)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        status = "done" if task.completed else "pending"
        print(f"{task.preferred_time}  {task.description} ({task.duration} min) [{status}]")

    print("\nPending tasks only (filter_tasks)")
    print("-" * 30)
    for task in scheduler.filter_tasks(completed=False):
        print(f"{task.description} — {task.priority}")

    print("\nBiscuit's tasks only (filter_tasks)")
    print("-" * 30)
    for task in scheduler.filter_tasks(pet_name="Biscuit"):
        print(f"{task.description} — {task.priority}")

    print("\nCompleting Biscuit's Feeding task (recurs daily)")
    print("-" * 30)
    feeding_task = next(t for t in biscuit.tasks if t.description == "Feeding")
    biscuit.complete_task(feeding_task)
    for task in biscuit.tasks:
        status = "done" if task.completed else "pending"
        print(f"{task.description} ({task.frequency}) [{status}]")

    print("\nConflict check")
    print("-" * 30)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"⚠️  {warning}")
    else:
        print("No conflicts found.")

    print("\nToday's Schedule")
    print("-" * 30)
    plan_by_pet = scheduler.plan_by_pet(time_available=60)
    for pet_name, tasks in plan_by_pet.items():
        if not tasks:
            continue
        print(f"\n{pet_name}:")
        for task in tasks:
            print(f"  {task.description} ({task.duration} min) [priority: {task.priority}]")


if __name__ == "__main__":
    main()
