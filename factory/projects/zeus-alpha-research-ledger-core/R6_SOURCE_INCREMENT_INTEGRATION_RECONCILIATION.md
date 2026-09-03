---
project_id: zeus-alpha-research-ledger-core
task_id: zeus-alpha-research-ledger-core-reconcile-source-increment-not-integrated
phase: delivery
status: validated
validated: yes
reviewed: pending
origin_main_before_current_rerun: d8194b268807ef2bb701b6d3f4302967a9e5e5be
previous_run_id: run-1788299716-de25115b
current_run_id: run-1788403567-0d8e963b
---

# R6 source increment integration reconciliation

## Scope
This artifact records the R6 reconciliation for the canonical `source_increment_not_integrated` anomaly. It is evidence-only for Factory source containment; it does not authorize deploy, runtime propagation, direct SQL, credential changes, product dispatch, trading/paper/live actions, or primary checkout mutation.

## R6 rerun — 2026-09-03T02:55:33Z
Current run `run-1788403567-0d8e963b` re-inspected Agent Core Factory status from the assigned worktree after the task was reopened again by the recurring `source_increment_not_integrated` projection:

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, branch `factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Worktree/base synchronization: before reconciliation the assigned branch was at prior contained R6 evidence/base commit `dde53dbe0207bdbce22d417b32ffd3cb802ab29b` and `HEAD...origin/main` was `0 309`; local `origin/main` and remote `refs/heads/main` both resolved `d8194b268807ef2bb701b6d3f4302967a9e5e5be`. The assigned branch was fast-forwarded to that current base; after the fast-forward `HEAD`, `origin/main`, and merge-base all equal `d8194b268807ef2bb701b6d3f4302967a9e5e5be` with ahead/behind `0 0`.
- Sanctioned Factory status input: `/tmp/r6-status-current-run-1788403567.json` (`4991441` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal the assigned worktree, `factory_status_delegated=false`).
- Current Agent Core project metadata still reports `reconciliation_anomalies=['source_increment_not_integrated']`, `reconciliation_required=True`, `reconciliation_projection_source=current_document_status`, and `factory_auto_integration_forbidden=True`; the R6 reconciliation task is `running` with `reopen_reason=canonical_anomaly_recurred`.
- Current project document rows are not the source of the recurrence: sanctioned status readback shows `22` document rows, `14/14` `g1_required` rows, `0` blocking rows, `readiness_source=configured_base_ref`, and `base_commit=d8194b268807ef2bb701b6d3f4302967a9e5e5be`.
- Positive terminal source-bearing task audit output is `/tmp/r6-source-increment-audit-run-1788403567.tsv`; exact summary: `76` positive terminal source-bearing tasks, `76/76` commit objects present, `76/76` contained in `origin/main`, `76/76` `increment_base_commit_after` commits present, `76/76` source→base-after ancestry chains valid, `76/76` base-after→origin/main ancestry chains valid, `76/76` integration metadata valid, `0` failures, and `0` accepted source-containment waivers used. Summary output is `/tmp/r6-source-increment-audit-run-1788403567.summary.txt`.
- Source-containment verdict: the current recurrence is still control-plane/projection drift, not missing Git containment; every audited immutable source commit is already an ancestor of current `origin/main` `d8194b268807ef2bb701b6d3f4302967a9e5e5be`.
- The final immutable branch commit and resulting `origin/main` commit must be recorded in Factory gate notes and the worker final response after this refreshed evidence commit is pushed. A commit cannot self-embed its own final SHA before it exists.

## R6 rerun — 2026-09-01T22:03:51Z
Current run `run-1788299716-de25115b` re-inspected Agent Core Factory status from the assigned worktree after the task was reopened again by the recurring `source_increment_not_integrated` projection:

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, branch `factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Worktree/base synchronization: before reconciliation the assigned branch was at prior R6 evidence commit `50a5d59530ae49997a4968e029d8da639bf9a946` and `HEAD...origin/main` was `0 2297`; `git ls-remote origin refs/heads/main` and local `origin/main` both resolved `71653bbadfa2bd06eaa6ac4a5c03d933332af7de`. The assigned branch was fast-forwarded to that current base; after the fast-forward `HEAD`, `origin/main`, and merge-base all equal `71653bbadfa2bd06eaa6ac4a5c03d933332af7de` with ahead/behind `0 0`.
- Sanctioned Factory status input: `/tmp/r6-status-current.json` (`4968275` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal the assigned worktree).
- Current Agent Core project metadata still reports `reconciliation_anomalies=['source_increment_not_integrated']`, `reconciliation_required=True`, `reconciliation_projection_source=current_document_status`, and `factory_auto_integration_forbidden=True`; the R6 reconciliation task is `running` with `reopen_reason=canonical_anomaly_recurred`.
- Current project document rows are not the source of the recurrence: sanctioned status readback shows `22` document rows, `14/14` `g1_required` rows, `0` blocking rows, `readiness_source=configured_base_ref`, and `base_commit=71653bbadfa2bd06eaa6ac4a5c03d933332af7de`.
- Positive terminal source-bearing task audit output is `/tmp/r6-source-increment-audit-run-1788299716.tsv`; exact summary: `71` positive terminal source-bearing tasks, `71/71` commit objects present, `71/71` contained in `origin/main`, `71/71` `increment_base_commit_after` commits present, `71/71` source→base-after ancestry chains valid, `71/71` base-after→origin/main ancestry chains valid, `71/71` integration metadata valid, `0` failures, and `0` accepted source-containment waivers used. Summary output is `/tmp/r6-source-increment-audit-run-1788299716.summary.txt`.
- Source-containment verdict: the current recurrence is still control-plane/projection drift, not missing Git containment; every audited immutable source commit is already an ancestor of current `origin/main` `71653bbadfa2bd06eaa6ac4a5c03d933332af7de`.
- The final immutable branch commit and resulting `origin/main` commit must be recorded in Factory gate notes and the worker final response after this refreshed evidence commit is pushed. A commit cannot self-embed its own final SHA before it exists.

