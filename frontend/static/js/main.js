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
    .catch(() => {
      statusDiv.textContent = "Failed to load language list.";
    });

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
      statusDiv.textContent = "Please enter text to translate.";
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
          statusDiv.textContent = "Error: " + result.error;
        } else {
          outputText.value = result.translated_text || "";
          statusDiv.textContent = "Translation completed.";
        }
      })
      .catch(() => {
        statusDiv.textContent = "Translation request failed.";
      });
  });

  // Speech-to-text: record audio, convert to text only, put in input box
  let mediaRecorder;
  let audioChunks = [];

  if (recordBtn) {
    recordBtn.addEventListener("click", () => {
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
                    recordingStatus.textContent = "Error: " + data.error;
                  } else {
                    inputText.value = data.text || "";
                    recordingStatus.textContent = "Speech recognized.";
                  }
                })
                .catch(() => {
                  recordingStatus.textContent = "Failed to get transcription.";
                });
            });
          })
          .catch(() => {
            recordingStatus.textContent = "Microphone permission denied.";
          });
      }
    });
  }

  // Speak button for input text using browser TTS
  if (speakInputBtn) {
    speakInputBtn.addEventListener("click", () => {
      const text = inputText.value.trim();
      if (!text) return;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = sourceLangSelect.value;
      window.speechSynthesis.speak(utterance);
    });
  }

  // Speak button for output text (translated) using browser TTS
  if (speakOutputBtn) {
    speakOutputBtn.addEventListener("click", () => {
      const text = outputText.value.trim();
      if (!text) return;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = targetLangSelect.value;
      window.speechSynthesis.speak(utterance);
    });
  }
});
