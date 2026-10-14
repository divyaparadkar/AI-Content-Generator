"""⚡ NexusAI Studio — Streamlit Cloud Web Application
Autonomous Multi-Model Content Generator with Grounded RAG & JAV Fast Decision Engine.
Optimized for deployment on Streamlit Community Cloud (streamlit.io / share.streamlit.io).
"""

import os
import time
import json
import streamlit as st

from rag.rag_engine import RAGEngine
from generator.content_generator import ContentGenerator, compute_content_metrics
from generator.prompts import CONTENT_TYPES, TONE_OPTIONS, LENGTH_OPTIONS
from generator.llm_client import LLMClient
from generator.jav_decision_engine import JAVDecisionEngine

# ---------------------------------------------------------
# Page Configuration & Global Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="NexusAI Studio — AI Content Generator with RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* Modern Glassmorphic Studio Theme */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Gradient Header Card */
.header-hero {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(59, 130, 246, 0.1) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(12px);
}

.header-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 6px;
}

.badge-indigo { background: rgba(99, 102, 241, 0.25); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }
.badge-purple { background: rgba(168, 85, 247, 0.25); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); }
.badge-emerald { background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-amber { background: rgba(245, 158, 11, 0.25); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }

/* Metric Card */
.metric-box {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.metric-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f8fafc;
}
.metric-lbl {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.06em;
    margin-top: 2px;
}

/* JAV HUD Card */
.jav-hud {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.85) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 16px 0;
}

/* Content Output Card */
.output-card {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.3);
}

/* Hide default streamlit menu decoration */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "content_generator" not in st.session_state:
    st.session_state.content_generator = ContentGenerator(rag_engine=st.session_state.rag_engine)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Active input session state defaults
if "input_topic" not in st.session_state:
    st.session_state.input_topic = "Why Retrieval-Augmented Generation (RAG) is Replacing Pure LLM Fine-Tuning in 2026"
if "input_content_type" not in st.session_state:
    st.session_state.input_content_type = "blog_post"
if "input_tone" not in st.session_state:
    st.session_state.input_tone = "professional"
if "input_length" not in st.session_state:
    st.session_state.input_length = "medium"
if "input_audience" not in st.session_state:
    st.session_state.input_audience = "Software Engineers & Tech Leaders"
if "input_custom_instructions" not in st.session_state:
    st.session_state.input_custom_instructions = "Highlight hallucination reduction, vector embeddings, cost efficiency, and verifiable citations."

# ---------------------------------------------------------
# Demo Presets
# ---------------------------------------------------------
PRESETS = {
    "tech_rag_blog": {
        "title": "🤖 Tech: AI & RAG Deep Dive",
        "topic": "Why Retrieval-Augmented Generation (RAG) is Replacing Pure LLM Fine-Tuning in 2026",
        "content_type": "blog_post",
        "tone": "professional",
        "length": "medium",
        "audience": "Software Engineers & Tech Leaders",
        "instructions": "Highlight hallucination reduction, vector embeddings, cost efficiency, and citations."
    },
    "fitness_social": {
        "title": "⚡ Fitness: 15-Min Workout Hook",
        "topic": "The 15-Minute Micro-Workout Habit for Busy High Performers",
        "content_type": "social_caption",
        "tone": "enthusiastic",
        "length": "short",
        "audience": "Busy Professionals & Entrepreneurs",
        "instructions": "Start with a high-stakes hook, break into 3 bullet points, include an engaging CTA and hashtags."
    },
    "cloud_exec_summary": {
        "title": "☁️ Cloud: Hybrid AI Architecture ROI",
        "topic": "Strategic and Cost Implications of Migrating from Monolithic LLM APIs to Hybrid Edge-Cloud Inference",
        "content_type": "summary",
        "tone": "professional",
        "length": "short",
        "audience": "CTOs, VP Engineering, and Chief Financial Officers",
        "instructions": "Provide Executive Overview, 3 Key Strategic Findings, and Recommended 90-Day Implementation Plan."
    },
    "newsletter_tech": {
        "title": "📧 Newsletter: Weekly AI Pulse",
        "topic": "The Rise of Agentic Workflows and Small Language Models in 2026",
        "content_type": "email_newsletter",
        "tone": "casual",
        "length": "medium",
        "audience": "Tech Enthusiasts & Founders",
        "instructions": "Offer 3 catchy subject lines, friendly conversational intro, key takeaways, and personal signoff."
    },
    "linkedin_growth": {
        "title": "💼 Career: Engineering Leadership Lesson",
        "topic": "The Counter-Intuitive Truth About Scaling Engineering Teams: Why Adding More Devs Slowed Us Down",
        "content_type": "linkedin_post",
        "tone": "persuasive",
        "length": "medium",
        "audience": "Founders, Engineering Managers, and Tech Leads",
        "instructions": "Bold 1-line hook, vulnerability story, 3-point framework, and engaging closing question."
    }
}

