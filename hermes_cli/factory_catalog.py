"""Static SitioUno Factory catalog shared by Postgres runtime and CLI.

This module intentionally contains no persistence backend. Keep static role and
methodology definitions here so production code never imports the legacy SQLite
module just to reuse constants.
"""
from __future__ import annotations

import re

VALID_METHODS = {"zeus_native", "bmad_hybrid", "hybrid", "dual_lane"}
DEFAULT_LANES = (
    ("zeus", "Zeus Native", "zeus_native"),
    ("bmad", "BMAD Hybrid", "bmad_hybrid"),
)
FACTORY_CANONICAL_SKILL = "factory-agent-operating-canon"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def factory_skills(*skills: str) -> list[str]:
    """Return every role skill list with the shared Factory operating canon first."""

    ordered: list[str] = []
    for skill in (FACTORY_CANONICAL_SKILL, *skills):
        if skill and skill not in ordered:
            ordered.append(skill)
    return ordered


def slugify(value: str) -> str:
    text = (value or "").strip().lower()
    text = _SLUG_RE.sub("-", text).strip("-")
    return text or "factory-project"


FACTORY_AGENTS = [
    ("factory-orchestrator", "Factory Orchestrator", "Intake, routing, gates, metrics, reports", "zeus", ["factory", "delegation", "terminal", "file", "cronjob", "skills", "web"], factory_skills("software-factory-orchestration", "programming-delegation-engines"), ["deploy", "destructive", "credential-change"]),
    ("product-analyst", "Product Analyst", "Functional analysis, PRD, acceptance criteria", "zeus", ["file", "web", "session_search", "skills", "factory"], factory_skills("writing-plans", "agent-core-followup-reminders"), ["publish"]),
    ("solution-architect", "Solution Architect", "Architecture, boundaries, integration design", "claude_code", ["terminal", "file", "web", "skills", "factory"], factory_skills("writing-plans", "codebase-inspection"), ["architecture-approval"]),
    ("implementation-planner", "Implementation Planner", "Epics, stories, dependencies, task graph", "zeus", ["file", "terminal", "skills", "factory", "session_search", "todo"], factory_skills("writing-plans", "test-driven-development", "software-factory-orchestration"), []),
    ("ux-ui-designer", "UX/UI Designer", "Specialized UX/UI design, Open Design prototyping, frontend interface implementation, premium visual QA, responsive/browser evidence, and design-system handoff", "zeus", ["browser", "vision", "file", "terminal", "web", "factory", "skills", "session_search"], factory_skills("open-design-hermes", "ux-ui-open-tech-stack", "ui-ux-pro-max", "impeccable", "design-taste-frontend", "high-end-visual-design", "popular-web-designs", "professional-copy-auditor", "sitiouno-reference-assets", "playwright-factory-qa", "dogfood", "claude-design", "sketch", "excalidraw", "hyperframes-render"), ["external-write", "commercial-license", "production-deploy"]),
    ("claude-builder", "Claude Builder", "Complex implementation and refactors with native Anthropic Claude Code / Opus", "claude_code", ["terminal", "file", "web", "skills", "factory"], factory_skills("claude-code", "test-driven-development"), []),
    ("claude-deepseek-builder", "Claude DeepSeek Builder", "Claude Code workflow backed by DeepSeek Anthropic-compatible adapter", "claude_code_deepseek", ["terminal", "file", "web", "skills", "factory"], factory_skills("claude-code", "test-driven-development"), []),
    ("codex-builder", "Codex Builder", "Bounded fixes, tests, QA on diffs", "codex", ["terminal", "file", "web", "skills", "factory"], factory_skills("codex", "test-driven-development", "github-code-review"), []),
    ("openhands-builder", "OpenHands Builder", "OpenHands VM sandbox implementation with OpenAI Codex supervisor", "openhands_vm_openai_codex", ["terminal", "file", "web", "skills", "factory"], factory_skills("openhands-gcp", "test-driven-development"), ["external-write"]),
    ("openhands-lab", "OpenHands Lab", "OpenHands VM sandbox experiments with DeepSeek supervisor", "openhands_vm_deepseek", ["terminal", "file", "web", "skills", "factory"], factory_skills("openhands-gcp", "test-driven-development", "spike"), ["external-write"]),
    ("quality-reviewer", "Quality Reviewer", "Independent spec and quality gate", "codex", ["terminal", "file", "web", "skills", "factory"], factory_skills("requesting-code-review", "github-code-review"), []),
    ("security-reviewer", "Security Reviewer", "Security and fintech/PII gates", "codex", ["terminal", "file", "web", "skills", "factory"], factory_skills("requesting-code-review", "systematic-debugging"), ["security-waiver"]),
    ("qa-verifier", "QA Verifier", "Smoke tests and evidence capture", "zeus", ["terminal", "file", "browser", "vision", "skills", "factory"], factory_skills("dogfood", "systematic-debugging", "test-driven-development", "factory-sandbox-kidu"), ["waive-tests"]),
    ("devops-release", "DevOps Release", "CI, environments, release readiness", "claude_code", ["terminal", "file", "web", "skills", "factory", "session_search", "cronjob"], factory_skills("github-pr-workflow", "repo-origin-sync", "systematic-debugging", "agent-vm-operations", "factory-sandbox-kidu"), ["deploy", "credential-change"]),
    ("factory-reporter", "Factory Reporter", "Executive reports, Notion PM docs, benchmarks", "zeus", ["terminal", "file", "web", "session_search", "skills", "factory"], factory_skills("software-factory-orchestration", "notion"), []),
]
