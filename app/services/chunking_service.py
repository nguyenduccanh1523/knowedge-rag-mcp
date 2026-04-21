from app.config import settings


class ChunkingService:
    def __init__(self) -> None:
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def split_text(self, text: str) -> list[str]:
        normalized = " ".join(text.split())
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        text_len = len(normalized)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_len:
                break

            start = max(end - self.chunk_overlap, start + 1)

        return chunks
