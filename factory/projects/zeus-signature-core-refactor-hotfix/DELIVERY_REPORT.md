# Delivery Report — Zeus Signature Core Refactor + PDF Signing Collection Hotfix

Project: `zeus-signature-core-refactor-hotfix`
Task: `zeus-signature-core-refactor-hotfix-t15-release-readiness-and-runtime-propag`
Owner: Jean García / SitioUno
Profile: `devops-release`
Run: `run-1781842572-f132f7d5`
Last updated: 2026-06-19T00:22:27-04:00

## T15 Decision

**Release readiness decision:** NOT READY for delivery/critical-readiness pass.

**Runtime propagation decision:** HOLD. Do **not** propagate to `SiteOneTech/sitiouno-agent-runtime` and do **not** deploy production/runtime changes until the blockers below are cleared and Jean/orchestrator explicitly authorizes propagation.

**Reason:** Zeus fork `origin/main` has the integrated security hardening and CI is green, but the canonical delivery/sandbox contract is not satisfied for this deliverable: no T15 sandbox deployment path or docker-compose artifact is present, the public sandbox `/user/` route currently returns `501`, and no live DB-backed signer-token end-to-end sandbox proof was captured for this release decision.

## Source-of-truth snapshot

- Factory DB backend: `agent_core_postgres:zeus_agent.factory`.
- G0 repository strategy from Factory DB:
  - `repo_scope`: `zeus_then_runtime`
  - primary repo: `SiteOneTech/hermes-agent-original`
  - primary path: `/home/jean/Projects/hermes-agent-original`
  - remote: `https://github.com/SiteOneTech/hermes-agent-original.git`
  - base branch: `main`
  - branch prefix: `factory/zeus-signature-core-refactor-hotfix`
  - propagation: Zeus fork first, then evaluate propagation to `sitiouno-agent-runtime` after Zeus core is green.
- T15 assignment initially had no branch/worktree prepared; this report was written in isolated T15 worktree:
  - branch: `factory/zeus-signature-core-refactor-hotfix/t15-release-readiness-runtime-propagation`
  - worktree: `/home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t15-release-readiness-runtime-propagation`

## G1 / project docs consulted

- `factory/projects/zeus-signature-core-refactor-hotfix/DOCUMENTATION_INDEX.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TASK_GRAPH.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/REQUIREMENTS_ANALYSIS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/ADRS.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TECHNICAL_BLUEPRINT.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/SECURITY_GATES.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QA_REPORT_T13.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/QUALITY_REVIEW.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R_SECURITY_REWORK_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R2_CORE_APPROVAL_OTP_TOKEN_HARDENING_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/T14R3_TERMINAL_OTP_PRIVILEGED_HARDENING_EVIDENCE.md`
- `factory/projects/zeus-signature-core-refactor-hotfix/TRACKER.md`

## Commits and repo state

### Zeus fork / source repo

Remote: `https://github.com/SiteOneTech/hermes-agent-original.git`

`origin/main` at decision time:

- `1a29da5c0c2853b90739fecfcbbddf6091cf42ba` — Merge Factory increment `t14r3-terminal-state-otp-outbox-and-priv` into `main`.
- Includes earlier integrated Signature security commits:
  - `a1a3e2361` — merge T14R integrated security rework into `main`.
  - `fc6431770` — T14R integrate signature security rework.
  - `f8fc5a5e9` — merge T14R2 into `main`.
  - `509c133bf7bb80041d76d9098739661d8b1ec48d` — require OTP-bound signer token for approvals.
  - `1a29da5c0` / `d4d1d57240d5accdc48cc92ef47c7b7db9785be4` — harden terminal OTP privileged paths.

Files verified present on `origin/main`:

- `tools/signature_tool.py`
- `tools/signature_pdf.py`
- `scripts/runtime/publish_delivery_sandbox.py`
- `scripts/runtime/ingest_delivery_events.py`
- `scripts/runtime/delivery_document_actions.py`
- `scripts/runtime/sitiouno_document_workspace.py`
- `db/modules/signature/000002_signature_security_rework.sql`
- T14R/T14R2/T14R3 evidence docs under this project pack.

### Runtime propagation target

Candidate runtime repo exists:

- `SiteOneTech/sitiouno-agent-runtime`
- URL: `https://github.com/SiteOneTech/sitiouno-agent-runtime`
- default branch: `main`
- remote `main`: `2338b4457c30148caabd4a1c7a999a0d21360002`
- no signature-specific remote heads were found with `git ls-remote --heads ... '*signature*'`.

## Tests and checks executed

### Focused local release-readiness tests

Worktree:
`/home/jean/workspace/.worktrees/zeus-signature-core-refactor-hotfix/t14r3-terminal-otp-privileged-hardening`

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  tests/tools/test_signature_tool.py \
  tests/tools/test_signature_pdf.py \
  tests/test_delivery_document_actions.py \
  tests/test_publish_delivery_sandbox_document_actions.py \
  tests/test_delivery_event_ingest.py \
  tests/test_sitiouno_document_workspace_template.py \
  tests/test_user_dashboard_otp_dispatcher.py \
  tests/gateway/test_webhook_signature_rate_limit.py
