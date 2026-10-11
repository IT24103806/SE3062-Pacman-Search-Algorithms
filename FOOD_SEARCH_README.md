# Q7 - Food Search: implementation, run guide and viva notes

## Scope
Your assigned Food Search task corresponds to Q7, "Eating All The Dots:
Food Heuristic". Implemented function: foodHeuristic in searchAgents.py.
FoodSearchProblem and AStarFoodSearchAgent were already supplied.

The uploaded starter also had an empty aStarSearch in search.py.
A working Q4 implementation is included ONLY as the dependency needed to run
Q7. Q1-Q3, Q5-Q6 and the unassigned Q8 starter remain unfinished.
This package completes Food Search, not the whole group's assignment.

## Run on Windows
Use Python 3.11 (assignment supports 3.9-3.11). Extract the ZIP, open the search
folder in VS Code and open its terminal. With Conda, the assignment setup is:

    conda create -n cs188 python=3.11
    conda activate cs188
    pip install numpy matplotlib

Run the tests (includes dependency Q4 automatically):

    python autograder.py -q q7 --no-graphics

Show the graphical demonstration:

    python pacman.py -l trickySearch -p AStarFoodSearchAgent

For a smaller demonstration:

    python pacman.py -l tinySearch -p AStarFoodSearchAgent

For a terminal-only demonstration:

    python pacman.py -l trickySearch -p AStarFoodSearchAgent -q

If python is unavailable but the Windows launcher exists, use py -3.11
instead of python. A graphical run needs Tkinter/Tk and a desktop display.

## Verified results
Actually executed in the supplied environment using Python 3.12.14:
- Q4 dependency: all six supplied tests pass; raw score 3/3.
- Q7: all 17 heuristic cases and the trickySearch grading case pass.
- trickySearch expanded nodes: 4,137.
- trickySearch solution cost: 60 moves; game won; score 570.
- Raw Q7 score: 5/4, because the bundled Berkeley grader has an additional
  7,000-node bonus threshold. This is not the assignment's mark scale.
- The assignment PDF's 8/8 performance criterion is at most 9,000 nodes.
  4,137 meets that criterion; final marks are determined by your lecturer.

Actual terminal logs are in evidence/. The GUI was not tested in this headless
environment. Run locally to capture a genuine autograder screenshot for the
group report. Do not present terminal log files as screenshots.

## How the heuristic works
State = (Pacman's position, remaining-food Grid).
Goal = no food dots remain.
h(state) = maximum exact maze distance from Pacman to any remaining food.

For each food coordinate, a BFS computes distances to every reachable open
cell, using util.Queue as required. These maps are cached in
problem.heuristicInfo["foodDistanceMaps"], scoped to that problem.
Subsequent evaluations read the distances without repeating BFS.

This BFS is inside the heuristic; the outer solution search is A* using
util.PriorityQueue with f = g + h. No dependency on an unfinished search.bfs
implementation is introduced. No walls, food grids or expanded counters are
modified by the heuristic.

## Why it is admissible and consistent
Admissible: every solution must reach every remaining dot, including the
farthest one. Its total cost cannot be less than that dot's shortest distance.

Consistent: for a one-step move p -> p', any uneaten dot f satisfies
d(p,f) <= 1 + d(p',f). Taking the maximum preserves this inequality.
If the move eats a dot, that dot was at distance 1 before the move, so its
contribution also satisfies 1 <= 1 + h(next). Thus h(s) <= 1 + h(next).
The empty-food goal explicitly returns zero; values are nonnegative.
Unreachable food has infinite distance, correctly indicating no finite solution.

With F original food dots and V walkable cells, cached distance maps take
O(FV) memory and O(F(V+E)) total BFS preprocessing work; each later evaluation
also scans the food Grid via asList and looks up each remaining dot.

## Report paragraph (under 200 words)
For Q7, we implemented foodHeuristic in searchAgents.py for the provided
FoodSearchProblem. A state contains Pacman's position and the remaining food
grid. The heuristic returns the maximum shortest maze distance from Pacman
to any remaining food dot. Exact distances are computed by breadth-first
search using util.Queue, respecting walls, and cached in problem.heuristicInfo
to avoid repeated searches. When no food remains, the heuristic returns zero.
It is admissible because every complete solution must reach the farthest
remaining dot. It is consistent because a legal move changes the distance
to any uneaten dot by at most one; a dot eaten on that move was one step away.
AStarFoodSearchAgent uses this estimate with A* priority g+h. All supplied Q7
tests passed. On trickySearch, A* found a 60-step solution while expanding
4,137 nodes, satisfying the assignment's threshold of at most 9,000 nodes.
The provided autograder prints 5/4 due to its additional bonus threshold;
the course rubric separately allocates eight marks to Q7.

## Merge into the group's project
1. Copy only the foodHeuristic function into the group's searchAgents.py.
   All of its logic is inside that function; no new imports are needed.
2. Keep your teammates' CornersProblem, cornersHeuristic and other changes.
   Do not overwrite their complete searchAgents.py with this starter-based file.
3. If the team already implemented aStarSearch, use their version and run Q7.
   Otherwise the included aStarSearch provides the needed implementation.
4. Run the Q7 tests after merging and capture the output.
5. In your own group repository, commit your real changes under your identity,
   for example: feat(q7): add cached maze-distance food heuristic
   No remote repository or commits were created by this delivery.

## Submission checklist from the assignment
- Group PDF: one <=200-word explanation per Q1-Q7, edited functions, actual
  autograder screenshots, repository URL, genuine contribution screenshots,
  member names/IDs/tasks, and AI usage declaration with exact prompts.
- Final code ZIP: ONLY the group's completed search.py and searchAgents.py,
  named using the group ID. This full runnable ZIP is a working package,
  not the final two-file portal submission.
- Merge and finish the other members' work before submitting the group files.
- Everyone needs to understand all algorithms for the individual viva.

## AI usage declaration to adapt truthfully
ChatGPT was used to inspect the assignment and starter project, implement the
Food Search heuristic and supporting A* dependency, run the supplied tests,
and draft explanatory notes. The exact user prompt was:
"Assiment ek hodata kiyawanna , mage part ek food search , mage part ek kerannako"
Add any subsequent prompts and describe your own review and changes accurately.

## Viva quick answers
- What is your part? Q7: an admissible, consistent heuristic for collecting all food.
- What is g? Cost of the path already travelled.
- What is h? A lower bound on the cost still required.
- What is f? g+h, used as A*'s priority.
- Why not add every food distance? That can double-count shared travel and overestimate.
- Why maze distance? It accounts for walls, unlike Manhattan distance.
- Why BFS? Each legal maze move costs one, so BFS gives shortest distances.
- Why cache? The walls do not change during this search.
- Does h give the full remaining tour cost? No, only a lower bound.
- Why store the food Grid? Same position with different remaining food is a different state.
- Does zero food return zero? Yes.
- Can closest-dot greedy replace this? It need not find the globally shortest full tour.
- Which data structures? util.Queue for distance BFS; util.PriorityQueue for A*;
  dictionaries for distance caches and best path costs.
- What changed besides Q7? Only aStarSearch, as the missing dependency.
- Evidence? 4,137 expansions, 60 moves, all bundled Q7 tests passed.

Original project attribution: UC Berkeley Pacman AI Projects,
http://ai.berkeley.edu. Original license notices are retained in all source files.
