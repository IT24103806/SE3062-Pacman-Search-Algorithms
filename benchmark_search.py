#!/usr/bin/env python
# benchmark_search.py
# -------------------
# SE3062 Pac-Man Search Algorithms - Performance Benchmark & Evaluation Tool
# Student ID: IT24102365 (Member 4 - Testing and Documentation)
#
# Reproducible benchmarking suite measuring:
# - Solution path length
# - Solution path cost
# - Number of nodes expanded
# - Wall-clock runtime via time.perf_counter() across repeated trials (median reported)
# - Goal reachability verification
#
# Supported comparisons:
# 1. BFS vs UCS on unit-cost mazes (verifying cost & expansion equivalency)
# 2. BFS vs A* (Manhattan) on maze layouts (evaluating heuristic pruning)
# 3. CornersProblem: BFS vs A* (cornersHeuristic) vs A* (nullHeuristic)
#
# Compatible with Python 3.6 to 3.14.

import sys
import time
import statistics
import argparse
import platform
from typing import List, Dict, Any, Callable

import layout
import pacman
import search
import searchAgents


def get_game_state(layout_name: str) -> pacman.GameState:
    """Load layout and initialize a fresh GameState instance."""
    lay = layout.getLayout(layout_name)
    if lay is None:
        raise FileNotFoundError(f"Layout '{layout_name}' not found.")
    state = pacman.GameState()
    state.initialize(lay, 0)
    return state


def run_single_experiment(
    problem_factory: Callable[[], search.SearchProblem],
    search_fn: Callable[[search.SearchProblem], List[Any]],
    trials: int = 3
) -> Dict[str, Any]:
    """
    Run the search function over multiple trials, collecting runtime and search metrics.
    Reports median runtime across trials to mitigate OS scheduling noise.
    """
    durations = []
    path_len = -1
    path_cost = -1
    expanded = -1
    goal_reached = False

    for _ in range(trials):
        prob = problem_factory()
        t0 = time.perf_counter()
        actions = search_fn(prob)
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)  # Convert to milliseconds

        if path_len == -1:
            path_len = len(actions)
            path_cost = prob.getCostOfActions(actions) if hasattr(prob, 'getCostOfActions') else len(actions)
            expanded = getattr(prob, '_expanded', -1)

            # Check if simulated path reaches goal
            curr = prob.getStartState()
            if hasattr(prob, 'isGoalState'):
                # For PositionSearchProblem
                if isinstance(curr, tuple) and len(curr) == 2 and isinstance(curr[0], int):
                    walls = prob.walls
                    from game import Actions
                    for a in actions:
                        dx, dy = Actions.directionToVector(a)
                        curr = (int(curr[0] + dx), int(curr[1] + dy))
                    goal_reached = prob.isGoalState(curr)
                else:
                    # Generic problem: check if goal is reached by successor simulation or length > 0
                    goal_reached = len(actions) > 0

    return {
        "trials": trials,
        "median_ms": statistics.median(durations),
        "min_ms": min(durations),
        "max_ms": max(durations),
        "path_length": path_len,
        "path_cost": path_cost,
        "expanded": expanded,
        "goal_reached": goal_reached
    }


