# ADRs — Factory Runtime Remediation

## ADR-001 — Notion es obligatorio para todo proyecto Factory

**Estado:** Accepted

**Decisión:** Todo proyecto Factory debe crear una página Notion project-specific al kickoff o, si se detecta que falta, debe quedar como anomalía real hasta construirse. No se debe usar `notion_waived` como ruta normal para proyectos Factory.

**Rationale:** Jean necesita supervisión ejecutiva y PM estándar sin pedirla. Notion es la capa humana del Factory, mientras Factory DB/repo siguen siendo la fuente canónica operativa.

**Consecuencia:** El reconciler y el proceso operativo deben tratar `missing_notion_project` como deuda metodológica que se corrige, no como algo que se esquiva.

---

## ADR-002 — Paquete documental obligatorio antes del cierre

**Estado:** Accepted

**Decisión:** Un proyecto Factory no debe cerrarse como `completed` si faltan documentos requeridos: PRD, ADRs, methodology plan, technical blueprint, sprint plan, task graph, tracker, documentation index, QA/security gates, QA/security reports y delivery report.

**Rationale:** El objetivo del Factory es proceso repetible, no ejecución ad-hoc.

**Consecuencia:** Los waivers de documentos solo deben existir para excepciones explícitas aprobadas por Jean, no para acelerar un correctivo.

---

## ADR-003 — Factory DB sigue siendo fuente operativa

**Estado:** Accepted

**Decisión:** Las páginas Notion y documentos repo son capas de PM/evidencia; las decisiones operativas se reconcilian desde Agent Core Postgres `factory.*`.

**Rationale:** Evita que Notion/Kanban sustituyan el runtime.

**Consecuencia:** Metadata de Factory DB debe linkear Notion y artifacts, pero no depender de Notion para claimed/dispatch/gates.

---

## ADR-004 — Blocked no es estado absorbente

**Estado:** Accepted

**Decisión:** El dispatcher puede actuar sobre proyectos `blocked` para reparar huérfanos, reabrir blockers resueltos y continuar tareas independientes con dependencias satisfechas.

**Rationale:** Un blocker no debe paralizar todo el proyecto si Zeus puede resolver o avanzar otras tareas.

**Consecuencia:** `p.status IN ('active','planned','intake','blocked')` en claims seguros, manteniendo single-active-run y dependency guards.

---

## ADR-005 — Alertas determinísticas y silenciosas por defecto

**Estado:** Accepted

**Decisión:** El watchdog debe ser script-only y silencioso sin alertas. Solo emite mensajes para alertas no suprimidas y debe entregar a `origin,telegram`.

**Rationale:** Jean no debe monitorear logs ni recibir spam.

**Consecuencia:** `factory_watchdog_alerts.py` registra estado de supresión y sólo imprime cuando se requiere atención.
