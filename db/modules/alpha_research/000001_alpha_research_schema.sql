-- Alpha Research Ledger Core: private local Agent Core research ledger foundation.
CREATE SCHEMA IF NOT EXISTS alpha_research;

INSERT INTO agent_core.modules(module, description, owner, schema_name, metadata)
VALUES (
  'alpha_research',
  'Private local Zeus alpha research ledger: programs, sources, immutable evidence, cards, reviews, cycles, result references, inert handoffs, and readiness.',
  'agent-runtime',
  'alpha_research',
  '{"scope":"private-local-research-ledger","authority":"research_only","dispatch":"not_dispatched"}'::jsonb
)
ON CONFLICT (module) DO UPDATE
SET description = EXCLUDED.description,
    schema_name = EXCLUDED.schema_name,
    metadata = EXCLUDED.metadata,
    updated_at = now();

INSERT INTO agent_core.module_databases(module, database_name, connection_role, migration_role, metadata)
VALUES (
  'alpha_research',
  current_database(),
  'alpha_research_runtime',
  'agent_admin',
  '{"option":"same-agent-db-private-schema","author_role":"alpha_research_runtime","reviewer_role":"alpha_research_reviewer"}'::jsonb
)
ON CONFLICT (module) DO UPDATE
SET database_name = EXCLUDED.database_name,
    connection_role = EXCLUDED.connection_role,
    migration_role = EXCLUDED.migration_role,
    metadata = EXCLUDED.metadata;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alpha_research_runtime') THEN
    CREATE ROLE alpha_research_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5;
  ELSE
    ALTER ROLE alpha_research_runtime WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alpha_research_reviewer') THEN
    CREATE ROLE alpha_research_reviewer LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5;
  ELSE
    ALTER ROLE alpha_research_reviewer WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 5;
  END IF;
END $$;

ALTER ROLE alpha_research_runtime SET search_path = alpha_research, pg_catalog;
ALTER ROLE alpha_research_reviewer SET search_path = alpha_research, pg_catalog;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'program_status') THEN
    CREATE TYPE alpha_research.program_status AS ENUM ('draft', 'active', 'archived');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'source_class') THEN
    CREATE TYPE alpha_research.source_class AS ENUM ('local_normalized_batch', 'manual_reference_metadata', 'licensed_local_document');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'terms_status') THEN
    CREATE TYPE alpha_research.terms_status AS ENUM ('approved', 'unknown', 'rejected', 'expired');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'freshness_mode') THEN
    CREATE TYPE alpha_research.freshness_mode AS ENUM ('static', 'max_age');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'cycle_outcome') THEN
    CREATE TYPE alpha_research.cycle_outcome AS ENUM ('open', 'closed', 'empty', 'rejected', 'failed');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'alpha_card_status') THEN
    CREATE TYPE alpha_research.alpha_card_status AS ENUM ('draft', 'reviewable', 'revision_requested', 'archived');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'lineage_relation') THEN
    CREATE TYPE alpha_research.lineage_relation AS ENUM ('parent', 'variant', 'family');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'review_type') THEN
    CREATE TYPE alpha_research.review_type AS ENUM ('adversarial', 'methodological');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'review_disposition') THEN
    CREATE TYPE alpha_research.review_disposition AS ENUM ('research_acknowledged', 'revision_requested', 'rejected', 'archived');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'classification_scope') THEN
    CREATE TYPE alpha_research.classification_scope AS ENUM ('research_only');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'validation_state') THEN
    CREATE TYPE alpha_research.validation_state AS ENUM ('unvalidated');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'dispatch_state') THEN
    CREATE TYPE alpha_research.dispatch_state AS ENUM ('not_dispatched');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'alpha_research' AND t.typname = 'readiness_status') THEN
    CREATE TYPE alpha_research.readiness_status AS ENUM ('passed', 'failed');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS alpha_research.research_programs (
  program_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 140),
  universe text NOT NULL CHECK (char_length(universe) BETWEEN 1 AND 500),
  status alpha_research.program_status NOT NULL DEFAULT 'draft',
  created_by name NOT NULL DEFAULT session_user,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (created_by = 'alpha_research_runtime')
);

