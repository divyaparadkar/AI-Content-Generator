"""Prompt Engineering Templates & Specifications for Multi-Type AI Content Generation.
Provides structured prompt templates, tone guidelines, and RAG context grounding rules.
"""

from typing import Dict, Any, Optional

CONTENT_TYPES = {
    "blog_post": {
        "label": "Blog Post",
        "icon": "newspaper",
        "description": "Engaging, SEO-structured article with headings, subheadings, actionable insights, and conclusion.",
        "default_length": "medium",
        "system_instruction": (
            "You are an award-winning content strategist and expert blog writer. "
            "Write comprehensive, high-value, and naturally engaging articles with proper markdown formatting "
            "(H1 title, H2/H3 subheadings, bullet points, callout takeaways, and a compelling conclusion)."
        ),
        "structure_guide": (
            "- Catchy H1 Title\n"
            "- Engaging introductory hook addressing the reader's problem or curiosity\n"
            "- Structured body sections with informative H2 and H3 subheadings\n"
            "- Actionable takeaways formatted in bullet points\n"
            "- Thought-provoking conclusion with a closing takeaway or question"
        )
    },
    "social_caption": {
        "label": "Social Media Caption",
        "icon": "share-2",
        "description": "High-engagement caption optimized for Instagram, Twitter/X, or LinkedIn with hooks and hashtags.",
        "default_length": "short",
        "system_instruction": (
            "You are a top-tier viral social media copywriter. "
            "Your copy stops the scroll, grabs curiosity in the first 80 characters, delivers immediate punchy value, "
            "and ends with a crisp Call-To-Action (CTA) and relevant, trending hashtags."
        ),
        "structure_guide": (
            "- Scroll-stopping opening hook (under 100 characters)\n"
            "- Punchy, spaced body copy delivering high-density value\n"
            "- Clear, high-conversion Call-To-Action (CTA)\n"
            "- 4 to 6 curated, relevant hashtags (#topic #niche #trend)"
        )
    },
    "summary": {
        "label": "Text / Executive Summary",
        "icon": "file-text",
        "description": "Dense, executive-level summary highlighting core thesis, key findings, and action items.",
        "default_length": "short",
        "system_instruction": (
            "You are a C-suite executive briefing specialist and synthesis expert. "
            "Distill complex subjects into clear, high-signal, zero-fluff executive summaries."
        ),
        "structure_guide": (
            "- Executive Overview / Core Thesis (2-3 sentences)\n"
            "- Key Insights & Strategic Findings (bullet points)\n"
            "- Practical Implications & Recommended Next Steps"
        )
    },
    "email_newsletter": {
        "label": "Email Newsletter",
        "icon": "mail",
        "description": "Conversational, high-open-rate newsletter with subject lines, preview text, and personal signoff.",
        "default_length": "medium",
        "system_instruction": (
            "You are a master email newsletter writer for top tech and lifestyle publications. "
            "Write friendly, direct, 1-to-1 conversational emails with high click-through potential."
        ),
        "structure_guide": (
            "- 3 Catchy Subject Line Options (A/B testing ready)\n"
            "- Preview / Pre-header Text\n"
            "- Warm, personal opening\n"
            "- Main story / core value lesson\n"
            "- Clear CTA button/link suggestion and friendly sign-off"
        )
    },
    "linkedin_post": {
        "label": "LinkedIn Thought Leadership",
        "icon": "linkedin",
        "description": "Professional thought leadership post with storytelling, whitespace, and discussion prompts.",
        "default_length": "medium",
        "system_instruction": (
            "You are a viral LinkedIn creator with over 500,000 followers. "
            "Write impactful professional thought leadership stories with clean line breaks, vulnerability, "
            "frameworks, and strong community engagement questions."
        ),
        "structure_guide": (
            "- Bold single-line hook\n"
            "- Short 1-2 sentence paragraphs with whitespace\n"
            "- The conflict or realization\n"
            "- The framework or 3-step lesson\n"
            "- Closing question inviting discussion in the comments"
        )
    }
}

TONE_OPTIONS = {
    "professional": "Professional, authoritative, data-backed, and polished.",
    "casual": "Casual, friendly, conversational, approachable, and warm.",
    "persuasive": "Persuasive, compelling, sales-oriented, and urgency-driven.",
    "humorous": "Witty, humorous, entertaining, with clever analogies and lighthearted tone.",
    "informative": "Informative, objective, educational, clear, and structured.",
    "inspirational": "Inspirational, uplifting, motivational, and emotionally resonant.",
    "academic": "Academic, rigorous, analytical, objective, and scholarly."
}

