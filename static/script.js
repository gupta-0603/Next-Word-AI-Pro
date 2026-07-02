/* ==========================================================================
   Next Word AI — frontend logic
   No framework, no build step: plain fetch() calls against the FastAPI
   backend. State (history, theme) lives in localStorage since there's no
   login system in this version.
   ========================================================================== */

const API = {
  predict: "/api/predict",
  generate: "/api/generate",
  spellcheck: "/api/spellcheck",
  synonyms: "/api/synonyms",
  summarize: "/api/summarize",
  sentiment: "/api/sentiment",
};

const el = {
  inputText: document.getElementById("inputText"),
  predictBtn: document.getElementById("predictBtn"),
  predictionsWrap: document.getElementById("predictionsWrap"),
  predictionKeys: document.getElementById("predictionKeys"),
  emptyState: document.getElementById("emptyState"),
  latencyBadge: document.getElementById("latencyBadge"),
  copyBtn: document.getElementById("copyBtn"),
  downloadBtn: document.getElementById("downloadBtn"),

  numWords: document.getElementById("numWords"),
  numWordsVal: document.getElementById("numWordsVal"),
  temperature: document.getElementById("temperature"),
  tempVal: document.getElementById("tempVal"),
  tempHint: document.getElementById("tempHint"),
  generateBtn: document.getElementById("generateBtn"),
  generateOutput: document.getElementById("generateOutput"),

  toolTabs: document.querySelectorAll(".tool-tab"),
  toolPanels: document.querySelectorAll(".tool-panel"),
  toolSourceBar: document.getElementById("toolSourceBar"),
  toolSourceText: document.getElementById("toolSourceText"),
  toolSourceEdit: document.getElementById("toolSourceEdit"),

  spellcheckBtn: document.getElementById("spellcheckBtn"),
  spellcheckResult: document.getElementById("spellcheckResult"),
  spellcheckText: document.getElementById("spellcheckText"),
  spellcheckCorrections: document.getElementById("spellcheckCorrections"),
  applyCorrectionsBtn: document.getElementById("applyCorrectionsBtn"),

  synonymWord: document.getElementById("synonymWord"),
  synonymBtn: document.getElementById("synonymBtn"),
  synonymResult: document.getElementById("synonymResult"),
  synonymChips: document.getElementById("synonymChips"),

  sentenceCount: document.getElementById("sentenceCount"),
  sentenceCountVal: document.getElementById("sentenceCountVal"),
  summarizeBtn: document.getElementById("summarizeBtn"),
  summarizeResult: document.getElementById("summarizeResult"),

  sentimentBtn: document.getElementById("sentimentBtn"),
  sentimentResult: document.getElementById("sentimentResult"),
  sentimentLabel: document.getElementById("sentimentLabel"),
  barPositive: document.getElementById("barPositive"),
  barNeutral: document.getElementById("barNeutral"),
  barNegative: document.getElementById("barNegative"),

  historyList: document.getElementById("historyList"),
  historyEmpty: document.getElementById("historyEmpty"),
  clearHistoryBtn: document.getElementById("clearHistoryBtn"),

  themeToggle: document.getElementById("themeToggle"),
  toastContainer: document.getElementById("toastContainer"),
};

