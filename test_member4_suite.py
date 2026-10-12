# test_member4_suite.py
# --------------------
# SE3062 Pac-Man Search Algorithms - Member 4 Testing Suite
# Student ID: IT24102365 (Testing and Documentation)
#
# This test suite verifies search algorithms, state transitions, goal tests,
# path legalities, and heuristic mathematical properties (admissibility, consistency,
# non-triviality) without altering existing implementations in search.py or searchAgents.py.

import unittest
import sys
import os
from typing import List, Tuple, Dict, Any

# Framework modules
import util
import search
import searchAgents
import run_tests
import layout
import pacman
from game import Directions, Actions


class DummyGraphProblem(search.SearchProblem):
    """
    A deterministic graph problem for unit testing search algorithms in isolation.
    Nodes: A, B, C, D, E, G
    Edges with (successor, action, cost):
      A -> (B, 'to_B', 2), (C, 'to_C', 5)
      B -> (D, 'to_D', 4), (G, 'to_G_from_B', 10)
      C -> (D, 'to_D_from_C', 1), (G, 'to_G_from_C', 6)
      D -> (G, 'to_G_from_D', 2)
    Goals: {G}
    """
    def __init__(self, start='A', goals=('G',), graph=None):
        self.start = start
        self.goals = set(goals)
        if graph is not None:
            self.graph = graph
        else:
            self.graph = {
                'A': [('B', 'to_B', 2), ('C', 'to_C', 5)],
                'B': [('D', 'to_D', 4), ('G', 'to_G_from_B', 10)],
                'C': [('D', 'to_D_from_C', 1), ('G', 'to_G_from_C', 6)],
                'D': [('G', 'to_G_from_D', 2)],
                'G': []
            }
        self.expanded_states = []

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state in self.goals

    def getSuccessors(self, state):
        self.expanded_states.append(state)
        return list(self.graph.get(state, []))

    def getCostOfActions(self, actions):
        current = self.start
        total_cost = 0
        for act in actions:
            matched = False
            for succ, a, cost in self.graph.get(current, []):
                if a == act:
                    current = succ
                    total_cost += cost
                    matched = True
                    break
            if not matched:
                raise ValueError("Illegal action %s from state %s" % (act, current))
        return total_cost


