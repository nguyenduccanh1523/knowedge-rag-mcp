from app.repositories.knowledge_repository import KnowledgeRepository


class LexicalSearchService:
    def __init__(self):
        self.repo = KnowledgeRepository()

    def search(self, workspace_id: str, query: str, top_k: int) -> list[dict]:
        return self.repo.lexical_search(workspace_id, query, top_k)
