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

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    text = (value or "").strip().lower()
    text = _SLUG_RE.sub("-", text).strip("-")
    return text or "factory-project"


FACTORY_AGENTS = [
    ("factory-orchestrator", "Factory Orchestrator", "Intake, routing, gates, metrics, reports", "zeus", ["factory", "delegation", "terminal", "file", "cronjob", "skills", "web"], ["software-factory-orchestration", "programming-delegation-engines"], ["merge", "deploy", "destructive", "credential-change"]),
    ("product-analyst", "Product Analyst", "Functional analysis, PRD, acceptance criteria", "zeus", ["file", "web", "session_search", "skills", "factory"], ["writing-plans", "agent-core-followup-reminders"], ["publish"]),
    ("solution-architect", "Solution Architect", "Architecture, boundaries, integration design", "claude_code", ["terminal", "file", "web", "skills", "factory"], ["writing-plans", "codebase-inspection"], ["architecture-approval"]),
    ("implementation-planner", "Implementation Planner", "Epics, stories, dependencies, task graph", "zeus", ["file", "skills", "factory"], ["writing-plans", "software-factory-orchestration"], []),
    ("claude-builder", "Claude Builder", "Complex implementation and refactors with native Anthropic Claude Code / Opus", "claude_code", ["terminal", "file", "web", "skills", "factory"], ["claude-code", "test-driven-development"], ["push", "merge"]),
    ("claude-deepseek-builder", "Claude DeepSeek Builder", "Claude Code workflow backed by DeepSeek Anthropic-compatible adapter", "claude_code_deepseek", ["terminal", "file", "web", "skills", "factory"], ["claude-code", "test-driven-development"], ["push", "merge"]),
    ("codex-builder", "Codex Builder", "Bounded fixes, tests, QA on diffs", "codex", ["terminal", "file", "web", "skills", "factory"], ["codex", "test-driven-development", "github-code-review"], ["push", "merge"]),
    ("openhands-builder", "OpenHands Builder", "OpenHands VM sandbox implementation with OpenAI Codex supervisor", "openhands_vm_openai_codex", ["terminal", "file", "web", "skills", "factory"], ["openhands-gcp", "test-driven-development"], ["external-write"]),
    ("openhands-lab", "OpenHands Lab", "OpenHands VM sandbox experiments with DeepSeek supervisor", "openhands_vm_deepseek", ["terminal", "file", "web", "skills", "factory"], ["openhands-gcp", "test-driven-development", "spike"], ["external-write"]),
    ("quality-reviewer", "Quality Reviewer", "Independent spec and quality gate", "codex", ["terminal", "file", "web", "skills", "factory"], ["requesting-code-review", "github-code-review"], ["approve-merge"]),
    ("security-reviewer", "Security Reviewer", "Security and fintech/PII gates", "codex", ["terminal", "file", "web", "skills", "factory"], ["requesting-code-review", "systematic-debugging"], ["security-waiver"]),
    ("qa-verifier", "QA Verifier", "Smoke tests and evidence capture", "zeus", ["terminal", "file", "browser", "vision", "skills", "factory"], ["dogfood"], ["waive-tests"]),
    ("devops-release", "DevOps Release", "CI, environments, release readiness", "claude_code", ["terminal", "file", "web", "skills", "factory"], ["github-pr-workflow"], ["deploy", "credential-change"]),
    ("factory-reporter", "Factory Reporter", "Executive reports, Notion PM docs, benchmarks", "zeus", ["file", "session_search", "skills", "factory"], ["software-factory-orchestration", "notion"], []),
]
