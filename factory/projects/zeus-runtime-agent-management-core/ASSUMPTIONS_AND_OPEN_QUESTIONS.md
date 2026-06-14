---
project_id: zeus-runtime-agent-management-core
project_name: Zeus Runtime Agent Management Core
validated: yes
reviewed: yes
status: draft-ready
---

# Assumptions and Open Questions

## Assumptions
- Infisical at `http://100.68.195.19:8080/` remains the centralized vault.
- Each runtime agent keeps a distinct Infisical project and machine identity.
- A shared runtime-pack project will be created for operational keys intended to be shared across runtime agents.
- Shared SendGrid key will initially be scope-limited to mail sending and later may evolve to per-agent SendGrid subusers/API keys.
- Zeus is allowed to administer derived runtime agents; runtime agents must not administer Zeus or sibling agents.

## Open questions before production hardening
1. Exact Infisical project name/ID for the shared runtime pack.
2. Whether shared pack access is granted by organization-level identity membership or per-project identity grants in the current Infisical version.
3. Which SendGrid sender identities/domains are verified and approved for runtime agents.
4. Whether client/niche agents should use per-agent `FROM` addresses or a default `noreply@sitiouno.us` identity for PMV.
5. Whether billing/cost allocation should require per-agent API keys earlier than PMV.

## Decisions deferred
- Full ticket schema and runtime-to-Zeus ticket ingestion mechanism.
- Dashboard UI design for Zeus agent fleet management.
- Full VM provisioning workflow and cloud account boundary strategy.
