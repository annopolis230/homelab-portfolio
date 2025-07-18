# Homelab Infrastructure as Code

> **Status:** Living project  
> This repository mirrors the current state of my personal homelab. It is **not** a turnkey deployment template—sensitive values are redacted, and some resources (images, volumes) already exist on‑prem. Treat this codebase as documentation and inspiration, not a product.

## Purpose

1. **Sharpen blue‑team skills** — every service is an opportunity to practice hardening, detection engineering, and automated remediation.  
2. **Consolidate self‑hosting** — applications I rely on (blog, analytics, game servers) run on hardware I control.  
3. **Version control** — Git functions as a change‑log; pull requests double as change‑control tickets.

## High‑Level Architecture

| Layer | Components | Notes |
|-------|------------|-------|
| Hardware | Custom server running unRAID | 32 GB RAM, 8 vCPU, SSD cache pool, HDD array |
| Virtualization | Docker engine on unRAID | No production VMs; containers minimize overhead |
| Networking | Multiple bridge networks | `proxy_net`, `backend_net`, `games_net`, each on separate /24 subnets |
| Ingress | Cloudflare → cloudflared → nginx‑proxy‑manager | All inbound web traffic originates from Cloudflare tunnels; ports 80/443 are closed on the perimeter |
| Application Layer | Ghost, Authelia, Portainer, custom Flask API, MariaDB, Redis, Adminer, Minecraft, TeamSpeak | Grouped by use case with least‑privilege firewall rules |

See `docs/architecture.md` for diagrams and subnet details.

## Security Focus

| Blue‑Team Goal | Implementation Highlights |
|----------------|---------------------------|
| Reduce Attack Surface | • Inbound 80/443 closed on the external firewall<br>• No container runs in `host` mode<br>• Authelia SSO required for every exposed service |
| Increase Observability | • Centralized logging via Promtail → Grafana Cloud Loki<br>• Uptime Kuma external monitors<br>• Fail2Ban jails in nginx‑proxy‑manager watch for 401/403 anomalies |
| Integrate Access Controls | • Authelia enforces 2FA and role‑based policies<br>• Cloudflare Zero Trust rules restrict management paths<br>• Databases reachable only on `backend_net` |

Further details are documented in `docs/security.md`.

## Deployment Workflow

1. Edit or create Docker Compose files locally.  
2. Commit and push; every push triggers a manual security review.  
3. Pull updates on the unRAID host using a private CI runner.  
4. Execute `docker compose up -d` for forward rolls; rollbacks are simple `git checkout <sha>` plus `docker compose up -d`.

Secrets are mounted from host‑side Docker volumes and excluded from version control.

## Planned Improvements

- Terraform‑based disaster recovery to a cloud VPS  
- Dedicated Wazuh (OSSEC) VM for expanded endpoint telemetry  
- Automated container image scanning with Trivy and GitHub Advanced Security

## Contributing and Issues

Pull requests are welcome for typo fixes or design suggestions. Be aware that this lab is tailored to my hardware, threat model, and operational requirements.

## License

MIT © 2025 zane devore
