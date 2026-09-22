---
title: "Factory Sandbox Kidu — Check, restart, or deploy previews to the Kidu sandbox VM"
sidebar_label: "Factory Sandbox Kidu"
description: "Check, restart, or deploy previews to the Kidu sandbox VM"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Factory Sandbox Kidu

Check, restart, or deploy previews to the Kidu sandbox VM.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/devops/factory-sandbox-kidu` |
| Version | `1.0.0` |
| Author | Zeus / SitioUno |
| License | MIT |
| Platforms | linux |
| Tags | `factory`, `sandbox`, `gcp`, `tailscale`, `caddy`, `docker`, `kidu` |
| Related skills | [`hermes-agent`](../../bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Hermes loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Factory Sandbox Kidu

## Trigger

Use this skill when a Factory agent must check health, restart, deploy, route, or verify a public sandbox preview on Kidu (`kidu.app` / `*.kidu.app`).

## Canonical role

Factory Sandbox Kidu is a disposable/public-preview surface for SitioUno Software Factory work. It is not production approval. Delivery can pass only after public HTTPS plus browser/API evidence exists; Jean decides later whether to promote anything to production.

## Known non-secret endpoints

- SSH over Tailscale: `ubuntu@100.90.244.10`
- Public Kidu root: `https://kidu.app/`
- Standard project layout on the VM: `/srv/factory/projects/<project>/`
- Restart credential must come from Infisical/runtime env as `TOKEN_SANDBOX_KIDU`; never paste or store the bearer token in files, repo, logs, memory, wiki, or shell history.

## Health check pattern

```bash
ping -c 3 -W 2 100.90.244.10
ssh -o BatchMode=yes -o ConnectTimeout=8 ubuntu@100.90.244.10 '
  set -euo pipefail
  hostname -f || hostname
  id
  docker --version
  docker compose version
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
  caddy version
  systemctl is-active tailscaled docker caddy
'
curl -fsSIL --max-time 15 https://kidu.app/
```

Expected: Tailscale/SSH reachable, Docker+Caddy active, and HTTPS returns a valid response.

## Restart pattern

If the VM is stopped or unreachable, first verify whether the runtime environment contains `TOKEN_SANDBOX_KIDU` without printing its value. If missing, sync it through Infisical and restart the local runtime/session as needed. If present, call the restart Cloud Function using the env var only. Do not write the token anywhere.

## Deployment layout

Use scoped per-project directories:

```text
/srv/factory/projects/<project>/
  docker-compose.yml
  .env.sandbox
  app/
  data/
  logs/
  artifacts/
  README_DELIVERY.md
  QA_REPORT.md
```

Do not copy Zeus/Hermes secrets to the sandbox. Use only per-project sandbox/staging secrets. Do not mount `/var/run/docker.sock` inside project containers unless Jean explicitly authorizes that specific risk.

## Verification gate

Before recording delivery PASS for a UI/runnable deliverable, collect evidence for:

- Authorized public sandbox URL under `kidu.app` / `*.kidu.app` unless Jean explicitly authorized another host.
- Public HTTP/API health or smoke check against the same sandbox host.
- Browser/Playwright smoke against the same sandbox host for UI work.
- Desktop screenshot and mobile screenshot for UI work.
- Clean console error check for UI work.
- Core flow interaction result.
- `QA_REPORT.md` and explicit evidence paths.

## Pitfalls

- Do not treat Spot/preemptible VM outage as application code failure until the VM state is checked.
- Do not expose private dashboards/workspaces through `*-sandbox.kidu.app`; public sandbox domains must route only to customer-facing delivery surfaces.
- Do not mark delivery green from local checks only. Public HTTPS and browser/API verification are required.
- Do not use the sandbox as a production promotion. Production remains HOLD until Jean decides.
