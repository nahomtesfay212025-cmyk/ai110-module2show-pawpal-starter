import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species))

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into your scheduler.")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign task to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                description=task_title,
                duration=int(duration),
                priority=priority,
                preferred_time=preferred_time or None,
            )
        )

    scheduler = Scheduler(owner)

    if owner.all_tasks():
        st.write("Current tasks (sorted by preferred time):")
        sorted_tasks = scheduler.sort_by_time(owner.all_tasks())
        pet_by_task_id = {id(t): pet.name for pet in owner.pets for t in pet.tasks}
        st.table(
            [
                {
                    "pet": pet_by_task_id[id(task)],
                    "task": task.description,
                    "duration_minutes": task.duration,
                    "priority": task.priority,
                    "preferred_time": task.preferred_time or "-",
                    "completed": task.completed,
                }
                for task in sorted_tasks
            ]
        )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts detected.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan using the Scheduler.")

time_available = st.number_input("Time available (minutes)", min_value=1, max_value=1440, value=60)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(time_available=int(time_available))
    plan_by_priority = scheduler.sort_by_priority(plan)

    if plan_by_priority:
        used_time = sum(t.duration for t in plan_by_priority)
        st.success(f"Scheduled {len(plan_by_priority)} task(s), using {used_time} of {int(time_available)} minutes.")

        st.write("Today's Schedule (priority order):")
        st.table(
            [
                {
                    "task": t.description,
                    "duration_minutes": t.duration,
                    "priority": t.priority,
                    "preferred_time": t.preferred_time or "-",
                }
                for t in plan_by_priority
            ]
        )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
    else:
        st.info("No tasks fit in the available time.")
