from rag.vector_store import LocalVectorStore


class LocalRAGRetriever:
    def __init__(self):
        self.vector_store = LocalVectorStore()

    def search(self, question: str, top_k: int = 4) -> dict:
        return self.vector_store.search(
            question=question,
            top_k=top_k,
        )

    def rebuild_index(self) -> dict:
        return self.vector_store.rebuild()