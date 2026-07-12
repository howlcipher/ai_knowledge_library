---
name: l4d2_optimization
description: Performance optimization and resource management for L4D2 servers and clients.
---

# Left 4 Dead 2 Optimization

Focus on extracting the maximum performance out of the aging Source Engine for Left 4 Dead 2, addressing both server-side tickrate stability and client-side FPS/network optimization.

## Key Focus Areas
- **Server Tickrate**: Achieving stable 60 or 100+ tickrates, adjusting `sv_maxcmdrate`, `sv_maxupdaterate`, and `net_splitpacket_maxrate`.
- **Entity Limits**: Managing the edict limit to prevent engine crashes (Host_Error: ED_Alloc: no free edicts).
- **Client FPS**: Optimizing autoexec files, launch options, and visual settings for maximum visibility and frame rates.
- **Network Routing**: Reducing choke, loss, and latency jitter through optimal rate settings.
