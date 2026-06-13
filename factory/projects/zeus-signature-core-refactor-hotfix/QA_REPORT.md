# QA Report — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## Current State

T06 responsive signing UI implemented and visually verified. The public static renderer now produces a SitioUno-branded signing workspace with PDF stage, overlay fields, signer progress panel, high-DPI signature canvas, desktop two-column layout, and mobile sticky action bar. Later T07 owns OTP completion semantics.

## T06 Responsive Signer UI Evidence

- Test RED observed: `ModuleNotFoundError: No module named 'scripts.runtime.sitiouno_document_workspace'` before implementation.
- Unit/render tests: `PYTHONPATH=. /home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest tests/test_sitiouno_signature_workspace_t06.py -q -o 'addopts='` → `2 passed`.
- Regression bundle: `PYTHONPATH=. /home/jean/Projects/hermes-agent-original/venv/bin/python -m pytest tests/test_publish_delivery_sandbox_document_actions.py tests/test_sitiouno_signature_workspace_t06.py -q -o 'addopts='` → `6 passed`.
- Desktop browser QA: generated with `google-chrome --headless=new --window-size=1440,1000`, evidence `evidence/t06-responsive-signer-ui/desktop-1440x1000.png`.
- Mobile browser QA: generated with `google-chrome --headless=new --window-size=390,844`, evidence `evidence/t06-responsive-signer-ui/mobile-390x844.png`.

## Baseline Evidence Available Before V2

Existing codebase has tests around:

- `tests/tools/test_signature_tool.py`
- `tests/test_delivery_document_actions.py`
- `tests/test_publish_delivery_sandbox_document_actions.py`

Existing prior probes showed the Signature Core DB/tools layer can store approvals/events/completed PDF attachments, but the public `/sign/<slug>` route and full responsive signing UI were not complete.

## Required QA Evidence To Fill During Implementation

| Area | Evidence Required | Status |
|---|---|---|
| DB migrations | command output and status JSON | pending |
| Tool unit tests | pytest output | pending |
| Multi-signer completion | failing-before/fixed-after test | pending |
| PDF field placement | generated fixture + rendered page images | pending |
| Mobile signing UI | screenshot/browser result | passed — `evidence/t06-responsive-signer-ui/mobile-390x844.png` |
| Desktop signing UI | screenshot/browser result | passed — `evidence/t06-responsive-signer-ui/desktop-1440x1000.png` |
| OTP action flow | request/verify/action tests | pending |
| Reminder worker | idempotent due/reminder output | pending |
| Final copy/hash delivery | receipt rows/logs | pending |
| Dashboard | protected route/browser QA | pending |
