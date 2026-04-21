from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.lexical_search_service import LexicalSearchService
from app.services.vector_search_service import VectorSearchService
from app.services.rerank_service import RerankService


class KnowledgeService:
    def __init__(self) -> None:
        self.repo = KnowledgeRepository()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.lexical_search_service = LexicalSearchService()
        self.vector_search_service = VectorSearchService()
        self.rerank_service = RerankService()

    def upsert_documents(self, workspace_id: str, documents: list[dict]) -> dict:
        total_chunks = 0

        for document in documents:
            document_id = self.repo.upsert_document(
                workspace_id=workspace_id,
                source_type=document["source_type"],
                source_ref=document["source_ref"],
                title=document.get("title"),
                raw_text=document["text"],
                metadata=document.get("metadata", {}),
            )

            self.repo.delete_chunks_by_document(document_id)

            chunks = self.chunking_service.split_text(document["text"])
            embeddings = (
                self.embedding_service.embed_documents(chunks) if chunks else []
            )

            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                self.repo.insert_chunk(
                    document_id=document_id,
                    workspace_id=workspace_id,
                    chunk_index=idx,
                    content=chunk,
                    token_count=len(chunk.split()),
                    metadata={
                        **document.get("metadata", {}),
                        "source_type": document["source_type"],
                        "source_ref": document["source_ref"],
                        "title": document.get("title"),
                    },
                    embedding=embedding,
                )

            total_chunks += len(chunks)

        return {
            "document_count": len(documents),
            "chunk_count": total_chunks,
        }

    def hybrid_retrieve(self, workspace_id: str, query: str, top_k: int) -> dict:
        vector_hits = self.vector_search_service.search(workspace_id, query, top_k * 2)
        lexical_hits = self.lexical_search_service.search(
            workspace_id, query, top_k * 2
        )

        ranked = self.rerank_service.merge_and_rank(vector_hits, lexical_hits, top_k)

        return {"items": ranked}

    def get_related_chunks(self, workspace_id: str, chunk_ids: list[str]) -> dict:
        items = self.repo.get_related_chunks(workspace_id, chunk_ids)
        return {"items": items}

    def delete_by_source(
        self, workspace_id: str, source_type: str, source_ref: str
    ) -> dict:
        return self.repo.delete_by_source(workspace_id, source_type, source_ref)
