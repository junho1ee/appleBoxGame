import os
import datetime
import shutil
from typing import Optional


class Logger:
    def __init__(self):
        """Initialize logger with temporary log file"""
        self.logs_base_dir = "logs"
        self.current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        self.tmp_log_filename = (
            f"{self.logs_base_dir}/temp_game_log_{self.current_time}.txt"
        )
        self.final_log_dir = None
        self.log_filename = self.tmp_log_filename

        # Create log directory
        os.makedirs(self.logs_base_dir, exist_ok=True)

    def log_message(self, message: str, also_print: bool = True) -> None:
        """Record message to log file and optionally print to console"""
        if also_print:
            print(message)

        with open(self.log_filename, "a") as log_file:
            log_file.write(message + "\n")

    def setup_final_log_directory(
        self, score: int, mode: str = "gui", problem_file: Optional[str] = None
    ) -> None:
        """Set up final log directory based on score and execution mode"""
        # If we already have a final log directory (from initialize_log), use it
        if not self.final_log_dir:
            # Otherwise, create directory with datetime_score format
            if mode == "file" and problem_file:
                problem_name = os.path.splitext(os.path.basename(problem_file))[0]
                self.final_log_dir = (
                    f"{self.logs_base_dir}/{self.current_time}_{score}_{problem_name}"
                )
            else:
                self.final_log_dir = f"{self.logs_base_dir}/{self.current_time}_{score}"

            os.makedirs(self.final_log_dir, exist_ok=True)

            # If we're using a temporary log file, move it to the final location
            if self.log_filename == self.tmp_log_filename:
                new_log_filename = f"{self.final_log_dir}/game_log.txt"

                # Copy contents from temporary log file to new log file
                if os.path.exists(self.tmp_log_filename):
                    shutil.copy(self.tmp_log_filename, new_log_filename)
                    os.remove(self.tmp_log_filename)  # Delete temporary file

                # Update log filename
                self.log_filename = new_log_filename

    def initialize_log(
        self,
        mode: str = "gui",
        problem_file: Optional[str] = None,
        log_dir: Optional[str] = None,
    ) -> None:
        """Initialize log file with header information"""
        # Use provided log directory or create default one
        if log_dir:
            self.final_log_dir = log_dir
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            if mode == "file" and problem_file:
                problem_name = os.path.splitext(os.path.basename(problem_file))[0]
                self.final_log_dir = f"logs/file_{problem_name}/default/{timestamp}"
            else:
                self.final_log_dir = f"logs/gui/default/{timestamp}"

        # Create log directory if it doesn't exist
        os.makedirs(self.final_log_dir, exist_ok=True)

        # Set log filename directly to final location
        self.log_filename = os.path.join(self.final_log_dir, "log.txt")

        # Create header
        header = f"Fruit Box Game Log - {mode.capitalize()} Mode\n"
        header += f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

        if mode == "file" and problem_file:
            problem_filename = os.path.basename(problem_file)
            header += f"Problem File: {problem_filename}\n"

        header += "\n"

        with open(self.log_filename, "w") as log_file:
            log_file.write(header)
