"""Flask Web Server and REST API for AI Content Generator with RAG and Multi-Model Support.
"""

import os
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

from rag.rag_engine import RAGEngine
from generator.content_generator import ContentGenerator
from generator.prompts import CONTENT_TYPES, TONE_OPTIONS, LENGTH_OPTIONS
from generator.llm_client import LLMClient

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB max upload

# Initialize Core RAG Engine & Content Generator
rag_engine = RAGEngine()
content_generator = ContentGenerator(rag_engine=rag_engine)


@app.route("/")
def index():
    """Serves the single-page application interface."""
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns available options, models, tones, and content types."""
    return jsonify({
        "content_types": CONTENT_TYPES,
        "tones": TONE_OPTIONS,
        "lengths": LENGTH_OPTIONS,
        "providers": LLMClient.SUPPORTED_PROVIDERS,
        "rag_stats": rag_engine.get_stats()
    })


@app.route("/api/jav/decide", methods=["POST"])
def jav_decide():
    """
    JAV / Jev Fast System-1 Decision Endpoint.
    Performs sub-millisecond discriminative evaluation on prompt state:
    - RAG retrieval necessity
    - Optimal content type and tone classification
    - Complexity and routing strategy
    """
    try:
        data = request.get_json(force=True) or {}
        prompt = data.get("prompt", "").strip()
        content_type = data.get("content_type", "blog_post")
        tone = data.get("tone", "professional")

        decision = content_generator.jav_engine.decide(
            prompt=prompt,
            current_content_type=content_type,
            current_tone=tone,
            has_custom_docs=bool(rag_engine.get_sources())
        )
        return jsonify({"success": True, "data": decision})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate_content():
    """Generate content based on user topic, tone, content type, and RAG options."""
    try:
        data = request.get_json(force=True) or {}
        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({
                "success": False,
                "error": "Please provide a topic or prompt for content generation."
            }), 400

        content_type = data.get("content_type", "blog_post")
        tone = data.get("tone", "professional")
        length = data.get("length", "medium")
        custom_instructions = data.get("custom_instructions", "")
        target_audience = data.get("target_audience", "General")
        use_rag = bool(data.get("use_rag", True))
        rag_top_k = int(data.get("rag_top_k", 3))

        provider = data.get("provider", "offline")
        model = data.get("model") or None
        api_key = data.get("api_key") or None
        temperature = float(data.get("temperature", 0.7))

        result = content_generator.generate(
            topic=topic,
            content_type=content_type,
            tone=tone,
            length=length,
            custom_instructions=custom_instructions,
            target_audience=target_audience,
            use_rag=use_rag,
            rag_top_k=rag_top_k,
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )

        return jsonify(result)

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Generation failed: {str(e)}"}), 500


@app.route("/api/refine", methods=["POST"])
def refine_content():
    """Refine or iterate on previously generated content."""
    try:
        data = request.get_json(force=True) or {}
        original_content = data.get("original_content", "").strip()
        refinement_instruction = data.get("refinement_instruction", "").strip()

        if not original_content:
            return jsonify({"success": False, "error": "No existing content to refine."}), 400
        if not refinement_instruction:
            return jsonify({"success": False, "error": "Please specify how to refine the output."}), 400

        content_type = data.get("content_type", "blog_post")
        tone = data.get("tone")
        provider = data.get("provider", "offline")
        model = data.get("model") or None
        api_key = data.get("api_key") or None
        temperature = float(data.get("temperature", 0.6))

        result = content_generator.refine(
            original_content=original_content,
            refinement_instruction=refinement_instruction,
            content_type=content_type,
            tone=tone,
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )

        return jsonify(result)

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Refinement failed: {str(e)}"}), 500


@app.route("/api/rag/upload", methods=["POST"])
def upload_rag_file():
    """Upload documents (PDF, TXT, MD, etc.) to the RAG knowledge vector store."""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file attached in request."}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"success": False, "error": "Empty filename."}), 400

        filename = secure_filename(file.filename) or file.filename
        file_bytes = file.read()

        if not file_bytes:
            return jsonify({"success": False, "error": "Uploaded file is empty."}), 400

        result = rag_engine.ingest_file(file_bytes=file_bytes, filename=filename)
        return jsonify({
            "success": True,
            "message": f"Successfully indexed '{filename}' into RAG knowledge base.",
            "data": result,
            "stats": rag_engine.get_stats()
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Document upload failed: {str(e)}"}), 500


@app.route("/api/rag/add-text", methods=["POST"])
def add_rag_text():
    """Manually add a text snippet into the RAG knowledge base."""
    try:
        data = request.get_json(force=True) or {}
        text = data.get("text", "").strip()
        source_name = data.get("source_name", "User Note").strip() or "User Note"

        if not text:
            return jsonify({"success": False, "error": "Text cannot be empty."}), 400

        result = rag_engine.ingest_raw_text(text=text, source_name=source_name)
        return jsonify({
            "success": True,
            "message": f"Successfully indexed snippet '{source_name}'.",
            "data": result,
            "stats": rag_engine.get_stats()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/rag/documents", methods=["GET"])
def get_rag_documents():
    """Get all indexed sources and RAG knowledge base stats."""
    return jsonify({
        "success": True,
        "sources": rag_engine.get_sources(),
        "stats": rag_engine.get_stats()
    })


@app.route("/api/rag/documents/<path:source_name>", methods=["DELETE"])
def delete_rag_document(source_name):
    """Delete a specific document from RAG index."""
    removed = rag_engine.remove_source(source_name)
    return jsonify({
        "success": True,
        "removed_chunks": removed,
        "stats": rag_engine.get_stats()
    })


@app.route("/api/rag/reset", methods=["POST"])
def reset_rag():
    """Reset RAG knowledge base back to pre-loaded defaults."""
    rag_engine.clear()
    rag_engine._load_default_knowledge()
    return jsonify({
        "success": True,
        "message": "RAG knowledge base reset to default curated documents.",
        "stats": rag_engine.get_stats()
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "AI Content Generator with RAG"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] AI Content Generator running at: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