CREATE TABLE IF NOT EXISTS alpha_research.source_registry (
  source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_reference text NOT NULL CHECK (char_length(source_reference) BETWEEN 1 AND 2048),
  source_class alpha_research.source_class NOT NULL,
  terms_evidence_reference text NOT NULL CHECK (char_length(terms_evidence_reference) BETWEEN 1 AND 2048),
  terms_status alpha_research.terms_status NOT NULL DEFAULT 'unknown',
  enabled boolean NOT NULL DEFAULT false,
  freshness_mode alpha_research.freshness_mode NOT NULL DEFAULT 'static',
  max_age_seconds integer,
  policy_revision integer NOT NULL DEFAULT 1 CHECK (policy_revision > 0),
  approved_by name,
  approved_at timestamptz,
  approval_reason text,
  submitted_by name NOT NULL DEFAULT session_user,
  submitted_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((enabled = false) OR (terms_status = 'approved')),
  CHECK ((freshness_mode = 'static' AND max_age_seconds IS NULL) OR (freshness_mode = 'max_age' AND max_age_seconds BETWEEN 60 AND 31536000)),
  CHECK ((terms_status <> 'approved') OR (approved_by = 'agent_admin' AND approved_at IS NOT NULL AND approval_reason IS NOT NULL AND btrim(approval_reason) <> ''))
);

CREATE TABLE IF NOT EXISTS alpha_research.source_policy_revisions (
  source_policy_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES alpha_research.source_registry(source_id),
  revision integer NOT NULL CHECK (revision > 0),
  before_terms_status alpha_research.terms_status,
  after_terms_status alpha_research.terms_status NOT NULL,
  before_enabled boolean,
  after_enabled boolean NOT NULL,
  before_freshness_mode alpha_research.freshness_mode,
  after_freshness_mode alpha_research.freshness_mode NOT NULL,
  before_max_age_seconds integer,
  after_max_age_seconds integer,
  source_reference_snapshot text NOT NULL,
  terms_evidence_reference_snapshot text NOT NULL,
  changed_by name NOT NULL DEFAULT session_user,
  changed_at timestamptz NOT NULL DEFAULT now(),
  approval_reason text NOT NULL CHECK (btrim(approval_reason) <> ''),
  UNIQUE (source_id, revision)
);

