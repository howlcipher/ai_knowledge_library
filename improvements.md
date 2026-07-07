# Personal Library Improvements Backlog

This document outlines future enhancements for the AI Knowledge Library to maximize personal productivity and automation.

## Suggested Improvements

### Google Docs API Integration
* Build a custom Python tool in `tools/` that leverages the official Google Docs API to automatically push drafted Markdown documents directly into the user's personal workspace, totally eliminating manual copying.

### Automated Tool Testing Suite
* Establish a dedicated `tests/` directory leveraging `pytest` to automatically validate all custom Python utilities in the `tools/` and `scripts/` directories, preventing future regressions.

### Dynamic Statistics Badges
* Create a GitHub Action that executes `tools/library_statistics.py` on every commit and automatically updates a live "Library Size" or "Active Skills" badge at the top of the README.

### Expanded Dependency Monitoring
* Upgrade the repository dependency scanners to natively monitor and bump versions for Docker Compose images and GitHub Action workflows, keeping the infrastructure permanently up to date.

### Pre Commit Dead Link Prevention
* Port the custom Python dead link scanner into a native Git pre commit hook, making it mathematically impossible to commit broken documentation links locally.
