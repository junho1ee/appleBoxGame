import time
import math
import os
import datetime
import shutil
import argparse
import sys

import strategyDFS
import pyautogui
from pyautogui import (
    drag,
    easeOutQuad,
    leftClick,
    locateAllOnScreen,
    locateOnScreen,
    moveTo,
)


NUM_ROWS = 10
NUM_COLS = 17
SCALE = 1  # Screenshotting a retina display gives 2x the dimensions
SIZE = 33 * SCALE

# Create log base directory
logs_base_dir = "logs"
os.makedirs(logs_base_dir, exist_ok=True)

# Create temporary log filename with current time (excluding seconds)
current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M")
tmp_log_filename = f"{logs_base_dir}/temp_game_log_{current_time}.txt"

# Final log directory and filename will be set after the game ends and score is known
final_log_dir = None
log_filename = tmp_log_filename


def log_message(message, also_print=True):
    """Record message to log file and optionally print to console"""
    if also_print:
        print(message)
    with open(log_filename, "a") as log_file:
        log_file.write(message + "\n")


def print_grid(grid):
    """Print grid nicely formatted to terminal and log file"""
    grid_str = "\nCurrent Grid State:\n"
    for row in range(NUM_ROWS):
        row_str = ""
        for col in range(NUM_COLS):
            val = grid[row][col]
            row_str += f"{val} "
        grid_str += row_str + "\n"
    grid_str += "\n"

    # Print to terminal and log file
    log_message(grid_str, also_print=True)


def update_grid_after_box(grid, box):
    """Set all apples within box area to 0"""
    for i in range(box.y, box.y + box.height):
        for j in range(box.x, box.x + box.width):
            grid[i][j] = 0
    return grid


def setup_final_log_directory(score, mode="gui", problem_file=None):
    """Set up final log directory based on score and execution mode"""
    global final_log_dir, log_filename

    # Create directory with datetime_score format
    # If in file mode, add problem filename (without extension)
    if mode == "file" and problem_file:
        problem_name = os.path.splitext(os.path.basename(problem_file))[0]
        final_log_dir = f"{logs_base_dir}/{current_time}_{score}_{problem_name}"
    else:
        final_log_dir = f"{logs_base_dir}/{current_time}_{score}"

    os.makedirs(final_log_dir, exist_ok=True)

    # Set new log file path
    log_filename = f"{final_log_dir}/game_log.txt"

    # Copy contents from temporary log file to new log file
    if os.path.exists(tmp_log_filename):
        shutil.copy(tmp_log_filename, log_filename)
        os.remove(tmp_log_filename)  # Delete temporary file


def read_problem_from_file(problem_file):
    """Read grid from problem file"""
    grid = []
    try:
        with open(problem_file, "r") as f:
            for line in f:
                row = [int(val) for val in line.strip().split()]
                grid.append(row)

        # Validate grid dimensions
        if len(grid) != NUM_ROWS:
            log_message(
                f"Error: Problem file should have {NUM_ROWS} rows, but has {len(grid)}"
            )
            return None

        for i, row in enumerate(grid):
            if len(row) != NUM_COLS:
                log_message(
                    f"Error: Row {i} should have {NUM_COLS} columns, but has {len(row)}"
                )
                return None

        return grid
    except Exception as e:
        log_message(f"Error reading problem file: {e}")
        return None


