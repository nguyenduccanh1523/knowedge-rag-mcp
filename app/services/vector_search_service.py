from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.embedding_service import EmbeddingService


class VectorSearchService:
    def __init__(self):
        self.repo = KnowledgeRepository()
        self.embedding_service = EmbeddingService()

    def search(self, workspace_id: str, query: str, top_k: int) -> list[dict]:
        query_embedding = self.embedding_service.embed_query(query)
        return self.repo.vector_search(workspace_id, query_embedding, top_k)
