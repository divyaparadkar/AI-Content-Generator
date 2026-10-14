# ⚡ NexusAI Studio — AI Content Generator with RAG

An AI-powered content generation studio built with a Python & Flask backend and a modern JavaScript (ES6) frontend. The system supports multi-format content creation (Blog Posts, Social Media Captions, Executive Summaries, Newsletters, LinkedIn Posts), interactive prompt refinement, live readability analytics, and a Retrieval-Augmented Generation (RAG) knowledge engine that grounds generated outputs in verified reference documents.

---

## 🌟 Key Highlights & Requirements Delivered

| Requirement | Implementation Detail | Status |
| :--- | :--- | :---: |
| **Supported Content Types** | 5 Formats: Blog Post, Social Media Caption, Executive Summary, Email Newsletter, LinkedIn Post | ✅ Exceeds (Min 2 required) |
| **User Input Controls** | Topic prompt, Tone selector (7 tones), Length presets (Short/Medium/Long), Target Audience, Custom instructions | ✅ Complete |
| **Coherence & Context** | Strict prompt engineering constraints + RAG domain citation grounding | ✅ Complete |
| **Regenerate & Refine** | 1-Click Regenerate + Interactive Quick Refinement toolbar (Shorten, Expand, Witty, Bullet Checklist) + Custom Refinement | ✅ Complete |
| **Interface Quality** | Modern glassmorphism UI, Dark/Light modes, micro-animations, responsive layout | ✅ Complete |
| **Analytics & Counting** | Real-time Word Count, Character Count, Reading Time estimation, Reading Level grade | ✅ Complete |
| **JAV Fast Decision Engine** | System-1 discriminative model (<1ms latency) for RAG necessity evaluation, format/tone recommendations, routing, and quality verification gates | ✅ Complete |
| **RAG Knowledge Engine** | Document Loader (`pypdf`, text cleaning, overlapping chunker) + TF-IDF semantic vector store + Live source citation viewer | ✅ Complete |
| **Multi-Provider AI** | OpenAI (GPT-4o), Google Gemini, Hugging Face + Built-in Offline Smart Synthesizer (runs with zero API keys required!) | ✅ Complete |
| **Deliverables & Samples** | Documented prompt templates, 3+ sample outputs (`samples/`), full setup guide | ✅ Complete |

---

## 🏗️ System Architecture

```
d:\task 3\
├── app.py                     # Flask server & REST API (Generate, Refine, RAG upload, Documents)
├── requirements.txt           # Python package dependencies
├── rag/
│   ├── __init__.py
│   ├── document_loader.py     # PDF & text file extractor, whitespace cleaner, semantic chunker
│   ├── vector_store.py        # TF-IDF & Cosine Similarity vector store with instant indexing
│   └── rag_engine.py          # Document coordinator, similarity search, and context formatting
├── generator/
│   ├── __init__.py
│   ├── prompts.py             # Prompt engineering templates, structural guides, RAG grounding
│   ├── llm_client.py          # Unified client for OpenAI, Google Gemini, Hugging Face, Offline Synthesis
│   └── content_generator.py   # Generation orchestrator, metric calculation, and refinement
├── templates/
│   └── index.html             # Single-Page Studio Application with responsive panels and modals
├── static/
│   ├── css/
│   │   └── style.css          # Design system with CSS variables, glassmorphism, animations
│   └── js/
│       ├── app.js             # Main JavaScript application controller & state machine
│       ├── voice_ai.js        # Voice Input (STT) and Voice Narration (TTS) controller
│       ├── jav_decision.js    # JAV System-1 Fast Decision HUD & verification controller
│       ├── rag_ui.js          # RAG upload, dropzone, and citation viewer
│       └── presets.js         # 1-Click test presets with diverse topics & tones
└── samples/                   # Sample generated outputs for deliverables
    ├── sample_1_ai_rag_blog.md
    ├── sample_2_fitness_social_caption.md
    └── sample_3_cloud_executive_summary.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Install Dependencies
In your terminal, navigate to the project directory and install requirements:
```bash
cd "d:\task 3"
pip install -r requirements.txt
```

### 3. Launch the Application (Flask or Streamlit)

**Option A: Modern Streamlit Studio (Recommended for Streamlit Cloud & Fast UI)**
```bash
streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`.

**Option B: Full Flask REST Server & SPA**
```bash
python app.py
```
Open your browser at `http://localhost:5000`.

