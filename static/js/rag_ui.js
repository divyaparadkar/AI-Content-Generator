/**
 * RAG Knowledge Base Management UI Module
 * Handles file uploads (PDF, TXT, MD), text snippets, indexing, and source display.
 */

export class RAGManager {
  constructor(options = {}) {
    this.onStatsUpdate = options.onStatsUpdate || (() => {});
    this.onToast = options.onToast || (() => {});
    this.initElements();
    this.bindEvents();
    this.refreshDocuments();
  }

  initElements() {
    this.dropzone = document.getElementById("ragDropzone");
    this.fileInput = document.getElementById("ragFileInput");
    this.docsListContainer = document.getElementById("ragDocsList");
    this.addTextForm = document.getElementById("ragAddTextForm");
    this.textSnippetInput = document.getElementById("ragSnippetText");
    this.textSnippetTitle = document.getElementById("ragSnippetTitle");
    this.btnResetRag = document.getElementById("btnResetRag");
    this.ragBadgeCount = document.getElementById("navRagCountBadge");
    this.citationsCard = document.getElementById("ragCitationsCard");
    this.citationsList = document.getElementById("citationsList");
  }

  bindEvents() {
    if (this.dropzone && this.fileInput) {
      this.dropzone.addEventListener("click", () => this.fileInput.click());

      this.fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.uploadFile(e.target.files[0]);
          e.target.value = "";
        }
      });

      this.dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        this.dropzone.classList.add("dragover");
      });

      this.dropzone.addEventListener("dragleave", () => {
        this.dropzone.classList.remove("dragover");
      });

      this.dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        this.dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (this.addTextForm) {
      this.addTextForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.addTextSnippet();
      });
    }

    if (this.btnResetRag) {
      this.btnResetRag.addEventListener("click", () => this.resetKnowledgeBase());
    }
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    this.onToast(`Uploading & indexing "${file.name}"...`, "info");
    try {
      const resp = await fetch("/api/rag/upload", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      if (!resp.ok || !data.success) {
        throw new Error(data.error || "Upload failed");
      }
      this.onToast(`Indexed ${data.data.chunks_added} chunks from "${file.name}"!`, "success");
      this.refreshDocuments();
    } catch (err) {
      this.onToast(`Upload Error: ${err.message}`, "error");
    }
  }

  async addTextSnippet() {
    const text = this.textSnippetInput.value.trim();
    const sourceName = this.textSnippetTitle.value.trim() || "Manual Snippet";

    if (!text) {
      this.onToast("Please enter text content to index.", "error");
      return;
    }

    try {
      const resp = await fetch("/api/rag/add-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, source_name: sourceName })
      });
      const data = await resp.json();
      if (!resp.ok || !data.success) {
        throw new Error(data.error || "Failed to add snippet");
      }
      this.onToast(`Snippet "${sourceName}" indexed successfully!`, "success");
      this.textSnippetInput.value = "";
      this.textSnippetTitle.value = "";
      this.refreshDocuments();
    } catch (err) {
      this.onToast(`Error: ${err.message}`, "error");
    }
  }

  async refreshDocuments() {
    try {
      const resp = await fetch("/api/rag/documents");
      const data = await resp.json();
      if (resp.ok && data.success) {
        this.renderDocuments(data.sources);
        if (this.ragBadgeCount) {
          this.ragBadgeCount.textContent = `${data.stats.total_chunks} chunks`;
        }
        this.onStatsUpdate(data.stats);
      }
    } catch (err) {
      console.error("Failed to load RAG documents:", err);
    }
  }

  renderDocuments(sources) {
    if (!this.docsListContainer) return;
    if (!sources || sources.length === 0) {
      this.docsListContainer.innerHTML = `
        <div style="color: var(--text-muted); font-size: 0.82rem; text-align: center; padding: 1rem;">
          No custom documents indexed yet. Upload a PDF or paste text above.
        </div>
      `;
      return;
    }

    this.docsListContainer.innerHTML = sources.map(src => `
      <div class="history-item">
        <div style="display: flex; flex-direction: column; gap: 0.15rem;">
          <strong style="font-size: 0.85rem; color: var(--text-primary);">${this.escapeHtml(src.source)}</strong>
          <span style="font-size: 0.72rem; color: var(--text-muted);">
            ${src.chunk_count} chunk${src.chunk_count > 1 ? 's' : ''} • ~${src.word_count} words
          </span>
        </div>
        <button class="btn btn-secondary btn-sm delete-doc-btn" data-source="${encodeURIComponent(src.source)}" title="Remove document">
          🗑️
        </button>
      </div>
    `).join("");

    // Bind delete buttons
    this.docsListContainer.querySelectorAll(".delete-doc-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const sourceName = decodeURIComponent(btn.getAttribute("data-source"));
        if (confirm(`Remove "${sourceName}" from knowledge base?`)) {
          await this.deleteDocument(sourceName);
        }
      });
    });
  }

  async deleteDocument(sourceName) {
    try {
      const resp = await fetch(`/api/rag/documents/${encodeURIComponent(sourceName)}`, {
        method: "DELETE"
      });
      const data = await resp.json();
      if (resp.ok && data.success) {
        this.onToast(`Removed "${sourceName}".`, "info");
        this.refreshDocuments();
      }
    } catch (err) {
      this.onToast(`Failed to remove document: ${err.message}`, "error");
    }
  }

  async resetKnowledgeBase() {
    if (!confirm("Reset knowledge base back to default sample documents?")) return;
    try {
      const resp = await fetch("/api/rag/reset", { method: "POST" });
      const data = await resp.json();
      if (resp.ok && data.success) {
        this.onToast("Knowledge base reset to defaults.", "success");
        this.refreshDocuments();
      }
    } catch (err) {
      this.onToast(`Reset failed: ${err.message}`, "error");
    }
  }

  displayCitations(citations) {
    if (!this.citationsCard || !this.citationsList) return;

    if (!citations || citations.length === 0) {
      this.citationsCard.style.display = "none";
      return;
    }

    this.citationsCard.style.display = "flex";
    this.citationsList.innerHTML = citations.map(c => `
      <div class="citation-item">
        <div class="citation-meta">
          <span>📚 Ref ${c.reference_id}: ${this.escapeHtml(c.source)}</span>
          <span class="citation-score">Relevance: ${Math.round(c.similarity_score * 100)}%</span>
        </div>
        <div class="citation-excerpt">"${this.escapeHtml(c.excerpt)}"</div>
      </div>
    `).join("");
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}
