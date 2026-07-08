#!/usr/bin/env python3
import datetime
import glob
import os
import sys


def generate_adr(title):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = title.lower().replace(" ", "-")

    adrs_dir = "documentation/architecture/adrs"
    os.makedirs(adrs_dir, exist_ok=True)

    # Calculate ADR number
    existing_adrs = glob.glob(os.path.join(adrs_dir, "ADR-*.md"))
    max_adr = 0
    for adr in existing_adrs:
        basename = os.path.basename(adr)
        # Assuming format ADR-XXX-title.md
        parts = basename.split("-")
        if len(parts) >= 2 and parts[1].isdigit():
            adr_num = int(parts[1])
            if adr_num > max_adr:
                max_adr = adr_num

    adr_number = max_adr + 1
    adr_id = f"ADR-{adr_number:03d}"

    filename = os.path.join(adrs_dir, f"{adr_id}-{safe_title}.md")

    content = f"""# {adr_id}: {title}

## Date: {date_str}

## Status: Proposed

## Context
What is the issue we're seeing that motivates this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Generated ADR at {filename}")


if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "New Architecture Decision"
    generate_adr(title)
