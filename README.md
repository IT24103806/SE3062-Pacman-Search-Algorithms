# SE3062 Pac-Man Search Algorithms

Comprehensive implementation, verification, and performance evaluation of classical state-space search algorithms and heuristics for the university group assignment **SE3062 — Pac-Man Search Algorithms**.

Based on the UC Berkeley CS188 Pac-Man AI Projects framework, adapted for collaborative group development, rigorous testing, and integration.

---

## 1. Group Member Allocation & Scope

| Member | Student ID | Task Allocation & Question Scope | Dedicated Git Branch | Integration Status |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | `IT24104048` | **Q1–Q4:** DFS, BFS, UCS, and A* Search in `search.py` | `IT24104048-search-algorithms` | Integrated & Verified (12/12 pts) |
| **Member 2** | `IT24103806` | **Q5–Q6:** Corners Problem & Admissible Corners Heuristic in `searchAgents.py` | `IT24103806-corners` | Integrated & Verified (6/6 pts) |
| **Member 3** | `IT24510004` | **Q7–Q8:** Food Heuristic (`foodHeuristic`) & Closest Dot Search (`findPathToClosestDot`) | `IT24510004-food-search` | Integrated & Verified |
| **Member 4** | `IT24102365` | **Testing, Validation, Benchmarking & Documentation:** 29-Test Regression Suite, Test Runner, Benchmark Tool, Traceability Report | `IT24102365-testing-documentation` | Completed & Verified (100% QA scope) |

---

## 2. Repository Architecture

```text
SE3062-Pacman-Search-Algorithms/
├── search.py                  # Core search algorithms: DFS, BFS, UCS, A* (Member 1)
├── searchAgents.py            # Search problems and heuristics: CornersProblem, cornersHeuristic, foodHeuristic (Member 2 & 3)
├── pacman.py                  # Pac-Man simulation driver and main game loop
├── util.py                    # Core data structures: Stack, Queue, PriorityQueue
├── game.py                    # Game logic, state representations, Actions, Directions, Grid
├── layout.py                  # Maze layout parser and loader
├── layouts/                   # Maze configuration files (*.lay)
│   ├── tinyMaze.lay
│   ├── smallMaze.lay
│   ├── mediumMaze.lay
│   ├── bigMaze.lay
│   ├── openMaze.lay
│   ├── tinyCorners.lay
│   ├── mediumCorners.lay
│   └── trickyClassic.lay
├── autograder.py              # Official Berkeley autograder runner
├── grading.py                 # Grading framework and scoring logic
├── testcases/                 # Official autograder fixtures (q1 through q8)
├── test_member4_suite.py      # Standalone 29-test unit, graph, legality & heuristic math suite (Member 4)
├── benchmark_search.py        # Reproducible performance benchmark & evaluation suite (Member 4)
├── run_tests.py               # Portable automated test runner & test coordinator (Member 4)
├── TESTING_REPORT.md          # Comprehensive testing, traceability, benchmark & QA report (Member 4)
└── README.md                  # Project documentation & execution guide
```

---

## 3. Environment & Prerequisites

- **Python Version:** Python 3.6 through 3.14 (Verified and tested on `Python 3.14.6` 64-bit).
- **Dependencies:** Python Standard Library only (`unittest`, `subprocess`, `argparse`, `sys`, `time`, `statistics`, `platform`). No external pip packages required.
- **Operating Systems:** Fully portable across Windows, Linux, and macOS.

To verify Python syntax and compilation without executing tests:
```bash
python -m py_compile search.py searchAgents.py
```

---

## 4. Running Tests

Member 4 provides a multi-tiered automated verification package that runs independently of any graphical environment.

### 4.1 Automated Test Runner (`run_tests.py`)
`run_tests.py` is the single entry point for all project testing. It executes bytecode compilation checks, official autograder questions, and Member 4's standalone suite.

```bash
# 1. Run baseline integrated checks (Q1-Q6 + Member 4 regression suite)
python run_tests.py

# 2. Run all questions (Q1 through Q8) including Member 3's tasks
python run_tests.py --all
# (or use alias)
python run_tests.py --q1-q8

# 3. Run ONLY the 29-test Member 4 regression suite
python run_tests.py --suite-only

# 4. Run ONLY the official autograder for integrated questions (Q1-Q6)
python run_tests.py --q1-q6-only

# 5. Run performance benchmarks directly from the runner
python run_tests.py --benchmarks

# 6. Verbose mode (displays raw subprocess output for diagnostics)
python run_tests.py -v
```