## R6 rerun — 2026-08-25T21:37:55Z
Current run `run-1787693650-b05c5be2` re-inspected Agent Core Factory status from the assigned worktree after the task was reopened again by the recurring `source_increment_not_integrated` projection:

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, branch `factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Pre-push immutable state: `HEAD=0eae4a813731456ef5d5b10b9013e0c22dc75c64`, `origin/main=c8ff95b0daf84ffb5e931d1c9be7593ab406e275`, assigned remote branch `origin/factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated=3b6dca81f5633df64f47f5861d0b618adb8f76eb`, `HEAD...origin/main` ahead/behind `2 0`, and `HEAD...origin/assigned` ahead/behind `6 0`; remote `SiteOneTech/hermes-agent-original`.
- Sanctioned Factory status input: `/tmp/r6_factory_status_run_1787693650.json` (`4871316` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal the assigned worktree, `factory_status_delegated=false`).
- Current Agent Core project metadata still reports `reconciliation_anomalies=['source_increment_not_integrated']`, `reconciliation_required=True`, `reconciliation_projection_source=current_document_status`, and `factory_auto_integration_forbidden=True`.
- Positive terminal source-bearing task audit output is `/tmp/r6_source_increment_audit_run_1787693650.tsv`; exact summary: `65` positive terminal source-bearing tasks, `65/65` commit objects present, `65/65` contained in `origin/main`, `65/65` `increment_base_commit_after` commits present, `65/65` source→base-after ancestry chains valid, `65/65` base-after→origin/main ancestry chains valid, `65/65` integration metadata valid, `0` failures, and `0` accepted source-containment waivers used.
- Source-containment verdict: the current recurrence is still control-plane/projection drift, not missing Git containment; every audited immutable source commit is already an ancestor of current `origin/main` `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`.
- The final immutable branch commit and resulting `origin/main` commit must be recorded in Factory gate notes and the worker final response after this refreshed evidence commit is pushed. A commit cannot self-embed its own final SHA before it exists.

## R6 rerun — 2026-08-25T21:10:28Z
Current run `run-1787691705-a3783e43` re-inspected Agent Core Factory status from the assigned worktree after the task was reopened by a recurring `source_increment_not_integrated` projection:

- Assigned worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, branch `factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Pre-push immutable state: `HEAD=a4bf78d50a7425c497cef16de6a1844aa8bdcd2d`, `origin/main=c8ff95b0daf84ffb5e931d1c9be7593ab406e275`, `HEAD...origin/main` ahead/behind `1 0`; remote `SiteOneTech/hermes-agent-original`.
- Sanctioned Factory status input: `/tmp/r6_factory_status_run_1787691705.json` (`4850864` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal the assigned worktree, `factory_status_delegated=false`).
- Current Agent Core project metadata reports `reconciliation_anomalies=['source_increment_not_integrated']`, `reconciliation_required=True`, `reconciliation_projection_source=current_document_status`, and `factory_auto_integration_forbidden=True`; the reopened R6 task is `running` and carries `65` finding blocker rows.
- Current required documentation rows are not the source of the R6 recurrence: sanctioned status readback shows all indexed project document rows under the configured base ref as `blocking=false`, including the 14 G1-required rows, at base commit `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`.
- Positive terminal source-bearing task audit output is `/tmp/r6_source_increment_audit_run_1787691705.tsv`; exact summary: `65` positive terminal source-bearing tasks, `65/65` commit objects present, `65/65` contained in `origin/main`, `65/65` `increment_base_commit_after` commits present, `65/65` base-after ancestry chains valid, `65/65` integration metadata valid, `0` failures, and `0` accepted source-containment waivers used.
- Source-containment verdict: the current recurrence is not caused by a missing Git integration for any positive terminal source-bearing increment; every audited immutable source commit is already an ancestor of current `origin/main` `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`.
- The final immutable branch commit and resulting `origin/main` commit must be recorded in Factory gate notes and the worker final response after the refreshed evidence commit is pushed. A commit cannot self-embed its own final SHA before it exists.

