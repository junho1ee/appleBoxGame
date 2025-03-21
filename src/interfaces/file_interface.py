import time
import os
from typing import Optional

from src.utils.logger import Logger
from src.utils.grid_utils import (
    read_problem_from_file,
    print_grid,
    update_grid_after_box,
)
from src.algorithms.dfs_solver import find_strategy
from src.models.box import Strategy


def run_from_problem_file(
    problem_file: str, algorithm: str = "dfs"
) -> Optional[Strategy]:
    """
    Run the solver using a problem file without PyAutoGUI.

    Args:
        problem_file: Path to the problem file
        algorithm: Algorithm to use ('dfs' or 'qubo')

    Returns:
        Strategy object if successful, None otherwise
    """
    # Initialize logger
    logger = Logger()
    logger.initialize_log(mode="file", problem_file=problem_file)

    logger.log_message(f"Reading problem from file: {problem_file}")

    # Read the grid from file
    grid = read_problem_from_file(problem_file)
    if grid is None:
        logger.log_message("Failed to read valid problem. Exiting.")
        return None

    # Calculate total apple sum
    total = sum(sum(row) for row in grid)

    # Print initial grid state
    logger.log_message(f"\nProblem Loaded! Total apple sum: {total}")
    logger.log_message(print_grid(grid))

    # Calculate strategy with timing
    logger.log_message("Starting strategy search...")
    search_start_time = time.time()

    if algorithm.lower() == "dfs":
        strategy = find_strategy(grid)
    elif algorithm.lower() == "qubo":
        # Import here to avoid circular imports
        from src.algorithms.qubo_solver import solve_fruit_box_with_qubo

        strategy = solve_fruit_box_with_qubo(grid)
    else:
        logger.log_message(f"Unknown algorithm: {algorithm}. Using DFS instead.")
        strategy = find_strategy(grid)

    search_end_time = time.time()
    search_duration = search_end_time - search_start_time
    logger.log_message(f"Strategy found with score: {strategy.score}")
    logger.log_message(f"Search algorithm completed in {search_duration:.2f} seconds")

    # Set up final log directory based on score
    logger.setup_final_log_directory(
        strategy.score, mode="file", problem_file=problem_file
    )

    # Save original problem
    problem_filename = f"{logger.final_log_dir}/problem.txt"
    with open(problem_filename, "w") as f:
        for row in grid:
            f.write(" ".join(str(cell) for cell in row) + "\n")

    # Save strategy
    strategy_filename = f"{logger.final_log_dir}/strategy.txt"
    with open(strategy_filename, "w") as f:
        f.write(f"Score: {strategy.score}\n")
        f.write(f"Number of boxes: {len(strategy.boxes)}\n\n")
        f.write("Boxes:\n")
        for i, box in enumerate(strategy.boxes):
            f.write(
                f"Box {i+1}: x={box.x}, y={box.y}, width={box.width}, height={box.height}\n"
            )

    # Simulate strategy execution process (like in GUI mode)
    logger.log_message("\n----- Simulating Strategy Execution -----")
    current_score = 0
    current_grid = [row.copy() for row in grid]  # Make a copy of the original grid

    for i, box in enumerate(strategy.boxes):
        # Calculate box score
        box_score = sum(
            1
            for i in range(box.y, box.y + box.height)
            for j in range(box.x, box.x + box.width)
            if current_grid[i][j] > 0
        )
        current_score += box_score

        # Log box information and grid update
        logger.log_message(
            f"\nMove {i+1}/{len(strategy.boxes)}: ({box.x}, {box.y}), width {box.width}, height {box.height}"
        )
        logger.log_message(f"Current score: {current_score}/{strategy.score}")

        # Update grid after applying box
        current_grid = update_grid_after_box(current_grid, box)
        logger.log_message(print_grid(current_grid))

    logger.log_message("\n----- Simulation Complete -----")
    logger.log_message(f"Final Score: {strategy.score}")

    # Save final grid state
    final_grid_filename = f"{logger.final_log_dir}/final_grid.txt"
    with open(final_grid_filename, "w") as f:
        for row in current_grid:
            f.write(" ".join(str(cell) for cell in row) + "\n")

    # Save result summary
    with open(logger.log_filename, "a") as log_file:
        log_file.write("\n" + "-" * 50 + "\n")
        log_file.write("Game Result Summary:\n")
        log_file.write(
            f"- Execution Mode: File Mode\n"
            f"- Problem File: {os.path.basename(problem_file)}\n"
            f"- Total Apple Sum: {total}\n"
            f"- Final Score: {strategy.score}\n"
            f"- Number of Boxes Used: {len(strategy.boxes)}\n"
            f"- Algorithm: {algorithm.upper()}\n"
            f"- Algorithm Search Time: {search_duration:.2f} seconds\n"
        )
        log_file.write("-" * 50 + "\n")

    logger.log_message(
        f"All log files have been saved to {logger.final_log_dir} directory."
    )

    return strategy
