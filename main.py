from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Alex")

    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby")

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    biscuit.add_task(Task(description="Morning walk", duration=30, priority="high"))
    biscuit.add_task(Task(description="Feeding", duration=10, priority="high"))
    whiskers.add_task(Task(description="Litter box cleaning", duration=5, priority="medium"))
    whiskers.add_task(Task(description="Playtime", duration=15, priority="low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=60)

    print("Today's Schedule")
    print("-" * 30)
    for task in plan:
        print(f"{task.description} ({task.duration} min) [priority: {task.priority}]")


if __name__ == "__main__":
    main()
