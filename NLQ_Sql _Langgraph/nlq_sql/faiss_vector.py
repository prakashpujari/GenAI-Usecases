"""
faiss_vector.py
---
Vector DB (FAISS) integration for RAG in Mortgage Insights NLQ.
Supports semantic-chunk ingestion and score-filtered retrieval.
"""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


class FaissVectorDB:
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.store = None

    def add_texts(self, texts, metadatas=None):
        """Build FAISS index from a list of text strings."""
        self.store = FAISS.from_texts(texts, self.embedding_model, metadatas=metadatas)

    def similarity_search(self, query, k=5):
        """Return top-k documents by cosine similarity."""
        if not self.store:
            raise ValueError("FAISS store not initialized.")
        return self.store.similarity_search(query, k=k)

    def similarity_search_with_threshold(self, query, k=5, score_threshold=0.75):
        """
        Return top-k documents whose relevance score >= score_threshold.
        FAISS returns L2 distance; we convert to a 0-1 relevance score.
        Lower distance = more relevant.
        score_threshold is applied to the normalised relevance (0=irrelevant, 1=identical).
        """
        if not self.store:
            raise ValueError("FAISS store not initialized.")
        results = self.store.similarity_search_with_score(query, k=k)
        # FAISS returns (doc, L2_distance). Convert to relevance: 1 / (1 + distance)
        filtered = []
        for doc, dist in results:
            relevance = 1.0 / (1.0 + dist)
            if relevance >= score_threshold:
                doc.metadata["relevance_score"] = round(relevance, 4)
                filtered.append(doc)
        return filtered

    def save(self, path):
        if not self.store:
            raise ValueError("FAISS store not initialized.")
        self.store.save_local(path)

    @classmethod
    def load(cls, path, embedding_model=None):
        embedding_model = embedding_model or OpenAIEmbeddings()
        store = FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)
        obj = cls(embedding_model)
        obj.store = store
        return obj