// --------------------------------------------------------------------------
// Theme
// --------------------------------------------------------------------------
function initTheme() {
  const saved = localStorage.getItem("nwa-theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  document.body.setAttribute("data-theme", saved);
  el.themeToggle.querySelector(".theme-icon").textContent = saved === "dark" ? "☾" : "☀";
}

el.themeToggle.addEventListener("click", () => {
  const current = document.body.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  document.body.setAttribute("data-theme", next);
  localStorage.setItem("nwa-theme", next);
  el.themeToggle.querySelector(".theme-icon").textContent = next === "dark" ? "☾" : "☀";
});

// --------------------------------------------------------------------------
// Toasts
// --------------------------------------------------------------------------
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "error" : ""}`;
  toast.textContent = message;
  el.toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// --------------------------------------------------------------------------
// History (session-persisted via localStorage, no backend needed)
// --------------------------------------------------------------------------
const HISTORY_KEY = "nwa-history";
const MAX_HISTORY = 25;

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
  } catch {
    return [];
  }
}

function addToHistory(type, text) {
  const history = getHistory();
  history.unshift({ type, text, ts: Date.now() });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)));
  renderHistory();
}

function renderHistory() {
  const history = getHistory();
  el.historyList.innerHTML = "";
  el.historyEmpty.hidden = history.length > 0;

  history.forEach((item) => {
    const li = document.createElement("li");
    li.className = "history-item";
    const time = new Date(item.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    li.innerHTML = `<span class="h-type">${item.type}</span><span class="h-text">${escapeHtml(item.text)}</span> <span class="h-text">· ${time}</span>`;
    el.historyList.appendChild(li);
  });
}

el.clearHistoryBtn.addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
  showToast("History cleared");
});

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// --------------------------------------------------------------------------
// Prediction
// --------------------------------------------------------------------------
async function predictNextWord() {
  const text = el.inputText.value.trim();
  if (!text) {
    showToast("Type something first", "error");
    return;
  }

  el.predictBtn.classList.add("is-loading");
  el.predictBtn.disabled = true;

  try {
    const res = await fetch(API.predict, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, top_k: 5 }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }

    const data = await res.json();
    renderPredictions(data.predictions);
    el.latencyBadge.textContent = `${data.latency_ms} ms`;
    el.latencyBadge.hidden = false;

    if (data.predictions.length > 0) {
      addToHistory("predict", `"${text}" → ${data.predictions[0].word}`);
    }
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    el.predictBtn.classList.remove("is-loading");
    el.predictBtn.disabled = false;
  }
}

function renderPredictions(predictions) {
  el.predictionKeys.innerHTML = "";

  if (!predictions || predictions.length === 0) {
    el.predictionsWrap.hidden = true;
    el.emptyState.hidden = false;
    showToast("No predictions available for that input", "error");
    return;
  }

  el.emptyState.hidden = true;
  el.predictionsWrap.hidden = false;

  const maxConfidence = Math.max(...predictions.map((p) => p.confidence), 1);

  predictions.forEach((p) => {
    const btn = document.createElement("button");
    btn.className = "pred-key";
    btn.type = "button";
    btn.title = "Click to append this word";
    btn.innerHTML = `
      <span class="pred-key-fill"></span>
      <span class="pred-key-word">${escapeHtml(p.word)}</span>
      <span class="pred-key-conf">${p.confidence}%</span>
    `;
    btn.addEventListener("click", () => appendWord(p.word));
    el.predictionKeys.appendChild(btn);

    // Animate the fill in on next frame so the CSS transition triggers
    requestAnimationFrame(() => {
      btn.querySelector(".pred-key-fill").style.width = `${(p.confidence / maxConfidence) * 100}%`;
    });
  });
}

function appendWord(word) {
  const current = el.inputText.value;
  el.inputText.value = current.endsWith(" ") || current === "" ? current + word : current + " " + word;
  el.inputText.focus();
}

el.predictBtn.addEventListener("click", predictNextWord);

// Debounced autocomplete while typing
let debounceTimer = null;
el.inputText.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  const text = el.inputText.value.trim();
  if (text.split(/\s+/).length < 2) return; // wait for at least a couple words
  debounceTimer = setTimeout(predictNextWord, 600);
});

// --------------------------------------------------------------------------
// Copy / download
// --------------------------------------------------------------------------
el.copyBtn.addEventListener("click", async () => {
  const text = el.inputText.value;
  if (!text) {
    showToast("Nothing to copy yet", "error");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    showToast("Copied to clipboard");
  } catch {
    showToast("Couldn't copy — try selecting the text manually", "error");
  }
});

el.downloadBtn.addEventListener("click", () => {
  const text = el.inputText.value;
  if (!text) {
    showToast("Nothing to download yet", "error");
    return;
  }
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `next-word-ai-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Downloaded");
});

