from pydantic import BaseModel
from typing import Any


class HybridRetrieveFinanceKnowledgeInput(BaseModel):
    workspace_id: str
    query: str
    top_k: int = 5


class RetrievedChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any]
    vector_score: float
    lexical_score: float
    final_score: float


class HybridRetrieveFinanceKnowledgeOutput(BaseModel):
    items: list[RetrievedChunkItem]


class GetRelatedChunksInput(BaseModel):
    workspace_id: str
    chunk_ids: list[str]


class RelatedChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any]


class GetRelatedChunksOutput(BaseModel):
    items: list[RelatedChunkItem]


class DeleteKnowledgeBySourceInput(BaseModel):
    workspace_id: str
    source_type: str
    source_ref: str


class DeleteKnowledgeBySourceOutput(BaseModel):
    deleted_documents: int
    deleted_chunks: int