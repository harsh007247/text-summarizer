/**
 * Text Summarizer - Frontend Client Script
 * Handles live counters, presets, slider controls, API communication, and metrics display.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const inputText = document.getElementById('inputText');
  const inputWordCount = document.getElementById('inputWordCount');
  const inputCharCount = document.getElementById('inputCharCount');
  const sampleBtn = document.getElementById('sampleBtn');
  const pasteBtn = document.getElementById('pasteBtn');
  const clearBtn = document.getElementById('clearBtn');

  // Sliders & Presets
  const maxLengthSlider = document.getElementById('maxLengthSlider');
  const minLengthSlider = document.getElementById('minLengthSlider');
  const maxLengthVal = document.getElementById('maxLengthVal');
  const minLengthVal = document.getElementById('minLengthVal');
  const presetBtns = document.querySelectorAll('.preset-btn');

  // Action Buttons
  const summarizeBtn = document.getElementById('summarizeBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const copyBtn = document.getElementById('copyBtn');
  const copyText = document.getElementById('copyText');
  const resetBtn = document.getElementById('resetBtn');
  const outputActions = document.getElementById('outputActions');

  // State Views
  const emptyState = document.getElementById('emptyState');
  const loadingState = document.getElementById('loadingState');
  const resultContent = document.getElementById('resultContent');
  const summaryText = document.getElementById('summaryText');
  const errorAlert = document.getElementById('errorAlert');
  const errorAlertTitle = document.getElementById('errorAlertTitle');
  const errorAlertMessage = document.getElementById('errorAlertMessage');

  // Metrics
  const metricInputWords = document.getElementById('metricInputWords');
  const metricInputTokens = document.getElementById('metricInputTokens');
  const metricSummaryWords = document.getElementById('metricSummaryWords');
  const metricSummaryTokens = document.getElementById('metricSummaryTokens');
  const metricReduction = document.getElementById('metricReduction');
  const metricLatency = document.getElementById('metricLatency');

  // Badges
  const modelStatusBadge = document.getElementById('modelStatusBadge');
  const modelStatusText = document.getElementById('modelStatusText');
  const deviceBadge = document.getElementById('deviceBadge');

  // Preset Configurations (mapped to PEGASUS generation tokens)
  const PRESETS = {
    concise: { max: 60, min: 15 },
    balanced: { max: 128, min: 25 },
    detailed: { max: 200, min: 60 },
  };

  // Curated Sample Texts (dialogues matching fine-tuning dataset)
  const SAMPLE_TEXTS = [
    `Hannah: Hey, are you free for lunch today?\nAmanda: Sure! What are you craving?\nHannah: Maybe sushi at Sakura around 12:30?\nAmanda: Sounds perfect, see you there at 12:30!`,
    `Alex: Did everyone review the quarterly financial report?\nSarah: Yes, revenue increased by 14% compared to Q2, driven mainly by enterprise cloud subscriptions.\nDavid: Operational costs also decreased slightly due to server migrations.\nAlex: Excellent work team. Let's prepare the executive summary slides for tomorrow morning's board meeting.`,
    `Dr. Miller: The patient presented with mild headaches and fatigue lasting four days.\nNurse Kelly: Blood pressure was 120/80 and temperature was normal at 98.6°F.\nDr. Miller: Laboratory blood panels showed no signs of infection or electrolyte imbalance. Recommended rest, increased hydration, and scheduled a follow-up in two weeks.`
  ];
  let sampleIndex = 0;

  // 1. Text Input Counter Updates
  function updateCounters() {
    const text = inputText.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const chars = inputText.value.length;

    inputWordCount.textContent = words.toLocaleString();
    inputCharCount.textContent = chars.toLocaleString();
  }

  inputText.addEventListener('input', updateCounters);

  // 2. Sample Text Button
  sampleBtn.addEventListener('click', () => {
    inputText.value = SAMPLE_TEXTS[sampleIndex];
    sampleIndex = (sampleIndex + 1) % SAMPLE_TEXTS.length;
    updateCounters();
    inputText.focus();
    showToast('Loaded sample text', 'info');
  });

  // 3. Paste Button
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        inputText.value = text;
        updateCounters();
        showToast('Pasted text from clipboard', 'info');
      }
    } catch (err) {
      showToast('Clipboard access was blocked by browser', 'error');
    }
  });

  // 4. Clear Button
  clearBtn.addEventListener('click', () => {
    inputText.value = '';
    updateCounters();
    inputText.focus();
  });

  // 5. Sliders and Presets Interaction
  function updateSliderDisplay() {
    maxLengthVal.textContent = `${maxLengthSlider.value} tokens`;
    minLengthVal.textContent = `${minLengthSlider.value} tokens`;
  }

  function syncPresetButton(activeName) {
    presetBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.preset === activeName);
    });
  }

  // Handle Preset Clicks
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const presetKey = btn.dataset.preset;
      syncPresetButton(presetKey);

      if (PRESETS[presetKey]) {
        maxLengthSlider.value = PRESETS[presetKey].max;
        minLengthSlider.value = PRESETS[presetKey].min;
        updateSliderDisplay();
      }
    });
  });

  // Handle Slider Movement
  maxLengthSlider.addEventListener('input', () => {
    const maxVal = parseInt(maxLengthSlider.value, 10);
    const minVal = parseInt(minLengthSlider.value, 10);

    // Keep min_length <= max_length
    if (minVal > maxVal) {
      minLengthSlider.value = Math.max(10, maxVal - 10);
    }

    updateSliderDisplay();
    syncPresetButton('custom');
  });

  minLengthSlider.addEventListener('input', () => {
    const maxVal = parseInt(maxLengthSlider.value, 10);
    const minVal = parseInt(minLengthSlider.value, 10);

    // Keep min_length <= max_length
    if (minVal > maxVal) {
      maxLengthSlider.value = Math.min(256, minVal + 10);
    }

    updateSliderDisplay();
    syncPresetButton('custom');
  });

  // 6. Keyboard Shortcut: Ctrl + Enter
  inputText.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      summarizeBtn.click();
    }
  });

  // 7. Health Check
  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      if (!res.ok) throw new Error('Health check failed');
      const data = await res.json();

      if (data.model_loaded) {
        modelStatusBadge.className = 'status-badge status-ready';
        modelStatusText.textContent = 'PEGASUS Ready';
      } else {
        modelStatusBadge.className = 'status-badge status-loading';
        modelStatusText.textContent = 'Model Initializing';
      }
      deviceBadge.textContent = (data.device || 'CPU').toUpperCase();
    } catch (err) {
      modelStatusBadge.className = 'status-badge status-error';
      modelStatusText.textContent = 'Model Offline';
    }
  }

  checkHealth();

  // 8. Summarize Request
  summarizeBtn.addEventListener('click', async () => {
    const text = inputText.value.trim();

    // Validation
    if (!text) {
      showError('Input Required', 'Please enter or paste some text before generating a summary.');
      inputText.focus();
      return;
    }

    const maxLength = parseInt(maxLengthSlider.value, 10);
    const minLength = parseInt(minLengthSlider.value, 10);

    if (minLength > maxLength) {
      showError('Invalid Settings', 'Minimum length cannot exceed maximum length.');
      return;
    }

    // Set UI to loading state
    setLoading(true);
    hideError();

    try {
      const payload = {
        text: text,
        max_length: maxLength,
        min_length: minLength,
        num_beams: 8,
        length_penalty: 0.8
      };

      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        let errDetail = 'Failed to generate summary.';
        try {
          const errData = await response.json();
          errDetail = errData.detail || errDetail;
        } catch (_) {}
        throw new Error(errDetail);
      }

      const data = await response.json();
      displayResult(data);
      showToast('Summary generated successfully', 'success');

    } catch (err) {
      showError('Generation Failed', err.message || 'An error occurred during inference.');
    } finally {
      setLoading(false);
    }
  });

  // Set Loading UI State
  function setLoading(isLoading) {
    summarizeBtn.disabled = isLoading;
    summarizeBtn.classList.toggle('loading', isLoading);

    if (isLoading) {
      btnText.textContent = 'Generating...';
      emptyState.style.display = 'none';
      resultContent.style.display = 'none';
      loadingState.style.display = 'flex';
      outputActions.style.display = 'none';
    } else {
      btnText.textContent = 'Generate Summary';
      loadingState.style.display = 'none';
    }
  }

  // Display Generated Result & Metrics
  function displayResult(data) {
    summaryText.textContent = data.summary;

    metricInputWords.innerHTML = `${data.input_words} <small>words</small>`;
    metricInputTokens.textContent = `${data.input_tokens} tokens`;

    metricSummaryWords.innerHTML = `${data.summary_words} <small>words</small>`;
    metricSummaryTokens.textContent = `${data.summary_tokens} tokens`;

    metricReduction.textContent = `${data.reduction_percentage}%`;
    metricLatency.textContent = `${data.inference_time_seconds}s`;

    emptyState.style.display = 'none';
    loadingState.style.display = 'none';
    resultContent.style.display = 'flex';
    outputActions.style.display = 'flex';
  }

  // Error Alert Display
  function showError(title, message) {
    errorAlertTitle.textContent = title;
    errorAlertMessage.textContent = message;
    errorAlert.style.display = 'flex';
  }

  function hideError() {
    errorAlert.style.display = 'none';
  }

  // 9. Copy Summary to Clipboard
  copyBtn.addEventListener('click', async () => {
    const textToCopy = summaryText.textContent.trim();
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);
      copyText.textContent = 'Copied!';
      copyBtn.classList.add('btn-primary');
      copyBtn.classList.remove('btn-secondary');

      showToast('Summary copied to clipboard', 'success');

      setTimeout(() => {
        copyText.textContent = 'Copy Summary';
        copyBtn.classList.remove('btn-primary');
        copyBtn.classList.add('btn-secondary');
      }, 2000);
    } catch (err) {
      showToast('Could not copy to clipboard', 'error');
    }
  });

  // 10. Reset Summary Output
  resetBtn.addEventListener('click', () => {
    resultContent.style.display = 'none';
    outputActions.style.display = 'none';
    emptyState.style.display = 'flex';
    summaryText.textContent = '';
    hideError();
  });

  // Toast System
  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  // Initial State
  updateCounters();
  updateSliderDisplay();
});
