name: "defensive_debugging"
description: "Triggers during error troubleshooting, crash analysis, or runtime exception reviews"

# Diagnostic Protocol

Execute this sequential isolation process before altering any source code:
1. Locate and inspect the active application log streams or terminal standard error outputs.
2. Isolate the exact file line or environment variable causing the execution block.
3. Present a clear root cause explanation prior to activating any tools that modify the filesystem.\n