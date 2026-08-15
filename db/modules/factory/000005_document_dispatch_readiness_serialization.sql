-- FRE-028: document-dispatch readiness must be invalidated by the same
-- database write that changes its authoritative project metadata source.
--
-- A Python reconciliation that runs later is intentionally not the safety
-- boundary: a direct product claim can interleave between a source mutation and
-- that later reconciliation under PostgreSQL READ COMMITTED. This trigger makes
-- the project row fail closed until reconcile_project() writes a readiness
-- snapshot derived from the current source-revision.

CREATE OR REPLACE FUNCTION factory.invalidate_document_dispatch_readiness_on_source_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  old_metadata jsonb := COALESCE(OLD.metadata, '{}'::jsonb);
  new_metadata jsonb := COALESCE(NEW.metadata, '{}'::jsonb);
  old_revision bigint := CASE
    WHEN (old_metadata->>'document_dispatch_readiness_source_revision') ~ '^[0-9]{1,18}$'
      THEN (old_metadata->>'document_dispatch_readiness_source_revision')::bigint
    ELSE 0
  END;
  readiness jsonb := new_metadata->'document_dispatch_readiness';
  reconciled_at_changed boolean;
BEGIN
  -- A project update that did not alter metadata (for example the serialized
  -- claim lease's updated_at touch) cannot invalidate readiness.
  IF new_metadata IS NOT DISTINCT FROM old_metadata THEN
    RETURN NEW;
  END IF;

  reconciled_at_changed :=
    (new_metadata->>'document_dispatch_readiness_reconciled_at')
    IS DISTINCT FROM
    (old_metadata->>'document_dispatch_readiness_reconciled_at');

  -- Only the reconciler is allowed to preserve/replace a readiness snapshot.
  -- Its snapshot must attest to the project source revision that was current
  -- when it read all authoritative inputs, and each reconciliation receives a
  -- fresh marker. A stale reconciliation that races a source mutation fails
  -- closed rather than restoring an obsolete green snapshot.
  IF jsonb_typeof(readiness) = 'object'
     AND jsonb_typeof(readiness->'source_revision') = 'number'
     AND (readiness->>'source_revision') ~ '^[0-9]+$'
     AND (readiness->>'source_revision')::bigint = old_revision
     AND reconciled_at_changed
  THEN
    RETURN NEW;
  END IF;

  NEW.metadata :=
    (new_metadata
      - 'document_dispatch_readiness'
      - 'document_dispatch_readiness_reconciled_at')
    || jsonb_build_object(
      'document_dispatch_readiness_source_revision', old_revision + 1,
      'document_dispatch_readiness_invalidated_at',
        to_char(clock_timestamp() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
      'document_dispatch_readiness_invalidated_reason',
        'authoritative_project_metadata_changed'
    );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS factory_projects_document_dispatch_readiness_guard
  ON factory.projects;

CREATE TRIGGER factory_projects_document_dispatch_readiness_guard
BEFORE UPDATE OF metadata ON factory.projects
FOR EACH ROW
EXECUTE FUNCTION factory.invalidate_document_dispatch_readiness_on_source_mutation();

-- The trigger executes as the table owner; Factory runtime writers retain only
-- their existing least-privilege UPDATE rights on factory.projects.
