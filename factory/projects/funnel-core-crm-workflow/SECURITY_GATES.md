# Security Gates — Funnel Core / CRM Sales Workflow

## Security Scope

This module handles lead/opportunity data. Key security concerns:

| Concern | Mitigation |
|---------|------------|
| PII in funnel events | Only lead_id and stage stored; no PII beyond identifiers |
| CRM credentials | Managed via Agent Core secrets; not hardcoded |
| Adapter input validation | All inputs validated before CRM API calls |
| SQL injection (if applicable) | Parameterized queries only |
| Secrets exposure | No secrets in logs, events, or artifacts |

## Security Review Status

| Check | Status |
|-------|--------|
| No hardcoded credentials | passed |
| Input validation in adapters | passed |
| Secrets via Agent Core | passed |
| No PII in funnel events | passed |
| Adapter protocol isolation | passed |

## Required Commands

```bash
grep -r "password\|secret\|api_key\|token" agent/crm/ --include="*.py" || echo "No secrets found"
```