class TestSearchAlgorithmsUnit(unittest.TestCase):
    """Unit tests for DFS, BFS, UCS, and A* on isolated deterministic graph problems."""

    def test_dfs_finds_goal_path(self):
        """Verifies DFS discovers a valid path from start to goal."""
        problem = DummyGraphProblem()
        path = search.depthFirstSearch(problem)
        self.assertIsInstance(path, list, "DFS must return a list of actions.")
        self.assertTrue(len(path) > 0, "DFS should return a non-empty path.")
        cost = problem.getCostOfActions(path)
        self.assertGreater(cost, 0, "DFS path cost should be positive.")

    def test_bfs_shortest_hop_path(self):
        """
        BFS finds the path with the fewest edges/hops.
        In DummyGraphProblem:
        A -> B -> G (2 hops)
        A -> C -> G (2 hops)
        A -> C -> D -> G (3 hops)
        A -> B -> D -> G (3 hops)
        """
        problem = DummyGraphProblem()
        path = search.breadthFirstSearch(problem)
        self.assertIsInstance(path, list, "BFS must return a list of actions.")
        self.assertEqual(len(path), 2, "BFS should find a 2-hop solution to G.")

    def test_ucs_lowest_total_cost(self):
        """
        In DummyGraphProblem:
        A -> B -> G has cost 2 + 10 = 12
        A -> C -> G has cost 5 + 6 = 11
        A -> B -> D -> G has cost 2 + 4 + 2 = 8
        A -> C -> D -> G has cost 5 + 1 + 2 = 8
        UCS must find a path of cost 8 (cheapest), not the 2-hop path of cost 11 or 12.
        """
        problem = DummyGraphProblem()
        path = search.uniformCostSearch(problem)
        self.assertIsInstance(path, list, "UCS must return a list of actions.")
        cost = problem.getCostOfActions(path)
        self.assertEqual(cost, 8, "UCS must find the minimum cost path (cost 8).")

    def test_astar_with_consistent_heuristic(self):
        """A* must find optimal path using an admissible and consistent heuristic."""
        problem = DummyGraphProblem()
        # Exact distance to G: A:8, B:6, C:3, D:2, G:0
        heuristic_map = {'A': 8, 'B': 6, 'C': 3, 'D': 2, 'G': 0}

        def test_h(state, prob=None):
            return heuristic_map.get(state, 0)

        path = search.aStarSearch(problem, test_h)
        self.assertIsInstance(path, list, "A* must return a list of actions.")
        cost = problem.getCostOfActions(path)
        self.assertEqual(cost, 8, "A* must find the optimal cost path (cost 8).")

    def test_start_state_already_goal(self):
        """If start state is already a goal, all algorithms must return [] immediately."""
        problem = DummyGraphProblem(start='G', goals=('G',))
        for algo, name in [
            (search.depthFirstSearch, "DFS"),
            (search.breadthFirstSearch, "BFS"),
            (search.uniformCostSearch, "UCS"),
            (search.aStarSearch, "A*")
        ]:
            path = algo(problem)
            self.assertEqual(path, [], "%s should return [] when start is goal." % name)

    def test_unreachable_goal(self):
        """If goal is disconnected, all algorithms must return [] without crashing."""
        disconnected_graph = {
            'A': [('B', 'to_B', 1)],
            'B': [],
            'Z': []
        }
        problem = DummyGraphProblem(start='A', goals=('Z',), graph=disconnected_graph)
        for algo, name in [
            (search.depthFirstSearch, "DFS"),
            (search.breadthFirstSearch, "BFS"),
            (search.uniformCostSearch, "UCS"),
            (search.aStarSearch, "A*")
        ]:
            path = algo(problem)
            self.assertEqual(path, [], "%s should return [] when goal is unreachable." % name)

    def test_graph_with_cycles_and_loops(self):
        """
        Verify that graph search algorithms correctly handle cycles and repeated states
        without infinite loops, discovering the true shortest/optimal paths.
        Cycle: S <-> A, S <-> B, A <-> B, B -> G
        """
        cyclic_graph = {
            'S': [('A', 'S->A', 1), ('B', 'S->B', 10)],
            'A': [('S', 'A->S', 1), ('B', 'A->B', 2)],
            'B': [('S', 'B->S', 10), ('A', 'B->A', 2), ('G', 'B->G', 3)],
            'G': []
        }
        problem = DummyGraphProblem(start='S', goals=('G',), graph=cyclic_graph)

        for algo, name in [
            (search.depthFirstSearch, "DFS"),
            (search.breadthFirstSearch, "BFS"),
            (search.uniformCostSearch, "UCS"),
            (search.aStarSearch, "A*")
        ]:
            path = algo(problem)
            self.assertIsInstance(path, list, "%s must return a list." % name)
            self.assertTrue(len(path) > 0, "%s must find a path despite cycles." % name)
            cost = problem.getCostOfActions(path)
            self.assertGreater(cost, 0, "%s path cost must be positive." % name)

        # BFS shortest hop: S->B->G (2 hops, cost 13)
        bfs_path = search.breadthFirstSearch(problem)
        self.assertEqual(len(bfs_path), 2, "BFS must find the 2-hop path (S->B->G).")

        # UCS minimizes total cost: S->A->B->G has cost 1 + 2 + 3 = 6
        ucs_path = search.uniformCostSearch(problem)
        self.assertEqual(problem.getCostOfActions(ucs_path), 6, "UCS must find the cost-6 path.")

    def test_graph_with_zero_cost_edges(self):
        """
        Verify that UCS and A* correctly handle zero-cost edges without looping indefinitely.
        S -> (Z, cost 0) -> (G, cost 5)
        S -> (G, cost 10)
        """
        zero_cost_graph = {
            'S': [('Z', 'to_Z', 0), ('G', 'direct_G', 10)],
            'Z': [('G', 'Z_to_G', 5)],
            'G': []
        }
        problem = DummyGraphProblem(start='S', goals=('G',), graph=zero_cost_graph)

        ucs_path = search.uniformCostSearch(problem)
        self.assertEqual(problem.getCostOfActions(ucs_path), 5, "UCS must find the cost-5 path through zero-cost edge.")
        self.assertEqual(ucs_path, ['to_Z', 'Z_to_G'], "UCS should traverse zero-cost edge to find cheaper path.")

        astar_path = search.aStarSearch(problem, lambda s, p=None: 0)
        self.assertEqual(problem.getCostOfActions(astar_path), 5, "A* with zero heuristic must find cost-5 path.")

    def test_action_sequence_legality_and_return_type(self):
        """Verify that action sequences returned can be followed step-by-step to reach goal."""
        problem = DummyGraphProblem()
        for algo, name in [
            (search.depthFirstSearch, "DFS"),
            (search.breadthFirstSearch, "BFS"),
            (search.uniformCostSearch, "UCS"),
            (search.aStarSearch, "A*")
        ]:
            path = algo(problem)
            self.assertIsInstance(path, list, "%s must return a Python list." % name)
            curr = problem.getStartState()
            for action in path:
                successors = problem.graph.get(curr, [])
                matching = [s for s, a, c in successors if a == action]
                self.assertEqual(len(matching), 1, "Action %s must be legal from state %s in %s" % (action, curr, name))
                curr = matching[0]
            self.assertTrue(problem.isGoalState(curr), "%s path must end in goal state." % name)