def load_preset(preset_key: str):
    p = PRESETS.get(preset_key)
    if p:
        st.session_state.input_topic = p["topic"]
        st.session_state.input_content_type = p["content_type"]
        st.session_state.input_tone = p["tone"]
        st.session_state.input_length = p["length"]
        st.session_state.input_audience = p["audience"]
        st.session_state.input_custom_instructions = p["instructions"]

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ AI Model Engine")

    # API key detection from Streamlit secrets or OS env
    secrets_openai = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
    secrets_gemini = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    secrets_hf = st.secrets.get("HF_TOKEN", "") if hasattr(st, "secrets") else ""

    default_openai = secrets_openai or os.environ.get("OPENAI_API_KEY", "")
    default_gemini = secrets_gemini or os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    default_hf = secrets_hf or os.environ.get("HF_TOKEN", "")

    provider_options = [
        ("offline", "⚡ Offline Smart Synthesizer (No API Key Required)"),
        ("openai", "🧠 OpenAI (GPT-4o / GPT-4o-mini)"),
        ("gemini", "💎 Google Gemini (1.5 Flash / 2.0)"),
        ("huggingface", "🤗 Hugging Face Inference")
    ]
    provider_ids = [p[0] for p in provider_options]
    provider_labels = [p[1] for p in provider_options]

    selected_provider_label = st.selectbox(
        "Provider",
        options=provider_labels,
        index=0,
        help="Select AI backend. Built-in Offline Synthesizer works with zero API keys!"
    )
    selected_provider = provider_ids[provider_labels.index(selected_provider_label)]

    # Model name and API Key inputs conditional on provider
    api_key_input = None
    model_name_input = None

    if selected_provider == "offline":
        st.info("💡 **Ready out of the box!** Uses structured domain synthesis + local RAG vector retrieval without needing any API key.")
        model_name_input = "built-in-rag-synthesis"

    elif selected_provider == "openai":
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=default_openai,
            type="password",
            placeholder="sk-...",
            help="Configurable via Streamlit Cloud Secrets (OPENAI_API_KEY) or enter directly."
        )
        model_name_input = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)

    elif selected_provider == "gemini":
        api_key_input = st.text_input(
            "Gemini API Key",
            value=default_gemini,
            type="password",
            placeholder="AIzaSy...",
            help="Configurable via Streamlit Cloud Secrets (GEMINI_API_KEY) or enter directly."
        )
        model_name_input = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"], index=0)

    elif selected_provider == "huggingface":
        api_key_input = st.text_input(
            "Hugging Face Token",
            value=default_hf,
            type="password",
            placeholder="hf_...",
            help="Configurable via Streamlit Cloud Secrets (HF_TOKEN) or enter directly."
        )
        model_name_input = st.text_input("Model Repo ID", value="mistralai/Mistral-7B-Instruct-v0.3")

    st.markdown("---")
    st.markdown("### ⚙️ Generation Parameters")
    temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    rag_top_k = st.slider("RAG Top-K Chunks", min_value=1, max_value=5, value=3, step=1)

    st.markdown("---")
    st.markdown("### 🎯 1-Click Presets")
    for key, p in PRESETS.items():
        if st.button(p["title"], key=f"btn_preset_{key}", use_container_width=True):
            load_preset(key)
            st.rerun()

    st.markdown("---")
    st.markdown("### 📚 Knowledge Base Status")
    stats = st.session_state.rag_engine.get_stats()
    st.caption(f"📁 **Sources Indexed:** {stats.get('total_sources', 0)}")
    st.caption(f"🧩 **Indexed Chunks:** {stats.get('total_chunks', 0)}")
    st.caption(f"📝 **Vocabulary Size:** {stats.get('vocabulary_size', 0)} terms")

    if st.button("🔄 Reload Default Knowledge", use_container_width=True):
        st.session_state.rag_engine.clear()
        st.session_state.rag_engine._load_default_knowledge()
        st.success("Default knowledge base reloaded!")
        st.rerun()


# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
st.markdown(
    """
    <div class="header-hero">
        <div class="header-title">⚡ NexusAI Studio</div>
        <div style="color: #cbd5e1; font-size: 1.05rem; margin-bottom: 12px;">
            Autonomous AI Content Generation Studio with RAG Knowledge Grounding & JAV System-1 Fast Decision Engine
        </div>
        <div>
            <span class="badge badge-indigo">5 Content Formats</span>
            <span class="badge badge-purple">TF-IDF Vector RAG</span>
            <span class="badge badge-emerald">JAV Decision Engine &lt;1ms</span>
            <span class="badge badge-amber">Multi-Model AI (OpenAI · Gemini · HF · Offline)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Tabs Interface
# ---------------------------------------------------------
tab_studio, tab_rag, tab_jav, tab_guide = st.tabs([
    "✍️ Content Studio",
    "📚 RAG Knowledge Base",
    "⚡ JAV Decision Engine",
    "🚀 GitHub & Cloud Deployment"
])

# =========================================================
# TAB 1: CONTENT STUDIO
# =========================================================
with tab_studio:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("#### 📝 Studio Prompt & Controls")

        topic_input = st.text_area(
            "Topic / Core Prompt *",
            value=st.session_state.input_topic,
            height=90,
            placeholder="e.g. Why Retrieval-Augmented Generation is replacing pure LLM fine-tuning...",
            key="widget_topic"
        )
        # Update session state
        st.session_state.input_topic = topic_input

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            content_type_keys = list(CONTENT_TYPES.keys())
            content_type_labels = [f"{CONTENT_TYPES[k]['label']}" for k in content_type_keys]
            current_ct_idx = content_type_keys.index(st.session_state.input_content_type) if st.session_state.input_content_type in content_type_keys else 0
            
            selected_ct_label = st.selectbox(
                "Content Format",
                options=content_type_labels,
                index=current_ct_idx
            )
            selected_ct = content_type_keys[content_type_labels.index(selected_ct_label)]
            st.session_state.input_content_type = selected_ct

        with row1_col2:
            tone_keys = list(TONE_OPTIONS.keys())
            tone_labels = [k.capitalize() for k in tone_keys]
            current_tone_idx = tone_keys.index(st.session_state.input_tone) if st.session_state.input_tone in tone_keys else 0
            
            selected_tone_label = st.selectbox(
                "Tone & Style",
                options=tone_labels,
                index=current_tone_idx
            )
            selected_tone = tone_keys[tone_labels.index(selected_tone_label)]
            st.session_state.input_tone = selected_tone

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            length_keys = list(LENGTH_OPTIONS.keys())
            length_labels = [f"{k.capitalize()} ({LENGTH_OPTIONS[k]['target_words']})" for k in length_keys]
            current_len_idx = length_keys.index(st.session_state.input_length) if st.session_state.input_length in length_keys else 1
            
            selected_len_label = st.selectbox("Target Length", options=length_labels, index=current_len_idx)
            selected_length = length_keys[length_labels.index(selected_len_label)]
            st.session_state.input_length = selected_length

        with row2_col2:
            audience_input = st.text_input(
                "Target Audience",
                value=st.session_state.input_audience,
                placeholder="e.g. Tech Leaders, Beginners..."
            )
            st.session_state.input_audience = audience_input

        with st.expander("🛠️ Advanced Instructions & RAG Options", expanded=False):
            instructions_input = st.text_area(
                "Custom Instructions",
                value=st.session_state.input_custom_instructions,
                height=70,
                placeholder="Specific key points, phrases to include or avoid..."
            )
            st.session_state.input_custom_instructions = instructions_input
            use_rag_toggle = st.checkbox("Ground generation using RAG Knowledge Base", value=True)

        # Live JAV Fast Decision HUD
        if topic_input.strip():
            jav_engine = st.session_state.content_generator.jav_engine
            fast_decision = jav_engine.decide(
                prompt=f"{topic_input} {st.session_state.input_custom_instructions}".strip(),
                current_content_type=selected_ct,
                current_tone=selected_tone,
                has_custom_docs=bool(st.session_state.rag_engine.get_sources())
            )
            rag_rec = "✅ Highly Recommended" if fast_decision["needs_rag_grounding"] else "ℹ️ Optional"
            conf_pct = int(fast_decision["confidence"] * 100)

            st.markdown(
                f"""
                <div class="jav-hud">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.75rem; font-weight:700; color:#818cf8; text-transform:uppercase; letter-spacing:0.08em;">
                            ⚡ JAV Fast Decision Engine (System-1)
                        </span>
                        <span style="font-size:0.7rem; color:#94a3b8; font-family:monospace;">
                            Latency: {fast_decision.get('latency_ms', 0.2)}ms
                        </span>
                    </div>
                    <div style="margin-top:8px; font-size:0.85rem; color:#e2e8f0; display:flex; flex-wrap:wrap; gap:14px;">
                        <div><b>RAG Grounding:</b> {rag_rec} ({conf_pct}% conf)</div>
                        <div><b>Optimal Format:</b> {fast_decision['recommended_content_type'].replace('_', ' ').title()}</div>
                        <div><b>Complexity:</b> {fast_decision.get('domain_complexity', 0.5):.2f}</div>
                        <div><b>Routing:</b> {fast_decision.get('routing_strategy', 'Standard')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Primary Generate Button
        generate_clicked = st.button("⚡ Generate High-Impact Content", type="primary", use_container_width=True)

        if generate_clicked:
            if not topic_input.strip():
                st.error("Please enter a topic or prompt.")
            else:
                with st.spinner("🚀 Analyzing prompt, retrieving RAG knowledge, and generating content..."):
                    try:
                        result = st.session_state.content_generator.generate(
                            topic=topic_input.strip(),
                            content_type=selected_ct,
                            tone=selected_tone,
                            length=selected_length,
                            custom_instructions=st.session_state.input_custom_instructions.strip(),
                            target_audience=st.session_state.input_audience.strip(),
                            use_rag=use_rag_toggle,
                            rag_top_k=rag_top_k,
                            provider=selected_provider,
                            model=model_name_input,
                            api_key=api_key_input,
                            temperature=temperature
                        )
                        st.session_state.last_result = result
                        st.success(f"Generated successfully in {result['model_info']['duration_seconds']}s via {result['model_info']['provider']}!")
                    except Exception as e:
                        st.error(f"Generation Error: {str(e)}")

    with col_output:
        st.markdown("#### 📄 Generated Studio Output")

        if st.session_state.last_result:
            res = st.session_state.last_result
            metrics = res.get("metrics", {})
            m_info = res.get("model_info", {})
            content = res.get("content", "")

            # Metric Cards Row
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            with m_col1:
                st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics.get("word_count", 0)}</div><div class="metric-lbl">Words</div></div>', unsafe_allow_html=True)
            with m_col2:
                st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics.get("char_count", 0)}</div><div class="metric-lbl">Chars</div></div>', unsafe_allow_html=True)
            with m_col3:
                st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics.get("reading_time_minutes", 0.0)}m</div><div class="metric-lbl">Read Time</div></div>', unsafe_allow_html=True)
            with m_col4:
                st.markdown(f'<div class="metric-box"><div class="metric-val">{m_info.get("duration_seconds", 0.1)}s</div><div class="metric-lbl">Latency</div></div>', unsafe_allow_html=True)
            with m_col5:
                read_level = metrics.get("reading_level", "Standard").split()[0]
                st.markdown(f'<div class="metric-box"><div class="metric-val">{read_level}</div><div class="metric-lbl">Level</div></div>', unsafe_allow_html=True)

            st.write("")

            # Main Content Render
            with st.container():
                st.markdown(content)

            st.markdown("---")

            # Quick Refinement Toolbar
            st.markdown("##### 🪄 Interactive Refinement")
            ref_col1, ref_col2, ref_col3, ref_col4 = st.columns(4)

            def trigger_refine(instruction: str):
                with st.spinner(f"Refining ({instruction})..."):
                    try:
                        ref_res = st.session_state.content_generator.refine(
                            original_content=st.session_state.last_result.get("content", ""),
                            refinement_instruction=instruction,
                            content_type=st.session_state.last_result.get("content_type", "blog_post"),
                            tone=st.session_state.last_result.get("tone", "professional"),
                            provider=selected_provider,
                            model=model_name_input,
                            api_key=api_key_input
                        )
                        st.session_state.last_result["content"] = ref_res["content"]
                        st.session_state.last_result["metrics"] = ref_res["metrics"]
                        st.session_state.last_result["model_info"] = ref_res["model_info"]
                        st.success(f"Content refined: '{instruction}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Refinement error: {e}")

            with ref_col1:
                if st.button("✂️ Shorten", use_container_width=True):
                    trigger_refine("Make it significantly more concise and punchy while retaining all core facts.")
            with ref_col2:
                if st.button("📈 Expand", use_container_width=True):
                    trigger_refine("Expand on these points with deeper explanations, concrete examples, and strategic nuance.")
            with ref_col3:
                if st.button("✨ Make Witty", use_container_width=True):
                    trigger_refine("Add witty humor, clever analogies, and engaging hooks while keeping high value.")
            with ref_col4:
                if st.button("📋 Checklist", use_container_width=True):
                    trigger_refine("Convert the core takeaways into a structured, actionable markdown checklist (- [ ]).")

            with st.expander("🎯 Custom Refinement Prompt", expanded=False):
                custom_ref_text = st.text_input("Refinement Request", placeholder="e.g. Add 2 real-world case studies...")
                if st.button("Apply Custom Refinement"):
                    if custom_ref_text.strip():
                        trigger_refine(custom_ref_text.strip())

            # Citations Accordion
            rag_meta = res.get("rag", {})
            citations = rag_meta.get("citations", [])
            if citations:
                with st.expander(f"📚 Verified RAG Citations ({len(citations)} Chunks Grounded)", expanded=False):
                    for cit in citations:
                        st.markdown(
                            f"**[Ref {cit.get('reference_id', 1)}] {cit.get('source')}** "
                            f"*(Chunk {cit.get('chunk_index')}, Similarity: {cit.get('similarity_score', 0):.4f})*"
                        )
                        st.caption(cit.get("excerpt", ""))
                        st.write("")

            # Download Buttons
            st.markdown("##### 💾 Export Content")
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label="📥 Download as Markdown (.md)",
                    data=content,
                    file_name=f"nexusai_studio_{res.get('content_type', 'content')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    label="📄 Download as Plain Text (.txt)",
                    data=content,
                    file_name=f"nexusai_studio_{res.get('content_type', 'content')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        else:
            st.info("👈 Enter a topic on the left or select a 1-Click Preset in the sidebar, then click **Generate High-Impact Content**!")


