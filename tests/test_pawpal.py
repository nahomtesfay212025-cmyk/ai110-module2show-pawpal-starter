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


def test_generate_daily_plan_zero_time_available_returns_empty():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Walk", duration=10, priority="high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=0)

    assert plan == []


def test_generate_daily_plan_negative_time_available_returns_empty():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Walk", duration=10, priority="high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=-5)

    assert plan == []


def test_generate_daily_plan_exact_duration_fit():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Walk", duration=30, priority="high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=30)

    assert len(plan) == 1
    assert plan[0].description == "Walk"


def test_generate_daily_plan_stable_order_for_equal_priority():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="First", duration=5, priority="medium"))
    pet.add_task(Task(description="Second", duration=5, priority="medium"))
    pet.add_task(Task(description="Third", duration=5, priority="medium"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=15)

    assert [t.description for t in plan] == ["First", "Second", "Third"]


def test_sort_by_priority_unknown_priority_sorts_last():
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        Task(description="Weird", duration=5, priority="urgent"),
        Task(description="High", duration=5, priority="high"),
        Task(description="Low", duration=5, priority="low"),
    ]

    sorted_tasks = scheduler.sort_by_priority(tasks)

    assert [t.description for t in sorted_tasks] == ["High", "Low", "Weird"]


def test_sort_by_time_orders_ascending():
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        Task(description="Evening", duration=5, preferred_time="18:00"),
        Task(description="Morning", duration=5, preferred_time="07:00"),
        Task(description="Noon", duration=5, preferred_time="12:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [t.description for t in sorted_tasks] == ["Morning", "Noon", "Evening"]


def test_sort_by_time_unpadded_hours_sort_lexicographically():
    """Documents current behavior: preferred_time is compared as a raw string,
    so unpadded single-digit hours sort after any two-digit hour."""
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        Task(description="Ten AM", duration=5, preferred_time="10:00"),
        Task(description="Nine AM", duration=5, preferred_time="9:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    # "10:00" < "9:00" as strings, even though 9am is earlier in the day.
    assert [t.description for t in sorted_tasks] == ["Ten AM", "Nine AM"]


def test_sort_by_time_untimed_tasks_sort_last():
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)

    tasks = [
        Task(description="Untimed", duration=5, preferred_time=None),
        Task(description="Timed", duration=5, preferred_time="08:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [t.description for t in sorted_tasks] == ["Timed", "Untimed"]


def test_complete_task_daily_spawns_next_occurrence():
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(description="Walk", duration=10, frequency="daily")
    pet.add_task(task)

    pet.complete_task(task)

    assert task.completed is True
    pending = pet.pending_tasks()
    assert len(pending) == 1
    assert pending[0].description == "Walk"
    assert pending[0].completed is False


def test_complete_task_weekly_spawns_next_occurrence():
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(description="Groom", duration=20, frequency="weekly")
    pet.add_task(task)

    pet.complete_task(task)

    assert len(pet.pending_tasks()) == 1


def test_complete_task_non_recurring_frequency_does_not_spawn():
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(description="Vet visit", duration=60, frequency="once")
    pet.add_task(task)

    pet.complete_task(task)

    assert task.completed is True
    assert pet.pending_tasks() == []
    assert len(pet.tasks) == 1


def test_complete_task_called_again_on_already_completed_task_still_spawns():
    """Documents current behavior: complete_task has no guard against being
    called on an already-completed task, so re-calling it spawns another
    occurrence. This is a candidate bug worth revisiting."""
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(description="Walk", duration=10, frequency="daily")
    pet.add_task(task)

    pet.complete_task(task)
    pet.complete_task(task)

    assert len(pet.tasks) == 3
    assert len(pet.pending_tasks()) == 2


def test_next_occurrence_is_independent_copy():
    task = Task(description="Walk", duration=10, frequency="daily")
    task.mark_complete()

    next_task = task.next_occurrence()
    next_task.mark_complete()

    assert task.completed is True
    assert next_task is not task


def test_detect_conflicts_flags_shared_time_across_pets():
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Walk", duration=10, preferred_time="08:00"))
    cat.add_task(Task(description="Feed", duration=5, preferred_time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_flags_same_pet_double_booking():
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    owner.add_pet(dog)

    dog.add_task(Task(description="Walk", duration=10, preferred_time="08:00"))
    dog.add_task(Task(description="Brush", duration=5, preferred_time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1


def test_detect_conflicts_ignores_completed_tasks():
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    walk = Task(description="Walk", duration=10, preferred_time="08:00")
    walk.mark_complete()
    dog.add_task(walk)
    cat.add_task(Task(description="Feed", duration=5, preferred_time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert warnings == []


def test_detect_conflicts_ignores_untimed_tasks():
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    owner.add_pet(dog)

    dog.add_task(Task(description="Walk", duration=10, preferred_time=None))
    dog.add_task(Task(description="Brush", duration=5, preferred_time=None))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert warnings == []


def test_detect_conflicts_reports_three_way_conflict():
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    bird = Pet(name="Tweety", species="Bird")
    owner.add_pet(dog)
    owner.add_pet(cat)
    owner.add_pet(bird)

    dog.add_task(Task(description="Walk", duration=10, preferred_time="08:00"))
    cat.add_task(Task(description="Feed", duration=5, preferred_time="08:00"))
    bird.add_task(Task(description="Clean cage", duration=5, preferred_time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert warnings[0].count("'s") == 3


def test_filter_tasks_unknown_pet_name_returns_empty():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    pet.add_task(Task(description="Walk", duration=10))

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(pet_name="Nonexistent")

    assert result == []


def test_filter_tasks_completed_none_returns_all():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    done = Task(description="Walk", duration=10)
    done.mark_complete()
    pending = Task(description="Feed", duration=5)
    pet.add_task(done)
    pet.add_task(pending)

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(completed=None)

    assert len(result) == 2


def test_plan_by_pet_attributes_duplicate_tasks_to_correct_pet():
    """Task equality is value-based (dataclass default), so two pets with an
    identical task must still each get exactly their own copy in the plan."""
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Walk", duration=10, priority="high"))
    cat.add_task(Task(description="Walk", duration=10, priority="high"))

    scheduler = Scheduler(owner)
    grouped = scheduler.plan_by_pet(time_available=20)

    assert len(grouped["Biscuit"]) == 1
    assert len(grouped["Whiskers"]) == 1


def test_remove_task_with_duplicate_removes_only_one():
    pet = Pet(name="Biscuit", species="Dog")
    task_a = Task(description="Walk", duration=10, priority="high")
    task_b = Task(description="Walk", duration=10, priority="high")
    pet.add_task(task_a)
    pet.add_task(task_b)

    pet.remove_task(task_a)

    assert len(pet.tasks) == 1