// --------------------------------------------------------------------------
// Generation
// --------------------------------------------------------------------------
const TEMP_HINTS = [
  { max: 0.05, label: "greedy" },
  { max: 0.6, label: "conservative" },
  { max: 1.1, label: "balanced" },
  { max: 1.6, label: "creative" },
  { max: 2.01, label: "wild" },
];

function updateTempHint(value) {
  const hint = TEMP_HINTS.find((t) => value <= t.max);
  el.tempHint.textContent = hint ? hint.label : "balanced";
}

el.numWords.addEventListener("input", () => {
  el.numWordsVal.textContent = el.numWords.value;
});

el.temperature.addEventListener("input", () => {
  const val = parseFloat(el.temperature.value);
  el.tempVal.textContent = val.toFixed(1);
  updateTempHint(val);
});

el.generateBtn.addEventListener("click", async () => {
  const text = el.inputText.value.trim();
  if (!text) {
    showToast("Type something to generate from", "error");
    return;
  }

  el.generateBtn.classList.add("is-loading");
  el.generateBtn.disabled = true;

  try {
    const res = await fetch(API.generate, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        num_words: parseInt(el.numWords.value, 10),
        temperature: parseFloat(el.temperature.value),
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }

    const data = await res.json();
    el.generateOutput.hidden = false;
    el.generateOutput.textContent = data.generated_text;
    addToHistory("generate", data.generated_text);
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    el.generateBtn.classList.remove("is-loading");
    el.generateBtn.disabled = false;
  }
});

// --------------------------------------------------------------------------
// Keyboard shortcuts
// --------------------------------------------------------------------------
document.addEventListener("keydown", (e) => {
  const isMod = e.ctrlKey || e.metaKey;
  if (isMod && e.key === "Enter") {
    e.preventDefault();
    predictNextWord();
  }
});

// --------------------------------------------------------------------------
// Text tools: source preview bar
// Keeps the "what am I analyzing" text visible even when the composer box
// (up top) has scrolled out of view — this is what was confusing before:
// clicking "Analyze sentiment" silently read an out-of-view, empty box.
// --------------------------------------------------------------------------
const TEXT_DEPENDENT_BUTTONS = [el.spellcheckBtn, el.summarizeBtn, el.sentimentBtn];

function updateToolSourceBar() {
  const text = el.inputText.value.trim();

  if (text) {
    el.toolSourceText.textContent = text.length > 100 ? text.slice(0, 100) + "…" : text;
    el.toolSourceText.classList.remove("is-empty");
  } else {
    el.toolSourceText.textContent = "Nothing yet — type in the box above";
    el.toolSourceText.classList.add("is-empty");
  }

  TEXT_DEPENDENT_BUTTONS.forEach((btn) => { btn.disabled = !text; });
}

el.inputText.addEventListener("input", updateToolSourceBar);

el.toolSourceEdit.addEventListener("click", () => {
  el.inputText.scrollIntoView({ behavior: "smooth", block: "center" });
  el.inputText.focus();
});

// --------------------------------------------------------------------------
// Text tools: tab switching
// --------------------------------------------------------------------------
el.toolTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    el.toolTabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const target = tab.dataset.tool;
    el.toolPanels.forEach((panel) => {
      panel.hidden = panel.id !== `panel-${target}`;
    });
    // Synonyms uses its own dedicated word input, not the shared composer —
    // showing "Analyzing: <composer text>" there would be misleading.
    el.toolSourceBar.classList.toggle("is-hidden", target === "synonyms");
  });
});

// Shared helper: POST json, handle loading state + errors consistently
async function postJson(url, body, btn) {
  btn.classList.add("is-loading");
  btn.disabled = true;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }
    return await res.json();
  } finally {
    btn.classList.remove("is-loading");
    btn.disabled = false;
  }
}

