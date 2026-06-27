# Changelog — Signature Core Refactor

Project: zeus-signature-core-refactor-hotfix
Owner: Jean García / SitioUno
Created: 2026-06-12T18:09:47-04:00
Status: G1 bootstrap pack complete; implementation not started
Validated: yes — initial Zeus document consistency pass
Reviewed: yes — initial Zeus Factory orchestrator review; independent quality/security review remains a project task before delivery


## 2026-06-12

- Opened Factory project `zeus-signature-core-refactor-hotfix`.
- Captured G0 repository strategy.
- Completed external pattern research for DocuSeal, OpenSign, signature_pad, pdf-lib, PDF.js, and PyMuPDF.
- Seeded G1 document pack, task graph, QA/security gates, and delivery report.

## 2026-06-19

- Resolved PDF licensing decision: no paid/commercial PyMuPDF license path; commercial runtime must use permissive/open PDF stamping (`pypdf` + `reportlab`) or original SitioUno code. PyMuPDF remains allowed only as an R&D fallback while not distributed as a proprietary runtime requirement.

## 2026-06-27

- Closed final legacy-overlap review: no active SEIS/Superform signing implementation exists in current Zeus `main`; old branches are intentionally not merged.
- Confirmed canonical path as Signature Core v2: Agent Core `signature.*` schema, `tools/signature_tool.py`, `/w/<token>/`, `/api/document-actions*`, OTP proof, private `/user/signatures/`, completed/audit PDF artifacts.
- Added Signature Core to Agent Core migration/status/runtime wiring and exposed the full v2 signature toolset.
- Applied live migrations `signature:000001` and `signature:000002` to local Agent Core Postgres.
- Verified with 61 focused tests, compileall, and live Signature Core smoke; cleaned smoke rows after verification.
- Delivery public sandbox PASS waived because owner scope is private/VPN-only; internal live evidence recorded in `CLOSURE_RECONCILIATION_2026-06-27.md`.
