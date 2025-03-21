# Fruit Box Game Solver

A tool for solving and automating the Fruit Box Game, a puzzle where you need to select boxes that sum to 10 to maximize your score.

## Overview

This project provides an automated solver for the Fruit Box Game. It includes:

- Multiple solving algorithms (DFS and QUBO)
- GUI automation using PyAutoGUI
- File-based problem solving
- Detailed logging and result analysis

## Game Link

The Fruit Box Game can be played at: [https://en.gamesaien.com/game/fruit_box/](https://en.gamesaien.com/game/fruit_box/)

## Project Structure

```
fruit-box-bot/
├── src/                     # Source code
│   ├── models/              # Data models
│   ├── algorithms/          # Solving algorithms (DFS, QUBO)
│   ├── utils/               # Utility functions
│   ├── interfaces/          # File and GUI interfaces
│   └── config.py            # Configuration settings
├── main.py                  # Main entry point
├── tests/                   # Tests
├── data/                    # Problem files
│   └── problem0.txt
├── imgs/                    # Images for GUI recognition
│   └── apple*.png
└── logs/                    # Log output (gitignored)
```

## Usage

There are two ways to run the solver:

### GUI Mode (with PyAutoGUI)

This mode automates the game directly on the website:

1. Open the game at [https://en.gamesaien.com/game/fruit_box/](https://en.gamesaien.com/game/fruit_box/)
2. Make sure the game is fully visible on your screen
3. Run the following command:

```bash
python main.py
```

The bot will automatically:
- Locate the game on your screen
- Identify apple positions and values
- Play the game by making selections that sum to 10

### File Mode (without PyAutoGUI)

This mode solves a problem from a text file without interacting with the browser:

```bash
python main.py --file data/problem0.txt
```

### Algorithm Selection

By default, the solver uses the DFS algorithm which is stable and well-tested:

```bash
python main.py  # Uses DFS by default
```

The QUBO algorithm is also available but is still in testing:

```bash
python main.py --algorithm qubo  # Experimental
```

## Requirements

- Python 3.9+
- PyAutoGUI
- NumPy
- D-Wave dimod (for QUBO solver)

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install uv if you don't have it

uv sync

```

### Using pip

Alternatively, you can use pip:

```bash
pip install -e .
```

## Problem File Format

A problem file should contain a grid with apple values (1-9), where 0 represents an empty cell:

```
problem0.txt

0 0 1 0 2 0 1 0 3 0 1 0 2 0 0 0 0
0 2 0 1 0 2 0 1 0 2 0 3 0 1 0 0 0
3 0 1 0 3 0 1 0 3 0 1 0 3 0 0 0 0
0 1 0 3 0 1 0 2 0 1 0 3 0 2 0 0 0
2 0 3 0 1 0 3 0 1 0 2 0 1 0 0 0 0
0 3 0 1 0 3 0 1 0 3 0 1 0 3 0 0 0
1 0 2 0 3 0 1 0 2 0 3 0 1 0 0 0 0
0 3 0 1 0 2 0 3 0 1 0 2 0 1 0 0 0
3 0 1 0 3 0 1 0 3 0 1 0 3 0 0 0 0
0 2 0 3 0 1 0 2 0 3 0 1 0 2 0 0 0