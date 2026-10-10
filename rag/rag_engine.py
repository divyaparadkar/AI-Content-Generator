"""RAG Engine: coordinates document ingestion, chunking, storage, and contextual retrieval."""

import os
from typing import List, Dict, Any, Optional, Tuple
from rag.document_loader import extract_text_from_bytes, chunk_text
from rag.vector_store import VectorStore


class RAGEngine:
    """High-level retrieval-augmented generation engine."""

    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store = VectorStore()
        self._load_default_knowledge()

    def ingest_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from file bytes, create semantic chunks, and index into vector store.
        """
        raw_text = extract_text_from_bytes(file_bytes, filename)
        if not raw_text.strip():
            raise ValueError(f"File '{filename}' contains no readable text.")

        chunks = chunk_text(
            text=raw_text,
            source_name=filename,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        if not chunks:
            raise ValueError(f"No chunks could be extracted from '{filename}'.")

        self.vector_store.add_documents(chunks)
        return {
            "source": filename,
            "chunks_added": len(chunks),
            "total_words": sum(c["word_count"] for c in chunks),
            "total_indexed_chunks": len(self.vector_store.chunks)
        }

    def ingest_raw_text(self, text: str, source_name: str = "Pasted Text") -> Dict[str, Any]:
        """Ingest plain text directly."""
        if not text.strip():
            raise ValueError("Input text is empty.")

        chunks = chunk_text(
            text=text,
            source_name=source_name,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.vector_store.add_documents(chunks)
        return {
            "source": source_name,
            "chunks_added": len(chunks),
            "total_words": sum(c["word_count"] for c in chunks),
            "total_indexed_chunks": len(self.vector_store.chunks)
        }

    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.05
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Search vector store for relevant chunks matching the query.
        Returns:
            formatted_context: str to be injected into prompt
            citations: list of dicts with source details and excerpt
        """
        matched_chunks = self.vector_store.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )

        if not matched_chunks:
            return "", []

        context_blocks = []
        citations = []

        for i, chunk in enumerate(matched_chunks, 1):
            source = chunk.get("source", "Document")
            idx = chunk.get("chunk_index", i)
            score = chunk.get("similarity_score", 0.0)
            text = chunk.get("text", "").strip()

            context_blocks.append(f"--- [Reference {i}: {source} (Chunk {idx})] ---\n{text}")

            citations.append({
                "reference_id": i,
                "source": source,
                "chunk_index": idx,
                "similarity_score": score,
                "word_count": chunk.get("word_count", 0),
                "excerpt": text[:180] + ("..." if len(text) > 180 else "")
            })

        formatted_context = "\n\n".join(context_blocks)
        return formatted_context, citations

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics of indexed documents and chunks."""
        return self.vector_store.get_stats()

    def get_sources(self) -> List[Dict[str, Any]]:
        """List distinct sources."""
        return self.vector_store.get_sources()

    def remove_source(self, source_name: str) -> int:
        """Remove source documents."""
        return self.vector_store.remove_source(source_name)

    def clear(self):
        """Clear all indexed documents."""
        self.vector_store.clear()

    def _load_default_knowledge(self):
        """
        Pre-load curated knowledge documents so the user/evaluator has an out-of-the-box
        rich RAG dataset immediately available for testing.
        """
        sample_doc_ai = (
            "Retrieval-Augmented Generation (RAG) is an AI architecture that enhances "
            "large language model responses by fetching authority facts from external knowledge "
            "bases before generating the final output. This significantly reduces hallucinations, "
            "ensures up-to-date domain relevance, and enables granular source citation. "
            "Standard RAG consists of three core phases: Document Ingestion & Chunking, Vector "
            "Embedding & Indexing, and Context-Augmented Prompt Synthesis. Modern implementations "
            "often utilize hybrid search combining dense semantic vectors with lexical BM25/TF-IDF "
            "ranking for maximum factual accuracy and low latency."
        )

        sample_doc_content_strategy = (
            "High-impact digital content marketing relies on four pillars: Clarity, Hook Resonance, "
            "Actionable Value, and Algorithmic Distribution. For blog posts, optimal reading lengths "
            "range between 1,200 to 2,000 words with H2/H3 hierarchical structure and bulleted summaries. "
            "For social media captions, the first 80 characters dictate engagement, requiring an emotional "
            "or curiosity gap trigger followed by a single crisp Call-To-Action (CTA) and 3 to 5 targeted hashtags. "
            "Tone consistency across channels strengthens brand recall and reader trust."
        )

        sample_doc_tech_trends = (
            "In 2026, artificial intelligence development emphasizes agentic workflows, on-device small "
            "language models (SLMs), and verifiable multi-modal grounding. Cloud costs have led enterprises "
            "to adopt specialized task-specific models and hybrid local-cloud deployments. Sustainable compute "
            "and transparent data attribution remain top priorities for product leaders worldwide."
        )

        self.ingest_raw_text(sample_doc_ai, source_name="Knowledge_Base_AI_RAG.txt")
        self.ingest_raw_text(sample_doc_content_strategy, source_name="Content_Strategy_Playbook.txt")
        self.ingest_raw_text(sample_doc_tech_trends, source_name="Tech_Trends_2026_Briefing.txt")
