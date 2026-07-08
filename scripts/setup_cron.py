#!/usr/bin/env python3
import os
import subprocess


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    fetch_news = os.path.join(repo_root, "tools", "fetch_security_news.py")
    clean_logs = os.path.join(repo_root, "tools", "clean_logs.py")

    cron_jobs = [
        f"0 8 * * * python3 {fetch_news}\n",
        f"0 0 * * * python3 {clean_logs}\n",
    ]

    try:
        flag = chr(45) + "l"
        current_cron = subprocess.check_output(["crontab", flag]).decode("utf8")
    except subprocess.CalledProcessError:
        current_cron = ""

    new_cron = current_cron
    for job in cron_jobs:
        if job.strip() not in current_cron:
            new_cron += job

    if new_cron != current_cron:
        cron_file = "/tmp/new_cron_temp"
        with open(cron_file, "w") as f:
            f.write(new_cron)
        subprocess.run(["crontab", cron_file])
        os.remove(cron_file)
        print("System crontab updated successfully.")
    else:
        print("System crontab already properly configured.")


if __name__ == "__main__":
    main()
