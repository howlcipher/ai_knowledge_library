#!/usr/bin/env python3
"""
__main__.py

Package entry point for `python -m src.control_plane`.
"""

import sys
from src.control_plane.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
