from rag.local_retriever import LocalRAGRetriever


class RAGWorker:
    def __init__(self):
        self.retriever = LocalRAGRetriever()

    def search(self, question: str) -> dict:
        return self.retriever.search(question)