#!/usr/bin/env python
"""
Fruit Box Game Solver
=====================

A tool for solving and automating the Fruit Box Game, a puzzle where you
need to select boxes that sum to 10 to maximize your score.

Usage:
    python main.py                              # Run in GUI mode (using PyAutoGUI)
    python main.py --file problem0.txt          # Run from a problem file
    python main.py --file problem0.txt --algorithm qubo  # Use QUBO algorithm
"""

import argparse
import os
import sys
import datetime

from src.interfaces.file_interface import run_from_problem_file
from src.interfaces.gui_interface import run_with_pyautogui


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Fruit Box Game Solver")
    parser.add_argument("--file", "-f", type=str, help="Path to problem file")
    parser.add_argument(
        "--algorithm",
        "-a",
        type=str,
        default="dfs",
        choices=["dfs", "qubo"],
        help="Algorithm to use (dfs or qubo)",
    )
    args = parser.parse_args()

    # Validate file path if provided
    if args.file and not os.path.exists(args.file):
        print(f"Error: Problem file '{args.file}' not found.")
        sys.exit(1)

    # Create log directory structure
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.file:
        # For file mode: file_{problem_name}/{algorithm}/{datetime}/
        problem_name = os.path.splitext(os.path.basename(args.file))[0]
        log_dir = os.path.join(
            "logs", f"file_{problem_name}", args.algorithm, timestamp
        )

        # Run from problem file (without PyAutoGUI)
        run_from_problem_file(args.file, algorithm=args.algorithm, log_dir=log_dir)
    else:
        # For GUI mode: gui/{algorithm}/{datetime}/
        log_dir = os.path.join("logs", "gui", args.algorithm, timestamp)

        # Run with PyAutoGUI
        run_with_pyautogui(algorithm=args.algorithm, log_dir=log_dir)


if __name__ == "__main__":
    main()
