from app.config import settings


class RerankService:
    def merge_and_rank(
        self, vector_hits: list[dict], lexical_hits: list[dict], top_k: int
    ) -> list[dict]:
        merged: dict[str, dict] = {}

        for item in vector_hits:
            merged[item["chunk_id"]] = {
                **item,
                "vector_score": float(item.get("vector_score") or 0.0),
                "lexical_score": 0.0,
            }

        for item in lexical_hits:
            chunk_id = item["chunk_id"]
            if chunk_id not in merged:
                merged[chunk_id] = {
                    **item,
                    "vector_score": 0.0,
                    "lexical_score": float(item.get("lexical_score") or 0.0),
                }
            else:
                merged[chunk_id]["lexical_score"] = float(
                    item.get("lexical_score") or 0.0
                )

        max_vector = (
            max((v["vector_score"] for v in merged.values()), default=1.0) or 1.0
        )
        max_lexical = (
            max((v["lexical_score"] for v in merged.values()), default=1.0) or 1.0
        )

        ranked = []
        for item in merged.values():
            vector_score = item["vector_score"] / max_vector if max_vector > 0 else 0.0
            lexical_score = (
                item["lexical_score"] / max_lexical if max_lexical > 0 else 0.0
            )

            final_score = (
                settings.rerank_vector_weight * vector_score
                + settings.rerank_lexical_weight * lexical_score
            )

            ranked.append(
                {
                    **item,
                    "vector_score": round(vector_score, 6),
                    "lexical_score": round(lexical_score, 6),
                    "final_score": round(final_score, 6),
                }
            )

        ranked.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked[:top_k]
