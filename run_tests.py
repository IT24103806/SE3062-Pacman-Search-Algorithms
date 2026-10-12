#!/usr/bin/env python
# run_tests.py
# ------------
# SE3062 Pac-Man Search Algorithms - Automated Test Runner
# Student ID: IT24102365 (Member 4 - Testing and Documentation)
#
# Portable and robust test automation script that provides a single entry point for:
# 1. Bytecode compilation checks (py_compile)
# 2. Official autograder questions (Q1 to Q6 integrated baseline, plus Q7/Q8 when requested)
# 3. Member 4 regression and heuristic verification suite (test_member4_suite.py)
# 4. Search algorithm and heuristic performance benchmarks (benchmark_search.py)
#
# Emits structured reporting, distinguishes PASS, FAIL, BLOCKED, NOT RUN,
# preserves subprocess exit codes, and prints exact commands executed.

import os
import sys
import time
import argparse
import subprocess
from typing import List, Dict, Any, Optional


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Execute command synchronously, print command line, capture stdout/stderr, return status and timing."""
    cmd_str = " ".join(cmd)
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        duration = time.time() - start_time
        return {
            "cmd": cmd_str,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration": duration,
            "error": None
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "cmd": cmd_str,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": duration,
            "error": str(e)
        }


def parse_autograder_score(output: str, question: str) -> str:
    """Extract score string like '3/3' or '0/4' from autograder output."""
    target_lower = f"### question {question.lower()}:"
    target_plain = f"Question {question}:"
    for line in output.splitlines():
        line_clean = line.strip()
        if target_lower in line_clean.lower():
            # ### Question q1: 3/3 ###
            parts = line_clean.split(":")
            if len(parts) > 1:
                return parts[1].replace("#", "").strip()
        elif line_clean.startswith(target_plain) or line_clean.startswith(f"Question {question.lower()}:"):
            parts = line_clean.split(":")
            if len(parts) > 1:
                return parts[1].strip()
    return "N/A"


def main():
    parser = argparse.ArgumentParser(
        description="SE3062 Pac-Man Search Algorithms Unified Test Runner (Member 4)"
    )
    parser.add_argument(
        "--all", "--q1-q8", dest="run_all", action="store_true",
        help="Run all tests including Q7 and Q8 (food-search tasks assigned to Member 3) and regression suite."
    )
    parser.add_argument(
        "--q1-q6-only", action="store_true",
        help="Run only the official autograder for integrated questions Q1 through Q6."
    )
    parser.add_argument(
        "--suite-only", action="store_true",
        help="Run only the Member 4 standalone regression suite (test_member4_suite.py)."
    )
    parser.add_argument(
        "--benchmarks", action="store_true",
        help="Run the performance benchmarks (benchmark_search.py)."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print raw stdout/stderr for each test subprocess."
    )
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable
    test_directory = next(
        (
            directory
            for directory in ("testcases", "test_cases")
            if os.path.isdir(os.path.join(project_root, directory))
        ),
        None
    )
    if test_directory is None:
        print("ERROR: Could not find testcases/ or test_cases/ fixture directory.")
        sys.exit(1)

    print("=" * 90)
    print("SE3062 Pac-Man Search Algorithms - Automated Test Runner")
    print(f"Interpreter: {python_exe} ({sys.version.split()[0]})")
    print(f"Working Directory: {project_root}")
    print("=" * 90)

    results = []
    has_required_failures = False

    # Mode 1: Benchmark Only
    if args.benchmarks and not args.run_all and not args.suite_only and not args.q1_q6_only:
        print("\n[*] Executing Performance Benchmarks...")
        cmd = [python_exe, "benchmark_search.py"]
        print(f"    CMD: {' '.join(cmd)}")
        bench_res = run_command(cmd, cwd=project_root)
        print(bench_res["stdout"])
        if bench_res["stderr"]:
            print(bench_res["stderr"])
        sys.exit(bench_res["exit_code"])

    # Step 1: Bytecode Compilation Check
    if not args.suite_only and not args.q1_q6_only:
        print("\n[*] Step 1: Validating Python syntax & compilation...")
        compile_cmd = [python_exe, "-m", "py_compile", "search.py", "searchAgents.py"]
        print(f"    CMD: {' '.join(compile_cmd)}")
        comp_res = run_command(compile_cmd, cwd=project_root)

        if comp_res["exit_code"] == 0:
            status = "PASS"
            detail = "search.py & searchAgents.py compiled cleanly"
        else:
            status = "FAIL"
            detail = comp_res["stderr"].strip().splitlines()[-1] if comp_res["stderr"] else "Compile error"
            has_required_failures = True

        results.append({
            "id": "COMP-01",
            "name": "Syntax Compilation",
            "member": "All Members",
            "required": True,
            "status": status,
            "detail": detail,
            "duration": comp_res["duration"]
        })
        print(f"    -> [{status}] {detail} ({comp_res['duration']:.2f}s)")

    # Step 2: Official Autograder Questions
    if not args.suite_only:
        print("\n[*] Step 2: Running Official Autograder Tests...")
        autograder_questions = [
            ("q1", "Depth-First Search (DFS)", "Member 1 (IT24104048)", True),
            ("q2", "Breadth-First Search (BFS)", "Member 1 (IT24104048)", True),
            ("q3", "Uniform-Cost Search (UCS)", "Member 1 (IT24104048)", True),
            ("q4", "A* Search", "Member 1 (IT24104048)", True),
            ("q5", "Corners Problem", "Member 2 (IT24103806)", True),
            ("q6", "Corners Heuristic", "Member 2 (IT24103806)", True),
            ("q7", "Food Heuristic", "Member 3 (IT24510004)", False),
            ("q8", "Closest Dot Search", "Member 3 (IT24510004)", False),
        ]

        for q_id, q_desc, q_member, is_req in autograder_questions:
            # Skip optional Q7/Q8 unless --all is specified
            if not is_req and not args.run_all:
                results.append({
                    "id": f"AG-{q_id.upper()}",
                    "name": q_desc,
                    "member": q_member,
                    "required": is_req,
                    "status": "NOT RUN",
                    "detail": "Excluded from baseline (use --all or --q1-q8 to run)",
                    "duration": 0.0
                })
                continue

            q_cmd = [
                python_exe, "autograder.py", "--test-directory", test_directory,
                "-q", q_id, "--no-graphics"
            ]
            print(f"    CMD: {' '.join(q_cmd)}")
            q_res = run_command(q_cmd, cwd=project_root)
            stdout = q_res["stdout"]
            score = parse_autograder_score(stdout, q_id)

            if "Method not implemented" in stdout or "raiseNotDefined" in stdout:
                status = "BLOCKED"
                detail = f"Score: {score} (Method not implemented in searchAgents.py)"
            elif q_res["exit_code"] == 0 and ("FAIL:" not in stdout or "3/3" in score or "4/4" in score or "5/4" in score):
                status = "PASS"
                detail = f"Score: {score}"
            else:
                status = "FAIL"
                detail = f"Score: {score} (Failed tests detected)"

            if is_req and status != "PASS":
                has_required_failures = True

            results.append({
                "id": f"AG-{q_id.upper()}",
                "name": q_desc,
                "member": q_member,
                "required": is_req,
                "status": status,
                "detail": detail,
                "duration": q_res["duration"]
            })
            print(f"    -> [{status}] {q_id.upper()}: {q_desc} - {detail} ({q_res['duration']:.2f}s)")

            if args.verbose:
                print("--- stdout ---")
                print(stdout)
                if q_res["stderr"]:
                    print("--- stderr ---")
                    print(q_res["stderr"])

    # Step 3: Member 4 Regression Suite
    if not args.q1_q6_only:
        print("\n[*] Step 3: Running Member 4 Regression & Heuristic Verification Suite...")
        suite_cmd = [python_exe, "test_member4_suite.py"]
        print(f"    CMD: {' '.join(suite_cmd)}")
        suite_res = run_command(suite_cmd, cwd=project_root)
        suite_out = suite_res["stdout"] + "\n" + suite_res["stderr"]

        if suite_res["exit_code"] == 0:
            status = "PASS"
            ran_line = [l for l in suite_out.splitlines() if "Ran " in l and "tests in" in l]
            summary_info = ran_line[0].strip() if ran_line else "Regression suite passed"
            detail = f"{summary_info} (All Unit, Graph, Corners, Food & Heuristic Math tests passed)"
        else:
            status = "FAIL"
            ran_line = [l for l in suite_out.splitlines() if "Ran " in l and "tests in" in l]
            summary_info = ran_line[0].strip() if ran_line else "Regression tests executed"
            fail_line = [l.strip() for l in suite_out.splitlines() if "AssertionError:" in l]
            fail_reason = fail_line[0].split("AssertionError:", 1)[1].strip() if fail_line else "Test assertion failed"
            if len(fail_reason) > 75:
                fail_reason = fail_reason[:72] + "..."
            detail = f"{summary_info} (FAIL: {fail_reason})"
            has_required_failures = True

        results.append({
            "id": "M4-SUITE",
            "name": "Regression & Verification Suite",
            "member": "Member 4 (IT24102365)",
            "required": True,
            "status": status,
            "detail": detail,
            "duration": suite_res["duration"]
        })
        print(f"    -> [{status}] Member 4 Suite - {detail} ({suite_res['duration']:.2f}s)")

        if args.verbose or status == "FAIL":
            print(suite_out)

    # Step 4: Optional Benchmarks when requested alongside other tests
    if args.benchmarks:
        print("\n[*] Step 4: Running Performance Benchmarks...")
        bench_cmd = [python_exe, "benchmark_search.py", "--fast"]
        print(f"    CMD: {' '.join(bench_cmd)}")
        bench_res = run_command(bench_cmd, cwd=project_root)
        if bench_res["exit_code"] == 0:
            status = "PASS"
            detail = "All search benchmarks completed across layouts"
        else:
            status = "FAIL"
            detail = "Benchmark execution encountered an error"
            has_required_failures = True

        results.append({
            "id": "M4-BENCH",
            "name": "Performance Benchmarks",
            "member": "Member 4 (IT24102365)",
            "required": False,
            "status": status,
            "detail": detail,
            "duration": bench_res["duration"]
        })
        print(bench_res["stdout"])

    # Final Formatted Summary Table
    print("\n" + "=" * 95)
    print("TEST EXECUTION SUMMARY TABLE")
    print("=" * 95)
    print(f"{'Test ID':<10} | {'Test Name / Question':<32} | {'Responsibility':<22} | {'Status':<8} | {'Details'}")
    print("-" * 110)

    for r in results:
        req_marker = "*" if r["required"] else " "
        name_display = f"{r['name']}{req_marker}"
        print(f"{r['id']:<10} | {name_display:<32} | {r['member']:<22} | {r['status']:<8} | {r['detail']}")

    print("-" * 110)
    print("Note: (*) indicates mandatory requirement for integrated baseline (Q1-Q6 + M4).")

    # Final Verdict
    print("\n" + "=" * 95)
    if has_required_failures:
        print("FINAL VERDICT: FAIL - One or more required baseline tests failed.")
        print("=" * 95)
        sys.exit(1)
    else:
        # Check if optional Q7/Q8 failed/blocked under --all
        optional_issues = [r for r in results if not r["required"] and r["status"] in ("FAIL", "BLOCKED")]
        if optional_issues:
            print("FINAL VERDICT: PASS - Integrated baseline (Q1-Q6 + M4) passed completely.")
            print("                (Note: Unmerged Member 3 tasks Q7/Q8 are logged as BLOCKED/FAIL without breaking baseline)")
        else:
            print("FINAL VERDICT: PASS - All executed tests and verification suites passed.")
        print("=" * 95)
        sys.exit(0)


if __name__ == "__main__":
    main()
