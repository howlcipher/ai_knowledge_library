#!/usr/bin/env python3
import os
import datetime
import sys

def generate_adr(title):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = title.lower().replace(" ", "-")
    filename = f"documentation/architecture/adrs/{date_str}-{safe_title}.md"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    content = f"""# {title}

## Date: {date_str}

## Status: Proposed

## Context
What is the issue we're seeing that motivates this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Generated ADR at {filename}")

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "New Architecture Decision"
    generate_adr(title)
