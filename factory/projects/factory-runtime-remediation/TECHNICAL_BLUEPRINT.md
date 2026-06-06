# Technical Blueprint — Factory Runtime Remediation

## Componentes modificados

### `hermes_cli/factory_pg.py`

Responsable del runtime canónico Postgres.

Cambios:

- Clasificación de blockers:
  - `classify_factory_blocker()`
  - `classify_factory_blockers()`
  - `record_factory_blocker_actions()`
- Alertas:
  - `factory_watchdog_alerts()`
- Dispatcher seguro:
  - claims incluyen proyectos `blocked`
  - `force_tick()` repara/reabre antes de claim
- Reconciliación:
  - el proyecto expone `alerts` en `status()`.

### `~/.hermes/scripts/factory_blocker_detector.py`

Ahora:

- lee sólo Agent Core Postgres vía `factory_backend.get_backend()`;
- clasifica blockers;
- registra acciones;
- crea preguntas humanas indispensables;
- emite JSON con `needs_attention`.

### `~/.hermes/scripts/factory_orchestrator_tick.py`

Ahora:

- preserva contador `claimed_null_rounds`;
- reporta `alerts`;
- incluye reparaciones `unblocked`;
- no hereda stdout/stderr de workers.

### `~/.hermes/scripts/factory_status_sync.py`

Ahora incluye conteos de `alerts` por proyecto.

### `~/.hermes/scripts/factory_watchdog_alerts.py`

Nuevo cron script-only:

- silencioso cuando no hay alertas;
- suprime alertas repetidas;
- entrega a `origin,telegram`.

## Datos y contratos

### Blocker classification

```json
{
  "action_category": "auto_resolvable | technical_rework | human_question_required | stale_orphan_state",
  "blocker_category": "...",
  "recommended_action": "...",
  "requires_human": true,
  "alert_key": "factory:<project>:<task>:<category>"
}
```

### Alerts

```json
{
  "alert_type": "autonomous_project_blocked_too_long | blocked_without_human_question | orphan_inflight_without_active_run | cron_claimed_null_repeated",
  "severity": "medium | high",
  "project_id": "...",
  "message": "..."
}
```

## Seguridad

- No incluir logs crudos ni secrets en notificaciones.
- `human_questions` debe contener pregunta clara y mínima.
- `blocked` no puede saltarse dependencies.
- Factory DB es la única fuente de estado operativo.
