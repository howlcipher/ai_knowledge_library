---
name: "l4d2_scripting"
description: "VScript and SourcePawn scripting for Left 4 Dead 2."
triggers:
  - "vscript"
  - "sourcepawn"
  - "sourcemod"
tier: 3
---

# Left 4 Dead 2 Scripting

Guidelines for writing, debugging, and optimizing scripts for Left 4 Dead 2 using SourcePawn for SourceMod plugins and VScript (Squirrel language) for map-specific or mutation logic, ensuring compatibility with server performance optimizations and security controls.

## SourcePawn Development (SourceMod)
* **Event Hooking and Performance**: Write efficient event hooks (e.g., `player_death`, `weapon_fire`) and callbacks. Avoid CPU-heavy calculations inside frequent frames or tick callbacks to maintain target 60/100 tickrate stability.
* **Entity Manipulation and Edict Limits**: Safeguard entity references; verify entity validity before performing operations. Implement cleanup routines to delete temporary entities and stay well below engine edict limits.
* **Memory and Handle Management**: Prevent memory leaks by explicitly closing handles and freeing resources. Ensure plugins support idempotent reload states to prevent memory leaks during server updates.
* **Access Control and Security**: Secure commands and CVARs by assigning appropriate admin permission flags. Prevent script-level exploits that could compromise RCON or bypass server security.

## VScript Development (Squirrel)
* **Custom Mutations**: Implement custom gameplay parameters and logic using the Squirrel VScript engine, profiling scripts to avoid garbage collection spikes and game-thread blocking.
* **Director Scripts**: Modify AI Director behaviors, spawn rates, and tempo dynamically, ensuring AI pathfinding and spawning do not choke server resources.
* **Map Logic**: Build interactive map events and script-controlled entity behaviors.

## Navigation Mesh and Debugging
* **NavMesh Integration**: Script interactions with navigation meshes and pathfinding behaviors.
* **Profiling and Diagnosis**: Debug memory leaks, logic faults, and runtime errors. Log script exceptions and performance profiles to centralized logs for auditing and diagnostic analysis.
