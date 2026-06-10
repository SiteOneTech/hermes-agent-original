# Notion Update

Project: `factory-runtime-docs-notion-refactor`
Updated: 2026-06-10T00:33:44Z

## R1 status

Status: `DONE` for canonical Notion PM metadata linking.

Project-specific Notion PM page:

- Title: `Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM`
- Page ID: `37b37b39-cad6-817e-ab89-c881329c0db0`
- URL: `https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0`
- Parent page: `🏭 Software Factory — Reportes Ejecutivos` (`36d37b39-cad6-81c6-8b83-db65c4bf6e95`)

## Evidence

Creation/linking evidence:

```text
python3 Notion API create-page smoke (no repo temp script)
result: {"ok": true, "action": "created", "id": "37b37b39-cad6-817e-ab89-c881329c0db0", "url": "https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0"}
```

Canonical Factory metadata command:

```text
./hermes factory project link-notion factory-runtime-docs-notion-refactor \
  --page-id 37b37b39-cad6-817e-ab89-c881329c0db0 \
  --url https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0 \
  --page-title 'Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM' \
  --actor factory-orchestrator --json
```

Readback returned by the canonical command:

```json
{
  "action": "link-notion",
  "project_id": "factory-runtime-docs-notion-refactor",
  "readback": {
    "notion_tracker_page_id": "37b37b39-cad6-817e-ab89-c881329c0db0",
    "notion_tracker_title": "Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM",
    "notion_tracker_url": "https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0"
  },
  "reconcile": {
    "status": "active",
    "anomalies": []
  }
}
```

Independent Factory status readback after link:

```text
./hermes factory status factory-runtime-docs-notion-refactor --json | jq '{...}'
```

Returned:

```json
{
  "db_backend": "agent_core_postgres",
  "project": {
    "project_id": "factory-runtime-docs-notion-refactor",
    "status": "active",
    "metadata": {
      "notion_tracker_page_id": "37b37b39-cad6-817e-ab89-c881329c0db0",
      "notion_tracker_url": "https://app.notion.com/p/Factory-Runtime-Docs-Notion-Control-Plane-Refactor-Factory-PM-37b37b39cad6817eab89c881329c0db0",
      "notion_tracker_title": "Factory Runtime Docs/Notion Control-Plane Refactor — Factory PM",
      "notion_tracker_linked_at": "2026-06-10T00:33:44.742932Z",
      "notion_tracker_source": "hermes factory project link-notion",
      "reconciliation_anomalies": [],
      "reconciliation_required": false
    }
  },
  "alerts": []
}
```

## Acceptance mapping

- Project-specific Notion PM page exists: satisfied by Notion API create-page response and URL above.
- `hermes factory project link-notion` writes and reads back Notion metadata without direct SQL: satisfied by canonical command readback above.
- `missing_notion_project` cleared only after DB metadata readback: satisfied by post-link Factory status readback showing `reconciliation_anomalies: []` and `reconciliation_required: false` after `notion_tracker_*` metadata was present.

## Notes

No direct SQL, `psql`, `psycopg2`, or ad-hoc `factory.*` writes were used. Notion is a human PM projection only; Factory DB + repo artifacts remain canonical.
