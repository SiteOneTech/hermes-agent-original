# Tracker — Funnel Core / CRM Sales Workflow

## Status Summary

| Item | Status | Notes |
|------|--------|-------|
| FunnelCore module | Implemented | agent/crm/funnel_core.py |
| CRMFunnelAdapter protocol | Implemented | agent/crm/adapters/base.py |
| Twenty CRM adapter | Implemented | agent/crm/adapters/twenty.py |
| Unit tests | Implemented | tests/agent/crm/test_funnel_core.py |
| Integration tests | Implemented | tests/agent/crm/test_twenty_adapter.py |
| QA gate | Passed | reviewer=product-analyst |
| Test gate | Passed | reviewer=factory-orchestrator |
| Spec gate | Passed | reviewer=factory-reporter |
| Implementation gate | Passed | reviewer=factory-reporter |
| Required Factory docs | In progress | R2 reconciliation task |
| Reconciliation | In progress | Missing docs being created |

## Notion Tracker

- Page ID: `37a37b39-cad6-8146-b9f2-e1fdf0bdf727`
- URL: `https://app.notion.com/p/Funnel-Core-CRM-Sales-Workflow-Factory-PM-37a37b39cad68146b9f2e1fdf0bdf727`

## Blocker

R0 identified a CLI gap: `hermes factory` CLI has no subcommand to write `notion_tracker_page_id` into Factory DB metadata. This is a known limitation pending Zeus/code-owner resolution. Notion page exists and is linked in artifacts, but Factory DB metadata cannot be updated via CLI.