# =========================================================
# TAB 2: RAG KNOWLEDGE BASE
# =========================================================
with tab_rag:
    st.markdown("### 📚 RAG Knowledge Base & Vector Store")
    st.markdown(
        "Upload reference documents (PDF, Markdown, TXT) to ground generated content in verified domain knowledge. "
        "The engine performs automatic text extraction, semantic chunking, and TF-IDF cosine similarity indexing."
    )

    rag_col1, rag_col2 = st.columns([1, 1], gap="large")

    with rag_col1:
        st.markdown("#### 📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload Reference Files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            help="Supported: PDF reports, Markdown documentation, Plain text files."
        )

        if uploaded_files:
            if st.button("Index Uploaded Files", type="primary"):
                with st.spinner("Extracting text, chunking, and indexing..."):
                    success_count = 0
                    for up_file in uploaded_files:
                        try:
                            file_bytes = up_file.read()
                            res = st.session_state.rag_engine.ingest_file(file_bytes, up_file.name)
                            success_count += 1
                            st.success(f"Indexed '{up_file.name}': {res['chunks_added']} chunks, {res['total_words']} words.")
                        except Exception as e:
                            st.error(f"Failed to ingest {up_file.name}: {e}")
                    if success_count > 0:
                        st.rerun()

        st.markdown("#### ✍️ Or Ingest Raw Text Directly")
        raw_title = st.text_input("Source Document Name", value="Custom_Notes.txt")
        raw_text_input = st.text_area("Paste Content Here", height=120, placeholder="Paste proprietary knowledge, articles, or notes...")
        if st.button("Index Raw Text"):
            if raw_text_input.strip():
                res = st.session_state.rag_engine.ingest_raw_text(raw_text_input.strip(), source_name=raw_title)
                st.success(f"Indexed {res['chunks_added']} chunks from '{raw_title}'!")
                st.rerun()
            else:
                st.error("Please paste text before indexing.")

    with rag_col2:
        st.markdown("#### 📑 Currently Indexed Sources")
        sources = st.session_state.rag_engine.get_sources()

        if sources:
            for s in sources:
                with st.container():
                    s_col1, s_col2 = st.columns([4, 1])
                    with s_col1:
                        st.markdown(f"**📄 {s['source']}**")
                        st.caption(f"{s['chunks_count']} chunks • ~{s['total_words']} words")
                    with s_col2:
                        if st.button("🗑️ Remove", key=f"del_{s['source']}"):
                            st.session_state.rag_engine.remove_source(s["source"])
                            st.success(f"Removed '{s['source']}'")
                            st.rerun()
                    st.write("")
        else:
            st.warning("No documents currently indexed. Click 'Reload Default Knowledge' in the sidebar or upload files.")

        st.markdown("---")
        st.markdown("#### 🔍 Test Semantic Retrieval")
        test_query = st.text_input("Test Query", placeholder="e.g. What are the core phases of RAG?")
        if test_query.strip():
            context, hits = st.session_state.rag_engine.retrieve_context(test_query, top_k=3)
            if hits:
                st.markdown(f"**Found {len(hits)} matching chunks:**")
                for h in hits:
                    st.markdown(f"• **{h['source']}** *(Score: {h['similarity_score']:.4f})*")
                    st.caption(h["excerpt"])
            else:
                st.caption("No matching chunks above threshold.")


