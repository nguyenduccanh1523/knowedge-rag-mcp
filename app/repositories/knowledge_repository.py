import json
from sqlalchemy import text

from app.repositories.db import SessionLocal


def to_pgvector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(v)) for v in values) + "]"


class KnowledgeRepository:
    def upsert_document(
        self,
        workspace_id: str,
        source_type: str,
        source_ref: str,
        title: str | None,
        raw_text: str,
        metadata: dict,
    ) -> str:
        sql = text(
            """
            INSERT INTO knowledge_documents (
                workspace_id,
                source_type,
                source_ref,
                title,
                raw_text,
                metadata,
                status,
                created_at,
                updated_at
            )
            VALUES (
                :workspace_id::uuid,
                :source_type,
                :source_ref,
                :title,
                :raw_text,
                CAST(:metadata AS jsonb),
                'ACTIVE',
                NOW(),
                NOW()
            )
            ON CONFLICT (workspace_id, source_type, source_ref)
            DO UPDATE SET
                title = EXCLUDED.title,
                raw_text = EXCLUDED.raw_text,
                metadata = EXCLUDED.metadata,
                status = 'ACTIVE',
                updated_at = NOW()
            RETURNING id::text
        """
        )

        with SessionLocal() as session:
            row = session.execute(
                sql,
                {
                    "workspace_id": workspace_id,
                    "source_type": source_type,
                    "source_ref": source_ref,
                    "title": title,
                    "raw_text": raw_text,
                    "metadata": json.dumps(metadata),
                },
            ).first()
            session.commit()

        return row[0]

    def delete_chunks_by_document(self, document_id: str) -> int:
        sql = text(
            """
            DELETE FROM knowledge_chunks
            WHERE document_id = :document_id::uuid
        """
        )

        with SessionLocal() as session:
            result = session.execute(sql, {"document_id": document_id})
            session.commit()

        return result.rowcount or 0

    def insert_chunk(
        self,
        document_id: str,
        workspace_id: str,
        chunk_index: int,
        content: str,
        token_count: int,
        metadata: dict,
        embedding: list[float],
    ) -> str:
        sql = text(
            """
            INSERT INTO knowledge_chunks (
                document_id,
                workspace_id,
                chunk_index,
                content,
                token_count,
                metadata,
                embedding,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                :document_id::uuid,
                :workspace_id::uuid,
                :chunk_index,
                :content,
                :token_count,
                CAST(:metadata AS jsonb),
                CAST(:embedding AS vector),
                TRUE,
                NOW(),
                NOW()
            )
            RETURNING id::text
        """
        )

        with SessionLocal() as session:
            row = session.execute(
                sql,
                {
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "chunk_index": chunk_index,
                    "content": content,
                    "token_count": token_count,
                    "metadata": json.dumps(metadata),
                    "embedding": to_pgvector_literal(embedding),
                },
            ).first()
            session.commit()

        return row[0]

    def vector_search(
        self,
        workspace_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        sql = text(
            """
            SELECT
                kc.id::text AS chunk_id,
                kc.document_id::text AS document_id,
                kc.chunk_index,
                kc.content,
                kc.metadata,
                1 - (kc.embedding <=> CAST(:query_embedding AS vector)) AS vector_score
            FROM knowledge_chunks kc
            WHERE kc.workspace_id = :workspace_id::uuid
              AND kc.is_active = TRUE
              AND kc.embedding IS NOT NULL
            ORDER BY kc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
        """
        )

        with SessionLocal() as session:
            rows = (
                session.execute(
                    sql,
                    {
                        "workspace_id": workspace_id,
                        "query_embedding": to_pgvector_literal(query_embedding),
                        "top_k": top_k,
                    },
                )
                .mappings()
                .all()
            )

        return [dict(r) for r in rows]

    def lexical_search(
        self,
        workspace_id: str,
        query: str,
        top_k: int,
    ) -> list[dict]:
        sql = text(
            """
            SELECT
                kc.id::text AS chunk_id,
                kc.document_id::text AS document_id,
                kc.chunk_index,
                kc.content,
                kc.metadata,
                ts_rank_cd(kc.content_tsv, websearch_to_tsquery('simple', :query)) AS lexical_score
            FROM knowledge_chunks kc
            WHERE kc.workspace_id = :workspace_id::uuid
              AND kc.is_active = TRUE
              AND kc.content_tsv @@ websearch_to_tsquery('simple', :query)
            ORDER BY lexical_score DESC
            LIMIT :top_k
        """
        )

        with SessionLocal() as session:
            rows = (
                session.execute(
                    sql,
                    {
                        "workspace_id": workspace_id,
                        "query": query,
                        "top_k": top_k,
                    },
                )
                .mappings()
                .all()
            )

        return [dict(r) for r in rows]

    def get_related_chunks(self, workspace_id: str, chunk_ids: list[str]) -> list[dict]:
        if not chunk_ids:
            return []

        sql = text(
            """
            SELECT
                kc.id::text AS chunk_id,
                kc.document_id::text AS document_id,
                kc.chunk_index,
                kc.content,
                kc.metadata
            FROM knowledge_chunks kc
            WHERE kc.workspace_id = :workspace_id::uuid
              AND kc.id::text = ANY(:chunk_ids)
            ORDER BY kc.chunk_index ASC
        """
        )

        with SessionLocal() as session:
            rows = (
                session.execute(
                    sql,
                    {
                        "workspace_id": workspace_id,
                        "chunk_ids": chunk_ids,
                    },
                )
                .mappings()
                .all()
            )

        return [dict(r) for r in rows]

    def delete_by_source(
        self, workspace_id: str, source_type: str, source_ref: str
    ) -> dict:
        select_doc_sql = text(
            """
            SELECT id::text
            FROM knowledge_documents
            WHERE workspace_id = :workspace_id::uuid
              AND source_type = :source_type
              AND source_ref = :source_ref
        """
        )

        delete_chunks_sql = text(
            """
            DELETE FROM knowledge_chunks
            WHERE document_id = :document_id::uuid
        """
        )

        delete_doc_sql = text(
            """
            DELETE FROM knowledge_documents
            WHERE id = :document_id::uuid
        """
        )

        deleted_documents = 0
        deleted_chunks = 0

        with SessionLocal() as session:
            doc_row = session.execute(
                select_doc_sql,
                {
                    "workspace_id": workspace_id,
                    "source_type": source_type,
                    "source_ref": source_ref,
                },
            ).first()

            if not doc_row:
                return {"deleted_documents": 0, "deleted_chunks": 0}

            document_id = doc_row[0]

            chunk_result = session.execute(
                delete_chunks_sql, {"document_id": document_id}
            )
            doc_result = session.execute(delete_doc_sql, {"document_id": document_id})
            session.commit()

            deleted_chunks = chunk_result.rowcount or 0
            deleted_documents = doc_result.rowcount or 0

        return {
            "deleted_documents": deleted_documents,
            "deleted_chunks": deleted_chunks,
        }
