# Security Overview

This document explains the security controls that protect‑in‑depth every layer of the homelab—hardware, network, application, and monitoring. The guiding principles are **defense‑in‑depth** (multiple complementary controls) and **zero‑trust** (all traffic is authenticated, authorized, and inspected regardless of origin).

---

## 1. Identity & Access Management (IAM)

| Control | Description |
|---------|-------------|
| **Authelia SSO** | Central identity provider enforcing TOTP‑based MFA and role‑based policies. All web‑facing services are placed behind Authelia, including administrative paths such as Portainer. dashboards. |
| **Cloudflare Zero Trust** | Additional policy layer that restricts sensitive URLs (e.g., `*/admin`, `*/metrics`) to authenticated Cloudflare users in an allow‑list. |
| **API Credentials** | The custom Flask API stores encryption‑at‑rest keys in MariaDB using AES‑256; keys are only decrypted in‑memory at runtime. Reverse‑proxy ACLs and rate limiting further constrain access. |

---

## 2. Network Segmentation & Firewalls

| Zone / Network | Purpose | Ingress Policy |
|----------------|---------|----------------|
| `proxt_net0` | Externally reachable services | Accepts traffic **only** from the local `cloudflared` connector; upstream firewall blocks inbound 80/443 entirely. |
| `backend_net` | Databases, caches, internal utilities | No direct ingress; reachable exclusively from `proxy_net` containers that require it. |
| `mc_net` | Minecraft and TeamSpeak | Exposed via SRV records and non‑standard ports; limited to game protocols. |

Additional segmentation is provided by unRAID’s built‑in bridge firewall rules, ensuring east‑west traffic is explicit rather than implicit.

**Perimeter Firewall**

* ISP router blocks unsolicited inbound TCP/UDP on 0‑65535.

---

## 3. Transport Security

| Layer | Mechanism |
|-------|-----------|
| **TLS Termination** | Cloudflare edge issues and renews certificates; origin communicates via **Origin CA** or valid LE certs. |
| **Authenticated Origin Pull** | The nginx reverse proxy trusts **only** Cloudflare edge IPs; mutual‑TLS token validates requests. |
| **Cloudflared Tunnel** | Outbound connector maintains long‑lived tunnel. |

---

## 4. Application‑Layer Controls

### Nginx Reverse Proxy

* **Rate Limiting** — token‑bucket rules mitigate credential‑stuffing and L7 DoS.
* **Security Headers** — HSTS, X‑Content‑Type‑Options, X‑Frame‑Options, and CSP are set globally.
* **HSTS** — enforces use of HTTPS.

### Custom Flask API (High‑Level Notes)

* Keys encrypted in MariaDB; never stored in plaintext.
* Reverse‑proxy ACL restricts paths by CIDR and Auth header.
* API runs behind Authelia and Cloudflare Zero Trust for MFA‑gated access.

---

## 5. Observability & Monitoring

| Component | Function |
|-----------|----------|
| **Wazuh Server** | Central SIEM receiving agent telemetry from key LAN devices (unRAID host, primary workstation). |
| **Docker Log Pipeline** | Planned: Vector sidecar → Wazuh JSON input; will provide container stdout/stderr plus nginx access/error logs. |

Alerts feed to a private Discord channel for real‑time triage.

---

## 6. Continuous Improvement Roadmap

1. **Full container log ingestion** into Wazuh with custom decoders for nginx and Authelia.  

---

The combination of IAM hardening, segmented networks, authenticated ingress, pervasive TLS, and layered monitoring forms a cohesive defense‑in‑depth posture while embracing zero‑trust assumptions throughout the stack. I wrote more about this on my [blog](https://blog.lightworks.dev/a-defense-in-depth-approach-to-securing-self-hosted-web-infrastructure-without-a-vpn/):