// --------------------------------------------------------------------------
// Spell check
// --------------------------------------------------------------------------
el.spellcheckBtn.addEventListener("click", async () => {
  const text = el.inputText.value.trim();
  if (!text) {
    showToast("Type something first", "error");
    el.toolSourceEdit.click();
    return;
  }

  try {
    const data = await postJson(API.spellcheck, { text }, el.spellcheckBtn);
    el.spellcheckText.textContent = data.corrected_text;
    el.spellcheckCorrections.innerHTML = "";

    if (data.corrections.length === 0) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = "No spelling issues found";
      el.spellcheckCorrections.appendChild(chip);
    } else {
      data.corrections.forEach((c) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.innerHTML = `<span class="chip-old">${escapeHtml(c.original)}</span>${escapeHtml(c.corrected)}`;
        el.spellcheckCorrections.appendChild(chip);
      });
    }

    el.spellcheckResult.hidden = false;
    addToHistory("spellcheck", `${data.corrections.length} correction(s)`);
  } catch (e) {
    showToast(e.message, "error");
  }
});

el.applyCorrectionsBtn.addEventListener("click", () => {
  el.inputText.value = el.spellcheckText.textContent;
  showToast("Applied corrections to text box");
});

// --------------------------------------------------------------------------
// Synonyms
// --------------------------------------------------------------------------
el.synonymBtn.addEventListener("click", async () => {
  const word = el.synonymWord.value.trim();
  if (!word) return showToast("Enter a word first", "error");

  try {
    const data = await postJson(API.synonyms, { word }, el.synonymBtn);
    el.synonymChips.innerHTML = "";

    if (data.synonyms.length === 0) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = "No synonyms found";
      el.synonymChips.appendChild(chip);
    } else {
      data.synonyms.forEach((syn) => {
        const chip = document.createElement("span");
        chip.className = "chip clickable";
        chip.textContent = syn;
        chip.title = "Click to insert into text box";
        chip.addEventListener("click", () => appendWord(syn));
        el.synonymChips.appendChild(chip);
      });
    }

    el.synonymResult.hidden = false;
    addToHistory("synonyms", `"${word}" → ${data.synonyms.length} found`);
  } catch (e) {
    showToast(e.message, "error");
  }
});

// --------------------------------------------------------------------------
// Summarize
// --------------------------------------------------------------------------
el.sentenceCount.addEventListener("input", () => {
  el.sentenceCountVal.textContent = el.sentenceCount.value;
});

el.summarizeBtn.addEventListener("click", async () => {
  const text = el.inputText.value.trim();
  if (!text) {
    showToast("Type something first", "error");
    el.toolSourceEdit.click();
    return;
  }

  try {
    const data = await postJson(
      API.summarize,
      { text, sentence_count: parseInt(el.sentenceCount.value, 10) },
      el.summarizeBtn
    );
    el.summarizeResult.hidden = false;
    el.summarizeResult.textContent = data.summary;
    addToHistory("summarize", data.summary);
  } catch (e) {
    showToast(e.message, "error");
  }
});

// --------------------------------------------------------------------------
// Sentiment
// --------------------------------------------------------------------------
el.sentimentBtn.addEventListener("click", async () => {
  const text = el.inputText.value.trim();
  if (!text) {
    showToast("Type something first", "error");
    el.toolSourceEdit.click();
    return;
  }

  try {
    const data = await postJson(API.sentiment, { text }, el.sentimentBtn);
    el.sentimentLabel.textContent = `${data.label} (${data.compound.toFixed(2)})`;
    el.barPositive.style.width = `${data.positive * 100}%`;
    el.barNeutral.style.width = `${data.neutral * 100}%`;
    el.barNegative.style.width = `${data.negative * 100}%`;
    el.sentimentResult.hidden = false;
    addToHistory("sentiment", data.label);
  } catch (e) {
    showToast(e.message, "error");
  }
});

// --------------------------------------------------------------------------
// Init
// --------------------------------------------------------------------------
initTheme();
renderHistory();
updateToolSourceBar();