class TestPositionSearchProblemIntegrity(unittest.TestCase):
    """Verifies search algorithms on standard Pac-Man maze layouts."""

    def _get_game_state(self, layout_name):
        lay = layout.getLayout(layout_name)
        if lay is None:
            raise FileNotFoundError("Layout %s not found" % layout_name)
        state = pacman.GameState()
        state.initialize(lay, 0)
        return state

    def test_tiny_maze_dfs_path_legality(self):
        state = self._get_game_state('tinyMaze')
        problem = searchAgents.PositionSearchProblem(state)
        path = search.depthFirstSearch(problem)
        self.assertTrue(len(path) > 0, "DFS should find a path in tinyMaze.")

        # Simulate path step by step to verify legality and goal reachability
        curr = problem.getStartState()
        walls = state.getWalls()
        for action in path:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = int(curr[0] + dx), int(curr[1] + dy)
            self.assertFalse(walls[next_x][next_y], "Action %s hit a wall at (%d, %d)" % (action, next_x, next_y))
            curr = (next_x, next_y)
        self.assertTrue(problem.isGoalState(curr), "Final state should be the goal state.")

    def test_medium_maze_optimality_bfs_vs_ucs_vs_astar(self):
        """
        On mediumMaze with uniform costs, BFS, UCS, and A*(manhattan) must all
        yield the identical optimal path length of 68.
        """
        state = self._get_game_state('mediumMaze')
        prob_bfs = searchAgents.PositionSearchProblem(state)
        prob_ucs = searchAgents.PositionSearchProblem(state)
        prob_astar = searchAgents.PositionSearchProblem(state)

        path_bfs = search.breadthFirstSearch(prob_bfs)
        path_ucs = search.uniformCostSearch(prob_ucs)
        path_astar = search.aStarSearch(prob_astar, searchAgents.manhattanHeuristic)

        self.assertEqual(len(path_bfs), 68, "BFS solution length on mediumMaze should be 68.")
        self.assertEqual(len(path_ucs), 68, "UCS solution length on mediumMaze should be 68.")
        self.assertEqual(len(path_astar), 68, "A* solution length on mediumMaze should be 68.")

        # A* with Manhattan heuristic must expand fewer nodes than BFS
        self.assertLess(prob_astar._expanded, prob_bfs._expanded,
                        "A* should expand fewer nodes than BFS on mediumMaze.")

    def test_maze_boundary_and_wall_invariants_across_algorithms(self):
        """
        Verify that for all 4 search algorithms on mediumMaze:
        - Every action is a valid Directions constant
        - Pac-Man never crosses outside the grid boundaries
        - Pac-Man never occupies a wall cell
        """
        state = self._get_game_state('mediumMaze')
        walls = state.getWalls()
        width, height = walls.width, walls.height

        algorithms = [
            ("DFS", lambda p: search.depthFirstSearch(p)),
            ("BFS", lambda p: search.breadthFirstSearch(p)),
            ("UCS", lambda p: search.uniformCostSearch(p)),
            ("A*", lambda p: search.aStarSearch(p, searchAgents.manhattanHeuristic))
        ]

        for name, algo_fn in algorithms:
            prob = searchAgents.PositionSearchProblem(state)
            path = algo_fn(prob)
            self.assertIsInstance(path, list, "%s must return a list of actions." % name)
            self.assertGreater(len(path), 0, "%s must return a non-empty path." % name)

            curr = prob.getStartState()
            for step, action in enumerate(path):
                self.assertIn(action, [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST],
                              "Invalid action '%s' in %s path at step %d" % (action, name, step))
                dx, dy = Actions.directionToVector(action)
                next_x, next_y = int(curr[0] + dx), int(curr[1] + dy)
                self.assertTrue(0 <= next_x < width and 0 <= next_y < height,
                                "%s moved out of maze bounds at step %d: (%d, %d)" % (name, step, next_x, next_y))
                self.assertFalse(walls[next_x][next_y],
                                 "%s moved into wall at step %d: (%d, %d)" % (name, step, next_x, next_y))
                curr = (next_x, next_y)
            self.assertTrue(prob.isGoalState(curr), "%s path must terminate at goal state." % name)