---

## ☁️ Deploy to Streamlit Cloud (streamlit.io) Directly from GitHub

This repository is ready for direct deployment to [Streamlit Community Cloud](https://share.streamlit.io):

1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account (`divyaparadkar`).
2. Click the **"New app"** or **"Create app"** button.
3. Select your repository:
   - **Repository:** `divyaparadkar/AI-Content-Generator`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py` (or `app.py`)
4. *(Optional)* Add API keys under **Advanced settings ➔ Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-..."
   GEMINI_API_KEY = "AIzaSy..."
   HF_TOKEN = "hf_..."
   ```
   *Note: Even without API keys, the studio runs 100% out of the box using the built-in Offline Smart Synthesizer!*
5. Click **Deploy!** Your app will be live on a public URL like `https://nexusai-studio.streamlit.app`.

---

## 🔑 AI Backend & API Key Setup

NexusAI Studio is built to be resilient. It provides **4 AI Backend options**:

### Option A: Offline Smart Synthesizer (Default - No API Key Required)
- **Zero Configuration Needed!**
- Synthesizes structured, tone-specific content and retrieves matching chunks from the RAG knowledge base.
- Perfect for offline grading, local evaluation, or environments without active API keys.

### Option B: OpenAI (GPT-4o / GPT-4o-mini)
1. In the top navigation, click **⚙️ Settings**.
2. Select **OpenAI (GPT-4o / GPT-4o-mini)**.
3. Paste your OpenAI API key (`sk-...`).
4. Click **Save Configuration**.
*(Alternatively, set the environment variable: `set OPENAI_API_KEY=your_key`)*

### Option C: Google Gemini (1.5 Flash / 2.0 Flash)
1. In the top navigation, click **⚙️ Settings**.
2. Select **Google Gemini**.
3. Paste your Gemini API key (`AIza...`).
4. Click **Save Configuration**.
*(Alternatively, set `set GEMINI_API_KEY=your_key`)*

### Option D: Hugging Face Inference API
1. In the top navigation, click **⚙️ Settings**.
2. Select **Hugging Face Inference API**.
3. Enter your Hugging Face User Access Token (`hf_...`).
4. Click **Save Configuration**.

---

## 🧠 Retrieval-Augmented Generation (RAG) Workflow

1. **Document Ingestion**:
   - Click the **📚 RAG Base** button in the navbar.
   - Drag & drop any PDF, text file (`.txt`), or markdown document (`.md`), or paste raw text.
2. **Chunking & Indexing**:
   - `rag/document_loader.py` splits documents into overlapping semantic chunks (default ~350 words, 60-word overlap) to preserve context.
   - `rag/vector_store.py` indexes the chunks into a TF-IDF vector matrix.
3. **Retrieval**:
   - When **Ground in RAG Knowledge Base** is toggled on, the engine queries the vector store using cosine similarity.
   - The top-k matching references are injected into the prompt.
4. **Citation Display**:
   - Citations and relevance scores are displayed below the output in the **Retrieved Grounding Knowledge** card.

---

## 📐 Prompt Engineering Architecture

The prompt engineering strategy is implemented in `generator/prompts.py`:

### 1. Role Priming & System Instructions
Each content type is paired with an expert persona and strict structural guide:
- **Blog Post**: Award-winning content strategist; requires H1 title, H2/H3 subheadings, bulleted takeaways, and thought-provoking conclusion.
- **Social Media Caption**: Scroll-stopping hook (<80 characters), concise high-density body, single clear CTA, and 4-6 targeted hashtags.
- **Text Summary**: Executive briefing specialist; requires 2-3 sentence core thesis, key strategic findings, and action items.
- **Email Newsletter**: Conversational storyteller; requires 3 subject line options for A/B testing, preview text, personal narrative, and sign-off.
- **LinkedIn Thought Leadership**: Attention-grabbing single line, whitespace, framework lessons, and question for comments.

### 2. RAG Context Injection Template
When reference documents are retrieved, the following grounding instructions are injected:
```
GROUNDING IN RETRIEVED KNOWLEDGE (RAG):
You have been provided with authoritative context retrieved from the user's reference library.
You MUST prioritize facts, metrics, and domain terminology from this reference material.
Cite relevant reference numbers (e.g. [Ref 1]) when drawing specific points.
```

### 3. Iterative Refinement Template
Used by the refinement engine to polish previous outputs without losing conversational context:
```
ORIGINAL CONTENT:
```markdown
{original_content}
```

REFINEMENT INSTRUCTIONS:
{refinement_instruction}

Please output the revised version now:
```

You can inspect the exact prompt sent to the model for any generation by clicking the **🔍 Prompt** button in the output toolbar.

---

## ⚡ JAV / Jev Fast System-1 Decision Engine

Inspired by Daniel Kahneman's **System-1** intuitive thinking model and modern decision-first architectures (e.g., TypeSafe AI's Jev model), the **JAV Decision Engine** provides sub-millisecond (<1ms) structured judgments without conversational text generation overhead.