## R6 rerun — 2026-08-23T04:31:29Z
Current run `run-1787458981-c83322e8` re-inspected Agent Core Factory status from the assigned worktree after the task was reopened by a recurring `source_increment_not_integrated` projection:

- Assigned worktree was fast-forwarded from prior R6 evidence commit `3b6dca81f5633df64f47f5861d0b618adb8f76eb` to current `origin/main` `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`; `HEAD`, `origin/main`, and merge-base were equal before this evidence edit, with ahead/behind `0 0`.
- Sanctioned Factory status input: `/tmp/r6_factory_status_current_run_1787458981.json` (`4440170` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, `factory_status_delegated=false`).
- Current Agent Core project metadata now reports `reconciliation_anomalies=[]`, `reconciliation_required=False`, and `reconciliation_projection_source=current_document_status`; the status payload has no active `source_increment_not_integrated` finding.
- Current G1 rows are not the source of the R6 recurrence: `14/14` `g1_required` rows are non-blocking from `readiness_source=configured_base_ref` at base commit `c8ff95b0daf84ffb5e931d1c9be7593ab406e275`.
- Positive terminal source-bearing task audit output is `/tmp/r6_source_increment_audit_run_1787458981.tsv`; exact summary: `65` positive terminal source-bearing tasks, `65/65` commit objects present, `65/65` contained in `origin/main`, `65/65` `increment_base_commit_after` chains valid, `65/65` metadata-valid, `0` failures, and `0` waivers used for accepted source containment.
- The project has `factory_auto_integration_forbidden=True`, so this run did not invoke automatic integration. It verified immutable Git containment only, preserving the no-direct-SQL/no-primary-mutation/no-runtime boundary.
- Recurrence guard: prior R6 evidence commit `3b6dca81f5633df64f47f5861d0b618adb8f76eb` is already contained in current `origin/main`; any remaining recurrence should be treated as stale control-plane/event projection unless a future sanctioned status readback produces a non-empty current finding.
- The final immutable branch commit and resulting `origin/main` commit are recorded in the Factory gate notes and worker final response. They are intentionally not self-embedded here because a commit cannot contain its own final SHA before it exists.

## R6 rerun — 2026-08-22T23:51:05Z
Current run `run-1787442400-3b168ecf` re-inspected Agent Core Factory status from the assigned worktree and re-ran the Git ancestry audit without direct `factory.*` SQL:

- Assigned worktree was fast-forwarded from previous R6 evidence commit `71a68478c3be0e28e65b730406c080b42a6b2115` to current `origin/main` `e0fee97133f2fc67ed764785bbe5aae86d86d38a`; `HEAD`, `origin/main`, and merge-base were equal before this evidence edit.
- Sanctioned Factory status input: `/tmp/r6_factory_status_current_run_1787442400.json` (`4401282` bytes, `db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`, `factory_status_delegated=false`).
- Current Factory project metadata still reports `reconciliation_anomalies=['source_increment_not_integrated', 'unvalidated_required_docs']` and `reconciliation_required=True`; current G1 rows are not the source of this R6 anomaly because `14/14` `g1_required` rows are non-blocking from `readiness_source=configured_base_ref` at base commit `e0fee97133f2fc67ed764785bbe5aae86d86d38a`.
- Current R6 finding lists `63` blocker rows. Full audit output is `/tmp/r6_source_increment_audit_run_1787442400.tsv`; exact summary: `63/63` commit objects present, `63/63` contained in `origin/main`, `63/63` `increment_base_commit_after` chains valid, `0` waivers, and `0` failure rows.
- Positive terminal source-bearing task audit independently matches the finding: `63` `done` tasks with `metadata.increment_branch_commit`, `63/63` contained in `origin/main`, and `63/63` valid base-after ancestry chains.
- Recurrence guard: the prior R6 evidence commit `71a68478c3be0e28e65b730406c080b42a6b2115` is already contained in current `origin/main`; the current recurrence is therefore control-plane metadata/projection drift, not missing Git containment. This rerun publishes the refreshed evidence commit to the assigned branch and fast-forwards `origin/main` to the same final commit after validation so the refreshed R6 evidence source is itself contained in the canonical base.
- The final immutable branch commit and resulting `origin/main` commit are recorded in the Factory gate notes and worker final response. They are intentionally not self-embedded here because a commit cannot contain its own final SHA before it exists.

