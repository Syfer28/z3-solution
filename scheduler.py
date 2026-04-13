# Meeting scheduler verification using Z3
# 4 people, 5 slots, find a time that works for everyone

from z3 import Bool, Solver, Or, Not, And, sat, unsat


def section(title: str) -> None:
    print(f"\n{'═' * 58}")
    print(f"  {title}")
    print(f"{'═' * 58}")


def solve_meeting(extra_constraints: list = None, label: str = "") -> None:
    """
    Runs the Z3 solver for the meeting scheduling problem.

    extra_constraints: optional list of Z3 constraints (used for UNSAT demo).
    label: scenario name shown in the output.
    """
    section(label)

    # One boolean per slot — True means the meeting is scheduled there
    mon_10 = Bool("Monday_10:00")
    mon_14 = Bool("Monday_14:00")
    tue_10 = Bool("Tuesday_10:00")
    tue_14 = Bool("Tuesday_14:00")
    wed_10 = Bool("Wednesday_10:00")

    all_slots = [mon_10, mon_14, tue_10, tue_14, wed_10]

    slot_name = {
        mon_10: "Monday    10:00",
        mon_14: "Monday    14:00",
        tue_10: "Tuesday   10:00",
        tue_14: "Tuesday   14:00",
        wed_10: "Wednesday 10:00",
    }

    solver = Solver()
    print("\n  Adding constraints:")

    # Exactly one slot must be picked.
    # at-least-one: disjunction of all slots
    solver.add(Or(all_slots))
    # at-most-one: no two slots can both be true
    for i in range(len(all_slots)):
        for j in range(i + 1, len(all_slots)):
            solver.add(Not(And(all_slots[i], all_slots[j])))
    print("  [+] Exactly one slot selected (at-least-one + at-most-one)")

    # Alice is busy on Monday 14:00 and Wednesday 10:00
    solver.add(Not(mon_14))
    solver.add(Not(wed_10))
    print("  [+] Alice:  unavailable Mon 14:00, Wed 10:00")

    # Bob is busy on Monday 10:00
    solver.add(Not(mon_10))
    print("  [+] Bob:    unavailable Mon 10:00")

    # Carol is busy on Tuesday 14:00 and Wednesday 10:00
    solver.add(Not(tue_14))
    solver.add(Not(wed_10))   # duplicate is fine, Z3 handles it
    print("  [+] Carol:  unavailable Tue 14:00, Wed 10:00")

    # Dave is busy on Monday 10:00 and Monday 14:00
    solver.add(Not(mon_10))
    solver.add(Not(mon_14))
    print("  [+] Dave:   unavailable Mon 10:00, Mon 14:00")

    # Company policy: no meetings on Wednesdays
    solver.add(Not(wed_10))
    print("  [+] Policy: no Wednesday meetings")

    if extra_constraints:
        for constraint in extra_constraints:
            solver.add(constraint)
            print(f"  [+] Extra constraint: {constraint}")

    print("\n  Running solver.check()...")
    result = solver.check()

    print()
    if result == sat:
        model = solver.model()
        print("  Result: SAT — solution found!\n")
        print("  Slot status:")
        chosen = None
        for slot in all_slots:
            # model[slot] returns the assigned boolean value
            is_chosen = bool(model[slot])
            marker = "  >>>" if is_chosen else "     "
            status  = "SELECTED" if is_chosen else "--------"
            print(f"  {marker}  {slot_name[slot]}   {status}")
            if is_chosen:
                chosen = slot_name[slot]
        print()
        print(f"  Meeting scheduled for: {chosen}")

    elif result == unsat:
        print("  Result: UNSAT — no solution exists!\n")
        print("  There is no time slot where all four participants")
        print("  are available. Scheduling is impossible.")

    else:
        # shouldn't happen for a problem this small
        print("  Result: UNKNOWN")


# --- Scenario 1: normal case, expect SAT ---
solve_meeting(
    label="Scenario 1 — find a slot that works for everyone"
)

# --- Scenario 2: block the only valid slot, expect UNSAT ---
# Tuesday 10:00 is the only slot that survives all constraints above.
# Adding one more blocker leaves nothing valid.
tue_10 = Bool("Tuesday_10:00")  # same Z3 variable as inside the function

solve_meeting(
    extra_constraints=[Not(tue_10)],
    label="Scenario 2 — UNSAT: Tuesday 10:00 also blocked"
)

print()
