/**
 * NexusAI Content Studio - Main JavaScript Controller
 * Orchestrates multi-model generation, RAG integration, interactive refinement,
 * live analytics, preset management, and export utilities.
 */

import { SAMPLE_PRESETS } from "./presets.js";
import { RAGManager } from "./rag_ui.js";
import { JAVDecisionController } from "./jav_decision.js";
import { VoiceAIController } from "./voice_ai.js";

class ContentStudioApp {
  constructor() {
    this.state = {
      contentType: "blog_post",
      tone: "professional",
      length: "medium",
      provider: "offline",
      apiKey: localStorage.getItem("nexus_api_key") || "",
      model: "",
      temperature: 0.7,
      useRag: true,
      lastGenerated: null,
      history: JSON.parse(localStorage.getItem("nexus_history") || "[]")
    };

    this.initDOMElements();
    this.initRAG();
    this.initJAV();
    this.initVoiceAI();
    this.bindEvents();
    this.initTheme();
    this.renderPresets();
    this.updateLiveCharCount();
  }

  initDOMElements() {
    // Form Inputs
    this.topicInput = document.getElementById("topicInput");
    this.customInstructions = document.getElementById("customInstructions");
    this.targetAudience = document.getElementById("targetAudience");
    this.toneSelect = document.getElementById("toneSelect");
    this.lengthSelect = document.getElementById("lengthSelect");
    this.useRagToggle = document.getElementById("useRagToggle");
    this.ragSwitchBox = document.getElementById("ragSwitchBox");
    this.btnGenerate = document.getElementById("btnGenerate");
    this.btnSendArrow = document.getElementById("btnSendArrow");

    // Output & Metrics
    this.outputBody = document.getElementById("outputBody");
    this.markdownPreview = document.getElementById("markdownPreview");
    this.rawEditor = document.getElementById("rawContentEditor");
    this.emptyState = document.getElementById("emptyState");
    this.loadingOverlay = document.getElementById("loadingOverlay");
    this.loadingStatusText = document.getElementById("loadingStatusText");

    this.badgeWordCount = document.getElementById("badgeWordCount");
    this.badgeCharCount = document.getElementById("badgeCharCount");
    this.badgeReadTime = document.getElementById("badgeReadTime");
    this.badgeReadLevel = document.getElementById("badgeReadLevel");
    this.badgeModelStatus = document.getElementById("badgeModelStatus");

    // Action Buttons
    this.btnCopy = document.getElementById("btnCopy");
    this.btnRegenerate = document.getElementById("btnRegenerate");
    this.btnInspectPrompt = document.getElementById("btnInspectPrompt");
    this.btnExport = document.getElementById("btnExport");

    // Quick Refine
    this.customRefineInput = document.getElementById("customRefineInput");
    this.btnCustomRefine = document.getElementById("btnCustomRefine");

    // Tabs
    this.tabPreview = document.getElementById("tabPreview");
    this.tabRaw = document.getElementById("tabRaw");

    // Modals
    this.modalSettings = document.getElementById("modalSettings");
    this.modalPromptInspector = document.getElementById("modalPromptInspector");
    this.modalRAG = document.getElementById("modalRAG");
    this.modalHistory = document.getElementById("modalHistory");
    this.toastContainer = document.getElementById("toastContainer");
  }

  initRAG() {
    this.ragManager = new RAGManager({
      onStatsUpdate: (stats) => {
        const statsEl = document.getElementById("ragStatsDesc");
        if (statsEl) {
          statsEl.textContent = `${stats.total_sources} sources (${stats.total_chunks} chunks indexed)`;
        }
      },
      onToast: (msg, type) => this.showToast(msg, type)
    });
  }