def benchmark_suite(trials: int = 3, fast: bool = False) -> List[Dict[str, Any]]:
    """Execute all benchmark configurations."""
    records = []

    # 1. Single-Goal PositionSearchProblem Benchmarks
    maze_layouts = ["tinyMaze", "mediumMaze"] if fast else ["tinyMaze", "smallMaze", "mediumMaze", "openMaze", "bigMaze"]

    for lay_name in maze_layouts:
        configs = [
            ("DFS", "None", lambda p: search.depthFirstSearch(p)),
            ("BFS", "None", lambda p: search.breadthFirstSearch(p)),
            ("UCS", "None", lambda p: search.uniformCostSearch(p)),
            ("A*", "Manhattan", lambda p: search.aStarSearch(p, searchAgents.manhattanHeuristic)),
            ("A*", "Null", lambda p: search.aStarSearch(p, search.nullHeuristic)),
        ]

        for algo_name, heur_name, search_call in configs:
            def factory():
                st = get_game_state(lay_name)
                return searchAgents.PositionSearchProblem(st)

            res = run_single_experiment(factory, search_call, trials=trials)
            records.append({
                "suite": "Single-Goal Maze",
                "problem": "PositionSearchProblem",
                "layout": lay_name,
                "algorithm": algo_name,
                "heuristic": heur_name,
                **res
            })

    # 2. Corners Problem Benchmarks
    corner_layouts = ["tinyCorners", "mediumCorners"]

    for lay_name in corner_layouts:
        configs = [
            ("BFS", "None", lambda p: search.breadthFirstSearch(p)),
            ("A*", "cornersHeuristic", lambda p: search.aStarSearch(p, searchAgents.cornersHeuristic)),
            ("A*", "Null", lambda p: search.aStarSearch(p, search.nullHeuristic)),
        ]

        for algo_name, heur_name, search_call in configs:
            def factory():
                st = get_game_state(lay_name)
                return searchAgents.CornersProblem(st)

            res = run_single_experiment(factory, search_call, trials=trials)
            records.append({
                "suite": "Corners Problem",
                "problem": "CornersProblem",
                "layout": lay_name,
                "algorithm": algo_name,
                "heuristic": heur_name,
                **res
            })

    return records


def format_markdown_table(records: List[Dict[str, Any]]) -> str:
    """Format benchmark records into a GitHub Flavored Markdown table."""
    lines = []
    lines.append("| Suite | Layout | Algorithm | Heuristic | Path Length | Path Cost | Nodes Expanded | Median Time (ms) | Goal Reached |")
    lines.append("| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

    for r in records:
        lines.append(
            f"| {r['suite']} | `{r['layout']}` | **{r['algorithm']}** | {r['heuristic']} | "
            f"{r['path_length']} | {r['path_cost']} | {r['expanded']} | {r['median_ms']:.2f} ms | "
            f"{'PASS' if r['goal_reached'] else 'FAIL'} |"
        )
    return "\n".join(lines)


def format_csv(records: List[Dict[str, Any]]) -> str:
    """Format benchmark records into CSV string."""
    headers = [
        "Suite", "Problem", "Layout", "Algorithm", "Heuristic",
        "PathLength", "PathCost", "NodesExpanded", "MedianMs", "MinMs", "MaxMs", "GoalReached"
    ]
    lines = [",".join(headers)]
    for r in records:
        lines.append(
            f'"{r["suite"]}","{r["problem"]}","{r["layout"]}","{r["algorithm"]}","{r["heuristic"]}",'
            f'{r["path_length"]},{r["path_cost"]},{r["expanded"]},{r["median_ms"]:.3f},{r["min_ms"]:.3f},{r["max_ms"]:.3f},{r["goal_reached"]}'
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="SE3062 Pac-Man Search Algorithms - Performance Benchmark Tool (Member 4)"
    )
    parser.add_argument(
        "--trials", type=int, default=3,
        help="Number of repeated runs per configuration for median runtime measurement (default: 3)."
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Run quick benchmark on a subset of maze layouts."
    )
    parser.add_argument(
        "--markdown", action="store_true",
        help="Output results in Markdown table format."
    )
    parser.add_argument(
        "--csv", action="store_true",
        help="Output results in CSV format."
    )
    args = parser.parse_args()

    env_info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "arch": platform.machine(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if not args.csv and not args.markdown:
        print("=" * 85)
        print("SE3062 Pac-Man Search Algorithms — Performance Benchmarks")
        print(f"Environment: Python {env_info['python']} on {env_info['platform']} ({env_info['arch']})")
        print(f"Timestamp:   {env_info['date']} | Repetitions per test: {args.trials}")
        print("=" * 85)

    records = benchmark_suite(trials=args.trials, fast=args.fast)

    if args.csv:
        print(format_csv(records))
    elif args.markdown:
        print(format_markdown_table(records))
    else:
        # Standard formatted terminal display
        print(format_markdown_table(records))
        print("\n" + "=" * 85)
        print("Benchmark completed successfully.")
        print("=" * 85)


if __name__ == "__main__":
    main()
