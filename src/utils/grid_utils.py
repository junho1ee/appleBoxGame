from typing import List
import numpy as np

from src.models.box import Box
import src.config as config


def print_grid(grid: List[List[int]]) -> str:
    """
    Format grid nicely for display and logging.
    Returns a string representation of the grid.
    """
    grid_str = "\nCurrent Grid State:\n"
    for row in range(config.HEIGHT):
        row_str = ""
        for col in range(config.WIDTH):
            val = grid[row][col]
            row_str += f"{val} "
        grid_str += row_str + "\n"
    grid_str += "\n"
    
    return grid_str


def update_grid_after_box(grid: List[List[int]], box: Box) -> List[List[int]]:
    """
    Set all values within box area to 0.
    Returns updated grid.
    """
    for i in range(box.y, box.y + box.height):
        for j in range(box.x, box.x + box.width):
            grid[i][j] = 0
    return grid


def compute_cumulative_sum(grid: List[List[int]]) -> List[List[int]]:
    """
    Compute cumulative sum matrix for efficient box sum calculations.
    Returns a 2D matrix of size (HEIGHT+1) x (WIDTH+1).
    """
    cum_sum = [[0 for _ in range(config.WIDTH + 1)] for _ in range(config.HEIGHT + 1)]
    for i in range(config.HEIGHT):
        for j in range(config.WIDTH):
            cum_sum[i + 1][j + 1] = (
                cum_sum[i + 1][j] + cum_sum[i][j + 1] - cum_sum[i][j] + grid[i][j]
            )
    return cum_sum


def read_problem_from_file(problem_file: str) -> List[List[int]]:
    """
    Read grid from problem file.
    Returns the grid as a 2D list or None if there was an error.
    """
    grid = []
    try:
        with open(problem_file, "r") as f:
            for line in f:
                row = [int(val) for val in line.strip().split()]
                grid.append(row)

        # Validate grid dimensions
        if len(grid) != config.HEIGHT:
            print(f"Error: Problem file should have {config.HEIGHT} rows, but has {len(grid)}")
            return None

        for i, row in enumerate(grid):
            if len(row) != config.WIDTH:
                print(f"Error: Row {i} should have {config.WIDTH} columns, but has {len(row)}")
                return None

        return grid
    except Exception as e:
        print(f"Error reading problem file: {e}")
        return None 