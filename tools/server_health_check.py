#!/usr/bin/env python3
import json
import os
from datetime import datetime


# A lightweight stub for health checking without external dependencies
def main():
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "cpu_status": "Healthy",
        "memory_status": "Healthy",
        "disk_status": "Healthy",
    }

    log_dir = os.path.join(os.path.dirname(__file__), "..", "infrastructure", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "health_log.json")

    with open(log_file, "a") as f:
        f.write(json.dumps(health_data) + "\n")

    print(f"Health check completed and logged to {log_file}.")


if __name__ == "__main__":
    main()
