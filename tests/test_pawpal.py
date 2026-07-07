from pawpal_system import Owner, Pet, Task, Scheduler


def test_generate_daily_plan_respects_time_available():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)

    pet.add_task(Task(description="Morning walk", duration=30, priority="high"))
    pet.add_task(Task(description="Feeding", duration=10, priority="high"))
    pet.add_task(Task(description="Grooming", duration=40, priority="low"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=45)

    assert sum(task.duration for task in plan) <= 45
    assert all(not task.completed for task in plan)


def test_generate_daily_plan_prioritizes_high_priority_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Whiskers", species="Cat")
    owner.add_pet(pet)

    pet.add_task(Task(description="Playtime", duration=15, priority="low"))
    pet.add_task(Task(description="Litter box cleaning", duration=5, priority="medium"))
    pet.add_task(Task(description="Vet meds", duration=5, priority="high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=5)

    assert len(plan) == 1
    assert plan[0].description == "Vet meds"
