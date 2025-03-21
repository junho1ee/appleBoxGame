import time
import math
import pyautogui
from pyautogui import (
    drag,
    easeOutQuad,
    leftClick,
    locateAllOnScreen,
    locateOnScreen,
    moveTo,
)

from src.utils.logger import Logger
from src.utils.grid_utils import update_grid_after_box, print_grid
from src.algorithms.dfs_solver import find_strategy
from src.models.box import Strategy
import src.config as config


def run_with_pyautogui(algorithm: str = "dfs") -> None:
    """
    Run the solver using PyAutoGUI to interact with the screen.
    
    Args:
        algorithm: Algorithm to use ('dfs' or 'qubo')
    """
    # Initialize logger
    logger = Logger()
    logger.initialize_log(mode="gui")
    
    # Find reset button to get game bounds
    try:
        left, top, _, _ = locateOnScreen("imgs/reset.png", confidence=0.99)
        logger.log_message(f"Reset button position: {left}, {top}")

        left += 8 * config.SCALE
        top -= 363 * config.SCALE
        region = (left, top, config.SIZE * config.NUM_COLS, config.SIZE * config.NUM_ROWS)
        logger.log_message(f"Game region: {region}")

        # Click to ensure game window is active
        leftClick(x=left / config.SCALE, y=top / config.SCALE)

        # Start the game
        leftClick(x=left / config.SCALE - 3, y=top / config.SCALE + 368)  # Click "Reset"
        leftClick(x=left / config.SCALE + 150, y=top / config.SCALE + 175)  # Click "Play"
        logger.log_message("\n----- New Game Started -----")

        # Figure out the apple values
        grid = [[0 for _ in range(config.NUM_COLS)] for _ in range(config.NUM_ROWS)]
        total = 0
        for digit in range(1, 10):
            for local_left, local_top, _, _ in locateAllOnScreen(
                f"imgs/apple{digit}.png", region=region, confidence=0.99
            ):
                row = int((local_top - top) // config.SIZE)
                col = int((local_left - left) // config.SIZE)
                if 0 <= row < config.NUM_ROWS and 0 <= col < config.NUM_COLS:
                    grid[row][col] = digit
                    total += digit

        # Print initial grid state
        logger.log_message(f"\nGame Started! Total apple sum: {total}")
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
        logger.setup_final_log_directory(strategy.score, mode="gui")

        # Save problem
        problem_filename = f"{logger.final_log_dir}/problem.txt"
        with open(problem_filename, "w") as f:
            for row in grid:
                f.write(" ".join(str(cell) for cell in row) + "\n")
        logger.log_message(f"Problem saved to: {problem_filename}")

        # Save strategy
        strategy_filename = f"{logger.final_log_dir}/strategy.txt"
        with open(strategy_filename, "w") as f:
            f.write(f"Strategy Score: {strategy.score}\n")
            f.write(f"Execution Mode: GUI Mode (PyAutoGUI)\n")
            f.write(f"Search Time: {search_duration:.2f} seconds\n\n")
            for i, box in enumerate(strategy.boxes):
                f.write(
                    f"Box {i+1}: ({box.x}, {box.y}), width {box.width}, height {box.height}\n"
                )
        logger.log_message(f"Strategy saved to: {strategy_filename}")

        # Play the game
        logger.log_message("\n----- Executing Strategy -----")
        current_score = 0
        for i, box in enumerate(strategy.boxes):
            moveTo((left + box.x * config.SIZE) / config.SCALE, (top + box.y * config.SIZE) / config.SCALE)
            duration = 0.08 * math.hypot(box.width, box.height)
            drag(
                box.width * config.SIZE / config.SCALE,
                box.height * config.SIZE / config.SCALE,
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
            logger.log_message(
                f"\nDrag {i+1}/{len(strategy.boxes)}: ({box.x}, {box.y}), width {box.width}, height {box.height}"
            )
            logger.log_message(f"Current score: {current_score}/{strategy.score}")
            logger.log_message(print_grid(grid))

            # Short delay to better observe results
            time.sleep(0.5)

        logger.log_message("\n----- Game Complete -----")
        logger.log_message(f"Final Score: {strategy.score}")

        # Save result summary
        with open(logger.log_filename, "a") as log_file:
            log_file.write("\n" + "-" * 50 + "\n")
            log_file.write(f"Game Result Summary:\n")
            log_file.write(
                f"- Execution Mode: GUI Mode (PyAutoGUI)\n"
                f"- Start Time: {time.strftime('%Y-%m-%d %H:%M')}\n"
            )
            log_file.write(f"- Total Apple Sum: {total}\n")
            log_file.write(f"- Final Score: {strategy.score}\n")
            log_file.write(f"- Number of Boxes Used: {len(strategy.boxes)}\n")
            log_file.write(
                f"- Algorithm Search Time: {search_duration:.2f} seconds\n"
            )
            log_file.write("-" * 50 + "\n")

        # Save final grid state
        final_grid_filename = f"{logger.final_log_dir}/final_grid.txt"
        with open(final_grid_filename, "w") as f:
            for row in grid:
                f.write(" ".join(str(cell) for cell in row) + "\n")

        logger.log_message(f"All log files have been saved to {logger.final_log_dir} directory.")

    except Exception as e:
        logger.log_message(f"Error in PyAutoGUI mode: {e}")
        import traceback
        logger.log_message(traceback.format_exc()) 