# =========================================================
# TAB 3: JAV FAST DECISION ENGINE
# =========================================================
with tab_jav:
    st.markdown("### ⚡ JAV System-1 Fast Decision Engine")
    st.markdown(
        "Inspired by TypeSafe AI's Jev model, this engine delivers sub-millisecond, deterministic, structured "
        "decision-making gates before and after text generation."
    )

    jav_test_prompt = st.text_area(
        "Test Prompt for JAV Evaluation",
        value="Explain how to implement hybrid search for enterprise vector databases with role-based access control.",
        height=90
    )

    if st.button("Run System-1 Evaluation", type="primary"):
        start_t = time.perf_counter()
        decision = st.session_state.content_generator.jav_engine.decide(
            prompt=jav_test_prompt,
            current_content_type="blog_post",
            current_tone="professional",
            has_custom_docs=True
        )
        latency = round((time.perf_counter() - start_t) * 1000, 2)

        st.success(f"Decision evaluated in **{latency} ms**!")

        j_col1, j_col2 = st.columns(2)
        with j_col1:
            st.markdown("#### 🎯 Structured Classifications")
            st.json({
                "needs_rag_grounding": decision.get("needs_rag_grounding"),
                "rag_confidence": decision.get("confidence"),
                "recommended_content_type": decision.get("recommended_content_type"),
                "recommended_tone": decision.get("recommended_tone"),
                "domain_complexity": decision.get("domain_complexity"),
                "routing_strategy": decision.get("routing_strategy")
            })

        with j_col2:
            st.markdown("#### 🛡️ Verification & Safety Gates")
            verification = st.session_state.content_generator.jav_engine.verify_generation(
                prompt=jav_test_prompt,
                generated_content="Sample technical overview explaining vector search...",
                content_type="blog_post",
                tone="professional",
                used_rag=True
            )
            st.json(verification)