  initJAV() {
    this.javController = new JAVDecisionController({
      onApplyRecommendations: (recs) => {
        // Apply optimal content type
        if (recs.contentType) {
          document.querySelectorAll(".content-type-card").forEach(c => {
            c.classList.toggle("active", c.getAttribute("data-type") === recs.contentType);
          });
          this.state.contentType = recs.contentType;
        }
        // Apply optimal tone
        if (recs.tone && this.toneSelect) {
          this.toneSelect.value = recs.tone;
          this.state.tone = recs.tone;
        }
        // Apply RAG recommendation
        if (recs.useRag !== undefined && this.useRagToggle) {
          this.useRagToggle.checked = recs.useRag;
          this.state.useRag = recs.useRag;
          if (this.ragSwitchBox) this.ragSwitchBox.classList.toggle("active", recs.useRag);
        }
      },
      onToast: (msg, type) => this.showToast(msg, type)
    });
  }

  initVoiceAI() {
    this.voiceAI = new VoiceAIController({
      onTranscription: (text) => {
        this.topicInput.value = text;
        this.updateLiveCharCount();
        if (this.javController) {
          this.javController.evaluatePromptDebounced(text, this.state.contentType, this.state.tone);
        }
      },
      onToast: (msg, type) => this.showToast(msg, type)
    });
  }

  bindEvents() {
    // Content Type Cards
    document.querySelectorAll(".content-type-card").forEach(card => {
      card.addEventListener("click", () => {
        document.querySelectorAll(".content-type-card").forEach(c => c.classList.remove("active"));
        card.classList.add("active");
        this.state.contentType = card.getAttribute("data-type");
      });
    });

    // Tone & Length Selects
    if (this.toneSelect) {
      this.toneSelect.addEventListener("change", (e) => this.state.tone = e.target.value);
    }
    if (this.lengthSelect) {
      this.lengthSelect.addEventListener("change", (e) => this.state.length = e.target.value);
    }

    // RAG Toggle
    if (this.useRagToggle) {
      this.useRagToggle.addEventListener("change", (e) => {
        this.state.useRag = e.target.checked;
        if (this.ragSwitchBox) {
          this.ragSwitchBox.classList.toggle("active", e.target.checked);
        }
      });
    }

    // Generate Button & Keyboard Shortcut
    if (this.btnGenerate) {
      this.btnGenerate.addEventListener("click", () => this.handleGenerate());
    }
    if (this.btnSendArrow) {
      this.btnSendArrow.addEventListener("click", () => this.handleGenerate());
    }
    if (this.topicInput) {
      this.topicInput.addEventListener("keydown", (e) => {
        // ONLY ENTER generates the answer! (Shift+Enter creates a newline)
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.handleGenerate();
        }
      });
      this.topicInput.addEventListener("input", () => {
        this.updateLiveCharCount();
        if (this.javController) {
          this.javController.evaluatePromptDebounced(this.topicInput.value, this.state.contentType, this.state.tone);
        }
      });
    }

    // Regenerate
    if (this.btnRegenerate) {
      this.btnRegenerate.addEventListener("click", () => this.handleRegenerate());
    }

    // Copy to Clipboard
    if (this.btnCopy) {
      this.btnCopy.addEventListener("click", () => this.handleCopy());
    }

    // Export Options
    if (this.btnExport) {
      this.btnExport.addEventListener("click", () => this.handleExport());
    }

