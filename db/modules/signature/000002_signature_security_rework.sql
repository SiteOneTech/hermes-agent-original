-- Signature Core T14R integrated security/runtime rework.
-- Adds multi-signer lifecycle columns and final-copy/reminder receipt tables used by
-- the integrated T07/T10/T11/T12 runtime path.

ALTER TABLE signature.document_requests
  ADD COLUMN IF NOT EXISTS template_version_id text,
  ADD COLUMN IF NOT EXISTS decline_blocks boolean NOT NULL DEFAULT true,
  ADD COLUMN IF NOT EXISTS signing_mode text NOT NULL DEFAULT 'parallel',
  ADD COLUMN IF NOT EXISTS sent_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_activity_at timestamptz;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conrelid = 'signature.document_requests'::regclass
      AND conname = 'signature_document_requests_signing_mode_check'
  ) THEN
    ALTER TABLE signature.document_requests
      ADD CONSTRAINT signature_document_requests_signing_mode_check
      CHECK (signing_mode IN ('parallel','sequential','mixed'));
  END IF;
END $$;

ALTER TABLE signature.submitters
  ADD COLUMN IF NOT EXISTS required boolean NOT NULL DEFAULT true,
  ADD COLUMN IF NOT EXISTS started_at timestamptz,
  ADD COLUMN IF NOT EXISTS approved_at timestamptz;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conrelid = 'signature.submitters'::regclass
      AND conname IN ('submitters_status_check','signature_submitters_status_check')
  ) THEN
    ALTER TABLE signature.submitters DROP CONSTRAINT IF EXISTS submitters_status_check;
    ALTER TABLE signature.submitters DROP CONSTRAINT IF EXISTS signature_submitters_status_check;
  END IF;

  ALTER TABLE signature.submitters
    ADD CONSTRAINT signature_submitters_status_check
    CHECK (status IN ('pending','sent','viewed','started','signed','approved','declined','expired','cancelled'));
END $$;

CREATE TABLE IF NOT EXISTS signature.reminder_policies (
  reminder_policy_id text PRIMARY KEY,
  request_id text NOT NULL UNIQUE REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  cadence text NOT NULL,
  next_due_at timestamptz NOT NULL,
  max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts > 0),
  escalation_settings jsonb NOT NULL DEFAULT '{}'::jsonb,
  enabled boolean NOT NULL DEFAULT true,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signature.reminder_attempts (
  reminder_attempt_id bigserial PRIMARY KEY,
  reminder_policy_id text REFERENCES signature.reminder_policies(reminder_policy_id) ON DELETE SET NULL,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  channel text NOT NULL,
  recipient text,
  provider_message_id text,
  status text NOT NULL DEFAULT 'sent' CHECK (status IN ('queued','sent','delivered','failed','bounced')),
  error_message text,
  scheduled_for timestamptz,
  attempted_at timestamptz NOT NULL DEFAULT now(),
  idempotency_key text NOT NULL UNIQUE,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signature.delivery_receipts (
  delivery_receipt_id bigserial PRIMARY KEY,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  receipt_type text NOT NULL CHECK (receipt_type IN ('invitation','otp','reminder','final_copy')),
  channel text NOT NULL,
  recipient text,
  provider_message_id text,
  status text NOT NULL DEFAULT 'sent' CHECK (status IN ('queued','sent','delivered','failed','bounced')),
  error_message text,
  delivered_at timestamptz,
  idempotency_key text NOT NULL UNIQUE,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_signature_document_requests_lifecycle ON signature.document_requests(status, expires_at, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_reminder_policies_due ON signature.reminder_policies(enabled, next_due_at);
CREATE INDEX IF NOT EXISTS idx_signature_reminder_attempts_request ON signature.reminder_attempts(request_id, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_delivery_receipts_request ON signature.delivery_receipts(request_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_delivery_receipts_type_status ON signature.delivery_receipts(receipt_type, status, created_at DESC);

DO $$
BEGIN
  ALTER TABLE signature.events DROP CONSTRAINT IF EXISTS events_event_type_check;
  ALTER TABLE signature.events DROP CONSTRAINT IF EXISTS signature_events_event_type_check;

  ALTER TABLE signature.events ADD CONSTRAINT signature_events_event_type_check
    CHECK (event_type IN (
      'created','sent','viewed','started','field_updated','signed','approved','declined','completed','downloaded','agent_note','hash_created',
      'invitation_sent','otp_sent','reminder_policy_updated','reminder_sent','final_copy_sent','delivery_receipt_recorded','delivery_failed',
      'final_copy_failed','owner_escalated','owner_escalation'
    ));
END $$;

GRANT SELECT, INSERT, UPDATE, DELETE ON signature.reminder_policies TO signature_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON signature.reminder_attempts TO signature_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON signature.delivery_receipts TO signature_runtime;
GRANT SELECT ON signature.reminder_policies TO agent_runtime;
GRANT SELECT ON signature.reminder_attempts TO agent_runtime;
GRANT SELECT ON signature.delivery_receipts TO agent_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA signature TO signature_runtime;
