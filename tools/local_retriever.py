import os
import time
from pathlib import Path

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


class LocalRAGRetriever:
    def __init__(self):
        self.documents_path = Path(settings.documents_path)
        self.chunk_size = 900
        self.chunk_overlap = 150

    def search(self, question: str, top_k: int = 4) -> dict:
        start_time = time.perf_counter()

        chunks = self._load_chunks()

        if not chunks:
            return {
                "query": question,
                "chunks": [],
                "sources": [],
                "latency_seconds": round(time.perf_counter() - start_time, 4),
                "message": "No hay documentos cargados en data/documents.",
            }

        texts = [chunk["text"] for chunk in chunks]

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,
            ngram_range=(1, 2),
        )

        matrix = vectorizer.fit_transform(texts)
        query_vector = vectorizer.transform([question])

        similarities = cosine_similarity(query_vector, matrix).flatten()

        ranked = sorted(
            enumerate(similarities),
            key=lambda item: item[1],
            reverse=True,
        )

        selected_chunks = []

        for index, score in ranked[:top_k]:
            chunk = chunks[index]
            selected_chunks.append(
                {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "score": round(float(score), 4),
                }
            )

        sources = sorted(set(chunk["source"] for chunk in selected_chunks))

        return {
            "query": question,
            "chunks": selected_chunks,
            "sources": sources,
            "latency_seconds": round(time.perf_counter() - start_time, 4),
        }

    def _load_chunks(self) -> list[dict]:
        self.documents_path.mkdir(parents=True, exist_ok=True)

        all_chunks = []

        for file_path in self.documents_path.iterdir():
            if file_path.suffix.lower() == ".txt":
                text = file_path.read_text(encoding="utf-8")
            elif file_path.suffix.lower() == ".pdf":
                text = self._read_pdf(file_path)
            else:
                continue

            chunks = self._split_text(text)

            for chunk in chunks:
                all_chunks.append(
                    {
                        "text": chunk,
                        "source": file_path.name,
                    }
                )

        return all_chunks

    def _read_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)

        return "\n".join(pages_text)

    def _split_text(self, text: str) -> list[str]:
        clean_text = " ".join(text.split())

        if not clean_text:
            return []

        chunks = []
        start = 0

        while start < len(clean_text):
            end = start + self.chunk_size
            chunk = clean_text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks