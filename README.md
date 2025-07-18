# Homelab Infrastructure

> This repository mirrors the current state of my personal homelab. It is **not** a turnkey deployment template—sensitive values are redacted, and some resources (images, volumes) already exist on‑prem. Treat this codebase as documentation and inspiration, not a product.

## Purpose

1. **Sharpen blue‑team skills** — every service is an opportunity to practice hardening, detection engineering, and automated remediation.  
2. **Consolidate self‑hosting** — applications I rely on (blog, analytics, game servers) run on hardware I control.  
3. **Version control** — Git functions as a change‑log.

Read the files in `docs/` for more details!

## High‑Level Architecture

| Layer | Components | Notes |
|-------|------------|-------|
| Hardware | Custom server running unRAID | 32 GB RAM, 8 vCPU, SSD cache pool, HDD array |
| Virtualization | Docker engine on unRAID + Libvirt/KVM/QEMU VMs | Mostly container based orchestration. A few VMs for experimentation and security monitoring. |
| Networking | Multiple bridge networks | `proxt_net0`, `mc_net`, `backend_net`, each on separate /24 subnets |
| Ingress | Cloudflare → cloudflared → nginx‑proxy‑manager | All inbound web traffic originates from Cloudflare tunnels; ports 80/443 are closed on the perimeter |
| Application Layer | Ghost, Authelia, Portainer, custom Flask API, MariaDB, Redis, Adminer, Minecraft, TeamSpeak | Grouped by use case with least‑privilege firewall rules |

See `docs/architecture.md` for diagrams and subnet details.

## Security Focus

| Goal | Implementation Highlights |
|----------------|---------------------------|
| Reduce Attack Surface | • Inbound 80/443 closed on the external firewall<br>• No container runs in `host` mode<br>• Authelia SSO required for every exposed service |
| Increase Observability | • Centralized logging via Wazuh <br>• Portainer external monitors |
| Integrate Access Controls | • Authelia enforces 2FA and role‑based policies<br>• Cloudflare Zero Trust rules restrict management paths |

Further details are documented in `docs/security.md`.

Secrets are mounted from host‑side Docker volumes and excluded from version control.

## Planned Improvements

- Fail2Ban joins with Nginx Proxy Manager to monitor for 401/403 anomalies
- Wazuh integration with Docker logs
- Automated backups of Docker bind volumes
