#!/usr/bin/env bash
# Safe wrapper for Hermes cron/no-agent runs.
# Default: dry-run only, no external sends, no DB report write.
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/home/jean/Projects/hermes-agent-original}"
CAMPAIGN_ID="${SALES_OPERATOR_CAMPAIGN_ID:-empleado-uno-1000-subscribers-q3-2026}"
FORMAT="${SALES_OPERATOR_DRY_RUN_FORMAT:-markdown}"
TARGET="${SALES_OPERATOR_DRY_RUN_TARGET:-/home/jean/zeus-runtime/delivery-sandbox/user-data/sales_operator_daily_dry_run.json}"

cd "$REPO_ROOT"
exec python3 scripts/runtime/sales_operator_daily_dry_run.py \
  --campaign-id "$CAMPAIGN_ID" \
  --format "$FORMAT" \
  --target "$TARGET" \
  "$@"
