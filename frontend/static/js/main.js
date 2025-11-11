document.addEventListener("DOMContentLoaded", () => {
  const sourceLangSelect = document.getElementById("sourceLang");
  const targetLangSelect = document.getElementById("targetLang");
  const inputText = document.getElementById("inputText");
  const outputText = document.getElementById("outputText");
  const translateBtn = document.getElementById("translateBtn");
  const statusDiv = document.getElementById("status");

  // Supported language codes with downloaded models
  const supportedLanguages = new Set([
    "en", "es", "de", "it", "nl", "ru", "zh", "ar",
    "fr", "hi", "tl", "mr", "guj", "pnb", "ml", "ori", "asm"
    // Excluding ja, ko, ben, tam due to missing models
  ]);

  // Fetch supported languages from backend and populate dropdowns
  fetch("/api/languages")
    .then((res) => res.json())
    .then((langs) => {
      for (const [code, name] of Object.entries(langs)) {
        if (!supportedLanguages.has(code)) {
          continue; // Skip unsupported languages
        }

        const option1 = document.createElement("option");
        option1.value = code;
        option1.textContent = name;
        sourceLangSelect.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = code;
        option2.textContent = name;
        targetLangSelect.appendChild(option2);
      }
      // Set defaults
      sourceLangSelect.value = "en";
      targetLangSelect.value = "hi";
    })
    .catch(() => {
      statusDiv.textContent = "Failed to load language list.";
    });

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
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((result) => {
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
});
