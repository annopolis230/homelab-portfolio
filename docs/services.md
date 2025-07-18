# Services Overview

This page summarizes every running stack in the homelab, why it exists, and any notable dependencies.

| Service | Role in the Lab | Key Dependencies | Notes |
|---------|-----------------|------------------|-------|
| **api** | Custom RESTful endpoint originally built for Roblox game telemetry and utility tasks (e.g., asset management). | MariaDB (encrypted key store), Redis (low‑latency cache) | Rate‑limited by the reverse proxy; authentication enforced by Authelia. |
| **authelia** | Single‑Sign‑On (SSO) and MFA gateway for all web apps. Provides role‑based access and JSON Web Tokens consumed by upstream services. | MariaDB (user data), Redis (session storage) | Integrates with Cloudflare Zero Trust to add an external policy layer. |
| **ghost** | Personal blog and project write‑ups (including the “Reverse‑Proxying Wazuh” article). | MariaDB | Runs on `proxy_net`; public traffic passes through tunnel → Authelia → Ghost. |
| **minecraft** | Survival and creative servers for friends; validates logins via Mojang. | — | Exposed on non‑standard host ports via SRV records; isolated in `games_net`. |
| **nginx‑proxy‑manager** | Central reverse proxy and SSL terminator inside the homelab. Routes traffic based on hostname, applies rate limits and security headers, and forwards auth to Authelia. | cloudflared tunnel (trusted source) | Accept‑list restricts inbound traffic to the tunnel container only. |
| **nginx (static)** | Lightweight container for serving simple HTML/CSS/JS sites and health‑check endpoints. | — | Internal‑only utilities and placeholder pages; no external exposure. |

> **Back‑end patterns**  
> * MariaDB provides durable storage for stateful apps.  
> * Redis accelerates session and cache workloads.  
> * All services that face users traverse the same ingress pipeline: **Cloudflare WAF → Tunnel → nginx‑proxy‑manager → Authelia (if applicable) → Service**.

This layout keeps the platform lean, secure, and easy to reason about while still supporting a variety of workloads—from personal blogging to full SIEM operations.
