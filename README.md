# Meeting Scheduler Verification with Z3

A small program that uses the Z3 SMT solver to find a meeting time that works for everyone — and to prove when no such time exists.

## How to run

**Requirements:** Python 3.8+

```bash
pip install z3-solver
python3 scheduler.py
```

That's it. No config, no extra files. The output shows two scenarios: one where the solver finds a valid slot, and one where it proves scheduling is impossible.

---

## The problem

Four people — Alice, Bob, Carol, Dave — need to find one shared meeting slot out of five options: Monday 10:00, Monday 14:00, Tuesday 10:00, Tuesday 14:00, and Wednesday 10:00.

Everyone has conflicts:

- **Alice** is unavailable Monday 14:00 and Wednesday 10:00
- **Bob** is unavailable Monday 10:00
- **Carol** is unavailable Tuesday 14:00 and Wednesday 10:00
- **Dave** is unavailable Monday 10:00 and Monday 14:00

On top of that, there's a rule that meetings can't happen on Wednesdays.

The question is: is there any slot where all four are free?

---

## How the problem is formalized

Each time slot becomes a boolean variable in Z3 — `True` means the meeting is scheduled there, `False` means it isn't. So instead of reasoning about calendars and times, the problem becomes a question about satisfying a set of logical constraints.

The constraints map directly to the real-world requirements:

- **Exactly one slot must be chosen** — encoded as "at least one is true" (`Or` of all slots) plus "no two are true at the same time" (pairwise `Not(And(a, b))` for every pair)
- **Participant unavailability** — if someone is busy at a given slot, that slot must be `False`, encoded as `Not(slot)`
- **Wednesday rule** — same thing, `Not(wed_10)`

After all constraints are added, we call `solver.check()`. If it returns `sat`, the solver also gives us a model — an assignment of True/False to each variable — and we can read off which slot was picked. If it returns `unsat`, the constraints are contradictory and no valid schedule exists.

---

## Why Z3 and not something else

The most obvious alternative is just looping through all five slots manually and checking each one against everyone's availability. For five slots and four people that's trivial to do by hand. But that approach doesn't scale: with 50 people, 30 slots, and room/equipment constraints, brute force gets messy fast.

Z3 (and SMT solvers in general) are built exactly for this kind of constraint reasoning. You describe *what* needs to be true and the solver figures out *how* to satisfy it. The code ends up looking almost like a direct translation of the problem statement, which makes it easy to read and extend.

Other reasonable approaches:

- **Constraint programming** (OR-Tools, python-constraint) — similar idea, good for larger scheduling problems, but more setup overhead for a small example like this
- **Integer linear programming** (PuLP, scipy) — works well when you need to optimize something (e.g. minimize travel time), overkill when you just want any valid assignment
- **Prolog** — naturally expressive for constraint problems, but less common and harder to integrate with modern tooling
- **Manual search** — fine for five slots, but gives you no proof of unsatisfiability; you can miss cases

The Z3 approach is the right level of complexity here: it's concise, it handles both SAT and UNSAT cleanly, and the `unsat` result is an actual formal proof that no solution exists — not just "I checked and didn't find one."

---

## Steps of the solution

**1. Declare boolean variables for each slot**

Each slot gets its own Z3 `Bool`. This is the encoding step — real-world concepts (time slots) become formal symbols the solver can reason about.

**2. Add the cardinality constraint**

We force exactly one slot to be selected. Without this, the solver could technically set all variables to `False` and call that a valid solution (no meeting scheduled = no conflicts), or pick multiple slots at once. The `Or` + pairwise `Not(And(...))` pattern handles this.

**3. Add unavailability constraints**

For each person and each slot they can't attend, we add `Not(slot)`. Adding the same constraint twice (e.g. `Not(wed_10)` for both Alice and Carol) doesn't cause any issues — Z3 just ignores duplicates.

**4. Call solver.check()**

This is where Z3 does the actual work. It searches for an assignment of True/False to all variables that satisfies every constraint simultaneously.

**5. Read the result**

If `sat`: extract the model and find which variable is `True`. That's the meeting slot.
If `unsat`: report that scheduling is impossible. This result is mathematically guaranteed — no assignment could satisfy all constraints.

The second scenario in the code demonstrates `unsat` by adding one extra constraint (`Not(tue_10)`), which blocks the only slot that survived all the previous constraints.

---

## Other problems you could solve this way

The same pattern — encode choices as booleans, add constraints, let Z3 find a valid assignment or prove none exists — applies to a lot of problems:

- **Exam scheduling** — assign exams to rooms and time slots such that no student has two exams at the same time
- **Resource allocation** — assign workers to shifts given their availability and required headcount per shift
- **Sudoku / puzzle solving** — constraints encode the rules, Z3 finds the solution
- **N-queens problem** — place N queens on an N×N board with no two attacking each other
- **Software verification** — check whether a program can reach a bad state (buffer overflow, null dereference) by encoding program paths as constraints
- **Security protocol verification** — model a communication protocol as a set of logical rules and check whether an attacker can violate a security property
- **Circuit equivalence** — verify that two different circuit implementations produce identical outputs for all inputs

In all these cases the core idea is the same: express the problem as a satisfiability query, hand it to the solver, and either get a solution or a proof that none exists.
