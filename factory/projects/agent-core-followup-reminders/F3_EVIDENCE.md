# F3 Evidence — Implementation Plan and Task Graph (Rework — Second Iteration)

## Estado

- Incremento: F3 — Implementation plan and task graph
- Run: `run-1780713290-73c13049` (segundo rework)
- Owner: `implementation-planner`
- Fecha de cierre: `2026-06-05`
- Reviewer: `factory-orchestrator`
- Run type: rework

## Contexto del rework (segunda iteracion)

El primer rework (`run-1780712703-2092c8a2`) entregó sprint decomposition y risk register, pero falló en:
1. F9/F10/F11 no estaban descompuestos en sub-tareas implementables en TASK_GRAPH.md
2. Owner/reviewer no eran explícitos a nivel sub-tarea (faltantes en F4.3-F4.7, F5.1-F5.8, F6.1-F6.2, F7.1-F7.5, F8.1-F8.3)
3. Sub-tareas sin table rows con file/artifact y verification command explícitos
4. IMPLEMENTATION_PLAN.md no incluía F9/F10/F11 como fases ejecutables
5. Typo: `clude-builder` en lugar de `claude-builder` en línea 404

Esta segunda iteración corrige los 5 puntos.

## Archivos generados / actualizados

|| Archivo | Status | Delta vs. iteracion anterior |
|---------|--------|------------------------------|
| `TASK_GRAPH.md` | actualizado | F9/F10/F11 completos añadidos; owner/reviewer/table rows en todas las sub-tareas F4.3-F8.3 |
| `IMPLEMENTATION_PLAN.md` | actualizado | F9/F10/F11 fases completas añadidas; typo `clude-builder` corregido |
| `F3_EVIDENCE.md` | este archivo | Refleja segunda iteracion de rework |
| `TRACKER.md` | actualizado separately | — |

## Gate request: planning

Este incremento solicita registrar gate `planning=pending` para que `factory-orchestrator` revise y apruebe/rechace. Gate requerido para iniciar Sprint 1 (F4).

## Verificación de completitud (AC de F3)

### AC1: Task graph descompone todos los incrementos en tareas implementables

- [x] F4.1–F4.8: cada una con table rows (File, Owner, Reviewer, Verification, Output, Evidence)
- [x] F5.1–F5.9: cada una con table rows completas
- [x] F6.1–F6.3: cada una con table rows completas
- [x] F7.1–F7.6: cada una con table rows completas
- [x] F8.1–F8.3: cada una con table rows completas
- [x] F9.1–F9.6: todas añadidas con table rows
- [x] F10.1–F10.5: todas añadidas con table rows
- [x] F11.1–F11.5: todas añadidas con table rows
- [x] Dependencias explícitas en cada sub-tarea
- [x] Verification commands exactos para cada sub-tarea

### AC2: Ninguna tarea tiene el mismo implementer y reviewer

Verificación por tabla:

|| Tarea | Owner | Reviewer | OK? |
|-------|-------|---------|-----|
| F4.1–F4.8 | claude-builder | codex-builder | OK |
| F5.1–F5.9 | claude-builder | quality-reviewer | OK |
| F6.1–F6.3 | claude-builder | devops-release | OK |
| F7.1–F7.6 | claude-builder | product-analyst | OK |
| F8.1–F8.3 | claude-builder | quality-reviewer | OK |
| F9.1–F9.6 | qa-verifier | quality-reviewer | OK |
| F10.1–F10.5 | security-reviewer | zeus | OK |
| F11.1–F11.5 | devops-release | factory-orchestrator | OK |

### AC3: Plan incluye delivery evidence requirements y gates

- [x] Cada sub-tarea tiene columna Evidence con artifact/output esperado
- [x] Gates table actualizada con F4–F11
- [x] Dependencias gates listadas en IMPLEMENTATION_PLAN.md
- [x] F9 incluye smoke test live/direct con verificación de flujo completo
- [x] F10 incluye comandos de verificación de security (SQL injection, PII, etc.)
- [x] F11 incluye Factory DB update commands como evidencia

## Gate dependencies verificadas

|| Gate | Status | Verificado en |
|------|--------|---------------|
| intake (F0) | passed | TRACKER.md |
| functional (F1) | passed | TRACKER.md |
| architecture (F2) | passed (security-reviewer) | TRACKER.md |
| planning (F3) | este incremento — solicita factory-orchestrator | — |
| implementation | blocked — esperando planning + architecture | TRACKER.md |

## Decisiones de planificación tomadas (segunda iteracion)

1. **F9-F11 sprint unificado**: Sprint 6 = QA (F9) + Security (F10) + Delivery (F11). Se ejecutan en secuencia pero dentro del mismo sprint para eficiencia.

