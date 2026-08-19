from __future__ import annotations

import hashlib
import re
import sqlite3
import uuid
from dataclasses import dataclass

from .errors import StorageError


@dataclass(frozen=True)
class RetrievalScope:
    handle: str
    tenant_id: str
    subject_id: str
    policy_version: int
    source_ids: frozenset[str]


@dataclass(frozen=True)
class StoredSource:
    source_id: str
    tenant_id: str
    project_id: str
    owner_id: str
    source_version: int
    classification: str
    content: str
    content_hash: str


class SQLiteForcedScopeAdapter:
    """SQLite adapter that simulates database-enforced forced RLS.

    Callers receive an opaque, server-issued scope handle.  Retrieval accepts
    only that handle and applies tenant and source predicates in SQL; no
    client-provided tenant/user/role value is accepted by the query method.
    """

    def __init__(self, sources: list[StoredSource]) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE sources (
              source_id TEXT PRIMARY KEY,
              tenant_id TEXT NOT NULL,
              project_id TEXT NOT NULL,
              owner_id TEXT NOT NULL,
              source_version INTEGER NOT NULL,
              classification TEXT NOT NULL,
              content TEXT NOT NULL,
              content_hash TEXT NOT NULL
            )
            """
        )
        self.connection.executemany(
            "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    source.source_id,
                    source.tenant_id,
                    source.project_id,
                    source.owner_id,
                    source.source_version,
                    source.classification,
                    source.content,
                    source.content_hash,
                )
                for source in sources
            ],
        )
        self.connection.commit()
        self._scopes: dict[str, RetrievalScope] = {}

    def issue_forced_scope(
        self,
        *,
        tenant_id: str,
        subject_id: str,
        policy_version: int,
        source_ids: frozenset[str],
    ) -> str:
        if not tenant_id or not subject_id:
            raise StorageError("Forced scope requires server-derived identity.")
        handle = uuid.uuid4().hex
        self._scopes[handle] = RetrievalScope(
            handle=handle,
            tenant_id=tenant_id,
            subject_id=subject_id,
            policy_version=policy_version,
            source_ids=source_ids,
        )
        return handle

    def _scope(self, handle: str) -> RetrievalScope:
        scope = self._scopes.get(handle)
        if scope is None:
            raise StorageError("Forced scope is unknown or expired.")
        return scope

    def retrieve(self, handle: str, query: str, *, limit: int = 5) -> list[StoredSource]:
        if not isinstance(query, str) or not query.strip():
            raise StorageError("Retrieval query must be non-empty text.")
        if not 1 <= limit <= 20:
            raise StorageError("Retrieval limit is outside the bounded range.")
        scope = self._scope(handle)
        if not scope.source_ids:
            return []
        placeholders = ",".join("?" for _ in scope.source_ids)
        # The tenant predicate is deliberately unconditional: this is the
        # application-level simulation of PostgreSQL FORCE ROW LEVEL SECURITY.
        rows = self.connection.execute(
            f"""
            SELECT * FROM sources
            WHERE tenant_id = ? AND source_id IN ({placeholders})
            ORDER BY source_id ASC
            LIMIT ?
            """,
            [scope.tenant_id, *sorted(scope.source_ids), limit],
        ).fetchall()
        terms = {term for term in re.findall(r"[A-Za-z0-9_.-]+", query.lower()) if term}
        scored = []
        for row in rows:
            haystack = f"{row['source_id']} {row['content']}".lower()
            score = sum(haystack.count(term) for term in terms)
            if score > 0:
                scored.append((score, row["source_id"], row))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            StoredSource(
                source_id=row["source_id"],
                tenant_id=row["tenant_id"],
                project_id=row["project_id"],
                owner_id=row["owner_id"],
                source_version=row["source_version"],
                classification=row["classification"],
                content=row["content"],
                content_hash=row["content_hash"],
            )
            for _score, _source_id, row in scored
        ]

    def close(self) -> None:
        self.connection.close()


def synthetic_source(
    source_id: str,
    tenant_id: str,
    project_id: str,
    owner_id: str,
    content: str,
    *,
    classification: str = "internal",
    source_version: int = 1,
) -> StoredSource:
    return StoredSource(
        source_id=source_id,
        tenant_id=tenant_id,
        project_id=project_id,
        owner_id=owner_id,
        source_version=source_version,
        classification=classification,
        content=content,
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )
