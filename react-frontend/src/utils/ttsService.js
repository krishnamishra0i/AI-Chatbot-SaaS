/**
 * TTS Service - Text-to-Speech using Web Speech API
 * Browser-based, no API key required
 */

class TTSService {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.isSpeaking = false;
    this.currentUtterance = null;
  }

  /**
   * Speak text aloud using Web Speech API
   * @param {string} text - Text to speak
   * @param {object} options - Voice options (voice, pitch, rate, volume)
   * @returns {Promise} Resolves when speech finishes
   */
  speak(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech Synthesis not supported in this browser'));
        return;
      }

      // Cancel any existing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);

      // Set voice
      if (options.voice) {
        const voices = this.synthesis.getVoices();
        const selectedVoice = voices.find((v) => v.name.includes(options.voice));
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
      }

      // Set voice characteristics
      utterance.pitch = options.pitch || 1;
      utterance.rate = options.rate || 1;
      utterance.volume = options.volume || 1;

      utterance.onend = () => {
        this.isSpeaking = false;
        resolve();
      };

      utterance.onerror = (event) => {
        this.isSpeaking = false;
        reject(new Error(`Speech error: ${event.error}`));
      };

      this.isSpeaking = true;
      this.currentUtterance = utterance;
      this.synthesis.speak(utterance);
    });
  }

  /**
   * Stop current speech
   */
  stop() {
    if (this.synthesis) {
      this.synthesis.cancel();
      this.isSpeaking = false;
    }
  }

  /**
   * Get available voices
   * @returns {Array} List of available voices
   */
  getVoices() {
    return this.synthesis ? this.synthesis.getVoices() : [];
  }

  /**
   * Check if speech is currently playing
   * @returns {boolean}
   */
  isSpeakingNow() {
    return this.isSpeaking;
  }

  /**
   * Speak with male voice (default)
   */
  speakAsMale(text) {
    return this.speak(text, { voice: 'Male', pitch: 0.8, rate: 1 });
  }

  /**
   * Speak with female voice
   */
  speakAsFemale(text) {
    return this.speak(text, { voice: 'Female', pitch: 1.2, rate: 1 });
  }
}

// Export singleton instance
export const ttsService = new TTSService();
