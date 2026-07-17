---
name: "l4d2_scripting"
description: "VScript and SourcePawn scripting for Left 4 Dead 2."
---

# Left 4 Dead 2 Scripting

Guidelines for writing, debugging, and optimizing scripts for Left 4 Dead 2 using SourcePawn for SourceMod plugins and VScript (Squirrel language) for map-specific or mutation logic.

## SourcePawn Development (SourceMod)
* **Event Hooking**: Write efficient event hooks (e.g., `player_death`, `weapon_fire`) and callbacks.
* **Entity Manipulation**: Safeguard entity references; verify entity validity before performing operations.
* **Memory and Handle Management**: Prevent memory leaks by explicitly closing handles and freeing resources when no longer needed.

## VScript Development (Squirrel)
* **Custom Mutations**: Implement custom gameplay parameters and logic using the Squirrel VScript engine.
* **Director Scripts**: Modify AI Director behaviors, spawn rates, and tempo dynamically.
* **Map Logic**: Build interactive map events and script-controlled entity behaviors.

## Navigation Mesh and Debugging
* **NavMesh Integration**: Script interactions with navigation meshes and pathfinding behaviors.
* **Profiling and Diagnosis**: Debug memory leaks, logic faults, and runtime errors in both SourcePawn plugins and Squirrel scripts.
