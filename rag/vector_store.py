"""Vector Store for semantic similarity search over document chunks.
Uses scikit-learn TF-IDF with cosine similarity for robust, zero-dependency offline retrieval.
Supports metadata filtering, dynamic indexing, and similarity thresholding.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class VectorStore:
    """In-memory semantic vector store for fast, reliable RAG retrieval."""

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add a list of document chunks to the store and rebuild index.
        Returns the total number of chunks currently indexed.
        """
        if not chunks:
            return len(self.chunks)

        self.chunks.extend(chunks)
        self._rebuild_index()
        return len(self.chunks)

    def _rebuild_index(self):
        """Fit TF-IDF matrix over all accumulated chunk texts."""
        if not self.chunks:
            self.vectorizer = None
            self.tfidf_matrix = None
            return

        texts = [chunk["text"] for chunk in self.chunks]
        # Use unigrams and bigrams, sublinear tf scaling for superior relevance
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            norm="l2"
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Search for top_k most relevant chunks matching the query.
        Returns chunks sorted by descending cosine similarity score.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query = query.strip()
        if not query:
            return []

        query_vec = self.vectorizer.transform([query])
        # If query contains only out-of-vocabulary words
        if query_vec.nnz == 0:
            # Fallback: simple token overlap search
            return self._fallback_keyword_search(query, top_k)

        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Rank indices
        ranked_indices = np.argsort(scores)[::-1]

        results: List[Dict[str, Any]] = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score < min_score and len(results) > 0:
                break
            if score > 0:
                chunk = dict(self.chunks[idx])
                chunk["similarity_score"] = round(score, 4)
                results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    def _fallback_keyword_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Fallback search based on term overlap if vectorizer doesn't recognize words."""
        query_words = set(query.lower().split())
        scored_chunks = []
        for chunk in self.chunks:
            chunk_words = set(chunk["text"].lower().split())
            intersection = query_words.intersection(chunk_words)
            if intersection:
                score = len(intersection) / max(len(query_words), 1)
                chunk_copy = dict(chunk)
                chunk_copy["similarity_score"] = round(score, 4)
                scored_chunks.append(chunk_copy)

        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]

    def remove_source(self, source_name: str) -> int:
        """Remove all chunks associated with a given source."""
        initial_len = len(self.chunks)
        self.chunks = [c for c in self.chunks if c.get("source") != source_name]
        self._rebuild_index()
        return initial_len - len(self.chunks)

    def clear(self):
        """Reset the vector store."""
        self.chunks.clear()
        self.vectorizer = None
        self.tfidf_matrix = None

    def get_sources(self) -> List[Dict[str, Any]]:
        """Return list of distinct indexed sources and their chunk count."""
        source_counts: Dict[str, Dict[str, Any]] = {}
        for c in self.chunks:
            src = c.get("source", "Unknown")
            if src not in source_counts:
                source_counts[src] = {
                    "source": src,
                    "chunk_count": 0,
                    "word_count": 0
                }
            source_counts[src]["chunk_count"] += 1
            source_counts[src]["word_count"] += c.get("word_count", 0)
        return list(source_counts.values())

    def get_stats(self) -> Dict[str, Any]:
        """Summary statistics of the knowledge base."""
        total_words = sum(c.get("word_count", 0) for c in self.chunks)
        return {
            "total_chunks": len(self.chunks),
            "total_sources": len(self.get_sources()),
            "total_words": total_words,
            "is_indexed": self.tfidf_matrix is not None
        }