### 4.2 Standalone Member 4 Regression Suite (`test_member4_suite.py`)
To run Member 4's deterministic 29-test unit and mathematical verification suite directly:
```bash
python test_member4_suite.py
```
This suite validates:
- **Graph Search Correctness:** DFS traversal, BFS hop optimality, UCS least-cost optimality, A* heuristic guidance on isolated deterministic mock graphs (`DummyGraphProblem`).
- **Edge Cases & Graph Topology:** Start state is goal (`[]`), unreachable/disconnected goals (`[]`), cycles and repeated state handling, zero-cost edge handling.
- **Path Legality & Invariants:** Step-by-step movement simulation ensuring Pac-Man never collides with walls, never moves out of layout boundaries, and only uses legal `Directions` actions on `tinyMaze` and `mediumMaze`.
- **CornersProblem Model:** State structure `(pos, (b0, b1, b2, b3))`, legal successor generation, visited corner tuple updates, and 28-step BFS optimality on `tinyCorners`.
- **cornersHeuristic Mathematical Properties:** Non-negativity ($h(s) \ge 0$), goal state valuation ($h(s_{goal}) = 0$), dynamic admissibility verification against true optimal cost ($h(s) \le h^*(s)$) via subproblem searches, consistency/triangle inequality ($h(s) \le c + h(s')$), and $< 1200$ node expansion limit on `mediumCorners`.
- **Food Search & Closest Dot Interfaces:** `FoodSearchProblem` state representation, food consumption on successor transition, `foodHeuristic` non-negativity and zero valuation at goal, and `AnyFoodSearchProblem` start state invariants.

### 4.3 Official Berkeley Autograder
To run individual questions via the official Berkeley autograder:
```bash
# Q1: Depth-First Search (DFS)
python autograder.py --test-directory testcases -q q1

# Q2: Breadth-First Search (BFS)
python autograder.py --test-directory testcases -q q2

# Q3: Uniform-Cost Search (UCS)
python autograder.py --test-directory testcases -q q3

# Q4: A* Search
python autograder.py --test-directory testcases -q q4

# Q5: Corners Problem
python autograder.py --test-directory testcases -q q5

# Q6: Corners Heuristic
python autograder.py --test-directory testcases -q q6

# Q7: Food Heuristic (Member 3)
python autograder.py --test-directory testcases -q q7

# Q8: Closest Dot Search (Member 3)
python autograder.py --test-directory testcases -q q8
```

---

## 5. Performance Evaluation & Benchmarking (`benchmark_search.py`)

Member 4 created `benchmark_search.py` to provide empirical performance evaluation across algorithms and maze configurations.

To execute the benchmark:
```bash
# Standard benchmark (3 repetitions per test, reports median runtime)
python benchmark_search.py

# Fast benchmark (subset of smaller layouts)
python benchmark_search.py --fast

# Generate Markdown table output
python benchmark_search.py --markdown

# Export measurements to CSV
python benchmark_search.py --csv > benchmark_results.csv
```

### Measured Performance Highlights:
- **BFS vs. UCS on Unit-Cost Mazes:** Across all 5 tested maze layouts (`tinyMaze`, `smallMaze`, `mediumMaze`, `openMaze`, `bigMaze`), BFS and UCS produce **identical** path lengths, path costs, and expanded node counts (e.g., both expand 269 nodes for length 68 on `mediumMaze`).
- **Pruning Power of A\* (Manhattan):** On `smallMaze`, A* expands only 53 nodes compared to BFS's 92 nodes (**42.4% reduction**). On `mediumMaze`, A* expands 221 nodes vs. BFS's 269 nodes (**17.8% reduction**). On `openMaze`, A* expands 535 nodes vs. BFS's 682 nodes (**21.6% reduction**).
- **Efficiency of cornersHeuristic:** On `mediumCorners`, A* with `cornersHeuristic` expands **1136 nodes** compared to **1966 nodes** for BFS / A*(Null) — achieving a **42.2% reduction in search space** and finishing well within the official 1200-node marking threshold.

---

## 6. Visual and Headless Gameplay Execution

You can run Pac-Man with graphical display or headlessly using `--quietTextGraphics` (`-q`):

### 6.1 Depth-First Search (DFS)
```bash
# Graphical display
python pacman.py -l mediumMaze -p SearchAgent

# Headless / Quiet text graphics
python pacman.py -l mediumMaze -p SearchAgent -q
```

### 6.2 Breadth-First Search (BFS)
```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs -q
```

### 6.3 Uniform-Cost Search (UCS)
```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs -q
```

### 6.4 A* Search (Manhattan Heuristic)
```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic -q
```

### 6.5 Corners Problem
```bash
# BFS on tinyCorners (optimal 28 steps)
python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem -q

# A* with cornersHeuristic on mediumCorners (optimal 106 steps, 1136 node expansions)
python pacman.py -l mediumCorners -p AStarCornersAgent -q
```

---

## 7. Quality Assurance vs. Official Assignment Scope

To ensure academic transparency and clear separation of concerns:
- **Official Assignment Scope:** Implementation of specific algorithms and heuristics requested by the problem sheets (Q1–Q4 in `search.py`, Q5–Q8 in `searchAgents.py`), evaluated via `autograder.py`.
- **Member 4 QA Engineering Scope:** Independent automated verification, deterministic unit testing on mock graphs, boundary/legality invariant validation, empirical mathematical checks of heuristic admissibility and consistency, reproducible performance benchmarking with median timing, and comprehensive technical documentation.
- **Integrity Rule:** Member 4's test scripts and benchmarks **do not modify** any search algorithms, problem formulations, or official test fixtures.

For detailed test logs, requirements traceability, baseline comparisons, defect logs, and full benchmark tables, see [TESTING_REPORT.md](TESTING_REPORT.md).
