from fastmcp import FastMCP

from app.schemas.ingest import UpsertFinanceKnowledgeInput, UpsertFinanceKnowledgeOutput
from app.schemas.retrieve import (
    HybridRetrieveFinanceKnowledgeInput,
    HybridRetrieveFinanceKnowledgeOutput,
    GetRelatedChunksInput,
    GetRelatedChunksOutput,
    DeleteKnowledgeBySourceInput,
    DeleteKnowledgeBySourceOutput,
)
from app.services.knowledge_service import KnowledgeService

knowledge_service = KnowledgeService()


def register_rag_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def upsert_finance_knowledge(input: UpsertFinanceKnowledgeInput) -> dict:
        result = knowledge_service.upsert_documents(
            workspace_id=input.workspace_id,
            documents=[doc.model_dump() for doc in input.documents],
        )
        return UpsertFinanceKnowledgeOutput.model_validate(result).model_dump()

    @mcp.tool
    def hybrid_retrieve_finance_knowledge(
        input: HybridRetrieveFinanceKnowledgeInput,
    ) -> dict:
        result = knowledge_service.hybrid_retrieve(
            workspace_id=input.workspace_id,
            query=input.query,
            top_k=input.top_k,
        )
        return HybridRetrieveFinanceKnowledgeOutput.model_validate(result).model_dump()

    @mcp.tool
    def get_related_chunks(input: GetRelatedChunksInput) -> dict:
        result = knowledge_service.get_related_chunks(
            workspace_id=input.workspace_id,
            chunk_ids=input.chunk_ids,
        )
        return GetRelatedChunksOutput.model_validate(result).model_dump()

    @mcp.tool
    def delete_knowledge_by_source(input: DeleteKnowledgeBySourceInput) -> dict:
        result = knowledge_service.delete_by_source(
            workspace_id=input.workspace_id,
            source_type=input.source_type,
            source_ref=input.source_ref,
        )
        return DeleteKnowledgeBySourceOutput.model_validate(result).model_dump()
