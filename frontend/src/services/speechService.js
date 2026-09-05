// Web Speech API + Backend Authentic TTS Audio Service

const LANG_CODES = {
  hi: "hi-IN",
  gu: "gu-IN",
  en: "en-IN",
};

export class SpeechService {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
    this.synth = window.speechSynthesis || null;
    this.isListening = false;
    this.currentLanguage = "hi";
    this.activeAudio = null; // Track playing HTML5 Audio element

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

  speak(text, lang = "hi", onEnd) {
    if (!text) return;

    // 1. Instantly silence and cancel any ongoing speech or audio
    this.stopSpeaking();

    // 2. For Gujarati (gu), standard Windows PCs lack an offline Gujarati voice pack.
    // Use our high-fidelity backend Google TTS audio stream for 100% authentic Gujarati voice.
    if (lang === "gu") {
      this.playBackendAudio(text, "gu", onEnd);
      return;
    }

    // 3. For Hindi & English, check if browser has native speech synthesis
    if (this.synth) {
      const targetLangCode = LANG_CODES[lang] || "hi-IN";
      const voices = this.synth.getVoices();
      const hasMatchingVoice = voices.some((v) => v.lang === targetLangCode || v.lang.startsWith(lang));

      if (hasMatchingVoice) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = targetLangCode;
        utterance.rate = 0.95;
        utterance.pitch = 1.0;

        const voice = voices.find((v) => v.lang === targetLangCode || v.lang.startsWith(lang));
        if (voice) utterance.voice = voice;

        utterance.onend = () => {
          if (onEnd) onEnd();
        };
        utterance.onerror = () => {
          if (onEnd) onEnd();
        };

        this.synth.speak(utterance);
        return;
      }
    }

    // 4. Fallback to backend audio stream if browser has no appropriate voice
    this.playBackendAudio(text, lang, onEnd);
  }

  playBackendAudio(text, lang, onEnd) {
    try {
      const audioUrl = `http://127.0.0.1:8000/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
      const audio = new Audio(audioUrl);
      this.activeAudio = audio;

      audio.onended = () => {
        this.activeAudio = null;
        if (onEnd) onEnd();
      };

      audio.onerror = (e) => {
        this.activeAudio = null;
        if (onEnd) onEnd();
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn("Autoplay blocked or audio interrupted:", err);
          // Auto-resume on first user click if browser autoplay policy blocked initial load
          if (err.name === "NotAllowedError") {
            const resumeOnInteraction = () => {
              const retryAudio = new Audio(audioUrl);
              this.activeAudio = retryAudio;
              retryAudio.play().catch(() => {});
            };
            window.addEventListener("click", resumeOnInteraction, { once: true });
            window.addEventListener("touchstart", resumeOnInteraction, { once: true });
          }
          this.activeAudio = null;
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