class SubproblemFromState(search.SearchProblem):
    """Helper problem that starts from an arbitrary state of an existing problem."""
    def __init__(self, problem, start_state):
        self.orig_problem = problem
        self.custom_start = start_state

    def getStartState(self):
        return self.custom_start

    def isGoalState(self, state):
        return self.orig_problem.isGoalState(state)

    def getSuccessors(self, state):
        return self.orig_problem.getSuccessors(state)

    def getCostOfActions(self, actions):
        return len(actions)


class TestCornersProblemAndHeuristic(unittest.TestCase):
    """
    Verifies Member 2's CornersProblem and cornersHeuristic implementations:
    - State space structure: (position, tuple_of_4_bools)
    - Goal test: all 4 corners visited
    - Successor validity
    - Mathematical properties: nonnegativity, goal=0, empirical admissibility, and empirical consistency
    """

    def setUp(self):
        lay = layout.getLayout('tinyCorners')
        state = pacman.GameState()
        state.initialize(lay, 0)
        self.tiny_prob = searchAgents.CornersProblem(state)

        lay_med = layout.getLayout('mediumCorners')
        state_med = pacman.GameState()
        state_med.initialize(lay_med, 0)
        self.med_prob = searchAgents.CornersProblem(state_med)

    def test_corners_start_and_goal_definition(self):
        start = self.tiny_prob.getStartState()
        self.assertIsInstance(start, tuple, "Start state must be a tuple.")
        self.assertEqual(len(start), 2, "Start state must be (position, visitedCorners).")
        pos, corners = start
        self.assertIsInstance(corners, tuple, "Visited corners must be a tuple.")
        self.assertEqual(len(corners), 4, "There must be exactly 4 corner flags.")

        # At start, since Pacman is at (4, 5) and corners are at (1,1),(1,6),(6,1),(6,6), all should be False
        self.assertFalse(self.tiny_prob.isGoalState(start), "Start state should not be a goal.")

        # Synthesized goal state: all True
        goal_state = (pos, (True, True, True, True))
        self.assertTrue(self.tiny_prob.isGoalState(goal_state), "State with all True corners must be a goal.")

    def test_corners_start_on_corner_is_recorded(self):
        corner_layout = layout.Layout([
            "%%%%%%%",
            "%.   .%",
            "%     %",
            "%     %",
            "%     %",
            "%P   .%",
            "%%%%%%%",
        ])
        state = pacman.GameState()
        state.initialize(corner_layout, 0)
        state.data.food[1][1] = True
        problem = searchAgents.CornersProblem(state)

        start_position, visited_corners = problem.getStartState()
        self.assertEqual(start_position, (1, 1))
        self.assertEqual(visited_corners, (True, False, False, False))
        self.assertFalse(problem.isGoalState(problem.getStartState()))

    def test_corners_successor_legality_and_transitions(self):
        start = self.tiny_prob.getStartState()
        successors = self.tiny_prob.getSuccessors(start)
        self.assertGreater(len(successors), 0, "Start state must have legal successors.")

        walls = self.tiny_prob.walls
        for succ_state, action, cost in successors:
            next_pos, next_corners = succ_state
            self.assertEqual(cost, 1, "CornersProblem step cost must be 1.")
            self.assertFalse(walls[next_pos[0]][next_pos[1]], "Successor position cannot be a wall.")
            # Check corner update logic
            for idx, c in enumerate(self.tiny_prob.corners):
                if next_pos == c:
                    self.assertTrue(next_corners[idx], "Visiting corner %s must set its flag to True." % str(c))

    def test_tiny_corners_bfs_solution_optimality(self):
        """BFS on tinyCorners must find the exact optimal solution of 28 steps."""
        path = search.breadthFirstSearch(self.tiny_prob)
        self.assertEqual(len(path), 28, "BFS on tinyCorners must produce an optimal path of length 28.")

    def test_heuristic_non_negative(self):
        """cornersHeuristic must be non-negative (h(s) >= 0) for all reachable states examined."""
        frontier = util.Queue()
        start = self.tiny_prob.getStartState()
        frontier.push(start)
        visited = {start}

        count = 0
        while not frontier.isEmpty() and count < 100:
            s = frontier.pop()
            count += 1
            h_val = searchAgents.cornersHeuristic(s, self.tiny_prob)
            self.assertGreaterEqual(h_val, 0, "Heuristic value %d must be >= 0." % h_val)
            for succ, _, _ in self.tiny_prob.getSuccessors(s):
                if succ not in visited:
                    visited.add(succ)
                    frontier.push(succ)

    def test_heuristic_goal_state_is_zero(self):
        """cornersHeuristic must be exactly 0 for any goal state."""
        goal_state = ((1, 1), (True, True, True, True))
        h_val = searchAgents.cornersHeuristic(goal_state, self.tiny_prob)
        self.assertEqual(h_val, 0, "Heuristic at goal state must be 0.")

    def test_heuristic_admissibility_against_optimal_remaining_cost(self):
        """
        Empirical admissibility check: h(s) <= h*(s) for reachable states examined.
        Computes true optimal remaining cost h*(s) by running BFS from state s to goal on tinyCorners.
        Note: This is an empirical check over evaluated states, not a universal proof.
        """
        frontier = util.Queue()
        start = self.tiny_prob.getStartState()
        frontier.push(start)
        visited = {start}

        tested_states = 0
        while not frontier.isEmpty() and tested_states < 30:
            s = frontier.pop()
            tested_states += 1

            h_val = searchAgents.cornersHeuristic(s, self.tiny_prob)

            # Compute exact optimal remaining cost h*(s) using BFS from state s
            subproblem = SubproblemFromState(self.tiny_prob, s)
            optimal_path = search.breadthFirstSearch(subproblem)
            h_star = len(optimal_path)

            self.assertLessEqual(
                h_val, h_star,
                "Admissibility violated at %s: h(s)=%d > h*(s)=%d" % (str(s), h_val, h_star)
            )

            for succ, _, _ in self.tiny_prob.getSuccessors(s):
                if succ not in visited:
                    visited.add(succ)
                    frontier.push(succ)

    def test_heuristic_consistency_triangle_inequality(self):
        """
        Empirical consistency check: h(s) <= c(s, a, s') + h(s') across legal transitions.
        In CornersProblem, c(s, a, s') == 1.
        Therefore: h(s) - h(s') <= 1.
        Note: This is an empirical check over evaluated transitions, not a universal proof.
        """
        frontier = util.Queue()
        start = self.tiny_prob.getStartState()
        frontier.push(start)
        visited = {start}

        checked_transitions = 0
        while not frontier.isEmpty() and checked_transitions < 150:
            s = frontier.pop()
            h_s = searchAgents.cornersHeuristic(s, self.tiny_prob)

            for s_next, action, cost in self.tiny_prob.getSuccessors(s):
                checked_transitions += 1
                h_next = searchAgents.cornersHeuristic(s_next, self.tiny_prob)
                self.assertLessEqual(
                    h_s, cost + h_next,
                    "Consistency violated! Transition from %s to %s with cost %d: h(s)=%d, h(s')=%d"
                    % (str(s), str(s_next), cost, h_s, h_next)
                )
                if s_next not in visited:
                    visited.add(s_next)
                    frontier.push(s_next)

    def test_medium_corners_astar_expansion_bound(self):
        """
        Official autograder requirement: cornersHeuristic must expand < 1200 nodes
        on mediumCorners to receive full marks (3/3).
        """
        path = search.aStarSearch(self.med_prob, searchAgents.cornersHeuristic)
        self.assertEqual(len(path), 106, "Optimal path length on mediumCorners is 106.")
        self.assertLess(
            self.med_prob._expanded, 1200,
            "cornersHeuristic expanded %d nodes, which exceeds the 1200 threshold." % self.med_prob._expanded
        )


