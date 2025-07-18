# Architecture

This document walks through the end‑to‑end flow of traffic, the internal network layout, and the small slice of IaC that provisions the one VM in an otherwise container‑first homelab.

---

## 1. External DNS & Cloudflare Edge

1. **Authoritative DNS** – All records live in Cloudflare.  
2. **Proxy‑mode CNAMEs / A records** –  
   * A single **CNAME** (`cf0a1771-3368‑…​.cfargotunnel.com`) anchors the Cloudflare Tunnel.  
   * A single **A** record maps to the dynamic public IP (updated by a Docker DDNS container).  
   * Every public service owns a CNAME → tunnel chain, so the origin IP never leaks.
3. **Edge controls**  
   * Cloudflare decrypts TLS (Origin CA cert) to run WAF rules, bot mitigation, and DoS protection.  
   * Ports 80/443 are **closed** on the ISP router; all inbound HTTP/S must originate from Cloudflare’s edge.  

Result: strict end‑to‑end TLS with visibility for Cloudflare’s managed security features.

---

## 2. Tunnel ➜ Reverse Proxy ➜ Applications

```text
Internet
  │  HTTPS (TLS terminated, WAF rules applied)
Cloudflare Edge
  │  HTTPS (re‑encrypted)
Cloudflare Tunnel (cloudflared)
  │  localhost:PORT
nginx‑proxy‑manager          ← only trusts cloudflared’s IP
  ├──> Ghost      (proxy_net)
  ├──> Authelia   (proxy_net)
  ├──> Portainer  (proxy_net)
  └──> Internal APIs, Wazuh Dashboard, etc.
```
- Tunnel settings: Public Hostname - no_tls_verify = false; origin certificates are always validated
- nginx-proxy-manager: Accept list limited to the container IP of `cloudflared`
- Domain routing: SNI / Host header selects backend

## 3. Network Topology (Docker Bridge Segmentation)

| Network | Purpose | Exposed Ports |
|----------------|---------|----------------|
| `proxt_net0` | Public facing apps + Authelia | No host ports; reachable only via tunnel |
| `backend_net` | Databases, caches, internal utilities | None |
| `mc_net` | Minecraft and TeamSpeak | Exposed via SRV records and non‑standard ports; limited to game protocols. |
| `utility_net` | PiHole, DDNS, etc | Internal only |

## 4. Local DNS & Pi-Hole

- Pi-Hole acts as the LAN resolver, blocking ads and telemetry.
- Conditional Forwarding: Internal hostnames such as wazuh.lightworks.dev resolve to private IPs.
- Split-Horizon: Internal FQDNs never leave the house, yet external CNAMEs continue to resolve via Cloudflare.

## 5. Wazuh Deployment & Hardening

| Aspect | Summary |
|-------|-----------|
| **Provisioning** | A Terraform plan (terraform/Wazuh) spins up a lightweight Ubuntu KVM guest via the Libvirt provider. |
| **Automation** | Python helper scripts download the cloud image, mkisofs, and Terraform, then inject cloud‑init to perform a full Wazuh‑all‑in‑one install. |
| **Hardening** | SSH via key‑pair only, no default username/password, agent enrollment token rotated at install time. |

## 6. Wazuh Dashboard Behind Reverse Proxy

- Replaced self-signed Wazuh certs with Let's Encrypt cert via `certbot`.
- Updated opensearch_dashboards.yml to reference the new certificates.
- Imported the same cert into nginx-proxy-manager; dashboard is reachable only via internal DNS.

A [full walkthrough](https://blog.lightworks.dev/securely-access-the-wazuh-dashboard-internally-with-nginx-proxy-manager-and-lets-encrypt/) of this is published on my blog.

