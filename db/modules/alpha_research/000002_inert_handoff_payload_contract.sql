-- Enforce inert handoff payloads at the database boundary.
-- This migration is intentionally separate from 000001 so already-applied local
-- Agent Core databases receive the payload trigger instead of skipping it via
-- the 000001 migration ledger row.
CREATE OR REPLACE FUNCTION alpha_research.enforce_inert_handoff_payload()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog, alpha_research
AS $$
DECLARE
  allowed_keys text[] := ARRAY[
    'schema_version',
    'classification_scope',
    'validation_state',
    'not_investment_advice',
    'advisory_disclaimer',
    'authority_scope',
    'dispatch_state',
    'program_id',
    'cycle_id',
    'card_ids',
    'evidence_ids',
    'prepared_at'
  ];
  prohibited_keys text[] := ARRAY[
    'validated_alpha',
    'investment_advice',
    'recommendation',
    'strategy_approved',
    'promotion',
    'order',
    'risk',
    'paper_activation',
    'live_activation',
    'deployment',
    'action',
    'recipient',
    'transport',
    'url',
    'token'
  ];
  payload_key text;
  canonical_payload jsonb;
BEGIN
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'alpha_research_handoff_payload_immutable';
  END IF;

  IF NEW.payload IS NULL OR jsonb_typeof(NEW.payload) <> 'object' THEN
    RAISE EXCEPTION 'alpha_research_handoff_payload_object_required';
  END IF;

  IF NEW.payload <> '{}'::jsonb THEN
    IF NEW.payload ?| prohibited_keys THEN
      RAISE EXCEPTION 'alpha_research_handoff_payload_prohibited_field';
    END IF;

    FOR payload_key IN SELECT jsonb_object_keys(NEW.payload) LOOP
      IF NOT payload_key = ANY(allowed_keys) THEN
        RAISE EXCEPTION 'alpha_research_handoff_payload_unknown_field';
      END IF;
    END LOOP;
  END IF;

  canonical_payload := jsonb_build_object(
    'schema_version', 'alpha_research/v1',
    'classification_scope', NEW.classification_scope,
    'validation_state', NEW.validation_state,
    'not_investment_advice', NEW.not_investment_advice,
    'advisory_disclaimer', NEW.advisory_disclaimer,
    'authority_scope', NEW.authority_scope,
    'dispatch_state', NEW.dispatch_state,
    'program_id', NEW.program_id,
    'cycle_id', NEW.cycle_id,
    'card_ids', NEW.card_ids,
    'evidence_ids', NEW.evidence_ids,
    'prepared_at', NEW.prepared_at
  );

  IF NEW.payload = '{}'::jsonb THEN
    NEW.payload := canonical_payload;
  ELSIF NEW.payload <> canonical_payload THEN
    RAISE EXCEPTION 'alpha_research_handoff_payload_invalid';
  END IF;

  RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION alpha_research.enforce_inert_handoff_payload() FROM PUBLIC, alpha_research_runtime, alpha_research_reviewer;

DROP TRIGGER IF EXISTS trg_alpha_research_handoff_00_payload ON alpha_research.inert_handoff_packages;
DROP TRIGGER IF EXISTS trg_alpha_research_handoff_payload ON alpha_research.inert_handoff_packages;
CREATE TRIGGER trg_alpha_research_handoff_00_payload
BEFORE INSERT OR UPDATE ON alpha_research.inert_handoff_packages
FOR EACH ROW EXECUTE FUNCTION alpha_research.enforce_inert_handoff_payload();
