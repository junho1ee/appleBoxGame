from typing import List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Constants
HEIGHT = 10
WIDTH = 17
MAX_NUM_MOVES = HEIGHT * WIDTH // 2 + 1
D = 4

# Type aliases (for documentation purposes)
Grid = List[List[int]]


@dataclass
class Box:
    x: int
    y: int
    width: int
    height: int


@dataclass
class Strategy:
    boxes: List[Box]
    score: int


def hash_grid(grid: Grid) -> int:
    """Generate a hash value for the grid state."""
    hash_val = 0
    for row in grid:
        for value in row:
            hash_val = hash_val * 11 + value
    return hash_val


def recurse(
    grid: Grid,
    visited: Set[int],
    current_strategy: Strategy,
    num_moves: int,
    best_intermediate_scores: List[int],
    best_strategy: Strategy,
) -> None:
    """Recursively find the best strategy for the grid."""
    # Update best strategy if current is better
    if current_strategy.score > best_strategy.score:
        best_strategy.boxes = current_strategy.boxes.copy()
        best_strategy.score = current_strategy.score

    # Pruning: Check if current strategy is underperforming
    if (
        num_moves > 0
        and current_strategy.score < best_intermediate_scores[num_moves - 1]
    ):
        return
    best_intermediate_scores[num_moves] = min(
        best_intermediate_scores[num_moves], current_strategy.score
    )

    # Pruning: Check if we've seen this grid state before
    grid_hash = hash_grid(grid)
    if grid_hash in visited:
        return

    # Pruning: Limit search depth
    if len(visited) > 1000:
        return

    visited.add(grid_hash)

    # Compute cumulative sums for efficient box sum calculations
    cum_sum = [[0 for _ in range(WIDTH + 1)] for _ in range(HEIGHT + 1)]
    for i in range(HEIGHT):
        for j in range(WIDTH):
            cum_sum[i + 1][j + 1] = (
                cum_sum[i + 1][j] + cum_sum[i][j + 1] - cum_sum[i][j] + grid[i][j]
            )

    # Find possible moves (boxes that sum to 10)
    possible_moves = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            for h in range(1, HEIGHT - y + 1):
                for w in range(1, WIDTH - x + 1):
                    # Calculate sum using cumulative sum array
                    box_sum = (
                        cum_sum[y + h][x + w]
                        - cum_sum[y + h][x]
                        - cum_sum[y][x + w]
                        + cum_sum[y][x]
                    )

                    if box_sum == 10:
                        # Count non-zero values in the box
                        count = 0
                        for i in range(y, y + h):
                            for j in range(x, x + w):
                                if grid[i][j] > 0:
                                    count += 1

                        # Only consider this move if it's one of the D best moves
                        if len(possible_moves) < D:
                            possible_moves.append((x, y, w, h, count))
                            possible_moves.sort(
                                key=lambda move: move[4]
                            )  # Sort by count
                        elif count < possible_moves[-1][4]:
                            possible_moves[-1] = (x, y, w, h, count)
                            possible_moves.sort(key=lambda move: move[4])

    # Try each of the best moves
    for x, y, w, h, _ in possible_moves:
        # Update grid by setting chosen values to 0
        new_grid = [row.copy() for row in grid]
        for i in range(y, y + h):
            for j in range(x, x + w):
                new_grid[i][j] = 0

        # Update strategy
        box = Box(x, y, w, h)
        current_strategy.boxes.append(box)
        count = sum(
            1 for i in range(y, y + h) for j in range(x, x + w) if grid[i][j] > 0
        )
        current_strategy.score += count

        # Recurse
        recurse(
            new_grid,
            visited,
            current_strategy,
            num_moves + 1,
            best_intermediate_scores,
            best_strategy,
        )

        # Backtrack
        current_strategy.boxes.pop()
        current_strategy.score -= count


def find_strategy(grid: Grid) -> Strategy:
    """Find the best strategy for the given grid."""
    best_strategy = Strategy(boxes=[], score=0)
    current_strategy = Strategy(boxes=[], score=0)
    visited = set()
    best_intermediate_scores = [float("inf")] * MAX_NUM_MOVES

    recurse(grid, visited, current_strategy, 0, best_intermediate_scores, best_strategy)

    return best_strategy


# Python module setup (equivalent to the Rust module)
# No need for explicit module definitions in Python
