/**
 * Voice AI Module for NexusAI Studio
 * Implements:
 * 1. Voice Input (Speech-to-Text): Speak your topic or prompt via microphone dictation.
 * 2. Voice Narration (Text-to-Speech): Natural audio read-out of generated content with play/pause/stop controls.
 */

export class VoiceAIController {
  constructor(options = {}) {
    this.onTranscription = options.onTranscription || (() => {});
    this.onToast = options.onToast || (() => {});

    this.isListening = false;
    this.isSpeaking = false;
    this.speechRecognition = null;
    this.synth = window.speechSynthesis || null;
    this.currentUtterance = null;

    this.initElements();
    this.initSpeechRecognition();
    this.bindEvents();
    this.loadVoices();
  }

  initElements() {
    this.btnMic = document.getElementById("btnVoiceInput");
    this.micStatus = document.getElementById("voiceInputStatus");
    this.btnReadAloud = document.getElementById("btnVoiceReadAloud");
    this.voiceWave = document.getElementById("voiceWaveIndicator");
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SpeechRecognition) {
      console.warn("[Voice AI] Web Speech Recognition API not supported in this browser.");
      if (this.btnMic) {
        this.btnMic.title = "Voice input is supported in Chrome, Edge, and Safari";
      }
      return;
    }

    this.speechRecognition = new SpeechRecognition();
    this.speechRecognition.continuous = false;
    this.speechRecognition.interimResults = true;
    this.speechRecognition.lang = "en-US";

    this.speechRecognition.onstart = () => {
      this.isListening = true;
      if (this.btnMic) {
        this.btnMic.classList.add("recording");
        this.btnMic.innerHTML = "<span>🔴</span> <span>Listening...</span>";
      }
      if (this.micStatus) this.micStatus.textContent = "Listening to your voice...";
      this.onToast("🎙️ Voice input active. Speak your prompt now...", "info");
    };

    this.speechRecognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript;
      }
      if (transcript.trim()) {
        this.onTranscription(transcript.trim());
      }
    };

    this.speechRecognition.onerror = (event) => {
      console.error("[Voice AI] Speech recognition error:", event.error);
      this.isListening = false;
      this.resetMicButton();
      this.onToast(`Voice Error: ${event.error}`, "error");
    };

    this.speechRecognition.onend = () => {
      this.isListening = false;
      this.resetMicButton();
      if (this.micStatus) this.micStatus.textContent = "";
      this.onToast("Voice input complete!", "success");
    };
  }

  bindEvents() {
    if (this.btnMic) {
      this.btnMic.addEventListener("click", () => this.toggleVoiceInput());
    }

    if (this.btnReadAloud) {
      this.btnReadAloud.addEventListener("click", () => this.toggleReadAloud());
    }

    if (this.synth) {
      if (this.synth.onvoiceschanged !== undefined) {
        this.synth.onvoiceschanged = () => this.loadVoices();
      }
    }
  }

  toggleVoiceInput() {
    if (!this.speechRecognition) {
      this.onToast("Voice dictation is supported in modern Chrome, Edge, and Safari.", "info");
      return;
    }

    if (this.isListening) {
      this.speechRecognition.stop();
    } else {
      try {
        this.speechRecognition.start();
      } catch (err) {
        console.warn("Speech recognition already active:", err);
      }
    }
  }

  resetMicButton() {
    if (this.btnMic) {
      this.btnMic.classList.remove("recording");
      this.btnMic.innerHTML = "<span>🎙️</span> <span>Voice Prompt</span>";
    }
  }

  loadVoices() {
    if (!this.synth) return;
    this.voices = this.synth.getVoices().filter(v => v.lang.startsWith("en"));
  }

  /**
   * Reads the generated text out loud using natural SpeechSynthesis.
   */
  toggleReadAloud() {
    if (!this.synth) {
      this.onToast("Text-to-speech is not supported in this browser.", "error");
      return;
    }

    if (this.isSpeaking) {
      this.stopSpeaking();
      return;
    }

    // Grab text from editor or output
    const rawEditor = document.getElementById("rawContentEditor");
    const textToSpeak = rawEditor ? rawEditor.value.trim() : "";

    if (!textToSpeak) {
      this.onToast("No generated content to read aloud. Generate content first!", "info");
      return;
    }

    // Strip Markdown symbols for clean, natural speech
    const cleanSpeechText = textToSpeak
      .replace(/#+/g, "")
      .replace(/\*+/g, "")
      .replace(/\[Ref \d+\]/g, "")
      .replace(/`+/g, "")
      .replace(/>/g, "")
      .replace(/---/g, "");

    this.speakText(cleanSpeechText);
  }

  speakText(text) {
    this.stopSpeaking();

    this.currentUtterance = new SpeechSynthesisUtterance(text);
    this.currentUtterance.rate = 1.0;
    this.currentUtterance.pitch = 1.0;

    // Pick best English voice
    if (this.voices && this.voices.length > 0) {
      const preferred = this.voices.find(v => v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Samantha")) || this.voices[0];
      this.currentUtterance.voice = preferred;
    }

    this.currentUtterance.onstart = () => {
      this.isSpeaking = true;
      if (this.btnReadAloud) {
        this.btnReadAloud.innerHTML = "<span>⏹️</span> <span>Stop Voice</span>";
        this.btnReadAloud.classList.add("speaking");
      }
      if (this.voiceWave) this.voiceWave.style.display = "inline-flex";
      this.onToast("🔊 Voice AI Narration playing...", "info");
    };

    this.currentUtterance.onend = () => {
      this.isSpeaking = false;
      this.resetReadAloudButton();
    };

    this.currentUtterance.onerror = (e) => {
      console.error("[Voice AI] Speech error:", e);
      this.isSpeaking = false;
      this.resetReadAloudButton();
    };

    this.synth.speak(this.currentUtterance);
  }

  stopSpeaking() {
    if (this.synth) {
      this.synth.cancel();
    }
    this.isSpeaking = false;
    this.resetReadAloudButton();
  }

  resetReadAloudButton() {
    if (this.btnReadAloud) {
      this.btnReadAloud.innerHTML = "<span>🔊</span> <span>Listen AI</span>";
      this.btnReadAloud.classList.remove("speaking");
    }
    if (this.voiceWave) this.voiceWave.style.display = "none";
  }
}