# =========================================================
# TAB 4: STREAMLIT CLOUD DEPLOYMENT GUIDE
# =========================================================
with tab_guide:
    st.markdown("### 🚀 How to Host Directly on Streamlit Community Cloud from GitHub")
    st.markdown(
        """
        You can host this entire studio on **Streamlit Community Cloud (share.streamlit.io)** in less than 2 minutes directly from GitHub!
        """
    )

    st.markdown("#### 📋 Step-by-Step Deployment Instructions")
    st.markdown(
        """
        1. **Sign in to Streamlit Community Cloud**:
           - Visit [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.

        2. **Create New App**:
           - Click the **"New app"** or **"Create app"** button.

        3. **Fill in the Deployment Form**:
           - **Repository**: `divyaparadkar/AI-Content-Generator`
           - **Branch**: `main`
           - **Main file path**: `streamlit_app.py`
           - **App URL**: Choose a custom domain like `nexusai-content-studio.streamlit.app`

        4. **Configure Secrets (Optional)**:
           - In **Advanced settings** -> **Secrets**, paste your API keys:
           ```toml
           OPENAI_API_KEY = "sk-..."
           GEMINI_API_KEY = "AIzaSy..."
           HF_TOKEN = "hf_..."
           ```
           *(Note: Even with NO API keys, the studio functions 100% out of the box using the built-in Offline Smart Synthesizer!)*

        5. **Click "Deploy!"**:
           - Streamlit Cloud will install `requirements.txt` and launch your live application with a public HTTPS URL!
        """
    )

    st.markdown("---")
    st.markdown("#### ⚡ 1-Click Streamlit Deploy Link")
    deploy_url = "https://share.streamlit.io/deploy?repository=divyaparadkar/AI-Content-Generator&branch=main&mainModule=streamlit_app.py"
    st.link_button("🌐 Click Here to Deploy on Streamlit Cloud", deploy_url, type="primary")
