import numpy as np
import dimod
from itertools import product
from typing import List, Tuple

from src.models.box import Box, Strategy
import src.config as config
from src.algorithms.solver import Solver


class QUBOSolver(Solver):
    """QUBO-based solver for the Apple Box Game"""

    def solve(self, grid: List[List[int]]) -> Strategy:
        """
        Find the best strategy using QUBO algorithm.

        Args:
            grid: The game grid with apple values

        Returns:
            A Strategy object containing the optimal solution
        """
        # 1. Find all possible boxes with sum 10
        possible_boxes = self._find_boxes_with_sum_10(grid)

        # 2. Construct QUBO matrix
        n_boxes = len(possible_boxes)
        Q = np.zeros((n_boxes, n_boxes))

        # Objective function: Maximize apple count (use negative for minimization)
        for i, (x, y, w, h, count) in enumerate(possible_boxes):
            Q[i, i] = -count  # Diagonal elements

        # Constraint: Each apple can only be used once
        P = max(abs(Q[i, i]) for i in range(n_boxes)) * 10  # Penalty constant

        # Add penalties for box pairs that share apples
        for r in range(config.HEIGHT):
            for c in range(config.WIDTH):
                if grid[r][c] > 0:  # Only consider cells with apples
                    boxes_covering_apple = []
                    for i, (x, y, w, h, _) in enumerate(possible_boxes):
                        if x <= c < x + w and y <= r < y + h:
                            boxes_covering_apple.append(i)

                    # Add penalty for all box pairs containing the same apple
                    for i in range(len(boxes_covering_apple)):
                        for j in range(i + 1, len(boxes_covering_apple)):
                            idx1, idx2 = (
                                boxes_covering_apple[i],
                                boxes_covering_apple[j],
                            )
                            Q[idx1, idx2] += P
                            Q[idx2, idx1] += P

        # 3. Solve the QUBO problem
        sampler = dimod.SimulatedAnnealingSampler()
        response = sampler.sample_qubo(Q, num_reads=1000)

        # 4. Extract the optimal solution
        best_solution = response.first.sample
        selected_boxes = [
            possible_boxes[i] for i in range(n_boxes) if best_solution[i] == 1
        ]

        # Create box objects
        box_objects = [
            Box(x=x, y=y, width=w, height=h) for x, y, w, h, _ in selected_boxes
        ]

        # 5. Determine optimal box selection order
        ordered_boxes = self._determine_optimal_box_order(grid, box_objects)

        # Calculate score
        total_score = sum(count for _, _, _, _, count in selected_boxes)

        strategy = Strategy(boxes=ordered_boxes, score=total_score)
        return strategy

    def _find_boxes_with_sum_10(
        self, grid: List[List[int]]
    ) -> List[Tuple[int, int, int, int, int]]:
        """
        Find all possible boxes with sum 10.
        Returns list of tuples (x, y, width, height, count) where count is number of non-zero cells.
        """
        # Calculate cumulative sum
        np_grid = np.array(grid, dtype=np.int32)
        cum_sum = np.zeros((config.HEIGHT + 1, config.WIDTH + 1), dtype=np.int32)
        cum_sum[1:, 1:] = np.cumsum(np.cumsum(np_grid, axis=0), axis=1)

        # Find all boxes with sum 10
        possible_boxes = []
        for y, x in product(range(config.HEIGHT), range(config.WIDTH)):
            for h, w in product(
                range(1, config.HEIGHT - y + 1), range(1, config.WIDTH - x + 1)
            ):
                box_sum = (
                    cum_sum[y + h][x + w]
                    - cum_sum[y + h][x]
                    - cum_sum[y][x + w]
                    + cum_sum[y][x]
                )

                if box_sum == 10:
                    count = np.sum(np_grid[y : y + h, x : x + w] > 0)
                    possible_boxes.append((x, y, w, h, count))

        return possible_boxes

    def _determine_optimal_box_order(
        self, grid: List[List[int]], boxes: List[Box]
    ) -> List[Box]:
        """
        Determine the optimal order for selecting boxes based on drag constraints.

        A box can only be selected if the drag path doesn't intersect with other apples.
        This is a complex problem that could be solved with various approaches:

        1. Try all permutations (only feasible for small number of boxes)
        2. Use a greedy algorithm (select the box that blocks the fewest other boxes)
        3. Use a topological sort based on box dependencies

        Args:
            grid: The original grid
            boxes: List of boxes to be ordered

        Returns:
            Ordered list of boxes that satisfies drag constraints
        """
        # Implementation would depend on the specific game rules
        # For example, a simple greedy approach:

        ordered_boxes = []
        remaining_boxes = boxes.copy()
        current_grid = [row.copy() for row in grid]

        while remaining_boxes:
            # Find box that can be selected without interference
            valid_boxes = []
            for box in remaining_boxes:
                if self._can_drag_box(current_grid, box):
                    valid_boxes.append(
                        (
                            box,
                            self._count_blocking_boxes(
                                current_grid, box, remaining_boxes
                            ),
                        )
                    )

            if not valid_boxes:
                # If no valid boxes, we might have a problem with our strategy
                # For simplicity, just add remaining boxes in any order
                ordered_boxes.extend(remaining_boxes)
                break

            # Select box that blocks the fewest other boxes
            valid_boxes.sort(key=lambda x: x[1])
            next_box = valid_boxes[0][0]

            ordered_boxes.append(next_box)
            remaining_boxes.remove(next_box)

            # Update grid after applying box
            for i in range(next_box.y, next_box.y + next_box.height):
                for j in range(next_box.x, next_box.x + next_box.width):
                    current_grid[i][j] = 0

        return ordered_boxes

    def _can_drag_box(self, grid: List[List[int]], box: Box) -> bool:
        """
        Check if a box can be dragged without intersecting other apples.

        Different games may have different drag rules. This is a simplified example.
        """
        # Check if the box itself contains only valid apples (no zeros)
        for i in range(box.y, box.y + box.height):
            for j in range(box.x, box.x + box.width):
                if grid[i][j] == 0:
                    return False

        return True

    def _count_blocking_boxes(
        self, grid: List[List[int]], box: Box, remaining_boxes: List[Box]
    ) -> int:
        """
        Count how many other boxes this box would block if selected.

        A box blocks another box if selecting it would remove apples needed by the other box.
        """
        # Create a copy of the grid after applying this box
        temp_grid = [row.copy() for row in grid]
        for i in range(box.y, box.y + box.height):
            for j in range(box.x, box.x + box.width):
                temp_grid[i][j] = 0

        # Count boxes that would become invalid
        blocked_count = 0
        for other_box in remaining_boxes:
            if other_box != box and not self._can_drag_box(temp_grid, other_box):
                blocked_count += 1

        return blocked_count
