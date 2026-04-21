from pydantic import BaseModel, Field
from typing import Any


class KnowledgeDocumentInput(BaseModel):
    source_type: str
    source_ref: str
    title: str | None = None
    text: str = Field(min_length=1)
    metadata: dict[str, Any] = {}


class UpsertFinanceKnowledgeInput(BaseModel):
    workspace_id: str
    documents: list[KnowledgeDocumentInput]


class UpsertFinanceKnowledgeOutput(BaseModel):
    document_count: int
    chunk_count: int