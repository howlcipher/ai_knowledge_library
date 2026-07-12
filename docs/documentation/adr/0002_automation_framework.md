# ADR 0002: Automation Framework

## Context
We needed a highly scalable way to automate library maintenance and backups.

## Decision
We chose to build highly modular Python scripts located primarily within the tools directory, leveraging native libraries.

## Pros
* Highly readable and extremely easy to scale.
* Zero external dependencies.
