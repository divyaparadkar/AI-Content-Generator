"""Content Generation Orchestrator.
Integrates RAG retrieval, prompt templates, LLM client, and content analytics.
"""

import time
import math
import re
from typing import Dict, Any, Optional, List
from generator.prompts import (
    build_generation_prompt,
    build_refine_prompt,
    CONTENT_TYPES,
    TONE_OPTIONS,
    LENGTH_OPTIONS
)
from generator.llm_client import LLMClient
from generator.jav_decision_engine import JAVDecisionEngine
from rag.rag_engine import RAGEngine


def compute_content_metrics(text: str) -> Dict[str, Any]:
    """Calculates rich readability and size metrics for generated text."""
    if not text:
        return {
            "word_count": 0,
            "char_count": 0,
            "char_count_no_spaces": 0,
            "reading_time_minutes": 0.0,
            "paragraph_count": 0,
            "sentence_count": 0,
            "reading_level": "N/A"
        }

    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(re.sub(r'\s+', '', text))
    
    # Reading time based on average 200 words per minute
    reading_time = round(word_count / 200.0, 1)
    if reading_time < 0.1 and word_count > 0:
        reading_time = 0.1

    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)

    # Approximate sentence count
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()]) or 1

    # Approximate readability (Flesch-Kincaid style heuristic)
    avg_words_per_sentence = word_count / max(sentence_count, 1)
    if avg_words_per_sentence < 12:
        reading_level = "Easy (Conversational)"
    elif avg_words_per_sentence < 22:
        reading_level = "Standard (High Engagement)"
    else:
        reading_level = "Advanced (Analytical)"

    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "reading_time_minutes": reading_time,
        "paragraph_count": paragraph_count,
        "sentence_count": sentence_count,
        "reading_level": reading_level
    }


class ContentGenerator:
    """End-to-end generator coordinating RAG knowledge retrieval and multi-model LLMs."""

    def __init__(self, rag_engine: Optional[RAGEngine] = None):
        self.rag_engine = rag_engine or RAGEngine()
        self.llm_client = LLMClient()
        self.jav_engine = JAVDecisionEngine()

    def generate(
        self,
        topic: str,
        content_type: str = "blog_post",
        tone: str = "professional",
        length: str = "medium",
        custom_instructions: str = "",
        target_audience: str = "General",
        use_rag: bool = True,
        rag_top_k: int = 3,
        provider: str = "offline",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Executes end-to-end generation:
        1. JAV System-1 Fast Decision analysis
        2. Context retrieval from RAG knowledge store (if requested)
        3. Prompt template construction
        4. LLM invocation with error handling
        5. Metrics computation and JAV verification
        """
        if not topic.strip():
            raise ValueError("The 'topic' field cannot be empty.")

        start_time = time.time()
        rag_context = ""
        citations: List[Dict[str, Any]] = []

        # 0. JAV Fast Decision (Pre-flight classification & routing)
        jav_decision = self.jav_engine.decide(
            prompt=f"{topic} {custom_instructions}".strip(),
            current_content_type=content_type,
            current_tone=tone,
            has_custom_docs=bool(self.rag_engine.get_sources()) if self.rag_engine else False
        )

        # 1. RAG Retrieval
        if use_rag and self.rag_engine:
            rag_query = f"{topic} {custom_instructions}".strip()
            rag_context, citations = self.rag_engine.retrieve_context(
                query=rag_query,
                top_k=rag_top_k
            )

        # 2. Build Prompt Templates
        prompt_data = build_generation_prompt(
            topic=topic,
            content_type=content_type,
            tone=tone,
            length=length,
            custom_instructions=custom_instructions,
            rag_context=rag_context,
            target_audience=target_audience
        )

        # 3. Call LLM
        llm_resp = self.llm_client.generate(
            system_prompt=prompt_data["system_prompt"],
            user_prompt=prompt_data["user_prompt"],
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )

        duration_sec = round(time.time() - start_time, 2)
        generated_content = llm_resp.get("content", "")

        # 4. Compute Metrics & JAV Verification
        metrics = compute_content_metrics(generated_content)
        jav_verification = self.jav_engine.verify_generation(
            prompt=topic,
            generated_content=generated_content,
            content_type=content_type,
            tone=tone,
            used_rag=bool(rag_context.strip())
        )

        return {
            "success": True,
            "content": generated_content,
            "content_type": content_type,
            "tone": tone,
            "length": length,
            "topic": topic,
            "metrics": metrics,
            "rag": {
                "used": bool(rag_context.strip()),
                "citations_count": len(citations),
                "citations": citations
            },
            "jav": {
                "decision": jav_decision,
                "verification": jav_verification
            },
            "model_info": {
                "provider": llm_resp.get("provider", provider),
                "model": llm_resp.get("model", model or "default"),
                "duration_seconds": duration_sec,
                "usage": llm_resp.get("usage", {})
            },
            "prompt_debug": {
                "system_prompt": prompt_data["system_prompt"],
                "user_prompt": prompt_data["user_prompt"]
            }
        }

    def refine(
        self,
        original_content: str,
        refinement_instruction: str,
        content_type: str = "blog_post",
        tone: Optional[str] = None,
        provider: str = "offline",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.6
    ) -> Dict[str, Any]:
        """
        Refines, polishes, or rewrites existing generated content based on instructions.
        """
        if not original_content.strip():
            raise ValueError("Original content to refine cannot be empty.")
        if not refinement_instruction.strip():
            raise ValueError("Refinement instruction cannot be empty.")

        start_time = time.time()
        prompt_data = build_refine_prompt(
            original_content=original_content,
            refinement_instruction=refinement_instruction,
            content_type=content_type,
            tone=tone
        )

        llm_resp = self.llm_client.generate(
            system_prompt=prompt_data["system_prompt"],
            user_prompt=prompt_data["user_prompt"],
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )

        duration_sec = round(time.time() - start_time, 2)
        refined_content = llm_resp.get("content", "")
        metrics = compute_content_metrics(refined_content)

        return {
            "success": True,
            "content": refined_content,
            "content_type": content_type,
            "refinement_instruction": refinement_instruction,
            "metrics": metrics,
            "model_info": {
                "provider": llm_resp.get("provider", provider),
                "model": llm_resp.get("model", model or "default"),
                "duration_seconds": duration_sec,
                "usage": llm_resp.get("usage", {})
            },
            "prompt_debug": {
                "system_prompt": prompt_data["system_prompt"],
                "user_prompt": prompt_data["user_prompt"]
            }
        }
