// Web Speech API + High-Fidelity Backend Authentic TTS Audio Service

const LANG_CODES = {
  hi: "hi-IN",
  gu: "gu-IN",
  en: "en-IN",
};

export class SpeechService {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
    this.synth = typeof window !== "undefined" ? window.speechSynthesis : null;
    this.isListening = false;
    this.currentLanguage = "hi";
    this.activeAudio = null; // Track playing HTML5 Audio element
    this.voices = [];
    this.prefetchedUrls = new Set();

    if (this.synth) {
      const loadVoices = () => {
        try {
          this.voices = this.synth.getVoices() || [];
        } catch (e) {
          this.voices = [];
        }
      };
      loadVoices();
      if (this.synth.onvoiceschanged !== undefined) {
        this.synth.onvoiceschanged = loadVoices;
      }
    }

    if (this.recognition) {
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 1;
    }
  }

  isSupported() {
    return {
      stt: !!this.recognition,
      tts: !!this.synth || true,
    };
  }

  startListening(lang = "hi", onResult, onError, onEnd) {
    // Stop any ongoing speech playback before listening
    this.stopSpeaking();

    if (!this.recognition) {
      if (onError) onError("Speech recognition not supported in this browser. Please use Chrome/Edge or type your message.");
      return;
    }

    try {
      this.currentLanguage = lang;
      this.recognition.lang = LANG_CODES[lang] || "hi-IN";
      this.isListening = true;

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (onResult) onResult(transcript);
      };

      this.recognition.onerror = (event) => {
        this.isListening = false;
        if (onError) onError(event.error);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        if (onEnd) onEnd();
      };

      this.recognition.start();
    } catch (err) {
      this.isListening = false;
      if (onError) onError(err.message);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  // Prefetch audio in background to make subsequent speak() instantaneous
  prefetch(text, lang = "gu") {
    if (!text) return;
    try {
      const audioUrl = `http://127.0.0.1:8000/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
      if (this.prefetchedUrls.has(audioUrl)) return;
      this.prefetchedUrls.add(audioUrl);

      const preloader = new Audio();
      preloader.preload = "auto";
      preloader.src = audioUrl;
    } catch (e) {
      // Non-critical prefetch error
    }
  }

  speak(text, lang = "hi", onEnd) {
    if (!text) {
      if (onEnd) onEnd();
      return;
    }

    // 1. Instantly silence and cancel any ongoing speech or audio
    this.stopSpeaking();

    // 2. Check if browser has native voice available (instant zero-network playback)
    if (this.synth) {
      const targetLangCode = LANG_CODES[lang] || "hi-IN";
      const voices = this.voices.length > 0 ? this.voices : (this.synth.getVoices() || []);
      const matchedVoice = voices.find(
        (v) =>
          v.lang === targetLangCode ||
          v.lang.toLowerCase().startsWith(lang) ||
          (v.name && v.name.toLowerCase().includes(lang === "gu" ? "gujarat" : lang === "hi" ? "hindi" : "english"))
      );

      // If authentic native voice exists in the browser, synthesize directly
      if (matchedVoice) {
        try {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.voice = matchedVoice;
          utterance.lang = targetLangCode;
          // Speed adjustment: Gujarati at 1.12x for energetic, fluent natural rhythm
          utterance.rate = lang === "gu" ? 1.12 : (lang === "hi" ? 1.05 : 1.0);
          utterance.pitch = 1.0;

          utterance.onend = () => { if (onEnd) onEnd(); };
          utterance.onerror = () => { if (onEnd) onEnd(); };

          this.synth.speak(utterance);
          return;
        } catch (synthErr) {
          console.warn("Browser synth failed, falling back to backend audio:", synthErr);
        }
      }
    }

    // 3. High-fidelity backend Google TTS audio stream with server caching & speed boost
    this.playBackendAudio(text, lang, onEnd);
  }

  playBackendAudio(text, lang, onEnd) {
    try {
      const audioUrl = `http://127.0.0.1:8000/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
      const audio = new Audio();
      this.activeAudio = audio;

      // Speed adjustment: Gujarati at 1.15x gives natural, brisk, and engaging conversational pace
      const speedRate = lang === "gu" ? 1.15 : (lang === "hi" ? 1.05 : 1.0);
      audio.defaultPlaybackRate = speedRate;
      audio.playbackRate = speedRate;
      audio.preload = "auto";
      audio.src = audioUrl;

      // Enforce speed rate across audio load lifecycle
      const applySpeed = () => {
        if (this.activeAudio === audio) {
          audio.playbackRate = speedRate;
        }
      };

      audio.onloadedmetadata = applySpeed;
      audio.oncanplay = applySpeed;
      audio.onplay = applySpeed;

      audio.onended = () => {
        if (this.activeAudio === audio) {
          this.activeAudio = null;
        }
        if (onEnd) onEnd();
      };

      audio.onerror = (e) => {
        console.warn("Backend TTS audio error, trying browser synth fallback:", e);
        if (this.activeAudio === audio) {
          this.activeAudio = null;
        }
        if (this.synth) {
          try {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = LANG_CODES[lang] || "gu-IN";
            utterance.rate = lang === "gu" ? 1.12 : 1.05;
            utterance.onend = () => { if (onEnd) onEnd(); };
            utterance.onerror = () => { if (onEnd) onEnd(); };
            this.synth.speak(utterance);
            return;
          } catch (synthErr) {
            console.error("Browser synth fallback failed:", synthErr);
          }
        }
        if (onEnd) onEnd();
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            applySpeed();
          })
          .catch((err) => {
            console.warn("Autoplay blocked or audio interrupted:", err);
            // Auto-resume on first user click if browser autoplay policy blocked initial load
            if (err.name === "NotAllowedError") {
              const resumeOnInteraction = () => {
                const retryAudio = new Audio(audioUrl);
                this.activeAudio = retryAudio;
                retryAudio.defaultPlaybackRate = speedRate;
                retryAudio.playbackRate = speedRate;
                retryAudio.play().catch(() => {});
              };
              window.addEventListener("click", resumeOnInteraction, { once: true });
              window.addEventListener("touchstart", resumeOnInteraction, { once: true });
            }
            if (this.activeAudio === audio) {
              this.activeAudio = null;
            }
            if (onEnd) onEnd();
          });
      }
    } catch (err) {
      console.error("Audio error:", err);
      if (onEnd) onEnd();
    }
  }

  stopSpeaking() {
    // Stop browser Web Speech Synthesis
    if (this.synth) {
      try {
        this.synth.cancel();
      } catch (e) {}
    }

    // Stop and reset HTML5 audio element
    if (this.activeAudio) {
      try {
        this.activeAudio.pause();
        this.activeAudio.currentTime = 0;
      } catch (e) {}
      this.activeAudio = null;
    }
  }
}

export const speechService = new SpeechService();
