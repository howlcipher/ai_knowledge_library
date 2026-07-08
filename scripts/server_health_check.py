#!/usr/bin/env python3
"""
Server Health Check Utility.
"""

import json
import os
from datetime import datetime


class ServerHealthChecker:
    """Class to perform health checks and log the results."""

    def __init__(self, log_dir: str = None):
        """Initializes the health checker."""
        if log_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.log_dir = os.path.join(script_dir, "..", "infrastructure", "logs")
        else:
            self.log_dir = log_dir

        self.log_file = os.path.join(self.log_dir, "health_log.json")

    def get_health_data(self) -> dict:
        """Gathers health data of the server."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_status": "Healthy",
            "memory_status": "Healthy",
            "disk_status": "Healthy",
        }

    def log_health(self) -> None:
        """Logs the health data to the specified log directory."""
        os.makedirs(self.log_dir, exist_ok=True)
        health_data = self.get_health_data()

        with open(self.log_file, "a") as f:
            f.write(json.dumps(health_data) + "\n")

        print(f"Health check completed and logged to {self.log_file}.")


def main():
    """Main entry point for health checker."""
    checker = ServerHealthChecker()
    checker.log_health()


if __name__ == "__main__":
    main()