CREATE TABLE IF NOT EXISTS alpha_research.research_cycles (
  cycle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  program_id uuid NOT NULL REFERENCES alpha_research.research_programs(program_id),
  cycle_key date NOT NULL,
  status alpha_research.cycle_outcome NOT NULL DEFAULT 'open',
  outcome alpha_research.cycle_outcome NOT NULL DEFAULT 'open',
  summary text,
  author_principal name NOT NULL DEFAULT session_user,
  opened_at timestamptz NOT NULL DEFAULT now(),
  closed_at timestamptz,
  status_changed_by name,
  UNIQUE (program_id, cycle_key),
  CHECK (author_principal = 'alpha_research_runtime'),
  CHECK ((status = 'open' AND outcome = 'open' AND closed_at IS NULL) OR (status <> 'open' AND outcome = status AND closed_at IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS alpha_research.evidence_items (
  evidence_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES alpha_research.source_registry(source_id),
  cycle_id uuid REFERENCES alpha_research.research_cycles(cycle_id),
  content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
  source_locator text NOT NULL CHECK (char_length(source_locator) BETWEEN 1 AND 2048),
  retrieved_at timestamptz NOT NULL,
  freshness_observed_at timestamptz NOT NULL,
  normalized_claim text NOT NULL CHECK (char_length(normalized_claim) BETWEEN 1 AND 8000),
  falsification_notes text NOT NULL DEFAULT '' CHECK (char_length(falsification_notes) <= 4000),
  supersedes_evidence_id uuid REFERENCES alpha_research.evidence_items(evidence_id),
  idempotency_key uuid NOT NULL DEFAULT gen_random_uuid(),
  recorded_by name NOT NULL DEFAULT session_user,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (source_id, content_sha256, source_locator),
  UNIQUE (idempotency_key),
  CHECK (freshness_observed_at >= retrieved_at)
);

CREATE TABLE IF NOT EXISTS alpha_research.alpha_cards (
  card_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  program_id uuid NOT NULL REFERENCES alpha_research.research_programs(program_id),
  status alpha_research.alpha_card_status NOT NULL DEFAULT 'draft',
  mechanism text NOT NULL CHECK (char_length(mechanism) BETWEEN 1 AND 2000),
  mechanism_fingerprint text NOT NULL CHECK (mechanism_fingerprint ~ '^[0-9a-f]{64}$'),
  universe text NOT NULL CHECK (char_length(universe) BETWEEN 1 AND 500),
  regime text NOT NULL CHECK (char_length(regime) BETWEEN 1 AND 1000),
  failure_regime text NOT NULL CHECK (char_length(failure_regime) BETWEEN 1 AND 1000),
  data_contract text NOT NULL CHECK (char_length(data_contract) BETWEEN 1 AND 4000),
  cost_capacity_assumptions text NOT NULL CHECK (char_length(cost_capacity_assumptions) BETWEEN 1 AND 4000),
  no_trade_conditions text NOT NULL CHECK (char_length(no_trade_conditions) BETWEEN 1 AND 4000),
  falsification_plan text NOT NULL CHECK (char_length(falsification_plan) BETWEEN 1 AND 4000),
  author_principal name NOT NULL DEFAULT session_user,
  classification_scope alpha_research.classification_scope NOT NULL DEFAULT 'research_only',
  validation_state alpha_research.validation_state NOT NULL DEFAULT 'unvalidated',
  not_investment_advice boolean NOT NULL DEFAULT true,
  advisory_disclaimer text NOT NULL DEFAULT 'Research only; unvalidated; not investment advice.',
  status_changed_at timestamptz NOT NULL DEFAULT now(),
  status_changed_by name,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (author_principal = 'alpha_research_runtime'),
  CHECK (classification_scope = 'research_only'),
  CHECK (validation_state = 'unvalidated'),
  CHECK (not_investment_advice = true),
  CHECK (advisory_disclaimer = 'Research only; unvalidated; not investment advice.')
);

CREATE TABLE IF NOT EXISTS alpha_research.alpha_card_evidence (
  card_id uuid NOT NULL REFERENCES alpha_research.alpha_cards(card_id) ON DELETE CASCADE,
  evidence_id uuid NOT NULL REFERENCES alpha_research.evidence_items(evidence_id),
  linked_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (card_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS alpha_research.alpha_lineage (
  lineage_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  card_id uuid NOT NULL REFERENCES alpha_research.alpha_cards(card_id),
  related_card_id uuid NOT NULL REFERENCES alpha_research.alpha_cards(card_id),
  relation alpha_research.lineage_relation NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (card_id <> related_card_id),
  UNIQUE (card_id, related_card_id, relation)
);

CREATE TABLE IF NOT EXISTS alpha_research.research_reviews (
  review_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  card_id uuid NOT NULL REFERENCES alpha_research.alpha_cards(card_id),
  reviewer_principal name NOT NULL DEFAULT session_user,
  review_type alpha_research.review_type NOT NULL,
  disposition alpha_research.review_disposition NOT NULL,
  rationale text NOT NULL CHECK (char_length(rationale) BETWEEN 1 AND 8000),
  evidence_gap_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  classification_scope alpha_research.classification_scope NOT NULL DEFAULT 'research_only',
  validation_state alpha_research.validation_state NOT NULL DEFAULT 'unvalidated',
  not_investment_advice boolean NOT NULL DEFAULT true,
  advisory_disclaimer text NOT NULL DEFAULT 'Research only; unvalidated; not investment advice.',
  reviewed_at timestamptz NOT NULL DEFAULT now(),
  CHECK (reviewer_principal = 'alpha_research_reviewer'),
  CHECK (classification_scope = 'research_only'),
  CHECK (validation_state = 'unvalidated'),
  CHECK (not_investment_advice = true),
  CHECK (advisory_disclaimer = 'Research only; unvalidated; not investment advice.')
);

CREATE TABLE IF NOT EXISTS alpha_research.experiment_result_refs (
  result_ref_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  card_id uuid NOT NULL REFERENCES alpha_research.alpha_cards(card_id),
  evidence_id uuid REFERENCES alpha_research.evidence_items(evidence_id),
  result_reference text NOT NULL CHECK (char_length(result_reference) BETWEEN 1 AND 2048),
  comparability_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  rankable boolean NOT NULL DEFAULT false,
  recorded_by name NOT NULL DEFAULT session_user,
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alpha_research.inert_handoff_packages (
  handoff_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  program_id uuid NOT NULL REFERENCES alpha_research.research_programs(program_id),
  cycle_id uuid REFERENCES alpha_research.research_cycles(cycle_id),
  card_ids uuid[] NOT NULL CHECK (array_length(card_ids, 1) BETWEEN 1 AND 100),
  evidence_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[] CHECK (COALESCE(array_length(evidence_ids, 1), 0) <= 100),
  authority_scope text NOT NULL DEFAULT 'research_only' CHECK (authority_scope = 'research_only'),
  dispatch_state alpha_research.dispatch_state NOT NULL DEFAULT 'not_dispatched',
  classification_scope alpha_research.classification_scope NOT NULL DEFAULT 'research_only',
  validation_state alpha_research.validation_state NOT NULL DEFAULT 'unvalidated',
  not_investment_advice boolean NOT NULL DEFAULT true,
  advisory_disclaimer text NOT NULL DEFAULT 'Research only; unvalidated; not investment advice.',
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  prepared_by name NOT NULL DEFAULT session_user,
  prepared_at timestamptz NOT NULL DEFAULT now(),
  CHECK (prepared_by = 'alpha_research_runtime'),
  CHECK (classification_scope = 'research_only'),
  CHECK (validation_state = 'unvalidated'),
  CHECK (not_investment_advice = true),
  CHECK (advisory_disclaimer = 'Research only; unvalidated; not investment advice.')
);

CREATE TABLE IF NOT EXISTS alpha_research.runtime_readiness (
  component text PRIMARY KEY,
  status alpha_research.readiness_status NOT NULL,
  source_commit text NOT NULL CHECK (source_commit ~ '^[0-9a-f]{40}$'),
  evidence_sha256 text NOT NULL CHECK (evidence_sha256 ~ '^[0-9a-f]{64}$'),
  verified_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  verified_by name NOT NULL DEFAULT session_user,
  CHECK (expires_at > verified_at)
);

CREATE OR REPLACE FUNCTION alpha_research.reject_mutation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
BEGIN
  RAISE EXCEPTION 'alpha_research_append_only';
END;
$$;

CREATE OR REPLACE FUNCTION alpha_research.protect_classification_tuple()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
BEGIN
  IF NEW.classification_scope <> OLD.classification_scope
     OR NEW.validation_state <> OLD.validation_state
     OR NEW.not_investment_advice <> OLD.not_investment_advice
     OR NEW.advisory_disclaimer <> OLD.advisory_disclaimer THEN
    RAISE EXCEPTION 'alpha_research_classification_immutable';
  END IF;
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION alpha_research.enforce_source_policy_write()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF session_user = 'alpha_research_runtime' AND (
      NEW.terms_status <> 'unknown'
      OR NEW.enabled IS DISTINCT FROM false
      OR NEW.policy_revision <> 1
      OR NEW.approved_by IS NOT NULL
      OR NEW.approved_at IS NOT NULL
      OR NEW.approval_reason IS NOT NULL
    ) THEN
      RAISE EXCEPTION 'alpha_research_source_candidate_only';
    END IF;
    RETURN NEW;
  END IF;

  IF NEW.source_reference <> OLD.source_reference
     OR NEW.terms_evidence_reference <> OLD.terms_evidence_reference THEN
    RAISE EXCEPTION 'alpha_research_source_references_immutable';
  END IF;
  IF session_user <> 'agent_admin' THEN
    RAISE EXCEPTION 'alpha_research_source_policy_admin_only';
  END IF;
  IF NEW.policy_revision <> OLD.policy_revision + 1 THEN
    RAISE EXCEPTION 'alpha_research_source_policy_revision_gap';
  END IF;
  IF NEW.approval_reason IS NULL OR btrim(NEW.approval_reason) = '' THEN
    RAISE EXCEPTION 'alpha_research_source_policy_reason_required';
  END IF;
  IF NEW.terms_status = 'approved'
     AND (NEW.approved_by <> 'agent_admin' OR NEW.approved_at IS NULL) THEN
    RAISE EXCEPTION 'alpha_research_source_policy_approval_required';
  END IF;

  INSERT INTO alpha_research.source_policy_revisions(
    source_id,
    revision,
    before_terms_status,
    after_terms_status,
    before_enabled,
    after_enabled,
    before_freshness_mode,
    after_freshness_mode,
    before_max_age_seconds,
    after_max_age_seconds,
    source_reference_snapshot,
    terms_evidence_reference_snapshot,
    changed_by,
    approval_reason
  ) VALUES (
    NEW.source_id,
    NEW.policy_revision,
    OLD.terms_status,
    NEW.terms_status,
    OLD.enabled,
    NEW.enabled,
    OLD.freshness_mode,
    NEW.freshness_mode,
    OLD.max_age_seconds,
    NEW.max_age_seconds,
    OLD.source_reference,
    OLD.terms_evidence_reference,
    session_user,
    NEW.approval_reason
  );

  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION alpha_research.validate_evidence_source()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
DECLARE
  source_row alpha_research.source_registry%ROWTYPE;
BEGIN
  SELECT * INTO source_row
  FROM alpha_research.source_registry
  WHERE source_id = NEW.source_id;

  IF NOT FOUND OR source_row.enabled IS DISTINCT FROM true OR source_row.terms_status <> 'approved' THEN
    RAISE EXCEPTION 'alpha_research_source_not_approved';
  END IF;

  IF NEW.retrieved_at > clock_timestamp() OR NEW.freshness_observed_at > clock_timestamp() THEN
    RAISE EXCEPTION 'alpha_research_future_evidence_time';
  END IF;

  IF source_row.freshness_mode = 'max_age'
     AND NEW.retrieved_at < clock_timestamp() - make_interval(secs => source_row.max_age_seconds) THEN
    RAISE EXCEPTION 'alpha_research_stale_evidence';
  END IF;

  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION alpha_research.transition_alpha_card(card_id uuid, target alpha_research.alpha_card_status)
RETURNS alpha_research.alpha_card_status
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
DECLARE
  card_row alpha_research.alpha_cards%ROWTYPE;
BEGIN
  SELECT * INTO card_row
  FROM alpha_research.alpha_cards
  WHERE alpha_cards.card_id = transition_alpha_card.card_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'alpha_research_card_missing';
  END IF;
  IF card_row.author_principal <> 'alpha_research_runtime' THEN
    RAISE EXCEPTION 'alpha_research_wrong_author';
  END IF;
  IF session_user NOT IN ('alpha_research_runtime', 'agent_admin') THEN
    RAISE EXCEPTION 'alpha_research_transition_denied';
  END IF;
  IF card_row.status = target THEN
    RAISE EXCEPTION 'alpha_research_self_transition_denied';
  END IF;

  IF session_user = 'alpha_research_runtime' AND NOT (
    (card_row.status = 'draft' AND target IN ('reviewable', 'archived')) OR
    (card_row.status = 'revision_requested' AND target IN ('reviewable', 'archived'))
  ) THEN
    RAISE EXCEPTION 'alpha_research_card_edge_denied';
  END IF;

  IF session_user = 'agent_admin' AND NOT (
    card_row.status IN ('draft', 'reviewable', 'revision_requested') AND target = 'archived'
  ) THEN
    RAISE EXCEPTION 'alpha_research_card_repair_denied';
  END IF;

  UPDATE alpha_research.alpha_cards
  SET status = target,
      status_changed_at = now(),
      status_changed_by = session_user
  WHERE alpha_cards.card_id = transition_alpha_card.card_id;

  RETURN target;
END;
$$;

CREATE OR REPLACE FUNCTION alpha_research.transition_research_cycle(cycle_id uuid, target alpha_research.cycle_outcome, summary text)
RETURNS alpha_research.cycle_outcome
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, alpha_research
AS $$
DECLARE
  cycle_row alpha_research.research_cycles%ROWTYPE;
BEGIN
  IF target NOT IN ('closed', 'empty', 'rejected', 'failed') THEN
    RAISE EXCEPTION 'alpha_research_cycle_target_denied';
  END IF;
  IF summary IS NULL OR btrim(summary) = '' OR char_length(summary) > 8000 THEN
    RAISE EXCEPTION 'alpha_research_cycle_summary_invalid';
  END IF;

  SELECT * INTO cycle_row
  FROM alpha_research.research_cycles
  WHERE research_cycles.cycle_id = transition_research_cycle.cycle_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'alpha_research_cycle_missing';
  END IF;
  IF cycle_row.author_principal <> 'alpha_research_runtime' THEN
    RAISE EXCEPTION 'alpha_research_wrong_cycle_author';
  END IF;
  IF session_user NOT IN ('alpha_research_runtime', 'agent_admin') THEN
    RAISE EXCEPTION 'alpha_research_cycle_transition_denied';
  END IF;
  IF cycle_row.status <> 'open' THEN
    RAISE EXCEPTION 'alpha_research_cycle_not_open';
  END IF;

  UPDATE alpha_research.research_cycles
  SET status = target,
      outcome = target,
      summary = transition_research_cycle.summary,
      closed_at = now(),
      status_changed_by = session_user
  WHERE research_cycles.cycle_id = transition_research_cycle.cycle_id;

  RETURN target;
END;
$$;

DROP TRIGGER IF EXISTS trg_alpha_research_evidence_policy ON alpha_research.evidence_items;
CREATE TRIGGER trg_alpha_research_evidence_policy
BEFORE INSERT ON alpha_research.evidence_items
FOR EACH ROW EXECUTE FUNCTION alpha_research.validate_evidence_source();

DROP TRIGGER IF EXISTS trg_alpha_research_source_policy_write ON alpha_research.source_registry;
CREATE TRIGGER trg_alpha_research_source_policy_write
BEFORE INSERT OR UPDATE ON alpha_research.source_registry
FOR EACH ROW EXECUTE FUNCTION alpha_research.enforce_source_policy_write();

DROP TRIGGER IF EXISTS trg_alpha_research_program_append_only ON alpha_research.research_programs;
CREATE TRIGGER trg_alpha_research_program_append_only
BEFORE UPDATE OR DELETE ON alpha_research.research_programs
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_source_policy_revision_append_only ON alpha_research.source_policy_revisions;
CREATE TRIGGER trg_alpha_research_source_policy_revision_append_only
BEFORE UPDATE OR DELETE ON alpha_research.source_policy_revisions
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_evidence_append_only_update ON alpha_research.evidence_items;
CREATE TRIGGER trg_alpha_research_evidence_append_only_update
BEFORE UPDATE OR DELETE ON alpha_research.evidence_items
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_card_evidence_append_only ON alpha_research.alpha_card_evidence;
CREATE TRIGGER trg_alpha_research_card_evidence_append_only
BEFORE UPDATE OR DELETE ON alpha_research.alpha_card_evidence
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_lineage_append_only ON alpha_research.alpha_lineage;
CREATE TRIGGER trg_alpha_research_lineage_append_only
BEFORE UPDATE OR DELETE ON alpha_research.alpha_lineage
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_reviews_append_only ON alpha_research.research_reviews;
CREATE TRIGGER trg_alpha_research_reviews_append_only
BEFORE UPDATE OR DELETE ON alpha_research.research_reviews
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_handoff_append_only ON alpha_research.inert_handoff_packages;
CREATE TRIGGER trg_alpha_research_handoff_append_only
BEFORE UPDATE OR DELETE ON alpha_research.inert_handoff_packages
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_result_refs_append_only ON alpha_research.experiment_result_refs;
CREATE TRIGGER trg_alpha_research_result_refs_append_only
BEFORE UPDATE OR DELETE ON alpha_research.experiment_result_refs
FOR EACH ROW EXECUTE FUNCTION alpha_research.reject_mutation();

DROP TRIGGER IF EXISTS trg_alpha_research_card_tuple ON alpha_research.alpha_cards;
CREATE TRIGGER trg_alpha_research_card_tuple
BEFORE UPDATE ON alpha_research.alpha_cards
FOR EACH ROW EXECUTE FUNCTION alpha_research.protect_classification_tuple();

DROP TRIGGER IF EXISTS trg_alpha_research_review_tuple ON alpha_research.research_reviews;
CREATE TRIGGER trg_alpha_research_review_tuple
BEFORE UPDATE ON alpha_research.research_reviews
FOR EACH ROW EXECUTE FUNCTION alpha_research.protect_classification_tuple();

DROP TRIGGER IF EXISTS trg_alpha_research_handoff_tuple ON alpha_research.inert_handoff_packages;
CREATE TRIGGER trg_alpha_research_handoff_tuple
BEFORE UPDATE ON alpha_research.inert_handoff_packages
FOR EACH ROW EXECUTE FUNCTION alpha_research.protect_classification_tuple();

REVOKE ALL ON SCHEMA alpha_research FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA alpha_research FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA alpha_research FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA alpha_research FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA alpha_research REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA alpha_research REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA alpha_research REVOKE ALL ON FUNCTIONS FROM PUBLIC;

GRANT CONNECT ON DATABASE zeus_agent TO alpha_research_runtime, alpha_research_reviewer;
GRANT USAGE ON SCHEMA alpha_research TO alpha_research_runtime, alpha_research_reviewer;

GRANT SELECT, INSERT ON alpha_research.research_programs TO alpha_research_runtime;
GRANT SELECT ON alpha_research.research_programs TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.source_registry TO alpha_research_runtime;
GRANT SELECT ON alpha_research.source_registry TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.research_cycles TO alpha_research_runtime;
GRANT SELECT ON alpha_research.research_cycles TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.evidence_items TO alpha_research_runtime;
GRANT SELECT ON alpha_research.evidence_items TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.alpha_cards TO alpha_research_runtime;
GRANT SELECT ON alpha_research.alpha_cards TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.alpha_card_evidence TO alpha_research_runtime;
GRANT SELECT ON alpha_research.alpha_card_evidence TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.alpha_lineage TO alpha_research_runtime;
GRANT SELECT ON alpha_research.alpha_lineage TO alpha_research_reviewer;
GRANT SELECT ON alpha_research.research_reviews TO alpha_research_runtime;
GRANT SELECT, INSERT ON alpha_research.research_reviews TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.experiment_result_refs TO alpha_research_runtime;
GRANT SELECT ON alpha_research.experiment_result_refs TO alpha_research_reviewer;
GRANT SELECT, INSERT ON alpha_research.inert_handoff_packages TO alpha_research_runtime;
GRANT SELECT ON alpha_research.inert_handoff_packages TO alpha_research_reviewer;
GRANT SELECT ON alpha_research.runtime_readiness TO alpha_research_runtime, alpha_research_reviewer;
GRANT SELECT ON alpha_research.source_policy_revisions TO alpha_research_runtime, alpha_research_reviewer;

REVOKE ALL ON FUNCTION alpha_research.transition_alpha_card(uuid, alpha_research.alpha_card_status) FROM PUBLIC, alpha_research_reviewer;
REVOKE ALL ON FUNCTION alpha_research.transition_research_cycle(uuid, alpha_research.cycle_outcome, text) FROM PUBLIC, alpha_research_reviewer;
GRANT EXECUTE ON FUNCTION alpha_research.transition_alpha_card(uuid, alpha_research.alpha_card_status) TO alpha_research_runtime;
GRANT EXECUTE ON FUNCTION alpha_research.transition_research_cycle(uuid, alpha_research.cycle_outcome, text) TO alpha_research_runtime;
