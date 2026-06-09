# Methodology Plan

Project: `factory-runtime-docs-notion-refactor`
Created: 2026-06-09T23:05:00Z

## Method

Hybrid Factory, high risk, docs-first, TDD-first for runtime changes.

## Gate order

G0 repo strategy → kickoff artifact pack → Notion/linking plan → failing regression tests → implementation → independent quality/security review → live smoke → delivery gate → Jean GO/NO-GO.

## Special rule

This project is allowed to implement the missing Notion metadata write path. It must not declare GREEN by manually muting Notion/docs anomalies.

## Worker contract

Workers must read `DOCUMENTATION_INDEX.md`, `PRD.md`, `ADRS.md`, `TECHNICAL_BLUEPRINT.md`, `SPRINT_PLAN.md`, `TASK_GRAPH.md`, and the Factory DB task acceptance criteria before editing code.
