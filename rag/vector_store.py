import hashlib
import pickle
import re
import time
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


class LocalVectorStore:
    """
    Vector store local persistente para el MVP.

    Este componente implementa:
    - ingesta de documentos TXT/PDF;
    - chunking con overlap;
    - vectorización local con TF-IDF;
    - almacenamiento persistente del índice;
    - recuperación por similitud coseno;
    - reranking híbrido con similitud vectorial + coincidencia léxica.

    En producción, este componente puede reemplazarse por:
    - Amazon Titan Embeddings v2;
    - Amazon OpenSearch Serverless;
    - pgvector en Amazon RDS.
    """

    def __init__(self):
        self.documents_path = Path(settings.documents_path)
        self.vector_store_path = Path(settings.vector_store_path)
        self.index_file = self.vector_store_path / "local_vector_index.pkl"

        self.chunk_size = 900
        self.chunk_overlap = 150
        self.max_features = 12000

        self.supported_extensions = {".txt", ".pdf"}

    def search(self, question: str, top_k: int = 4, candidate_k: int = 12) -> dict:
        start_time = time.perf_counter()

        index = self._load_or_build_index()

        chunks = index.get("chunks", [])
        vectorizer = index.get("vectorizer")
        matrix = index.get("matrix")

        if not chunks or vectorizer is None or matrix is None:
            return {
                "query": question,
                "chunks": [],
                "sources": [],
                "latency_seconds": round(time.perf_counter() - start_time, 4),
                "message": "No hay documentos indexados en el vector store local.",
                "index_mode": "local_persistent_vector_store",
            }

        query_vector = vectorizer.transform([question])
        similarities = cosine_similarity(query_vector, matrix).flatten()

        candidate_limit = min(candidate_k, len(chunks))
        candidate_indexes = similarities.argsort()[::-1][:candidate_limit]

        max_vector_score = max(
            [float(similarities[index]) for index in candidate_indexes],
            default=0.0,
        )

        query_terms = self._tokenize(question)
        reranked_candidates = []

        for index_position in candidate_indexes:
            chunk = chunks[int(index_position)]
            raw_vector_score = float(similarities[index_position])

            if max_vector_score > 0:
                normalized_vector_score = raw_vector_score / max_vector_score
            else:
                normalized_vector_score = 0.0

            keyword_score = self._keyword_overlap_score(
                query_terms=query_terms,
                text=chunk["text"],
            )

            combined_score = (
                0.75 * normalized_vector_score
                + 0.25 * keyword_score
            )

            reranked_candidates.append(
                {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "raw_score": round(raw_vector_score, 4),
                    "vector_score": round(normalized_vector_score, 4),
                    "keyword_score": round(keyword_score, 4),
                    "combined_score": round(combined_score, 4),
                }
            )

        reranked_candidates = sorted(
            reranked_candidates,
            key=lambda item: item["combined_score"],
            reverse=True,
        )

        top_candidates = reranked_candidates[:top_k]

        max_combined_score = max(
            [item["combined_score"] for item in top_candidates],
            default=0.0,
        )

        selected_chunks = []

        for item in top_candidates:
            if max_combined_score > 0:
                final_score = item["combined_score"] / max_combined_score
            else:
                final_score = 0.0

            selected_chunks.append(
                {
                    "text": item["text"],
                    "source": item["source"],
                    "chunk_id": item["chunk_id"],
                    "raw_score": item["raw_score"],
                    "vector_score": item["vector_score"],
                    "keyword_score": item["keyword_score"],
                    "rerank_score": item["combined_score"],
                    "score": round(final_score, 4),
                }
            )

        sources = sorted(set(chunk["source"] for chunk in selected_chunks))

        return {
            "query": question,
            "chunks": selected_chunks,
            "sources": sources,
            "latency_seconds": round(time.perf_counter() - start_time, 4),
            "index_mode": "local_persistent_vector_store",
            "chunks_indexed": len(chunks),
            "reranking_strategy": "hybrid_vector_keyword_reranking",
        }

    def rebuild(self) -> dict:
        index = self._build_index()
        self._save_index(index)

        return {
            "success": True,
            "index_file": str(self.index_file),
            "chunks_indexed": len(index.get("chunks", [])),
            "documents_fingerprint": index.get("documents_fingerprint"),
        }

    def _load_or_build_index(self) -> dict[str, Any]:
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)

        current_fingerprint = self._documents_fingerprint()

        if self.index_file.exists():
            try:
                with open(self.index_file, "rb") as file:
                    index = pickle.load(file)

                if self._is_index_valid(index, current_fingerprint):
                    return index

            except (pickle.PickleError, EOFError, AttributeError, ValueError):
                pass

        index = self._build_index(current_fingerprint=current_fingerprint)
        self._save_index(index)

        return index

    def _is_index_valid(
        self,
        index: dict[str, Any],
        current_fingerprint: str,
    ) -> bool:
        return (
            index.get("documents_fingerprint") == current_fingerprint
            and index.get("chunk_size") == self.chunk_size
            and index.get("chunk_overlap") == self.chunk_overlap
            and index.get("max_features") == self.max_features
        )

    def _build_index(self, current_fingerprint: str | None = None) -> dict[str, Any]:
        chunks = self._load_chunks()

        if not chunks:
            return {
                "chunks": [],
                "vectorizer": None,
                "matrix": None,
                "documents_fingerprint": current_fingerprint
                or self._documents_fingerprint(),
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "max_features": self.max_features,
            }

        texts = [chunk["text"] for chunk in chunks]

        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=self.max_features,
            strip_accents="unicode",
        )

        matrix = vectorizer.fit_transform(texts)

        return {
            "chunks": chunks,
            "vectorizer": vectorizer,
            "matrix": matrix,
            "documents_fingerprint": current_fingerprint
            or self._documents_fingerprint(),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_features": self.max_features,
            "vectorizer_type": "tfidf",
            "created_with": "LocalVectorStore",
        }

    def _save_index(self, index: dict[str, Any]) -> None:
        self.vector_store_path.mkdir(parents=True, exist_ok=True)

        with open(self.index_file, "wb") as file:
            pickle.dump(index, file)

    def _load_chunks(self) -> list[dict]:
        all_chunks = []

        document_files = sorted(
            file_path
            for file_path in self.documents_path.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower() in self.supported_extensions
        )

        for file_path in document_files:
            text = self._read_document(file_path)
            chunks = self._split_text(text)

            for chunk_number, chunk_text in enumerate(chunks, start=1):
                all_chunks.append(
                    {
                        "text": chunk_text,
                        "source": file_path.name,
                        "chunk_id": f"{file_path.stem}_{chunk_number}",
                    }
                )

        return all_chunks

    def _read_document(self, file_path: Path) -> str:
        if file_path.suffix.lower() == ".txt":
            return file_path.read_text(encoding="utf-8")

        if file_path.suffix.lower() == ".pdf":
            return self._read_pdf(file_path)

        return ""

    def _read_pdf(self, file_path: Path) -> str:
        try:
            reader = PdfReader(str(file_path))
            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)

            return "\n".join(pages_text)

        except Exception:
            return ""

    def _split_text(self, text: str) -> list[str]:
        clean_text = " ".join(text.split())

        if not clean_text:
            return []

        chunks = []
        start = 0

        while start < len(clean_text):
            end = start + self.chunk_size
            chunk = clean_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            next_start = end - self.chunk_overlap

            if next_start <= start:
                next_start = start + self.chunk_size

            start = next_start

        return chunks

    def _documents_fingerprint(self) -> str:
        self.documents_path.mkdir(parents=True, exist_ok=True)

        sha = hashlib.sha256()

        document_files = sorted(
            file_path
            for file_path in self.documents_path.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower() in self.supported_extensions
        )

        for file_path in document_files:
            sha.update(file_path.name.encode("utf-8"))
            sha.update(file_path.read_bytes())

        sha.update(str(self.chunk_size).encode("utf-8"))
        sha.update(str(self.chunk_overlap).encode("utf-8"))
        sha.update(str(self.max_features).encode("utf-8"))

        return sha.hexdigest()

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-záéíóúñüA-ZÁÉÍÓÚÑÜ0-9]+", text.lower())

        stopwords = {
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "de",
            "del",
            "a",
            "ante",
            "bajo",
            "con",
            "contra",
            "desde",
            "durante",
            "en",
            "entre",
            "hacia",
            "hasta",
            "para",
            "por",
            "segun",
            "según",
            "sin",
            "sobre",
            "tras",
            "y",
            "o",
            "que",
            "como",
            "cuál",
            "cual",
            "cuándo",
            "cuando",
            "qué",
            "que",
            "es",
            "son",
            "se",
            "al",
            "lo",
            "su",
            "sus",
            "mi",
            "mis",
        }

        return {token for token in tokens if token not in stopwords and len(token) > 2}

    def _keyword_overlap_score(self, query_terms: set[str], text: str) -> float:
        if not query_terms:
            return 0.0

        text_terms = self._tokenize(text)
        overlap = query_terms.intersection(text_terms)

        return len(overlap) / len(query_terms)