LENGTH_OPTIONS = {
    "short": {"label": "Short (~150 - 250 words)", "target_words": 200, "tokens": 450},
    "medium": {"label": "Medium (~400 - 650 words)", "target_words": 500, "tokens": 900},
    "long": {"label": "Long (~800 - 1200 words)", "target_words": 1000, "tokens": 1800}
}


def build_generation_prompt(
    topic: str,
    content_type: str = "blog_post",
    tone: str = "professional",
    length: str = "medium",
    custom_instructions: str = "",
    rag_context: str = "",
    target_audience: str = "General"
) -> Dict[str, str]:
    """
    Constructs the system prompt and user prompt based on user configurations
    and optional RAG knowledge context.
    """
    type_info = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog_post"])
    tone_desc = TONE_OPTIONS.get(tone, TONE_OPTIONS["professional"])
    length_info = LENGTH_OPTIONS.get(length, LENGTH_OPTIONS["medium"])

    system_prompt = (
        f"{type_info['system_instruction']}\n\n"
        f"STRICT OUTPUT GUIDELINES:\n"
        f"1. Target Tone: {tone_desc}\n"
        f"2. Target Length: Approximately {length_info['target_words']} words.\n"
        f"3. Target Audience: {target_audience}\n"
        f"4. Format: Use clean, standard Markdown.\n"
        f"5. Do NOT include meta-commentary like 'Sure, here is your blog post:' or 'I hope this helps!'. "
        f"Output ONLY the final content."
    )

    if rag_context.strip():
        system_prompt += (
            "\n\nGROUNDING IN RETRIEVED KNOWLEDGE (RAG):\n"
            "You have been provided with authoritative context retrieved from the user's reference library. "
            "You MUST prioritize facts, metrics, and domain terminology from this reference material. "
            "Cite relevant reference numbers (e.g. [Ref 1]) when drawing specific points."
        )

    user_prompt_lines = [
        f"CONTENT TYPE: {type_info['label']}",
        f"TOPIC / PROMPT: {topic.strip()}",
        f"TONE: {tone_desc}",
        f"ESTIMATED LENGTH: ~{length_info['target_words']} words",
        f"AUDIENCE: {target_audience}"
    ]

    if custom_instructions.strip():
        user_prompt_lines.append(f"ADDITIONAL CUSTOM INSTRUCTIONS:\n{custom_instructions.strip()}")

    user_prompt_lines.append(f"REQUIRED STRUCTURAL FRAMEWORK:\n{type_info['structure_guide']}")

    if rag_context.strip():
        user_prompt_lines.append(
            f"\nRETRIEVED REFERENCE CONTEXT:\n{rag_context.strip()}\n"
            f"(Integrate the above reference facts naturally into the generated piece.)"
        )

    user_prompt_lines.append("\nPlease generate the complete, high-quality content now:")

    return {
        "system_prompt": system_prompt,
        "user_prompt": "\n\n".join(user_prompt_lines)
    }


def build_refine_prompt(
    original_content: str,
    refinement_instruction: str,
    content_type: str = "blog_post",
    tone: Optional[str] = None
) -> Dict[str, str]:
    """
    Constructs a prompt to revise, refine, shorten, expand, or adjust an existing generation.
    """
    type_info = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog_post"])
    tone_str = f"Ensure tone is: {TONE_OPTIONS.get(tone, tone)}" if tone else "Maintain the existing tone."

    system_prompt = (
        f"You are a master editor and content polisher. "
        f"Your task is to refine, rewrite, or expand the provided {type_info['label']} "
        f"in strict accordance with the user's refinement instructions.\n"
        f"{tone_str}\n"
        f"Do NOT include introductory or concluding conversational chatter. Output ONLY the refined content in Markdown."
    )

    user_prompt = (
        f"ORIGINAL CONTENT:\n"
        f"```markdown\n{original_content.strip()}\n```\n\n"
        f"REFINEMENT INSTRUCTIONS:\n"
        f"{refinement_instruction.strip()}\n\n"
        f"Please output the revised version now:"
    )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }
