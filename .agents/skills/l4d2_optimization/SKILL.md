---
name: "l4d2_optimization"
description: "Performance optimization and resource management for L4D2 servers and clients."
triggers:
  - "l4d2"
---

# Left 4 Dead 2 Optimization

Focus on extracting maximum performance from the Source Engine for Left 4 Dead 2. This methodology addresses both server-side tickrate stability and client-side frame rates and network settings, aligned with secure server administration guidelines.

## Server-Side Performance and Stability

### Tickrate and Rate Settings
* **Target Rates**: Optimize for stable 60-tick or 100-tick performance, managed via structured `server.cfg` configurations to prevent configuration drift.
* **Server cvars**: Configure and enforce network performance cvars including `sv_maxcmdrate`, `sv_maxupdaterate`, and `net_splitpacket_maxrate` to eliminate packet queue bottlenecks.
* **Jitter and DoS Control**: Manage network buffers to minimize choke, packet loss, and latency jitter, while implementing network query limiting to prevent DoS amplification attacks from degrading CPU performance.

### Entity and Resource Limits
* **Edict Management**: Monitor and manage the edict limit using SourceMod/MetaMod profiling tools to prevent engine crashes (such as `Host_Error: ED_Alloc: no free edicts`).
* **Cleanup Routines**: Implement automated, idempotent scripts and plugin routines for aggressive garbage collection or entity deletion for temporary/unused entities.
* **Add-on and FastDL Resource Overhead**: Profile performance impact of Steam Workshop maps and server-side add-ons. Enforce FastDL to offload content delivery and prevent game-thread blocking during client connections.

## Client-Side Optimization

### Configuration and Launch Settings
* **Autoexec files**: Standardize client network rates and performance settings (`rate`, `cl_updaterate`, `cl_cmdrate`) matching the server's target update rates.
* **Launch Options**: Optimize startup arguments for thread allocation, memory usage, and display rates.
* **Visual settings**: Maximize visibility and frame rates by disabling high-cost aesthetic rendering features.