## R6 rerun — 2026-08-20T18:15:49Z
Current run `run-1787249479-190fd34d` re-inspected Agent Core Factory status from the assigned worktree and re-ran the Git ancestry audit without direct `factory.*` SQL:

- Sanctioned Factory status input: `/tmp/r6_factory_status_initial.json` (`db_backend=agent_core_postgres`, `factory_cli_source_root` and `factory_status_source_root` equal `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`).
- Current Factory project metadata still reports `reconciliation_anomalies=['source_increment_not_integrated']` and `reconciliation_required=True`; the active finding lists `53` blocker rows.
- Current G1 document rows are not the source of this anomaly: `14/14` required G1 rows are non-blocking at configured base `origin/main` `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- Current blocker audit output: `/tmp/r6_source_increment_audit_current.tsv`; exact summary `53/53` commit objects present, `53/53` contained in `origin/main`, `53/53` `increment_base_commit_after` chains valid, `0` waivers.
- Current positive terminal source-bearing task audit: `53/53` contained in `origin/main` with valid base-after chains.
- Recurrence guard: the prior R6 local evidence commit `60f19cb77c42dc0ef27dea43ecfdddd09b66e400` was not contained in `origin/main`, and remote `origin/factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated` still pointed at `9ea2756e6bfbce9d07c7ce32319a8b64bd8cea15`. This rerun therefore updates this evidence artifact and fast-forwards both the assigned branch and `origin/main` to the final R6 documentation commit after validation, so the reconciliation evidence source is itself contained in the canonical base.
- The final immutable branch commit and resulting `origin/main` commit are recorded in the Factory gate notes and worker final response. They are intentionally not self-embedded here because a commit cannot contain its own final SHA before it exists.

## Previous-run inputs and source roots
- Factory status before gate: `/tmp/r6_factory_status_after_ff.json` (Agent Core Postgres, generated from assigned worktree source root).
- Git audit table: `/tmp/r6_source_increment_audit_current.tsv`.
- Worktree: `/home/jean/Projects/.worktrees/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Assigned branch: `factory/zeus-alpha-research-ledger-core/reconcile-source_increment_not_integrated`.
- Worktree HEAD after fast-forward: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- `origin/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`; remote `refs/heads/main`: `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`.
- Current Factory task finding blocker rows inspected: `53`.
- G1 required blocking rows in sanctioned status readback: `0`.

## Previous-run verification commands
- `/home/jean/Projects/hermes-agent-original/venv/bin/python -m hermes_cli.main factory status zeus-alpha-research-ledger-core --json > /tmp/r6_factory_status_after_ff.json` → exit `0`, `db_backend=agent_core_postgres`, source roots equal the assigned worktree.
- `git fetch origin main +refs/heads/factory/zeus-alpha-research-ledger-core/*:refs/remotes/origin/factory/zeus-alpha-research-ledger-core/*` → exit `0`.
- For each blocker row: `git cat-file -e <commit>^{commit}`, `git merge-base --is-ancestor <commit> origin/main`, and, when `increment_base_commit_after` exists, `<commit> -> base_after -> origin/main` ancestry.
- `git merge --ff-only origin/main` on the assigned worktree → exit `0`; no primary checkout mutation.

## Previous run result
- Blockers audited: `53`.
- Commit objects present: `53/53`.
- Contained in current `origin/main`: `53/53`.
- `increment_base_commit_after` chain verified where present: `53/53`.
- Waivers used: `0`.
- Integration action performed in the previous run: no new merge to `main`; then-current origin base already contained every audited immutable source commit.

