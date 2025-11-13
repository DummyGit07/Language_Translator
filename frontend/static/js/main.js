document.addEventListener("DOMContentLoaded", () => {
  const sourceLangSelect = document.getElementById("sourceLang");
  const targetLangSelect = document.getElementById("targetLang");
  const inputText = document.getElementById("inputText");
  const outputText = document.getElementById("outputText");
  const translateBtn = document.getElementById("translateBtn");
  const statusDiv = document.getElementById("status");

  // Audio buttons for speak-to-text and speak input/output
  const recordBtn = document.getElementById("recordBtn");
  const recordingStatus = document.getElementById("recordingStatus");
  const speakInputBtn = document.getElementById("speakInputBtn");
  const speakOutputBtn = document.getElementById("speakOutputBtn");

  // Supported languages (downloaded models)
  const supportedLanguages = new Set([
    "en", "es", "de", "it", "nl", "ru", "zh", "ar",
    "fr", "hi", "tl", "mr", "guj", "pnb", "ml", "ori", "asm"
  ]);

  // State variables for utterances and mediaRecorder
  let inputUtterance = null;
  let outputUtterance = null;
  let mediaRecorder = null;
  let audioChunks = [];

  // Helper function to cancel all ongoing audio (speech & recording)
  function cancelAllAudioProcesses() {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      recordBtn.textContent = "Start Recording";
      recordingStatus.textContent = "";
    }
    resetSpeakButtons();
  }

  // Reset Speak buttons to initial state
  function resetSpeakButtons() {
    if (speakInputBtn) speakInputBtn.textContent = "Start Speaking";
    if (speakOutputBtn) speakOutputBtn.textContent = "Start Speaking";
  }

  // Centralized error popup and cancellation
  function showErrorPopup(message) {
    cancelAllAudioProcesses();
    alert(message);
  }

  // Populate language dropdowns
  fetch("/api/languages")
    .then(res => res.json())
    .then(langs => {
      for (const [code, name] of Object.entries(langs)) {
        if (!supportedLanguages.has(code)) continue;
        const optionSrc = document.createElement("option");
        optionSrc.value = code;
        optionSrc.textContent = name;
        sourceLangSelect.appendChild(optionSrc);

        const optionTgt = document.createElement("option");
        optionTgt.value = code;
        optionTgt.textContent = name;
        targetLangSelect.appendChild(optionTgt);
      }
      sourceLangSelect.value = "en";
      targetLangSelect.value = "hi";
    })
    .catch(() => showErrorPopup("Failed to load language list."));

  // Auto-detect language of input on input change (debounced)
  let detectTimeout;
  inputText.addEventListener("input", () => {
    clearTimeout(detectTimeout);
    detectTimeout = setTimeout(() => {
      const text = inputText.value.trim();
      if (!text) return;
      fetch("/api/detect-lang", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      })
        .then(res => res.json())
        .then(data => {
          if (data.lang && supportedLanguages.has(data.lang)) {
            sourceLangSelect.value = data.lang;
          }
        });
    }, 800);
  });

  // Translate button logic
  translateBtn.addEventListener("click", () => {
    statusDiv.textContent = "Translating...";
    outputText.value = "";

    const data = {
      text: inputText.value.trim(),
      source_lang: sourceLangSelect.value,
      target_lang: targetLangSelect.value,
    };

    if (!data.text) {
      showErrorPopup("Please enter text to translate.");
      statusDiv.textContent = "";
      return;
    }

    fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then(res => res.json())
      .then(result => {
        if (result.error) {
          showErrorPopup("Error: " + result.error);
          statusDiv.textContent = "";
        } else {
          outputText.value = result.translated_text || "";
          statusDiv.textContent = "Translation completed.";
        }
      })
      .catch(() => {
        showErrorPopup("Translation request failed.");
        statusDiv.textContent = "";
      });
  });

  // Speech-to-text: record audio, convert to text only, put in input box
  if (recordBtn) {
    recordBtn.addEventListener("click", () => {
      // Prevent recording if currently speaking
      if (window.speechSynthesis.speaking) {
        showErrorPopup("Speaking Stopped!!.");
        return;
      }
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.textContent = "Start Recording";
        recordingStatus.textContent = "Recording stopped.";
      } else {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            recordBtn.textContent = "Stop Recording";
            recordingStatus.textContent = "Recording...";

            audioChunks = [];
            mediaRecorder.addEventListener("dataavailable", e => audioChunks.push(e.data));

            mediaRecorder.addEventListener("stop", () => {
              const audioBlob = new Blob(audioChunks);
              const formData = new FormData();
              formData.append("audio", audioBlob, "recording.wav");

              recordingStatus.textContent = "Recognizing speech...";

              fetch("/api/stt", {
                method: "POST",
                body: formData,
              })
                .then(res => res.json())
                .then(data => {
                  if (data.error) {
                    showErrorPopup("Error: Permission Conflicted.");
                    recordingStatus.textContent = "";
                  } else {
                    inputText.value = data.text || "";
                    recordingStatus.textContent = "Speech recognized.";
                  }
                })
                .catch(() => {
                  showErrorPopup("Failed to get transcription.");
                  recordingStatus.textContent = "";
                });
            });
          })
          .catch(() => {
            showErrorPopup("Microphone permission denied.");
            recordingStatus.textContent = "";
          });
      }
    });
  }

  // Toggleable Speak/Stop for input text
  if (speakInputBtn) {
    speakInputBtn.addEventListener("click", () => {
      // If currently recording, prevent speaking
      if (mediaRecorder && mediaRecorder.state === "recording") {
        showErrorPopup("Please stop recording before speaking.");
        return;
      }
      // If already speaking (input or output), cancel all to avoid overlap
      if (window.speechSynthesis.speaking) {
        cancelAllAudioProcesses();
        resetSpeakButtons();
        return;
      }
      const text = inputText.value.trim();
      if (!text) return;
      inputUtterance = new SpeechSynthesisUtterance(text);
      inputUtterance.lang = sourceLangSelect.value;
      speakInputBtn.textContent = "Stop Speaking";

      inputUtterance.onend = () => {
        speakInputBtn.textContent = "Start Speaking";
      };
      inputUtterance.onerror = (e) => {
        // showErrorPopup("Speech synthesis error: " + e.error);
      };

      window.speechSynthesis.speak(inputUtterance);
    });
  }

  // Toggleable Speak/Stop for output text
  if (speakOutputBtn) {
    speakOutputBtn.addEventListener("click", () => {
      // If currently recording, prevent speaking
      if (mediaRecorder && mediaRecorder.state === "recording") {
        showErrorPopup("Please stop recording before speaking.");
        return;
      }
      // If already speaking (input or output), cancel all to avoid overlap
      if (window.speechSynthesis.speaking) {
        cancelAllAudioProcesses();
        resetSpeakButtons();
        return;
      }
      const text = outputText.value.trim();
      if (!text) return;
      outputUtterance = new SpeechSynthesisUtterance(text);
      outputUtterance.lang = targetLangSelect.value;
      speakOutputBtn.textContent = "Stop Speaking";

      outputUtterance.onend = () => {
        speakOutputBtn.textContent = "Start Speaking";
      };
      outputUtterance.onerror = (e) => {
        // showErrorPopup("Speech synthesis error: " + e.error);
      };

      window.speechSynthesis.speak(outputUtterance);
    });
  }
});