    // Quick Refine Chips
    document.querySelectorAll(".quick-refine-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const instruction = chip.getAttribute("data-refine");
        if (instruction) {
          this.handleRefine(instruction);
        }
      });
    });

    // Custom Refinement
    if (this.btnCustomRefine && this.customRefineInput) {
      const submitCustom = () => {
        const text = this.customRefineInput.value.trim();
        if (text) {
          this.handleRefine(text);
          this.customRefineInput.value = "";
        }
      };
      this.btnCustomRefine.addEventListener("click", submitCustom);
      this.customRefineInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          submitCustom();
        }
      });
    }

    // Tabs Switch
    if (this.tabPreview && this.tabRaw) {
      this.tabPreview.addEventListener("click", () => this.switchTab("preview"));
      this.tabRaw.addEventListener("click", () => this.switchTab("raw"));
    }

    // Raw Editor live updates
    if (this.rawEditor) {
      this.rawEditor.addEventListener("input", () => {
        const content = this.rawEditor.value;
        this.markdownPreview.innerHTML = this.renderMarkdown(content);
        this.updateMetricsUI(this.calculateMetrics(content));
      });
    }

    // Nav Modals
    this.bindModalTriggers();
    this.bindSettingsForm();
  }

  bindModalTriggers() {
    // Open triggers
    document.getElementById("btnOpenSettings")?.addEventListener("click", () => this.openModal(this.modalSettings));
    document.getElementById("btnOpenRag")?.addEventListener("click", () => this.openModal(this.modalRAG));
    document.getElementById("btnOpenHistory")?.addEventListener("click", () => {
      this.renderHistoryList();
      this.openModal(this.modalHistory);
    });
    this.btnInspectPrompt?.addEventListener("click", () => {
      this.renderPromptInspector();
      this.openModal(this.modalPromptInspector);
    });

    // Close triggers
    document.querySelectorAll(".modal-close, .modal-backdrop").forEach(el => {
      el.addEventListener("click", (e) => {
        if (e.target === el) {
          document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("open"));
        }
      });
    });

    // Theme Toggle
    document.getElementById("btnThemeToggle")?.addEventListener("click", () => this.toggleTheme());
  }

  bindSettingsForm() {
    const form = document.getElementById("settingsForm");
    const providerSelect = document.getElementById("settingsProvider");
    const apiKeyInput = document.getElementById("settingsApiKey");
    const modelInput = document.getElementById("settingsModel");
    const tempInput = document.getElementById("settingsTemp");
    const tempVal = document.getElementById("tempValueDisplay");

    if (tempInput && tempVal) {
      tempInput.addEventListener("input", () => tempVal.textContent = tempInput.value);
    }

    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.state.provider = providerSelect.value;
        this.state.apiKey = apiKeyInput.value.trim();
        this.state.model = modelInput.value.trim();
        this.state.temperature = parseFloat(tempInput.value) || 0.7;

        localStorage.setItem("nexus_provider", this.state.provider);
        localStorage.setItem("nexus_api_key", this.state.apiKey);
        localStorage.setItem("nexus_model", this.state.model);

        this.showToast("Settings updated successfully!", "success");
        this.closeAllModals();
        this.updateProviderBadge();
      });
    }

    // Load saved settings
    const savedProvider = localStorage.getItem("nexus_provider") || "offline";
    if (providerSelect) providerSelect.value = savedProvider;
    this.state.provider = savedProvider;
    if (apiKeyInput) apiKeyInput.value = this.state.apiKey;
    this.updateProviderBadge();
  }

  updateProviderBadge() {
    const labelMap = {
      offline: "Offline RAG Synthesis",
      openai: "OpenAI GPT-4o",
      gemini: "Google Gemini",
      huggingface: "Hugging Face"
    };
    const navBadge = document.getElementById("navModelBadge");
    if (navBadge) {
      navBadge.textContent = labelMap[this.state.provider] || this.state.provider;
    }
  }

  renderPresets() {
    const container = document.getElementById("presetPills");
    if (!container) return;

    container.innerHTML = SAMPLE_PRESETS.map(preset => `
      <div class="preset-chip" data-id="${preset.id}">
        <span>${preset.title}</span>
      </div>
    `).join("");

    container.querySelectorAll(".preset-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const preset = SAMPLE_PRESETS.find(p => p.id === chip.getAttribute("data-id"));
        if (preset) this.loadPreset(preset);
      });
    });
  }

  loadPreset(preset) {
    this.topicInput.value = preset.topic;
    this.targetAudience.value = preset.audience || "";
    this.customInstructions.value = preset.customInstructions || "";

    // Content Type Card
    document.querySelectorAll(".content-type-card").forEach(c => {
      c.classList.toggle("active", c.getAttribute("data-type") === preset.contentType);
    });
    this.state.contentType = preset.contentType;

    // Tone & Length
    if (this.toneSelect) this.toneSelect.value = preset.tone;
    this.state.tone = preset.tone;
    if (this.lengthSelect) this.lengthSelect.value = preset.length;
    this.state.length = preset.length;

    // RAG Toggle
    if (this.useRagToggle) {
      this.useRagToggle.checked = preset.useRag;
      this.state.useRag = preset.useRag;
      this.ragSwitchBox.classList.toggle("active", preset.useRag);
    }

    this.updateLiveCharCount();
    if (this.javController) {
      this.javController.evaluatePrompt(preset.topic, preset.contentType, preset.tone);
    }
    this.showToast(`Loaded preset: "${preset.title}"`, "info");

    // If sample output provided, optionally render as preview immediately!
    if (preset.sampleOutput) {
      this.renderOutput({
        content: preset.sampleOutput,
        topic: preset.topic,
        content_type: preset.contentType,
        tone: preset.tone,
        length: preset.length,
        metrics: this.calculateMetrics(preset.sampleOutput),
        rag: { used: preset.useRag, citations: [] },
        model_info: { provider: "Preset Showcase", model: "sample-demo", duration_seconds: 0.1 }
      });
    }
  }

  async handleGenerate() {
    const topic = this.topicInput.value.trim();
    if (!topic) {
      this.showToast("Please enter a topic or prompt to generate content.", "error");
      this.topicInput.focus();
      return;
    }

    this.showLoading(true, "Synthesizing content with RAG context...");

    const payload = {
      topic: topic,
      content_type: this.state.contentType,
      tone: this.state.tone,
      length: this.state.length,
      custom_instructions: this.customInstructions.value.trim(),
      target_audience: this.targetAudience.value.trim(),
      use_rag: this.state.useRag,
      provider: this.state.provider,
      api_key: this.state.apiKey,
      model: this.state.model,
      temperature: this.state.temperature
    };

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if (!resp.ok || !data.success) {
        throw new Error(data.error || "Generation request failed");
      }

      this.renderOutput(data);
      this.saveToHistory(data);
      this.showToast("Content generated successfully!", "success");

    } catch (err) {
      this.showToast(`Generation Error: ${err.message}`, "error");
    } finally {
      this.showLoading(false);
    }
  }

  async handleRegenerate() {
    if (!this.topicInput.value.trim()) {
      this.showToast("Enter a topic first.", "error");
      return;
    }
    this.handleGenerate();
  }

  async handleRefine(instruction) {
    const originalContent = this.rawEditor.value.trim();
    if (!originalContent) {
      this.showToast("No content available to refine.", "error");
      return;
    }

    this.showLoading(true, `Refining content: "${instruction}"...`);

    const payload = {
      original_content: originalContent,
      refinement_instruction: instruction,
      content_type: this.state.contentType,
      tone: this.state.tone,
      provider: this.state.provider,
      api_key: this.state.apiKey,
      model: this.state.model,
      temperature: this.state.temperature
    };

    try {
      const resp = await fetch("/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if (!resp.ok || !data.success) {
        throw new Error(data.error || "Refinement failed");
      }

      this.renderOutput(data);
      this.saveToHistory(data);
      this.showToast(`Refined: "${instruction}"!`, "success");

    } catch (err) {
      this.showToast(`Refinement Error: ${err.message}`, "error");
    } finally {
      this.showLoading(false);
    }
  }

  renderOutput(result) {
    this.state.lastGenerated = result;
    const content = result.content || "";

    if (this.emptyState) this.emptyState.style.display = "none";
    if (this.markdownPreview) {
      this.markdownPreview.style.display = "block";
      this.markdownPreview.innerHTML = this.renderMarkdown(content);
    }
    if (this.rawEditor) {
      this.rawEditor.value = content;
    }

    // Update Metrics
    const metrics = result.metrics || this.calculateMetrics(content);
    this.updateMetricsUI(metrics);

    // Update Model Status Badge
    if (this.badgeModelStatus) {
      const provider = result.model_info?.provider || this.state.provider;
      const duration = result.model_info?.duration_seconds ? `${result.model_info.duration_seconds}s` : "";
      this.badgeModelStatus.textContent = `${provider.toUpperCase()} ${duration ? '• ' + duration : ''}`;
    }

    // Citations
    if (result.rag && result.rag.citations) {
      this.ragManager.displayCitations(result.rag.citations);
    } else {
      this.ragManager.displayCitations([]);
    }

    // JAV Quality & Constraint Verification Gate
    if (result.jav && result.jav.verification && this.javController) {
      this.javController.renderVerification(result.jav.verification);
    } else if (this.javController) {
      this.javController.renderVerification(null);
    }

    // Switch to preview tab
    this.switchTab("preview");
  }

  updateMetricsUI(metrics) {
    if (this.badgeWordCount) {
      this.badgeWordCount.innerHTML = `<strong>${metrics.word_count}</strong> words`;
    }
    if (this.badgeCharCount) {
      this.badgeCharCount.innerHTML = `<strong>${metrics.char_count.toLocaleString()}</strong> chars`;
    }
    if (this.badgeReadTime) {
      this.badgeReadTime.innerHTML = `⏱️ <strong>${metrics.reading_time_minutes}</strong> min read`;
    }
    if (this.badgeReadLevel) {
      this.badgeReadLevel.innerHTML = `🎯 <strong>${metrics.reading_level || 'Standard'}</strong>`;
    }
  }

  calculateMetrics(text) {
    if (!text) return { word_count: 0, char_count: 0, reading_time_minutes: 0, reading_level: "N/A" };
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const word_count = words.length;
    const char_count = text.length;
    const reading_time_minutes = Math.max(0.1, Math.round((word_count / 200) * 10) / 10);
    return {
      word_count,
      char_count,
      reading_time_minutes,
      reading_level: word_count > 400 ? "Comprehensive" : "Concise"
    };
  }

  switchTab(tabName) {
    if (tabName === "preview") {
      this.tabPreview.classList.add("active");
      this.tabRaw.classList.remove("active");
      this.markdownPreview.style.display = "block";
      this.rawEditor.style.display = "none";
    } else {
      this.tabRaw.classList.add("active");
      this.tabPreview.classList.remove("active");
      this.markdownPreview.style.display = "none";
      this.rawEditor.style.display = "block";
    }
  }

  async handleCopy() {
    const text = this.rawEditor.value;
    if (!text) {
      this.showToast("Nothing to copy yet.", "error");
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      this.btnCopy.innerHTML = "<span>✅</span> <span>Copied!</span>";
      setTimeout(() => {
        this.btnCopy.innerHTML = "<span>📋</span> <span>Copy</span>";
      }, 2000);
      this.showToast("Copied content to clipboard!", "success");
    } catch (err) {
      // Fallback
      this.rawEditor.select();
      document.execCommand("copy");
      this.showToast("Copied to clipboard!", "success");
    }
  }

  handleExport() {
    const text = this.rawEditor.value;
    if (!text) {
      this.showToast("No content to export.", "error");
      return;
    }

    const type = this.state.contentType || "content";
    const filename = `nexus_${type}_${Date.now()}.md`;
    const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    this.showToast(`Exported "${filename}"`, "success");
  }

  renderPromptInspector() {
    const systemPromptEl = document.getElementById("inspectorSystemPrompt");
    const userPromptEl = document.getElementById("inspectorUserPrompt");

    if (this.state.lastGenerated && this.state.lastGenerated.prompt_debug) {
      const debug = this.state.lastGenerated.prompt_debug;
      if (systemPromptEl) systemPromptEl.textContent = debug.system_prompt;
      if (userPromptEl) userPromptEl.textContent = debug.user_prompt;
    } else {
      if (systemPromptEl) systemPromptEl.textContent = "Generate content first to inspect the prompt templates.";
      if (userPromptEl) userPromptEl.textContent = "";
    }
  }

  saveToHistory(result) {
    if (!result || !result.content) return;
    const item = {
      id: Date.now(),
      topic: result.topic || this.topicInput.value,
      contentType: result.content_type || this.state.contentType,
      tone: result.tone || this.state.tone,
      wordCount: result.metrics?.word_count || 0,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: result.content,
      result: result
    };

    this.state.history.unshift(item);
    if (this.state.history.length > 20) this.state.history.pop();
    localStorage.setItem("nexus_history", JSON.stringify(this.state.history));
  }

  renderHistoryList() {
    const list = document.getElementById("historyListContainer");
    if (!list) return;

    if (!this.state.history || this.state.history.length === 0) {
      list.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No saved generations yet.</div>`;
      return;
    }

    list.innerHTML = this.state.history.map(item => `
      <div class="history-item" data-id="${item.id}">
        <div style="display: flex; flex-direction: column; gap: 0.2rem;">
          <strong style="color: var(--text-primary); font-size: 0.88rem;">${this.escapeHtml(item.topic)}</strong>
          <span style="font-size: 0.72rem; color: var(--text-muted);">
            ${item.contentType} • ${item.wordCount} words • ${item.timestamp}
          </span>
        </div>
        <button class="btn btn-secondary btn-sm load-history-btn">Restore</button>
      </div>
    `).join("");

    list.querySelectorAll(".history-item").forEach(el => {
      el.addEventListener("click", () => {
        const id = parseInt(el.getAttribute("data-id"));
        const item = this.state.history.find(h => h.id === id);
        if (item) {
          this.renderOutput(item.result || { content: item.content, topic: item.topic });
          this.closeAllModals();
          this.showToast(`Restored "${item.topic.slice(0, 30)}..."`, "info");
        }
      });
    });
  }

  updateLiveCharCount() {
    const countEl = document.getElementById("topicCharCounter");
    if (countEl && this.topicInput) {
      const len = this.topicInput.value.length;
      countEl.textContent = `${len} characters`;
    }
  }

  showLoading(isLoading, message = "Generating...") {
    if (!this.loadingOverlay) return;
    this.loadingOverlay.style.display = isLoading ? "flex" : "none";
    if (this.loadingStatusText) this.loadingStatusText.textContent = message;
    if (this.btnGenerate) this.btnGenerate.disabled = isLoading;
    if (this.btnSendArrow) this.btnSendArrow.disabled = isLoading;
  }

  showToast(message, type = "info") {
    if (!this.toastContainer) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const iconMap = { success: "✅", error: "❌", info: "ℹ️" };
    toast.innerHTML = `<span>${iconMap[type] || '✨'}</span><span>${this.escapeHtml(message)}</span>`;
    this.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  openModal(modal) {
    if (modal) modal.classList.add("open");
  }

  closeAllModals() {
    document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("open"));
  }

  initTheme() {
    const savedTheme = localStorage.getItem("nexus_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
  }

  toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("nexus_theme", next);
    this.showToast(`Switched to ${next} mode`, "info");
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /**
   * Lightweight, robust markdown parser converting Markdown syntax into clean HTML.
   */
  renderMarkdown(md) {
    if (!md) return "";

    let html = md;
    // Code blocks
    html = html.replace(/```([a-z0-9]*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre><code class="language-${lang}">${this.escapeHtml(code.trim())}</code></pre>`;
    });

    // Blockquotes
    html = html.replace(/^>\s?(.*)$/gm, '<blockquote>$1</blockquote>');

    // Headings
    html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');

    // Bold & Italics
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Horizontal Rule
    html = html.replace(/^---$/gm, '<hr style="border:0;border-top:1px solid var(--surface-border);margin:1.5rem 0;" />');

    // Unordered lists
    html = html.replace(/^\s*[-•]\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    // Deduplicate nested <ul> tags from regex
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Paragraphs
    const paragraphs = html.split(/\n{2,}/);
    html = paragraphs.map(p => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith('<h') || p.startsWith('<pre') || p.startsWith('<ul') || p.startsWith('<blockquote') || p.startsWith('<hr')) {
        return p;
      }
      return `<p>${p.replace(/\n/g, '<br/>')}</p>`;
    }).join('\n\n');

    return html;
  }
}

// Bootstrap App
document.addEventListener("DOMContentLoaded", () => {
  window.nexusApp = new ContentStudioApp();
});