```

Result:

```text
47 passed in 2.45s
```

Pre/post git status for that worktree remained clean:

```text
## factory/zeus-signature-core-refactor-hotfix/t14r3-terminal-otp-privileged-hardening
```

### GitHub CI on `origin/main`

Checked `origin/main` head `1a29da5c0c2853b90739fecfcbbddf6091cf42ba` via GitHub Actions check-runs.

Green/complete checks observed:

- `Tests` run: success, including `e2e`, `test (1)` through `test (6)`, and `save-durations`.
- `Lint (ruff + ty)`: success, including `ruff enforcement (blocking)`, `ruff + ty diff`, and `Windows footguns (blocking)`.
- `Typecheck`: success, including web/ui/desktop/bootstrap/shared typecheck jobs.

Skipped:

- `Docker Build and Publish`: skipped for this push.

### Factory gates recorded/observed

Latest Factory DB gates at T15 decision:

- `573` — `security` passed, reviewer `factory-orchestrator`, task T14.
- `572` — `security` passed, reviewer `security-reviewer`, task T14.
- `570` — `implementation` passed, reviewer `claude-builder`, task T14R3.
- `577` — `delivery` failed, reviewer `devops-release`, task T15. Recorded by this T15 run after report branch push.
- `576` — `critical_readiness` failed, reviewer `devops-release`, task T15. Recorded by this T15 run after report branch push.

The failed T15 gates are intentional HOLD gates. They prevent an unsafe delivery pass while runtime/sandbox evidence is incomplete.

## Sandbox and runtime status

### Authorized sandbox

Authorized boundary: `kidu.app` / `*.kidu.app`.

Read-only public checks:

- `https://kidu.app` → HTTP `200`.
- `https://zeus-sandbox.kidu.app` → HTTP `200`.
- `https://zeus-sandbox.kidu.app/healthz` → HTTP `200`.
- `https://zeus-sandbox.kidu.app/w/` → HTTP `403` (protected workspace without token; expected for blank route).
- `https://zeus-sandbox.kidu.app/user/` → HTTP `501` (not release-ready for protected dashboard flow).

Read-only Kidu VM status over Tailscale SSH:

- host: `factory-sandbox-kidu-01.c.su-office-2030.internal`
- services: `tailscaled`, `docker`, `caddy` all active.
- visible containers included `qr-soap-mvp`, `twenty-worker-1`, `twenty-server-1`, `twenty-db-1`, `twenty-redis-1`; no T15-specific signature deployment was verified.

### Delivery/sandbox evidence contract

| Required evidence | T15 status |
|---|---|
| `sandbox_url` público autorizado | PARTIAL: `https://zeus-sandbox.kidu.app` reachable, but `/user/` returns `501` and no live `/w/<token>/` E2E was verified. |
| `sandbox_deploy_path` | MISSING / not deployed in this task. |
| `docker_compose_path` | MISSING / no T15 compose artifact. |
| health/public URL | PARTIAL: `/healthz` is `200`; full signer/dashboard flow not green. |
| `QA_REPORT.md` / QA evidence | Existing QA evidence: `QA_REPORT_T13.md`; no fresh live DB-backed sandbox E2E for T15. |
| evidence paths | T14R/T14R2/T14R3 evidence docs plus CI/test output above. |

Because this contract is incomplete, delivery and critical-readiness remain failed/HOLD.

## Unresolved risks and blockers

1. **No public delivery pass evidence for this release:** sandbox is reachable, but no T15 deployment path/compose artifact/live tokenized signing flow was verified.
2. **`/user/` sandbox route returns `501`:** protected dashboard readiness is not proven on public sandbox.
3. **No production deploy authorization:** this task did not request production deployment, credential changes, or runtime restarts outside read-only checks.
4. **Propagation target not evaluated deeply:** `SiteOneTech/sitiouno-agent-runtime` exists, but was not cloned or patched in this task. Propagation requires a separate authorized runtime branch/review.
5. **PyMuPDF/`fitz` commercial-runtime risk:** no direct `pyproject.toml` dependency was found during T14, but `tools/signature_pdf.py` still has lazy `fitz`/PyMuPDF support. Before commercial/proprietary runtime propagation, decide licensed PyMuPDF use or a permissive fallback.
6. **Multi-replica OTP/rate-limit design:** acceptable for Zeus main security gate, but should be reviewed before production multi-replica/runtime deployment.

## Propagation plan when HOLD is lifted

Do not propagate now. When Jean/orchestrator lifts HOLD:

1. Create an explicit runtime branch in `SiteOneTech/sitiouno-agent-runtime` from its current `main`.
2. Port/cherry-pick only the Signature Core changes proven on Zeus `origin/main` (`fc6431770`, `509c133bf`, `d4d1d5724` and merge-equivalent context), not old divergent feature branches.
3. Resolve runtime-specific path/config differences without introducing production secrets into public containers.
4. Run the focused 47-test signature suite plus the runtime repo CI.
5. Deploy only to authorized sandbox under `/srv/factory/projects/zeus-signature-core-refactor-hotfix` with a documented `docker-compose.yml` or explicit waiver.
6. Capture public `kidu.app` evidence for `/w/<token>/`, `/user/signatures/`, final PDF/artifact download authorization, OTP negative cases, and dashboard auth.
7. Record new delivery/critical-readiness gates only after the public sandbox proof passes.
8. Production remains HOLD until Jean explicitly approves deployment.

## Push/merge policy decision

- Code/security hardening is already merged to Zeus fork `origin/main` and CI is green.
- This T15 report branch was pushed for review/evidence preservation after local diff validation.
- Do **not** merge this T15 report branch or propagate to `sitiouno-agent-runtime` as a release pass while gates `576` and `577` are failed.
- Merge/push to runtime is deferred to a follow-up authorized propagation increment after HOLD is lifted.

## Final state

T15 worker decision is complete, but the release is HOLD:

- Code readiness on Zeus fork: GREEN enough for source branch review.
- Security gate: PASSED.
- Delivery gate: FAILED/HOLD.
- Critical readiness gate: FAILED/HOLD.
- Runtime propagation: DEFERRED / no deployment.
