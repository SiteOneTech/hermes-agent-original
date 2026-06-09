# Methodology Plan — Factory Runtime Evolution

## Método

**Hybrid Factory**: combina disciplina documental/PM tipo BMAD con Agent Core Factory DB, gates determinísticos y ejecución supervisada por Zeus.

## Contrato metodológico

| Elemento | Decisión |
|---|---|
| Fuente operativa | Agent Core Postgres `factory.*` |
| Capa PM humana | Notion project page obligatoria |
| Artifacts repo | `factory/projects/factory-runtime-evolution/` |
| Autonomía | Nivel 3: agentes/Zeus ejecutan, gates/reconciliación verifican |
| Kanban | No usado; Factory DB es canónico |
| Cierre | Solo con docs + Notion + gates + reconciliación sin anomalías |

## Fases

1. **F0 — Intake y metodología**: definir scope, PRD, ADRs, task graph, Notion.
2. **F1 — Blocker detector**: clasificar blockers y crear acciones.
3. **F2 — Watchdog/alerts**: cron/dashboard y notificación.
4. **F3 — Dispatcher blocked-safe**: reparación y continuación autónoma.
5. **F4 — QA y cierre**: tests, smoke, delivery report, Notion update.
6. **F5 — Corrección metodológica**: cerrar deuda de documentos/Notion generada por el primer intento.

## Gates requeridos

- Intake
- Planning
- Implementation
- Quality
- Test
- Security
- Delivery
- Reconciliation

## Regla corregida

Un proyecto Factory no se marca `completed` si falta Notion o documentos requeridos. Si se ejecutó por urgencia, se marca deuda metodológica y se corrige antes del cierre final.
