#!/usr/bin/env python3
import os
import time

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), "infrastructure", "logs")
    
    if not os.path.exists(log_dir):
        print("Log directory does not exist.")
        return
        
    current_time = time.time()
    seven_days = 7 * 24 * 60 * 60
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            file_mod_time = os.path.getmtime(filepath)
            if current_time > file_mod_time + seven_days:
                os.remove(filepath)
                print(f"Removed old log: {filename}")
                
    print("Log cleanup complete.")

if __name__ == "__main__":
    main()
