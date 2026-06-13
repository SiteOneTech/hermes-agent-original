-- Signature Core V2: normalized template versions, field placement, collection data, reminders, receipts, and dashboard metrics.

ALTER TABLE signature.document_requests
  ADD COLUMN IF NOT EXISTS template_version_id text,
  ADD COLUMN IF NOT EXISTS decline_blocks boolean NOT NULL DEFAULT true,
  ADD COLUMN IF NOT EXISTS signing_mode text NOT NULL DEFAULT 'parallel' CHECK (signing_mode IN ('parallel','sequential','mixed')),
  ADD COLUMN IF NOT EXISTS sent_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_activity_at timestamptz;

ALTER TABLE signature.submitters
  ADD COLUMN IF NOT EXISTS required boolean NOT NULL DEFAULT true,
  ADD COLUMN IF NOT EXISTS started_at timestamptz,
  ADD COLUMN IF NOT EXISTS approved_at timestamptz;

CREATE TABLE IF NOT EXISTS signature.template_versions (
  template_version_id text PRIMARY KEY,
  template_id text NOT NULL REFERENCES signature.templates(template_id) ON DELETE CASCADE,
  version_number integer NOT NULL CHECK (version_number > 0),
  source_document_attachment_id text REFERENCES signature.attachments(attachment_id) ON DELETE SET NULL,
  document_sha256 text,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','archived')),
  field_schema jsonb NOT NULL DEFAULT '[]'::jsonb,
  submitter_schema jsonb NOT NULL DEFAULT '[]'::jsonb,
  preparation_notes text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_by text,
  created_at timestamptz NOT NULL DEFAULT now(),
  activated_at timestamptz,
  archived_at timestamptz,
  UNIQUE (template_id, version_number)
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'document_requests_template_version_id_fkey'
  ) THEN
    ALTER TABLE signature.document_requests
      ADD CONSTRAINT document_requests_template_version_id_fkey
      FOREIGN KEY (template_version_id)
      REFERENCES signature.template_versions(template_version_id)
      ON DELETE SET NULL;
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS signature.field_placements (
  field_id text PRIMARY KEY,
  template_version_id text NOT NULL REFERENCES signature.template_versions(template_version_id) ON DELETE CASCADE,
  role text NOT NULL DEFAULT 'signer',
  field_type text NOT NULL CHECK (field_type IN ('signature','initials','name','date','text','long_comment','checkbox','select','attachment','internal_note')),
  label text NOT NULL,
  required boolean NOT NULL DEFAULT true,
  page_number integer NOT NULL CHECK (page_number > 0),
  x numeric(12,4) NOT NULL CHECK (x >= 0),
  y numeric(12,4) NOT NULL CHECK (y >= 0),
  width numeric(12,4) NOT NULL CHECK (width > 0),
  height numeric(12,4) NOT NULL CHECK (height > 0),
  rotation numeric(8,4) NOT NULL DEFAULT 0,
  x_pct numeric(9,6) NOT NULL CHECK (x_pct >= 0 AND x_pct <= 1),
  y_pct numeric(9,6) NOT NULL CHECK (y_pct >= 0 AND y_pct <= 1),
  w_pct numeric(9,6) NOT NULL CHECK (w_pct > 0 AND w_pct <= 1),
  h_pct numeric(9,6) NOT NULL CHECK (h_pct > 0 AND h_pct <= 1),
  anchor_text text,
  anchor_occurrence integer,
  anchor_bbox jsonb,
  anchor_strategy text,
  anchor_tolerance numeric(9,6),
  validation jsonb NOT NULL DEFAULT '{}'::jsonb,
  appearance jsonb NOT NULL DEFAULT '{}'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signature.field_values (
  field_value_id text PRIMARY KEY,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  field_id text NOT NULL REFERENCES signature.field_placements(field_id) ON DELETE RESTRICT,
  value_text text,
  value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  attachment_id text REFERENCES signature.attachments(attachment_id) ON DELETE SET NULL,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','submitted','voided')),
  ip_address text,
  user_agent text,
  created_at timestamptz NOT NULL DEFAULT now(),
  submitted_at timestamptz,
  voided_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (request_id, submitter_id, field_id)
);

CREATE TABLE IF NOT EXISTS signature.comments (
  comment_id text PRIMARY KEY,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  field_id text REFERENCES signature.field_placements(field_id) ON DELETE SET NULL,
  parent_comment_id text REFERENCES signature.comments(comment_id) ON DELETE SET NULL,
  comment_type text NOT NULL DEFAULT 'comment' CHECK (comment_type IN ('comment','rejection_reason','help_request','internal_note')),
  visibility text NOT NULL DEFAULT 'owner' CHECK (visibility IN ('signer','owner','internal')),
  trusted_identity boolean NOT NULL DEFAULT false,
  actor_type text NOT NULL DEFAULT 'customer' CHECK (actor_type IN ('customer','owner','agent','system','adapter')),
  actor_ref text,
  body text NOT NULL,
  ip_address text,
  user_agent text,
  created_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS signature.reminder_policies (
  reminder_policy_id text PRIMARY KEY,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  template_version_id text REFERENCES signature.template_versions(template_version_id) ON DELETE SET NULL,
  enabled boolean NOT NULL DEFAULT true,
  cadence text NOT NULL DEFAULT 'daily' CHECK (cadence IN ('manual','daily','business_daily','custom')),
  channel text NOT NULL DEFAULT 'email' CHECK (channel IN ('email','sms','whatsapp','telegram','internal')),
  next_due_at timestamptz,
  max_attempts integer CHECK (max_attempts IS NULL OR max_attempts >= 0),
  attempts_count integer NOT NULL DEFAULT 0 CHECK (attempts_count >= 0),
  escalation_after_attempts integer CHECK (escalation_after_attempts IS NULL OR escalation_after_attempts >= 0),
  escalate_to text,
  last_attempt_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (request_id, channel)
);

CREATE TABLE IF NOT EXISTS signature.reminder_attempts (
  reminder_attempt_id text PRIMARY KEY,
  reminder_policy_id text NOT NULL REFERENCES signature.reminder_policies(reminder_policy_id) ON DELETE CASCADE,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  attempt_number integer NOT NULL CHECK (attempt_number > 0),
  channel text NOT NULL CHECK (channel IN ('email','sms','whatsapp','telegram','internal')),
  recipient text,
  due_at timestamptz,
  sent_at timestamptz,
  status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','sent','delivered','failed','skipped','cancelled')),
  provider_message_id text,
  error_message text,
  next_due_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signature.delivery_receipts (
  delivery_receipt_id text PRIMARY KEY,
  request_id text NOT NULL REFERENCES signature.document_requests(request_id) ON DELETE CASCADE,
  submitter_id text REFERENCES signature.submitters(submitter_id) ON DELETE SET NULL,
  attachment_id text REFERENCES signature.attachments(attachment_id) ON DELETE SET NULL,
  kind text NOT NULL CHECK (kind IN ('invitation','otp','reminder','final_copy','hash_notice','download_link')),
  channel text NOT NULL CHECK (channel IN ('email','sms','whatsapp','telegram','internal','download')),
  recipient text,
  provider_message_id text,
  status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','sent','delivered','opened','downloaded','failed','bounced','skipped')),
  sha256 text,
  sent_at timestamptz,
  delivered_at timestamptz,
  opened_at timestamptz,
  failed_at timestamptz,
  error_message text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signature.metric_snapshots (
  metric_snapshot_id bigserial PRIMARY KEY,
  metric_scope text NOT NULL DEFAULT 'global' CHECK (metric_scope IN ('global','template','request','owner')),
  scope_ref text,
  active_requests integer NOT NULL DEFAULT 0,
  pending_signers integer NOT NULL DEFAULT 0,
  expiring_soon integer NOT NULL DEFAULT 0,
  completed_this_month integer NOT NULL DEFAULT 0,
  declined_this_month integer NOT NULL DEFAULT 0,
  average_seconds_to_sign numeric(16,2),
  reminder_success_rate numeric(9,6),
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  captured_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_signature_document_requests_template_version ON signature.document_requests(template_version_id);
CREATE INDEX IF NOT EXISTS idx_signature_document_requests_lifecycle ON signature.document_requests(status, expires_at, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_template_versions_template ON signature.template_versions(template_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_signature_template_versions_status ON signature.template_versions(status, activated_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_field_placements_version_role ON signature.field_placements(template_version_id, role, page_number);
CREATE INDEX IF NOT EXISTS idx_signature_field_placements_type ON signature.field_placements(field_type, required);
CREATE INDEX IF NOT EXISTS idx_signature_field_values_request_submitter ON signature.field_values(request_id, submitter_id, status);
CREATE INDEX IF NOT EXISTS idx_signature_field_values_field ON signature.field_values(field_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_comments_request_field ON signature.comments(request_id, field_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_comments_submitter ON signature.comments(submitter_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_reminder_policies_next_due ON signature.reminder_policies(enabled, next_due_at);
CREATE INDEX IF NOT EXISTS idx_signature_reminder_attempts_policy_due ON signature.reminder_attempts(reminder_policy_id, due_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_reminder_attempts_request_status ON signature.reminder_attempts(request_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_delivery_receipts_request_kind ON signature.delivery_receipts(request_id, kind, status);
CREATE INDEX IF NOT EXISTS idx_signature_delivery_receipts_submitter ON signature.delivery_receipts(submitter_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signature_metric_snapshots_captured ON signature.metric_snapshots(metric_scope, scope_ref, captured_at DESC);

CREATE OR REPLACE VIEW signature.request_metrics AS
SELECT
  r.request_id,
  r.template_id,
  r.template_version_id,
  r.status,
  r.expires_at,
  r.created_at,
  r.sent_at,
  r.completed_at,
  count(s.submitter_id) FILTER (WHERE s.required AND s.role IN ('signer','approver')) AS required_submitters,
  count(s.submitter_id) FILTER (WHERE s.required AND s.role IN ('signer','approver') AND s.status IN ('signed','approved')) AS completed_required_submitters,
  count(s.submitter_id) FILTER (WHERE s.status IN ('pending','sent','viewed','started')) AS pending_submitters,
  count(s.submitter_id) FILTER (WHERE s.status = 'declined') AS declined_submitters,
  count(ra.reminder_attempt_id) FILTER (WHERE ra.status IN ('sent','delivered')) AS reminders_sent,
  count(ra.reminder_attempt_id) FILTER (WHERE ra.status = 'failed') AS reminder_failures,
  count(dr.delivery_receipt_id) FILTER (WHERE dr.kind = 'final_copy' AND dr.status IN ('sent','delivered','opened','downloaded')) AS final_copy_receipts,
  EXTRACT(EPOCH FROM (r.completed_at - r.sent_at))::numeric AS seconds_to_complete
FROM signature.document_requests r
LEFT JOIN signature.submitters s ON s.request_id = r.request_id
LEFT JOIN signature.reminder_attempts ra ON ra.request_id = r.request_id
LEFT JOIN signature.delivery_receipts dr ON dr.request_id = r.request_id
GROUP BY r.request_id;

CREATE OR REPLACE VIEW signature.dashboard_metrics AS
SELECT
  count(*) FILTER (WHERE status IN ('sent','viewed','partially_signed')) AS active_requests,
  coalesce(sum(pending_submitters), 0)::bigint AS pending_signers,
  count(*) FILTER (
    WHERE status IN ('sent','viewed','partially_signed')
      AND expires_at IS NOT NULL
      AND expires_at <= now() + interval '7 days'
  ) AS expiring_soon,
  count(*) FILTER (WHERE status = 'completed' AND completed_at >= date_trunc('month', now())) AS completed_this_month,
  avg(seconds_to_complete) FILTER (WHERE status = 'completed' AND seconds_to_complete IS NOT NULL) AS average_seconds_to_sign,
  CASE
    WHEN coalesce(sum(reminders_sent + reminder_failures), 0) = 0 THEN NULL
    ELSE sum(reminders_sent)::numeric / sum(reminders_sent + reminder_failures)::numeric
  END AS reminder_success_rate,
  now() AS measured_at
FROM signature.request_metrics;

GRANT USAGE ON SCHEMA signature TO signature_runtime, agent_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA signature TO signature_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA signature TO agent_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA signature TO signature_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA signature GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO signature_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA signature GRANT SELECT ON TABLES TO agent_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA signature GRANT USAGE, SELECT ON SEQUENCES TO signature_runtime;
