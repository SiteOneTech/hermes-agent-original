-- Structured social/contact-channel profiles for CRM contacts.
-- Keep social identities as first-class CRM rows instead of burying them in contact metadata.
CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.contact_social_profiles (
  social_profile_id text PRIMARY KEY,
  contact_id text NOT NULL REFERENCES crm.contacts(contact_id) ON DELETE CASCADE,
  platform text NOT NULL,
  handle text,
  external_id text,
  profile_url text,
  display_name text,
  status text NOT NULL DEFAULT 'active',
  is_primary boolean NOT NULL DEFAULT false,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (platform <> ''),
  CHECK (handle IS NOT NULL OR external_id IS NOT NULL OR profile_url IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_crm_contact_social_profiles_contact
  ON crm.contact_social_profiles(contact_id, platform, status);

CREATE INDEX IF NOT EXISTS idx_crm_contact_social_profiles_handle
  ON crm.contact_social_profiles(platform, handle)
  WHERE handle IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_crm_contact_social_profiles_external_id
  ON crm.contact_social_profiles(platform, external_id)
  WHERE external_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_crm_contact_social_profiles_contact_platform_handle
  ON crm.contact_social_profiles(contact_id, platform, lower(handle))
  WHERE handle IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_crm_contact_social_profiles_contact_platform_external_id
  ON crm.contact_social_profiles(contact_id, platform, external_id)
  WHERE external_id IS NOT NULL;

GRANT SELECT, INSERT, UPDATE ON crm.contact_social_profiles TO crm_runtime;