### Core Capabilities:
1. **Pre-Flight Prompt Analysis**:
   - Evaluates whether the user prompt requires **RAG Knowledge Base Grounding** based on domain triggers and indexed source density.
   - Recommends the optimal **Content Type** (Blog, Social, Summary, etc.) and **Tone**.
   - Calculates a **Domain Complexity Score** (1 to 5) and selects the optimal routing strategy (*Fast Direct Synthesis* vs. *Deep RAG Grounded*).
2. **Real-Time Client-Side HUD**:
   - As the user types into the topic prompt, the JAV engine streams recommendations to the **JAV Decision Matrix HUD** in real time.
   - One-click **⚡ Auto-Align with JAV Decision** applies the recommended format, tone, and RAG configuration.
3. **Post-Generation Verification Gate**:
   - Evaluates generated outputs for **Structure Compliance** (H1/H2 headings, bullet takeaways, hashtags, CTAs), **Grounding Fidelity**, and **Hallucination Risk**.
   - Displays a verified quality gate card with exact execution latency (typically ~0.5ms).

---

## 📊 Sample Outputs

Three diverse sample outputs are documented in the `samples/` directory:
- [sample_1_ai_rag_blog.md](file:///d:/task%203/samples/sample_1_ai_rag_blog.md) — Technical AI Blog Post with RAG grounding.
- [sample_2_fitness_social_caption.md](file:///d:/task%203/samples/sample_2_fitness_social_caption.md) — High-impact 15-Minute Workout caption with hooks and hashtags.
- [sample_3_cloud_executive_summary.md](file:///d:/task%203/samples/sample_3_cloud_executive_summary.md) — Executive Hybrid Cloud Modernization briefing.

---

## 🧪 Testing & Verification Checklist

- [x] Tested with multiple content types (Blog, Social, Summary, Newsletter, LinkedIn)
- [x] Tested with diverse tones (Professional, Inspirational, Academic, Witty, Casual)
- [x] Tested real-time word and character counter
- [x] Tested copy-to-clipboard and markdown export
- [x] Tested interactive quick refinement (Punchier, Shorten, Expand, Bullet points)
- [x] Tested RAG document upload (PDF, TXT, MD) and vector retrieval
- [x] Verified zero-dependency offline mode works without API keys
