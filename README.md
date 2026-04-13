# Meeting Scheduler Verification with Z3

A Python program that uses the Z3 SMT solver to figure out when four people can meet, and to formally prove when they can't.

## How to run

You need Python 3.8+ and one package:

```bash
pip install z3-solver
python3 scheduler.py
```

The program runs two scenarios on its own: one where it finds a valid slot, and one where it proves no valid slot exists.

## The problem

Four people need to find one shared meeting time out of five options. Everyone has days or times they can't make it, and there's also a rule that meetings can't happen on Wednesdays. The task is to find a slot where all four are free at the same time, or show that no such slot exists.

## How it's formalized

Each time slot is represented as a boolean variable in Z3. True means the meeting is scheduled there, False means it isn't. The constraints then just describe the rules: if someone is unavailable at a given slot, that slot has to be False. There's also a constraint that exactly one slot gets picked, not zero and not two.

Once all constraints are in, you call `solver.check()`. It either comes back with `sat` and a concrete assignment showing which slot works, or with `unsat`, which is a formal proof that no assignment can satisfy all the constraints at once.

## Why Z3

For five slots you could just check them by hand. But the point of using an SMT solver is that the approach generalizes: you write down the rules and the solver figures out whether they can be satisfied. You also get `unsat` as an actual guarantee, not just "I looked and didn't find anything."

The natural alternatives would be something like OR-Tools for constraint programming, or just brute force. Brute force works fine here but gives you no proof of unsatisfiability. OR-Tools is a better fit when the problem is larger or when you need to optimize something. For this size and purpose Z3 is the simplest option that still gives you the formal verification angle.

## What's happening step by step

First the code declares a boolean variable for each slot. Then it adds the cardinality constraint so exactly one slot ends up selected. After that it adds all the unavailability rules, one `Not(slot)` per conflict. Then `solver.check()` runs and either returns a model (the chosen slot) or unsat.

The second scenario adds one extra constraint blocking Tuesday 10:00, which happens to be the only slot that survives everything else. That makes the problem unsatisfiable and the solver confirms it.

## Other places where this works

The same idea applies to a lot of problems. Exam scheduling with room and student conflicts, shift assignment for workers, verifying that a piece of software can't reach a bad state, checking security protocols for vulnerabilities, solving logic puzzles like Sudoku or N-queens. Anywhere you can phrase the problem as "find an assignment that satisfies these rules, or tell me it's impossible" is a good fit for this approach.