class TestFoodSearchAndClosestDot(unittest.TestCase):
    """
    Verifies FoodSearchProblem, foodHeuristic, and ClosestDotSearchAgent interfaces
    and empirical mathematical properties (Q7 and Q8 scope).
    """

    def setUp(self):
        lay = layout.getLayout('tinySearch')
        state = pacman.GameState()
        state.initialize(lay, 0)
        self.gameState = state
        self.foodProblem = searchAgents.FoodSearchProblem(state)

    def test_food_search_problem_representation_and_goal(self):
        """Verifies FoodSearchProblem state structure ((x,y), foodGrid) and goal criteria."""
        start = self.foodProblem.getStartState()
        self.assertIsInstance(start, tuple, "Start state must be a tuple.")
        self.assertEqual(len(start), 2, "Start state must be (pacmanPosition, foodGrid).")
        pos, foodGrid = start
        self.assertIsInstance(pos, tuple, "Position must be (x, y) tuple.")
        self.assertFalse(self.foodProblem.isGoalState(start), "Start state with food remaining cannot be goal.")

        # Synthesized goal state: empty food grid
        emptyFoodGrid = foodGrid.copy()
        for x in range(emptyFoodGrid.width):
            for y in range(emptyFoodGrid.height):
                emptyFoodGrid[x][y] = False
        goalState = (pos, emptyFoodGrid)
        self.assertTrue(self.foodProblem.isGoalState(goalState), "State with no remaining food must be goal.")

    def test_food_search_successor_food_consumption(self):
        """Verifies moving onto a food cell decrements the remaining food count in successor."""
        start = self.foodProblem.getStartState()
        pos, foodGrid = start
        initialCount = foodGrid.count()
        successors = self.foodProblem.getSuccessors(start)
        self.assertGreater(len(successors), 0, "Start state must have successors.")

        for succ_state, action, cost in successors:
            next_pos, next_food = succ_state
            self.assertEqual(cost, 1, "FoodSearchProblem step cost must be 1.")
            if foodGrid[next_pos[0]][next_pos[1]]:
                self.assertEqual(next_food.count(), initialCount - 1,
                                 "Successor food count must decrement by 1 when entering food dot.")
            else:
                self.assertEqual(next_food.count(), initialCount,
                                 "Successor food count must remain unchanged when not entering food dot.")

    def test_food_heuristic_goal_state_is_zero(self):
        """foodHeuristic must evaluate to exactly 0 when no food remains."""
        start = self.foodProblem.getStartState()
        pos, foodGrid = start
        emptyFoodGrid = foodGrid.copy()
        for x in range(emptyFoodGrid.width):
            for y in range(emptyFoodGrid.height):
                emptyFoodGrid[x][y] = False
        goalState = (pos, emptyFoodGrid)
        h_goal = searchAgents.foodHeuristic(goalState, self.foodProblem)
        self.assertEqual(h_goal, 0, "foodHeuristic must evaluate to 0 at goal states.")

    def test_food_heuristic_non_triviality_when_food_remains(self):
        """
        Non-triviality check: when food dots remain, foodHeuristic MUST return h(s) > 0.
        A trivial stub returning 0 is not acceptable and fails this test.
        """
        start = self.foodProblem.getStartState()
        foodCount = start[1].count()
        self.assertGreater(foodCount, 0, "Start state must have remaining food for this test.")
        h_val = searchAgents.foodHeuristic(start, self.foodProblem)
        self.assertGreater(
            h_val, 0,
            "foodHeuristic failed non-triviality check: returned %d when %d food dots remain. "
            "A non-trivial heuristic is required for Q7 (stub returns 0)." % (h_val, foodCount)
        )

    def test_closest_dot_problem_structure(self):
        """
        Verifies AnyFoodSearchProblem initialization and start state.
        Checks ClosestDotSearchAgent contract and records implementation status.
        """
        anyFoodProb = searchAgents.AnyFoodSearchProblem(self.gameState)
        self.assertEqual(anyFoodProb.getStartState(), self.gameState.getPacmanPosition(),
                         "AnyFoodSearchProblem start state must equal Pac-Man's starting position.")
        self.assertEqual(anyFoodProb.walls.width, self.gameState.getWalls().width,
                         "AnyFoodSearchProblem must preserve maze wall dimensions.")

        agent = searchAgents.ClosestDotSearchAgent()
        self.assertTrue(hasattr(agent, 'findPathToClosestDot'),
                        "ClosestDotSearchAgent must declare findPathToClosestDot.")


class TestAutograderScoreParser(unittest.TestCase):
    """Verifies score parsing for the autograder output formats used by the runner."""

    def test_parses_formatted_q7_bonus_score(self):
        output = "### Question q7: 5/4 ###"
        self.assertEqual(run_tests.parse_autograder_score(output, "q7"), "5/4")

    def test_parses_plain_question_score(self):
        output = "Question q3: 3/3"
        self.assertEqual(run_tests.parse_autograder_score(output, "q3"), "3/3")

    def test_missing_question_score_returns_na(self):
        output = "Question q3: 3/3"
        self.assertEqual(run_tests.parse_autograder_score(output, "q7"), "N/A")


def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    test_suite.addTest(loader.loadTestsFromTestCase(TestSearchAlgorithmsUnit))
    test_suite.addTest(loader.loadTestsFromTestCase(TestPositionSearchProblemIntegrity))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCornersProblemAndHeuristic))
    test_suite.addTest(loader.loadTestsFromTestCase(TestFoodSearchAndClosestDot))
    test_suite.addTest(loader.loadTestsFromTestCase(TestAutograderScoreParser))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