2. **F5 dividida en 9 sub-tareas** (F5.1–F5.9) para granularidad de review. F5.9 = tests.

3. **F7 reza sobre `activity_plan_tool.py`** (nuevo archivo) para separar concerns de F5.

4. **F8 ahora modifica `crm_tool.py`** existente, no crea adapter nuevo.

5. **Smoke test live/direct (F9.5)**: se ejecuta desde CLI de Hermes Agent real, no solo pytest.

6. **F10 security-reviewer ≠ implementer**: todas las tasks de security son `security-reviewer` como owner, nunca `claude-builder`.

7. **Typo corregido**: `clude-builder` → `claude-builder` en IMPLEMENTATION_PLAN.md línea 404.

## Handoff a siguientes workers

### Para `claude-builder` (Sprint 1 — F4)

**Requisitos:**
- Esperar hasta que `architecture=passed` (F2) Y `planning=passed` (F3) estén en Factory DB.
- Crear directorio `db/modules/activity/` y 8 archivos de migración.
- Cada migración debe ser idempotente (IF NOT EXISTS / ON CONFLICT).
- Ejecutar dry-run antes de apply real.
- Verificar cada tabla con `\d` y query de readback.
- Registrar evidencia en `tests/migrations/test_activity_schema.py`.

**Entregables de Sprint 1:**
- 8 archivos SQL en `db/modules/activity/`
- Output de dry-run para cada archivo
- Readback queries confirmando schema creado
- Tests de idempotencia (ejecutar migración dos veces → mismo resultado)

### Para `claude-builder` (Sprint 2 — F5)

**Requisitos:**
- Esperar hasta que Sprint 1 (F4) esté verificado en test DB.
- Crear `tools/activity_tool.py` con todos los handlers listados.
- Registrar cada handler con `registry.register()`.
- Tests van en `tests/tools/test_activity_tool.py`.
- Tool output siempre JSON (no prose).

### Para `devops-release` (F6 reviewer)

- F6 incluye `cron/activity_dispatcher.py` — revisar que no tenga side effects externos sin audit.
- Dispatcher no envía notificaciones; solo prepara output para consumo interno.

### Para `codex-builder` (F8)

- Leer `tools/crm_tool.py` antes de modificar.
- Mantener backward compatibility.
- Schema audit en F8.1 antes de implementar bridge.

### Para `qa-verifier` (F9)

- F9 smoke tests requieren que F5-F8 estén implementados.
- F9.5 smoke test live/direct debe ejecutarse manualmente desde Hermes Agent CLI.
-证据: pytest output + smoke test output del CLI.

### Para `security-reviewer` (F10)

- F10 puede iniciar en cuanto F9 tenga todos los tests pasando.
- F10.3 (dedupe_key PII review) requiere DB con datos de prueba.

### Para `devops-release` (F11)

- F11.3 dry-run de migrations puede ejecutarse en paralelo con F10.
- F11.5 requiere acceso a Factory DB.

## Verificación de completitud F3 (esta iteracion)

- [x] `TASK_GRAPH.md` — F9/F10/F11 completos con sub-tareas, owner, reviewer, table rows
- [x] `TASK_GRAPH.md` — F4.3-F4.8 con owner/reviewer/table rows explícitos
- [x] `TASK_GRAPH.md` — F5.1-F5.9 con owner/reviewer/table rows explícitos
- [x] `TASK_GRAPH.md` — F6.1-F6.3 con owner/reviewer/table rows explícitos
- [x] `TASK_GRAPH.md` — F7.1-F7.6 con owner/reviewer/table rows explícitos
- [x] `TASK_GRAPH.md` — F8.1-F8.3 con owner/reviewer/table rows explícitos
- [x] `IMPLEMENTATION_PLAN.md` — F9/F10/F11 como fases completas
- [x] `IMPLEMENTATION_PLAN.md` — typo `clude-builder` corregido
- [x] `IMPLEMENTATION_PLAN.md` — Gates table incluye F9/F10/F11
- [x] `F3_EVIDENCE.md` — refleja segunda iteracion de rework
- [x] AC1: todas las sub-tareas tienen table rows con verification command
- [x] AC2: ningún owner=reviewer en ninguna sub-tarea
- [x] AC3: delivery evidence y gates completos

## Siguiente accion

1. `factory-orchestrator` revisa este package y registra `planning=passed` o `planning=failed` en Factory DB.
2. Una vez `planning=passed` Y `architecture=passed` (F2), `claude-builder` puede iniciar Sprint 1 (F4).
3. Gates F9/F10 se registran automáticamente cuando F8/F9 completen.
