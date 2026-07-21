# ADR 0004: Homelab MCP Server Architecture

## Context
We need to build an MCP (Model Context Protocol) server to monitor, debug, and manage local Docker containers and network infrastructure within the homelab environment. This tool must adhere to our `system_administration`, `devops_sre`, and `technical_writing` standards, specifically ensuring least privilege access, container host security, and reliable operations.

We need to decide on the programming language/technology stack for the MCP server, and the method of interacting with and managing Docker containers on the host.

## Status
Accepted

## Decision
1. **Technology Stack:** We will use **Go** to build the MCP server.
2. **Container Management Approach:** We will use **SSH** to remotely manage Docker containers and execute monitoring commands, avoiding direct Docker socket mounting.

## Consequences
- **Positive:**
  - **Go** provides a statically compiled, single binary without runtime dependencies, making it easy to deploy on homelab servers. It is performant and has excellent standard library support for concurrency and network operations.
  - Using **SSH** for remote execution adheres to the `system_administration` rule of **Least Privilege Access**. We can configure SSH to use key-based authentication with restricted, non-root users, applying strict sudo rules just for necessary Docker commands.
  - Avoids the severe security risk of mounting the Docker socket (`/var/run/docker.sock`) into a container, which could otherwise allow full root-level access to the host.
- **Negative:**
  - Managing SSH keys and restricted sudo configurations adds some overhead compared to just mounting a socket.
  - SSH requires proper configuration and hardening on the target hosts.

## Alternatives Considered
- **Python / TypeScript:** While Python is used in the repository and is good for rapid prototyping, Go offers better performance and easier deployment for a system daemon. TypeScript was rejected as it introduces Node.js runtime dependencies not typical for this repository's system-level components.
- **Docker Socket Mounting:** Mounting `/var/run/docker.sock` directly into the MCP server container is the easiest method but violates our `system_administration` container host security guidelines, as it grants effectively root-level access to the host system.
- **Docker HTTP API:** Exposing the Docker daemon via HTTP/TLS is more secure than socket mounting, but managing mutual TLS certificates adds significant operational complexity compared to using existing SSH infrastructure.