## 2026-08-20 rerun result
- Blockers audited from the current Factory finding: `53`.
- Commit objects present: `53/53`.
- Contained in current pre-push `origin/main` `71e5e7b2f4ace3b081f9446483784a3c5fb0b981`: `53/53`.
- `increment_base_commit_after` chain verified where present: `53/53`.
- Positive terminal source-bearing tasks independently audited: `53/53` contained in `origin/main`.
- Waivers used: `0`.
- Additional source-containment fix: publish this R6 evidence commit to the assigned branch and fast-forward `origin/main` to the same final commit after `git diff --check` and post-push readback.
- Scope boundary unchanged: docs/evidence only under `factory/projects/zeus-alpha-research-ledger-core/`; no deploy, no sandbox, no credential, no direct SQL, no primary checkout mutation.

## 2026-08-20 audited source increments

| Task | Branch | Immutable source commit | Commit source | Recorded/resulting base commit | Present | Contained in origin/main | Base-after chain | Waiver |
|---|---|---|---|---|---|---|---|---|
| `zeus-alpha-research-ledger-core-g1-document-status-technical-recovery-re` | `factory/zeus-alpha-research-ledger-core/inc-000-g1-document-status-technical-rec` | `0e991f41f05524a5aecf59747d42e166c59d14d7` | metadata_increment_branch_commit | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cl-canonical-g1-stale-primary-checkout` | `factory/zeus-alpha-research-ledger-core/inc-000-r2cl-canonical-g1-stale-primary` | `a5d297f6bc0f8211e28572b4eb5ce286193e8cab` | metadata_increment_branch_commit | `0ecd9019ba8ec111aaead60a911c9accd854f731` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2j-repair-pr-29-g1-canonical-state-evid` | `factory/zeus-alpha-research-ledger-core/inc-001-r2j-repair-pr-29-g1-canonical-st` | `c1943efb2b97b54b42bc5eabe858340d8c391116` | metadata_increment_branch_commit | `83d5ee06ba25859f047469baed223fe88e9467e3` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2k-repair-stale-canonical-g1-review-pro` | `factory/zeus-alpha-research-ledger-core/inc-001-r2k-repair-stale-canonical-g1-re` | `73b74f03e3c73830f69fb487a7439529190c21c2` | metadata_increment_branch_commit | `ab08b13669903a87b3d60d6c80231d23d6313782` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2m-current-base-g1-documentation-pr-rec` | `factory/zeus-alpha-research-ledger-core/inc-001-r2m-current-base-g1-documentatio` | `892a0b1e0845e9ede67b9fd57b08d9770a2a1b6a` | metadata_increment_branch_commit | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2w-canonical-g1-reviewed-frontmatter-pr` | `factory/zeus-alpha-research-ledger-core/inc-001-r2w-canonical-g1-reviewed-frontm` | `ce79f0159694fda5e74de7cd5913ab0e2704e2a7` | metadata_increment_branch_commit | `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2z-repair-canonical-g1-document-status-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2z-repair-canonical-g1-document` | `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` | metadata_increment_branch_commit | `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2c5-independent-current-base-g1-review-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2c5-independent-current-base-g1` | `e81db07a832a66643ac8f30f652c5e4da4fe8748` | metadata_increment_branch_commit | `40a188b23a384901f983e4d959d3ebbecf50b318` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2c6-bounded-current-origin-g1-resolver-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2c6-bounded-current-origin-g1-r` | `005a844cb630b2298dd01ede0279e2f69e88e5f3` | metadata_increment_branch_commit | `784d880d17f1c58fc6c8e1c0e1f3b73af7a569b3` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2aj-canonical-g1-document-status-recove` | `factory/zeus-alpha-research-ledger-core/inc-001-r2aj-canonical-g1-document-statu` | `b525254809fba0ad46e6b7e9405778c44e64bae9` | metadata_increment_branch_commit | `bf422968f9ea73d70d4ac1e8b8bae4af644ce079` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2at-current-origin-g1-documentation-val` | `factory/zeus-alpha-research-ledger-core/inc-001-r2at-current-origin-g1-documenta` | `d4ac6d89994adf823bb50b79afe5a39fd204fdfd` | metadata_increment_branch_commit | `2b53ee0f14491ff43da7683d475654a03af5d678` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2au-current-origin-g1-document-status-p` | `factory/zeus-alpha-research-ledger-core/inc-001-r2au-current-origin-g1-document` | `1afd37a61a8d21af393e393cb77083adb25b41c7` | metadata_increment_branch_commit | `af9fa27eaaaa52ef173f1578fb7f572ce52cebc6` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2aw-isolated-current-origin-factory-g1-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2aw-isolated-current-origin-fac` | `dcd9c74f252d288269d746ab59079a0221de7a46` | metadata_increment_branch_commit | `b05afe59c88cfa7f7dbec0117603b2f052267ce0` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cm-repair-g1-review-state-provenance-a` | `factory/zeus-alpha-research-ledger-core/inc-001-r2cm-repair-g1-review-state-prov` | `271241a0dc9525b90fdb706b1fe23f7d53199a18` | metadata_increment_branch_commit | `fa24950a228f28d5106ee2125d42045e872f9504` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ap-reconcile-residual-g1-task-metadata` | `factory/zeus-alpha-research-ledger-core/inc-001-r2ap-reconcile-residual-g1-task` | `8e3ac22d7ec0f11d29c9c1938a69a33247bb86ec` | metadata_increment_branch_commit | `34a58a6e1c89a66d1e6f177771ba6f9a8cb78af4` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ba-current-base-g1-independent-review-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2ba-current-base-g1-independent` | `2dfa2d9a56f15ab89094173db9674bc50f260679` | metadata_increment_branch_commit | `faddaf5afb4c1754e03d8c97dd6706353b5b0865` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2bl-non-destructive-canonical-g1-eviden` | `factory/zeus-alpha-research-ledger-core/inc-001-r2bl-non-destructive-canonical-g` | `5448acf3a4a27061966665f9fbe509280cb4ed2c` | metadata_increment_branch_commit | `42c86619b91b3a290462c9582e81499e7de8c4c4` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cx-current-origin-documentation-index-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2cx-current-origin-documentatio` | `5a3b1caaa87abb42e37035c8c52a17cca4af9817` | metadata_increment_branch_commit | `c3c9332e7a5f0e3a41c49cfb0b190dfe16a8e12e` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2dg-bounded-g1-exact-sha-independent-re` | `factory/zeus-alpha-research-ledger-core/inc-001-r2dg-bounded-g1-exact-sha-indepe` | `5f13f71407a0ff6966666c016d47d281ba02a5af` | metadata_increment_branch_commit | `abc164184d588a7a9e5e4838f5a101d9f4e3a0f2` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2dl-g1-documentation-dispatch-validator` | `factory/zeus-alpha-research-ledger-core/inc-001-r2dl-g1-documentation-dispatch-v` | `598993a75cbc9e77db4b95119870cf6435d06a59` | metadata_increment_branch_commit | `71e5e7b2f4ace3b081f9446483784a3c5fb0b981` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2i-g1-documentation-independent-exact-s` | `factory/zeus-alpha-research-ledger-core/inc-002-r2i-g1-documentation-independent` | `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` | metadata_increment_branch_commit | `5e1e4622e93d8d2fabdfe0f2176889a29afa7f7c` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ab-independent-g1-review-recovery-for-` | `factory/zeus-alpha-research-ledger-core/inc-001-r2ab-independent-g1-review-pr43` | `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` | metadata_increment_branch_commit | `1b6bc0f65d3ad49845d20e056203e3b3702ac2a7` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2v-canonical-g1-status-and-no-auto-merg` | `factory/zeus-alpha-research-ledger-core/inc-005-r2v-canonical-g1-status-and-no-a` | `214b48b00d5db8c4766bb634cba305e95d0adb53` | metadata_increment_branch_commit | `df79aac9d306c0b055fe88dbde5ebd54d9635e36` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2di-docs-first-fail-closed-review-termi` | `factory/zeus-alpha-research-ledger-core/inc-009-r2di-docs-first-fail-closed-revi` | `4819f5ff47ad8f2a55f00b7c96edac22646d5d43` | metadata_increment_branch_commit | `71e5e7b2f4ace3b081f9446483784a3c5fb0b981` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2dh-docs-first-current-base-g1-review-s` | `factory/zeus-alpha-research-ledger-core/inc-010-r2dh-docs-first-current-base-g1` | `e4b00fd57759420cb81c8f3ee0df98af490a9e2b` | metadata_increment_branch_commit | `cc43e6dace789da06d103ba512a3f4863fb0edc9` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cn-bounded-canonical-g1-docs-gate-and-` | `factory/zeus-alpha-research-ledger-core/inc-015-r2cn-bounded-canonical-g1-docs-g` | `da1c70dc197a584791ed2ee66a3641eb84cbd3ab` | metadata_increment_branch_commit | `6c07c2fee59679a5b0063e635f0332895dbb3ec5` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cz-exact-sha-quality-gate-948-recovery` | `factory/zeus-alpha-research-ledger-core/inc-016-r2cz-exact-sha-quality-gate-948` | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` | metadata_increment_branch_commit | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2dc-bounded-g1-reviewed-state-recovery-` | `factory/zeus-alpha-research-ledger-core/inc-016-r2dc-bounded-g1-reviewed-state-r` | `02597d60712bba07a2fd9153c002143d86cf3e0f` | metadata_increment_branch_commit | `538ffcbe16012f330b2a21734af7dec4bd442934` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2aj-isolated-current-base-g1-documentat` | `factory/zeus-alpha-research-ledger-core/inc-017-r2aj-isolated-current-base-g1-do` | `32e41ce325a140812303ac898e64702478f5d338` | metadata_increment_branch_commit | `4a0a6bbaea3b1acaf8e83084c058b831d865d8c4` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ao-repair-current-origin-g1-control-pl` | `factory/zeus-alpha-research-ledger-core/inc-017-r2ao-repair-current-origin-g1-co` | `d2fa09bf67a144b32b23d62bca53c4cbd7d6e3c4` | metadata_increment_branch_commit | `3e32da02c218e06a69b851641b2d454113654378` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ar-isolated-current-base-g1-spec-secur` | `factory/zeus-alpha-research-ledger-core/inc-017-r2ar-isolated-current-base-g1-sp` | `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1` | metadata_increment_branch_commit | `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2av-current-origin-g1-status-projection` | `factory/zeus-alpha-research-ledger-core/inc-017-r2av-current-origin-g1-status-pr` | `7c9aac624534f676f33527416ff209cdbbfb9270` | metadata_increment_branch_commit | `52df8d7c6599e3ec2ec4559e0139ffd91ec74011` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2bj-bounded-canonical-g1-documentation-` | `factory/zeus-alpha-research-ledger-core/inc-017-r2bj-bounded-canonical-g1-docume` | `8f5f858c5f7b0ad696cff8c8945364b32dd2df25` | metadata_increment_branch_commit | `b260baea223e863b35fe561e6c5d3d77f3a914c9` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ai-r2-non-destructive-current-origin-g` | `factory/zeus-alpha-research-ledger-core/inc-017-r2ai-r2-non-destructive-current` | `dfdb8d91e604e16a039299ea7872230c3bad2a94` | metadata_increment_branch_commit | `c31e937111bba64e478d3c319e896774bf09e40e` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2az-non-destructive-current-base-g1-evi` | `factory/zeus-alpha-research-ledger-core/inc-017-r2az-non-destructive-current-bas` | `bb99d21547ff14fabe175741d5a5e400c99c922e` | metadata_increment_branch_commit | `756ac62a4c69278216b2b7e66b34e6f11ad54c29` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2da-exact-sha-security-gate-949-recover` | `factory/zeus-alpha-research-ledger-core/inc-017-r2da-exact-sha-security-gate-949` | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` | metadata_increment_branch_commit | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2db-current-origin-g1-reviewed-state-pr` | `factory/zeus-alpha-research-ledger-core/inc-017-r2db-current-origin-g1-reviewed` | `bd820a57818db852b07ef9c4c69085087c0c1c98` | metadata_increment_branch_commit | `538ffcbe16012f330b2a21734af7dec4bd442934` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2c2-autonomous-canonical-g1-documentati` | `factory/zeus-alpha-research-ledger-core/inc-018-r2c2-autonomous-canonical-g1-doc` | `71e428a18ba486c313995f5a1a69a9bd48264a59` | metadata_increment_branch_commit | `2a32066398d500d6dac071bd7f2184d47bb3bcb4` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2bb-current-base-g1-status-projection-a` | `factory/zeus-alpha-research-ledger-core/inc-018-r2bb-current-base-g1-status-proj` | `ad4c94d2d33e58aa4741c8c7f5e90e460495cfdc` | metadata_increment_branch_commit | `b503ba3b57fd606956d0ebf925c83eda253bdcc5` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2as-r2-independent-exact-sha-g1-source-` | `factory/zeus-alpha-research-ledger-core/inc-018-r2as-r2-independent-exact-sha-g1` | `e45601137fbb5b783f48b95c0e06e73ec505dbf4` | metadata_increment_branch_commit | `e7e216272ea64a83351ae38f27688ecda47cbbbf` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ax-current-origin-factory-cli-g1-recov` | `factory/zeus-alpha-research-ledger-core/inc-018-r2ax-current-origin-factory-cli` | `0ff5d3f4471c41bf1203d0c02b80794dcd972d5a` | metadata_increment_branch_commit | `3b7bc91f2ee1ef603bb512d147c692568c1b465f` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2bm-canonical-g1-docs-gate-source-root-` | `factory/zeus-alpha-research-ledger-core/inc-018-r2bm-canonical-g1-docs-gate-sour` | `06051d990821bc7127004313ca3458e0394832d8` | metadata_increment_branch_commit | `9ebaa9e7b44c61bb871ca4da0a838c52e62666b2` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2bn-canonical-g1-review-state-source-ro` | `factory/zeus-alpha-research-ledger-core/inc-018-r2bn-canonical-g1-review-state-s` | `5dcf7d14746457148b045e2ed94aed6114054e6d` | metadata_increment_branch_commit | `0db9bed7ed9e8ec4dbefda41f95a335ab82fbbc0` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2u-canonical-g1-document-status-preflig` | `factory/zeus-alpha-research-ledger-core/inc-019-r2u-canonical-g1-document-status` | `a520b42ffd9d479b03989738b6807ec101ff808b` | metadata_increment_branch_commit | `50a9a29c4bb7cee39c8ffafa857ce962066e35cb` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ah-current-origin-g1-reviewed-marker-a` | `factory/zeus-alpha-research-ledger-core/inc-019-r2ah-current-origin-g1-reviewed` | `1075c3e570432b4b7b77b57ff8dfdf210d84610f` | metadata_increment_branch_commit | `dbde1790f8d45f111bc69b3491a1862eafb29fa2` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2c4-repair-canonical-g1-document-status` | `factory/zeus-alpha-research-ledger-core/inc-019-r2c4-repair-canonical-g1-documen` | `5c9eb14563422a8bb468f127a449784c95ecb4f5` | metadata_increment_branch_commit | `91aa62b11f02f69d88f7d8c18c30033edb4b7355` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2c7-repair-current-origin-g1-document-s` | `factory/zeus-alpha-research-ledger-core/inc-019-r2c7-repair-current-origin-g1-do` | `b145e3b9fb87f3a42f1b313a51ebcb6c0b898279` | metadata_increment_branch_commit | `b525254809fba0ad46e6b7e9405778c44e64bae9` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ap-current-origin-g1-document-validati` | `factory/zeus-alpha-research-ledger-core/inc-019-r2ap-current-origin-g1-document` | `b50585881869686c4db2904f98726aca7471dd57` | metadata_increment_branch_commit | `a41acdc4820b92a31b7d42d9a9c28e95b875a3d1` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2ct-bounded-canonical-g1-documentation-` | `factory/zeus-alpha-research-ledger-core/inc-019-r2ct-bounded-canonical-g1-docume` | `8d19b1a47c4ec91002306cc03345d0b4ab2f5cbb` | metadata_increment_branch_commit | `ccbbcb131cfdbeb6ce170ed8cf57dc6edbb6a257` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cu-primary-root-docs-first-g1-resolver` | `factory/zeus-alpha-research-ledger-core/inc-019-r2cu-primary-root-docs-first-g1` | `e2e46c0b22efc8446dad449bdf3c71658e2b9e53` | metadata_increment_branch_commit | `12f5696882f04ee24b6fd1bf957abafaf76eab31` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2cv-current-origin-g1-documentation-val` | `factory/zeus-alpha-research-ledger-core/inc-019-r2cv-current-origin-g1-documenta` | `acdbb1f7fafa90311e897ba3f7f1693041f25921` | metadata_increment_branch_commit | `18ef28e6845d2d15dd0ec3cd7d8bb9b7630b71cc` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2al-current-base-factory-cli-source-ske` | `factory/zeus-alpha-research-ledger-core/inc-035-r2al-current-base-factory-cli-so` | `b525254809fba0ad46e6b7e9405778c44e64bae9` | metadata_increment_branch_commit | `b525254809fba0ad46e6b7e9405778c44e64bae9` | yes | yes | yes | false |
| `zeus-alpha-research-ledger-core-r2am-repair-stale-primary-factory-tick-s` | `factory/zeus-alpha-research-ledger-core/inc-035-r2am-repair-stale-primary-factor` | `e07925bc20e9220de92dbb8804560348d471dbe7` | metadata_increment_branch_commit | `139df9ae49137bb4b16152550d53d385310de3b6` | yes | yes | yes | false |

## Boundary notes
- No deploy or sandbox was performed; this increment has no runtime delivery scope.
- No direct `factory.*` SQL was used. Factory DB interaction is limited to sanctioned `factory status` and `factory gate record`.
- No credentials were read or changed.
- The primary checkout `/home/jean/Projects/hermes-agent-original` was not checked out, merged, or modified.
