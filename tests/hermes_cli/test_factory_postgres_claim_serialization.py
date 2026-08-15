"""Real PostgreSQL concurrency coverage for Factory task claims.

This is deliberately isolated from the Agent Core database: each test starts an
unnamed-network PostgreSQL container and destroys it during teardown.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path

import pytest

from hermes_cli import factory_pg


class _EphemeralPostgresSql:
    def __init__(self, container_name: str) -> None:
        self.container_name = container_name

    @staticmethod
    def quote_literal(value):
        return "NULL" if value is None else "'" + str(value).replace("'", "''") + "'"

    @staticmethod
    def quote_jsonb(value):
        return "'" + json.dumps(value if value is not None else {}, sort_keys=True).replace("'", "''") + "'::jsonb"

    @staticmethod
    def runtime_env():
        return {}

    def _psql(self, statement: str, *, application_name: str) -> str:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                self.container_name,
                "psql",
                "-U",
                "postgres",
                "-d",
                "factorytest",
                "-v",
                "ON_ERROR_STOP=1",
                "-At",
            ],
            input=f"SET application_name={json.dumps(application_name)};\n{statement}",
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode:
            raise RuntimeError(proc.stderr)
        return "\n".join(line for line in proc.stdout.splitlines() if line != "SET").strip()

    def execute(self, statement: str, *, application_name: str = "factory-test") -> str:
        return self._psql(statement, application_name=application_name)

    def psql(self, statement: str, *, user=None):
        self._psql(statement, application_name="factory-claim-test")

    def json_query(self, statement: str, *, user=None):
        raw = self._psql(statement, application_name="factory-claim-test")
        return json.loads(raw) if raw else []


@pytest.fixture
def ephemeral_factory_postgres(monkeypatch):
    if not shutil.which("docker"):
        pytest.skip("Docker is required for real PostgreSQL claim serialization coverage")
    if subprocess.run(["docker", "info"], capture_output=True, text=True, check=False).returncode:
        pytest.skip("Docker daemon is unavailable for real PostgreSQL claim serialization coverage")

    container_name = f"factory-claim-test-{uuid.uuid4().hex[:10]}"
    started = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            container_name,
            "-e",
            "POSTGRES_PASSWORD=test",
            "-e",
            "POSTGRES_DB=factorytest",
            "postgres:16",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if started.returncode:
        pytest.skip(f"Unable to start isolated PostgreSQL container: {started.stderr.strip()}")

    database = _EphemeralPostgresSql(container_name)
    try:
        for _ in range(60):
            probe = subprocess.run(
                ["docker", "exec", container_name, "psql", "-U", "postgres", "-d", "factorytest", "-Atc", "select 1"],
                capture_output=True,
                text=True,
                check=False,
            )
            if probe.returncode == 0 and probe.stdout.strip() == "1":
                break
            time.sleep(0.2)
        else:
            pytest.fail("isolated PostgreSQL container never became queryable")

        database.execute(
            """
            CREATE SCHEMA factory;
            CREATE TABLE factory.projects(
                project_id text PRIMARY KEY,
                autonomous_enabled boolean NOT NULL,
                status text NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
                updated_at timestamptz
            );
            CREATE TABLE factory.tasks(
                task_id text PRIMARY KEY,
                project_id text NOT NULL,
                lane_id text,
                status text NOT NULL,
                claimed_by text,
                claimed_at timestamptz,
                lease_until timestamptz,
                retry_count integer DEFAULT 0,
                evidence_status text,
                result_summary text,
                metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
                updated_at timestamptz,
                owner_profile text,
                reviewer_profile text,
                engine text
            );
            CREATE TABLE factory.gates(
                gate_id bigserial PRIMARY KEY,
                project_id text NOT NULL,
                lane_id text,
                task_id text,
                gate_type text NOT NULL,
                status text NOT NULL,
                reviewer text,
                evidence jsonb NOT NULL DEFAULT '{}'::jsonb,
                notes text,
                timestamp timestamptz NOT NULL DEFAULT now()
            );
            CREATE TABLE factory.task_runs(
                run_id text PRIMARY KEY,
                task_id text,
                project_id text,
                lane_id text,
                worker_profile text,
                reviewer_profile text,
                engine text,
                status text,
                started_at timestamptz,
                heartbeat_at timestamptz,
                metadata jsonb
            );
            CREATE TABLE factory.events(
                id bigserial PRIMARY KEY,
                project_id text,
                lane_id text,
                task_id text,
                actor text,
                event_type text,
                message text,
                metadata jsonb
            );
            CREATE OR REPLACE FUNCTION factory.pause_writer() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                IF current_setting('application_name', true) = 'writer-lock-test' THEN
                    PERFORM pg_sleep(1.2);
                END IF;
                RETURN NEW;
            END
            $$;
            CREATE TRIGGER projects_pause
                BEFORE UPDATE ON factory.projects
                FOR EACH ROW EXECUTE FUNCTION factory.pause_writer();
            """
        )
        migration = (
            Path(__file__).resolve().parents[2]
            / "db/modules/factory/000005_document_dispatch_readiness_serialization.sql"
        )
        database.execute(migration.read_text(encoding="utf-8"))
        monkeypatch.setattr(factory_pg, "sql", database)
        monkeypatch.setattr(factory_pg, "ensure_runtime_schema", lambda: None)
        yield database
    finally:
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, text=True, check=False)


def _readiness(*, docs_ready: bool, source_revision: int = 0) -> dict[str, object]:
    return {
        "schema_version": 2,
        "source_revision": source_revision,
        "docs_ready": docs_ready,
        "notion_ready": True,
        "notion_required": False,
        "docs_first_waived": False,
    }


def test_readiness_source_update_invalidates_snapshot_before_product_claim(ephemeral_factory_postgres):
    """A canonical source mutation must invalidate a previously green snapshot.

    This models close_task's project Notion projection update occurring after a
    direct claimer performed its green preflight but before the claimer acquires
    its project lease. The database invariant—not a later Python reconcile—must
    make the stale product claim fail closed.
    """
    database = ephemeral_factory_postgres
    green = _readiness(docs_ready=True)
    database.execute(
        """
        INSERT INTO factory.projects(project_id, autonomous_enabled, status, metadata)
        VALUES ('source-gap', true, 'active', jsonb_build_object('document_dispatch_readiness', $json$%s$json$::jsonb));
        INSERT INTO factory.tasks(task_id, project_id, lane_id, status, owner_profile)
        VALUES ('source-gap-implementation', 'source-gap', 'lane', 'todo', 'builder');
        """ % json.dumps(green)
    )

    # This is the authoritative project metadata transition committed by a
    # canonical readiness writer before it can subsequently reconcile.
    database.execute(
        """
        UPDATE factory.projects
        SET metadata=metadata || '{"notion_projection_stale": true, "notion_sync_required": true}'::jsonb
        WHERE project_id='source-gap';
        """
    )

    snapshot_exists = database.execute(
        "SELECT metadata ? 'document_dispatch_readiness' FROM factory.projects WHERE project_id='source-gap';"
    )
    assert snapshot_exists == "f"

    claimed = factory_pg._claim_task_with_project_lease(
        project_id="source-gap",
        task_id="source-gap-implementation",
        expected_statuses=("todo",),
        claimed_status="claimed",
        worker="test-worker",
        worker_profile="builder",
        run_id="source-gap-run",
        run_type="normal",
        event_type="task_claimed",
        event_message="must be denied after source invalidation",
        document_dispatch_readiness=green,
    )

    assert claimed is None
    assert database.execute("SELECT status FROM factory.tasks WHERE task_id='source-gap-implementation';") == "todo"
    assert database.execute("SELECT count(*) FROM factory.task_runs WHERE project_id='source-gap';") == "0"
    assert database.execute("SELECT count(*) FROM factory.events WHERE project_id='source-gap';") == "0"


def test_record_gate_invalidates_snapshot_before_a_product_claim(ephemeral_factory_postgres, monkeypatch):
    database = ephemeral_factory_postgres
    green = _readiness(docs_ready=True)
    database.execute(
        """
        INSERT INTO factory.projects(project_id, autonomous_enabled, status, metadata)
        VALUES ('gate-gap', true, 'active', jsonb_build_object('document_dispatch_readiness', $json$%s$json$::jsonb));
        INSERT INTO factory.tasks(task_id, project_id, lane_id, status, owner_profile)
        VALUES ('gate-gap-implementation', 'gate-gap', 'lane', 'todo', 'builder');
        """ % json.dumps(green)
    )
    monkeypatch.setattr(factory_pg, "reconcile_project", lambda project_id: {"project_id": project_id})

    gate = factory_pg.record_gate("gate-gap", "review", "failed", reviewer="qa", evidence={"reason": "red"})

    assert gate["gate_id"]
    assert database.execute(
        "SELECT metadata ? 'document_dispatch_readiness' FROM factory.projects WHERE project_id='gate-gap';"
    ) == "f"
    assert factory_pg._claim_task_with_project_lease(
        project_id="gate-gap",
        task_id="gate-gap-implementation",
        expected_statuses=("todo",),
        claimed_status="claimed",
        worker="test-worker",
        worker_profile="builder",
        run_id="gate-gap-run",
        run_type="normal",
        event_type="task_claimed",
        event_message="must be denied after gate source mutation",
        document_dispatch_readiness=green,
    ) is None
    assert database.execute("SELECT count(*) FROM factory.task_runs WHERE project_id='gate-gap';") == "0"


def test_factory_claim_serializes_durable_readiness_and_queues_run_atomically(ephemeral_factory_postgres):
    database = ephemeral_factory_postgres
    green = _readiness(docs_ready=True)
    database.execute(
        """
        INSERT INTO factory.projects(project_id, autonomous_enabled, status, metadata)
        VALUES ('demo', true, 'active', jsonb_build_object('document_dispatch_readiness', $json$%s$json$::jsonb));
        INSERT INTO factory.tasks(task_id, project_id, lane_id, status, owner_profile)
        VALUES ('demo-implementation', 'demo', 'lane', 'todo', 'builder');
        """ % json.dumps(green)
    )

    writer_error: list[Exception] = []

    def regress_readiness() -> None:
        try:
            database.execute(
                """
                UPDATE factory.projects
                SET metadata=jsonb_set(metadata, '{document_dispatch_readiness,docs_ready}', 'false'::jsonb)
                WHERE project_id='demo';
                """,
                application_name="writer-lock-test",
            )
        except Exception as exc:  # pragma: no cover - assertion below reports it
            writer_error.append(exc)

    writer = threading.Thread(target=regress_readiness)
    writer.start()
    for _ in range(30):
        row_locks = database.execute(
            """
            SELECT count(*)
            FROM pg_locks lock_row
            JOIN pg_class relation_row ON relation_row.oid=lock_row.relation
            WHERE relation_row.relname='projects' AND lock_row.mode='RowExclusiveLock';
            """
        )
        if row_locks and int(row_locks) >= 1:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"readiness writer never acquired the project lock: {writer_error}")

    denied = factory_pg._claim_task_with_project_lease(
        project_id="demo",
        task_id="demo-implementation",
        expected_statuses=("todo",),
        claimed_status="claimed",
        worker="factory-test",
        worker_profile="builder",
        run_id="run-stale",
        run_type="implementation",
        event_type="task_claimed",
        event_message="claim should fail closed",
        document_dispatch_readiness=green,
    )
    writer.join(timeout=5)

    assert writer_error == []
    assert denied is None
    assert database.execute("SELECT status FROM factory.tasks WHERE task_id='demo-implementation';") == "todo"
    assert database.execute("SELECT count(*) FROM factory.task_runs;") == "0"

    green_after_writer = _readiness(docs_ready=True, source_revision=1)
    database.execute(
        """
        UPDATE factory.projects
        SET metadata=metadata || jsonb_build_object(
              'document_dispatch_readiness', $json$%s$json$::jsonb,
              'document_dispatch_readiness_reconciled_at', 'test-reconcile-after-writer'
            )
        WHERE project_id='demo';
        """ % json.dumps(green_after_writer)
    )
    claimed = factory_pg._claim_task_with_project_lease(
        project_id="demo",
        task_id="demo-implementation",
        expected_statuses=("todo",),
        claimed_status="claimed",
        worker="factory-test",
        worker_profile="builder",
        run_id="run-green",
        run_type="implementation",
        event_type="task_claimed",
        event_message="claim succeeds atomically",
        document_dispatch_readiness=green_after_writer,
    )

    assert claimed and claimed["task_id"] == "demo-implementation"
    assert database.execute("SELECT status FROM factory.tasks WHERE task_id='demo-implementation';") == "claimed"
    assert database.execute("SELECT count(*) FROM factory.task_runs WHERE status='queued';") == "1"
    assert database.execute("SELECT count(*) FROM factory.events WHERE event_type='task_claimed';") == "1"

    # A stale reconciliation snapshot cannot cancel a task after the atomic
    # claim has queued its run, even if an external writer corrupted the task
    # state back to a nominally cancellable value.
    database.execute(
        """
        UPDATE factory.tasks
        SET status='rework', metadata='{"factory_reconciliation_task": true, "reconciliation_anomaly": "missing_required_docs"}'::jsonb
        WHERE task_id='demo-implementation';
        """
    )
    cancelled = factory_pg.cancel_resolved_reconciliation_tasks(
        {"project_id": "demo", "metadata": {}},
        [],
        [{
            "project_id": "demo",
            "task_id": "demo-implementation",
            "status": "rework",
            "metadata": {"factory_reconciliation_task": True, "reconciliation_anomaly": "missing_required_docs"},
        }],
    )
    assert cancelled == []
    assert database.execute("SELECT status FROM factory.tasks WHERE task_id='demo-implementation';") == "rework"
