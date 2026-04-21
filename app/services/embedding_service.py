from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(
            settings.embedding_model_name,
            device=settings.embedding_device,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode_document(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self.model.encode_query(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.tolist()
