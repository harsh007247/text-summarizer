# Text Summarizer - PEGASUS Web Application

A clean, high-performance web application and REST API for abstractive text summarization powered by a fine-tuned Google **PEGASUS** model (trained on the SAMSum dialogue dataset). Built with **FastAPI**, **HTML5**, **CSS3**, and **Vanilla JavaScript**.

---

## 🚀 Key Features

- **Fine-Tuned PEGASUS Model**: Utilizes your locally trained model checkpoint for conversational & text summarization.
- **Simplified Single-File Backend (`app.py`)**: All FastAPI logic, routes, and validation consolidated in a single, clean Python file.
- **Simple Startup (`main.py`)**: Clean entry point that launches the Uvicorn ASGI server.
- **Single-Load Model Architecture**: Loads PEGASUS weights once at application startup into memory (`eval()` mode with `torch.no_grad()`).
- **Dynamic User-Controlled Length**:
  - Sliders for **Maximum Length** and **Minimum Length** in subword tokens.
  - Quick presets: **Concise** (~60 tokens), **Balanced** (~128 tokens), and **Detailed** (~200 tokens).
  - Clear UI distinction between subword tokens and exact word counts.
- **Modern, Polished Interface**:
  - Clean light theme with an Indigo / Violet accent palette and Inter typography.
  - Live word and character counting.
  - Preloaded conversation samples for instant testing.
  - Live status indicator (PEGASUS Ready / CPU or CUDA device detection).
  - Summary metrics dashboard: word counts, token counts, compression/reduction percentage, and inference latency.
  - One-click **Copy Summary** with visual feedback.
  - Keyboard shortcut: <kbd>Ctrl</kbd> + <kbd>Enter</kbd> (or <kbd>Cmd</kbd> + <kbd>Enter</kbd>).

---

## 📁 Clean & Simple File Structure

```text
text-summarizer/
│
├── config/
│   └── config.yaml                     # Model paths & dataset configuration
│
├── artifacts/
│   └── model_trainer/
│       ├── pegasus-samsum-model/       # Trained model checkpoint (weights, config)
│       └── tokenizer/                  # Tokenizer vocabulary & configuration
│
├── src/textsummarizer/
│   ├── config/configuration.py         # Reads config.yaml
│   └── pipeline/prediction.py          # PEGASUS inference pipeline
│
├── templates/
│   └── index.html                      # Semantic HTML5 frontend interface
│
├── static/
│   ├── css/style.css                   # Custom responsive stylesheet
│   └── js/script.js                    # Vanilla JS counters, sliders, API calls
│
├── app.py                              # All FastAPI backend routes & validation
├── main.py                             # Server entry point (uvicorn runner)
├── requirements.txt                    # Project dependencies
└── PROJECT_CHANGES.txt                 # Detailed change log documentation
```

---

## 🛠️ Quick Start & Setup

### 1. Activate Environment
```powershell
.\env\Scripts\activate
```

### 2. Run the Application
Run using `main.py`:
```powershell
python main.py
```

Or run via Uvicorn CLI:
```powershell
uvicorn app:app --host 127.0.0.1 --port 8080 --reload
```

The application will be accessible at:
👉 **http://127.0.0.1:8080**

Interactive Swagger API docs are available at:
👉 **http://127.0.0.1:8080/docs**

---

## 🔌 API Reference

### 1. Health Check
`GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### 2. Generate Summary
`POST /api/summarize`

**Request Body:**
```json
{
  "text": "Hannah: Hey, are you free for lunch today?\nAmanda: Sure! What are you craving?\nHannah: Maybe sushi at Sakura around 12:30?\nAmanda: Sounds perfect, see you there!",
  "max_length": 128,
  "min_length": 20,
  "num_beams": 8,
  "length_penalty": 0.8
}
```

**Response Body:**
```json
{
  "summary": "Hannah and Amanda are going to eat sushi at Sakura around 12:30 today. They will meet at the restaurant.",
  "input_words": 27,
  "summary_words": 19,
  "input_tokens": 39,
  "summary_tokens": 22,
  "reduction_percentage": 29.6,
  "inference_time_seconds": 1.85
}
```
385723258596.dkr.ecr.ap-southeast-2.amazonaws.com/texts