-- Harden Fitness body metric idempotency keys for smart-scale imports.
-- Blank keys are not valid idempotency keys. Existing duplicate active keys are
-- preserved in metadata under deduplicated_idempotency_key, while only the newest
-- row keeps the active idempotency_key used by the unique index.

DROP INDEX IF EXISTS fitness.idx_fitness_body_metrics_idempotency;

UPDATE fitness.body_metrics
SET metadata = metadata - 'idempotency_key'
WHERE metadata ? 'idempotency_key'
  AND btrim(metadata->>'idempotency_key') = '';

UPDATE fitness.body_metrics
SET metadata = jsonb_set(metadata, '{idempotency_key}', to_jsonb(btrim(metadata->>'idempotency_key')))
WHERE metadata ? 'idempotency_key'
  AND btrim(metadata->>'idempotency_key') <> ''
  AND metadata->>'idempotency_key' <> btrim(metadata->>'idempotency_key');

WITH ranked AS (
  SELECT
    body_metric_id,
    btrim(metadata->>'idempotency_key') AS idempotency_key,
    row_number() OVER (
      PARTITION BY profile_id, btrim(metadata->>'idempotency_key')
      ORDER BY measured_at DESC, body_metric_id DESC
    ) AS rank_for_key
  FROM fitness.body_metrics
  WHERE metadata ? 'idempotency_key'
    AND btrim(metadata->>'idempotency_key') <> ''
)
UPDATE fitness.body_metrics AS metric
SET metadata = (metric.metadata - 'idempotency_key') || jsonb_build_object('deduplicated_idempotency_key', ranked.idempotency_key)
FROM ranked
WHERE metric.body_metric_id = ranked.body_metric_id
  AND ranked.rank_for_key > 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_fitness_body_metrics_idempotency
  ON fitness.body_metrics(profile_id, (btrim(metadata->>'idempotency_key')))
  WHERE metadata ? 'idempotency_key' AND btrim(metadata->>'idempotency_key') <> '';
