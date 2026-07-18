---
name: "l4d2_server_management"
description: "Setup, configuration, and administration of Left 4 Dead 2 dedicated servers."
triggers:
  - "l4d2"
  - "left 4 dead"
  - "srcds"
  - "dedicated server"
tier: 3
---

# Left 4 Dead 2 Server Management

Methodologies for setting up, configuring, and managing Left 4 Dead 2 (L4D2) dedicated servers using Source Dedicated Server (srcds).

## Core Configuration and Administration

### Server Initialization and Automated Configuration
- **Source Dedicated Server (SRCDS)**: Maintain and update SRCDS configurations using `server.cfg`. Manage configurations using version control to prevent configuration drift.
- **Modding Frameworks**: Securely deploy and configure MetaMod:Source and SourceMod. Implement strict permission groups and admin overrides.
- **Maintenance and Updates**: Automate routine server patching and SteamCMD game file updates during scheduled maintenance windows, ensuring idempotent update processes that minimize player downtime.

### Workshop and Add-on Delivery
- **Content Delivery**: Deploy and update Steam Workshop maps and server-side add-ons. Use fast download servers (FastDL) to optimize client connectivity.

## Infrastructure and Security

### Networking and Performance Tuning
- **Rate and Network Tuning**: Apply the tickrate and rate cvar standards owned by `l4d2_optimization`.
- **Port Management and Firewalls**: Apply a default-deny host firewall policy. Explicitly permit only authorized protocols and ports (typically UDP/TCP 27015 for game traffic and FastDL ports).
- **Resource Monitoring**: Continuously monitor server CPU utilization, memory usage, and tickrate stability to alert on performance anomalies.

### Hardening, Access Control, and Auditability
- **Attack Mitigation**: Mitigate common Source Engine exploits and DDoS/DoS query amplification attacks.
- **Access Control**: Keep server RCON passwords highly secure, rotated, and never written in plaintext within public repositories or logs. Enforce strict firewall rules to restrict admin command queries.
- **Least Privilege Execution**: Run the SRCDS process under a dedicated, unprivileged system user account (never as root) to limit impact in case of system compromise.
- **Console Logging and Auditing**: Enable central logging of server console outputs and admin command execution, forwarding logs to centralized storage for auditing.

## Related Skills
- Defer to `l4d2_optimization` for tickrate targets, rate cvars, and entity/edict budgets.
- Defer to `l4d2_scripting` for SourceMod plugin and VScript development standards.
- Defer to `system_administration` for host hardening and `network_engineering` for firewall design.