def run_from_problem_file(problem_file):
    """Run the solver using a problem file without PyAutoGUI"""
    # Get problem filename without path for display
    problem_filename_only = os.path.basename(problem_file)

    # Initialize log file with problem file information
    with open(tmp_log_filename, "w") as log_file:
        log_file.write(
            f"Fruit Box Game Log - File Mode\n"
            f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Problem File: {problem_filename_only}\n\n"
        )

    log_message(f"Reading problem from file: {problem_file}")

    # Read the grid from file
    grid = read_problem_from_file(problem_file)
    if grid is None:
        log_message("Failed to read valid problem. Exiting.")
        return

    # Calculate total apple sum
    total = sum(sum(row) for row in grid)

    # Print initial grid state
    log_message(f"\nProblem Loaded! Total apple sum: {total}")
    print_grid(grid)

    # Calculate strategy with timing
    log_message("Starting strategy search...")
    search_start_time = time.time()
    strategy = strategyDFS.find_strategy(grid)
    search_end_time = time.time()
    search_duration = search_end_time - search_start_time
    log_message(f"Strategy found with score: {strategy.score}")
    log_message(f"Search algorithm completed in {search_duration:.2f} seconds")

    # Set up final log directory based on score
    setup_final_log_directory(strategy.score, mode="file", problem_file=problem_file)

    # Save original problem
    problem_filename = f"{final_log_dir}/problem.txt"
    with open(problem_filename, "w") as f:
        for row in grid:
            f.write(" ".join(str(cell) for cell in row) + "\n")

    # Save strategy
    strategy_filename = f"{final_log_dir}/strategy.txt"
    with open(strategy_filename, "w") as f:
        f.write(f"Strategy Score: {strategy.score}\n")
        f.write(f"Execution Mode: File Mode (No PyAutoGUI)\n")
        f.write(f"Problem File: {os.path.basename(problem_file)}\n")
        f.write(f"Search Time: {search_duration:.2f} seconds\n\n")
        for i, box in enumerate(strategy.boxes):
            f.write(
                f"Box {i+1}: ({box.x}, {box.y}), width {box.width}, height {box.height}\n"
            )

    # Simulate game execution (without PyAutoGUI)
    log_message("\n----- Simulating Strategy Execution -----")
    current_score = 0
    for i, box in enumerate(strategy.boxes):
        # Calculate score for this box
        box_score = sum(
            1
            for i in range(box.y, box.y + box.height)
            for j in range(box.x, box.x + box.width)
            if grid[i][j] > 0
        )
        current_score += box_score

        # Update grid
        grid = update_grid_after_box(grid, box)

        # Print box info and updated grid
        log_message(
            f"\nMove {i+1}/{len(strategy.boxes)}: ({box.x}, {box.y}), width {box.width}, height {box.height}"
        )
        log_message(f"Current score: {current_score}/{strategy.score}")
        print_grid(grid)

    log_message("\n----- Simulation Complete -----")
    log_message(f"Final Score: {strategy.score}")

    # Save result summary
    with open(log_filename, "a") as log_file:
        log_file.write("\n" + "-" * 50 + "\n")
        log_file.write(f"Simulation Result Summary:\n")
        log_file.write(
            f"- Execution Mode: File Mode (No PyAutoGUI)\n"
            f"- Problem File: {problem_filename_only}\n"
            f"- Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        )
        log_file.write(f"- Total Apple Sum: {total}\n")
        log_file.write(f"- Final Score: {strategy.score}\n")
        log_file.write(f"- Number of Boxes Used: {len(strategy.boxes)}\n")
        log_file.write(f"- Algorithm Search Time: {search_duration:.2f} seconds\n")
        log_file.write("-" * 50 + "\n")

    # Save final grid state
    final_grid_filename = f"{final_log_dir}/final_grid.txt"
    with open(final_grid_filename, "w") as f:
        for row in grid:
            f.write(" ".join(str(cell) for cell in row) + "\n")

    log_message(f"All log files have been saved to {final_log_dir} directory.")


def run_with_pyautogui():
    """Run the game using PyAutoGUI to interact with the screen"""
    # Initialize log file with PyAutoGUI information
    with open(tmp_log_filename, "w") as log_file:
        log_file.write(
            f"Fruit Box Game Log - GUI Mode (PyAutoGUI)\n"
            f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        )

    # Find reset button to get game bounds
    try:
        left, top, _, _ = locateOnScreen("imgs/reset.png", confidence=0.99)
        log_message(f"Reset button position: {left}, {top}")

        left += 8 * SCALE
        top -= 363 * SCALE
        region = (left, top, SIZE * NUM_COLS, SIZE * NUM_ROWS)
        log_message(f"Game region: {region}")

        # Click to ensure game window is active
        leftClick(x=left / SCALE, y=top / SCALE)

        while True:
            leftClick(x=left / SCALE - 3, y=top / SCALE + 368)  # Click "Reset"
            leftClick(x=left / SCALE + 150, y=top / SCALE + 175)  # Click "Play"
            log_message("\n----- New Game Started -----")

            # Figure out the apple values
            grid = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
            total = 0
            for digit in range(1, 10):
                for local_left, local_top, _, _ in locateAllOnScreen(
                    f"imgs/apple{digit}.png", region=region, confidence=0.99
                ):
                    row = (local_top - top) // SIZE
                    col = (local_left - left) // SIZE
                    grid[row][col] = digit
                    total += digit

            # Print initial grid state
            log_message(f"\nGame Started! Total apple sum: {total}")
            print_grid(grid)

            # Calculate strategy with timing
            log_message("Starting strategy search...")
            search_start_time = time.time()
            strategy = strategyDFS.find_strategy(grid)
            search_end_time = time.time()
            search_duration = search_end_time - search_start_time
            log_message(f"Strategy found with score: {strategy.score}")
            log_message(f"Search algorithm completed in {search_duration:.2f} seconds")

            # Set up final log directory based on score
            setup_final_log_directory(strategy.score, mode="gui")

            # Save problem
            problem_filename = f"{final_log_dir}/problem.txt"
            with open(problem_filename, "w") as f:
                for row in grid:
                    f.write(" ".join(str(cell) for cell in row) + "\n")
            log_message(f"Problem saved to: {problem_filename}")

            # Save strategy
            strategy_filename = f"{final_log_dir}/strategy.txt"
            with open(strategy_filename, "w") as f:
                f.write(f"Strategy Score: {strategy.score}\n")
                f.write(f"Execution Mode: GUI Mode (PyAutoGUI)\n")
                f.write(f"Search Time: {search_duration:.2f} seconds\n\n")
                for i, box in enumerate(strategy.boxes):
                    f.write(
                        f"Box {i+1}: ({box.x}, {box.y}), width {box.width}, height {box.height}\n"
                    )
            log_message(f"Strategy saved to: {strategy_filename}")

            # Play the game
            log_message("\n----- Executing Strategy -----")
            current_score = 0
            for i, box in enumerate(strategy.boxes):
                moveTo((left + box.x * SIZE) / SCALE, (top + box.y * SIZE) / SCALE)
                duration = 0.08 * math.hypot(box.width, box.height)
                drag(
                    box.width * SIZE / SCALE,
                    box.height * SIZE / SCALE,
                    duration,
                    easeOutQuad,
                    button="left",
                )

                # Update grid and calculate score after drag
                box_score = sum(
                    1
                    for i in range(box.y, box.y + box.height)
                    for j in range(box.x, box.x + box.width)
                    if grid[i][j] > 0
                )
                current_score += box_score
                grid = update_grid_after_box(grid, box)

                # Print box info and updated grid
                log_message(
                    f"\nDrag {i+1}/{len(strategy.boxes)}: ({box.x}, {box.y}), width {box.width}, height {box.height}"
                )
                log_message(f"Current score: {current_score}/{strategy.score}")
                print_grid(grid)

                # Short delay to better observe results
                time.sleep(0.5)

            log_message("\n----- Game Complete -----")
            log_message(f"Final Score: {strategy.score}")

            # Save result summary
            with open(log_filename, "a") as log_file:
                log_file.write("\n" + "-" * 50 + "\n")
                log_file.write(f"Game Result Summary:\n")
                log_file.write(
                    f"- Execution Mode: GUI Mode (PyAutoGUI)\n"
                    f"- Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                )
                log_file.write(f"- Total Apple Sum: {total}\n")
                log_file.write(f"- Final Score: {strategy.score}\n")
                log_file.write(f"- Number of Boxes Used: {len(strategy.boxes)}\n")
                log_file.write(
                    f"- Algorithm Search Time: {search_duration:.2f} seconds\n"
                )
                log_file.write("-" * 50 + "\n")

            # Save final grid state
            final_grid_filename = f"{final_log_dir}/final_grid.txt"
            with open(final_grid_filename, "w") as f:
                for row in grid:
                    f.write(" ".join(str(cell) for cell in row) + "\n")

            log_message(f"All log files have been saved to {final_log_dir} directory.")
            break

    except Exception as e:
        log_message(f"Error in PyAutoGUI mode: {e}")


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Fruit Box Game Solver")
    parser.add_argument("--file", "-f", type=str, help="Path to problem file")
    args = parser.parse_args()

    if args.file:
        # Run from problem file (without PyAutoGUI)
        run_from_problem_file(args.file)
    else:
        # Run with PyAutoGUI
        run_with_pyautogui()


if __name__ == "__main__":
    main()
