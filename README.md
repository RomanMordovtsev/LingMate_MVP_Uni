# LingMate

![LingMate Demo](demo.gif)

LingMate is an AI-powered language-learning platform focused on conversational practice and scenario-based lessons. Originally built as an undergraduate diploma project at ITMO University, the codebase has since been refactored around a provider-agnostic LLM layer so that the same application can run against a cloud model (Google Gemini) or a fully local model (Ollama) — chosen by a single environment variable.

---

## ✨ Features

- 💬 **Free Talk** — open conversation in the target language with gentle corrections, vocabulary surfacing, and encouragement.
- 🎯 **Lesson Mode** — 24 scripted scenarios across 6 languages (café, hotel check-in, airport, meeting a new person), each with a goal, situation, example dialogue, and key phrases.
- 🌐 **6 languages** — English, Español (Spain), Français, Deutsch, Italiano, Türkçe — both for Free Talk and Lesson Mode.
- 🔌 **Pluggable LLM backend** — `LLM_PROVIDER=gemini` / `ollama` / `auto`. In `auto` mode the service first tries Gemini and transparently falls back to Ollama on error (geo-block, quota, network), and to a rule-based responder if both are unavailable.
- 📈 **Adaptive progress** — vocabulary, completed scenarios, and progress notes are persisted per user.
- 🎤 **Voice in browser** — Web Speech API for dictation and TTS, language-aware (no English voice reading Spanish text).
- ✅ **Tested** — 14 unit tests with mocked HTTP, all under one second.

---

## 🏗 Architecture

```
┌──────────────────┐         ┌─────────────────────────────────────┐
│   FastAPI app    │  ───►   │    LLMService (provider-agnostic)   │
│  (main.py)       │         │                                     │
└──────────────────┘         │   ┌─────────────────────────────┐   │
                             │   │  Provider chain (auto):     │   │
                             │   │   1. GeminiProvider         │   │
                             │   │   2. OllamaProvider         │   │
                             │   │   3. rule-based fallback    │   │
                             │   └─────────────────────────────┘   │
                             └─────────────────────────────────────┘
```

All providers implement a single contract — `is_configured()`, `generate_json(system_prompt, user_prompt)`, and a `name` attribute — defined in `core/llm/base.py`. Adding a new backend (OpenAI, Anthropic, DeepSeek, a local LM Studio server) means writing one new file in `core/llm/` and adding it to the factory.

---

## 🛠 Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **LLM:** Google Gemini API (`google-genai`) or Ollama (any local model)
- **Frontend:** Vanilla HTML / CSS / JavaScript, Web Speech API
- **Testing:** pytest, httpx

---

## ⚙️ Setup

### 1. Clone and install

```bash
git clone https://github.com/RomanMordovtsev/LingMate_MVP_Uni.git
cd LingMate_MVP_Uni
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

### 2. Configure the LLM provider

Copy the example file and edit it:

```bash
cp .env.example .env
```

Choose one of three modes inside `.env`:

**Option A — Gemini (cloud, best quality):**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_from_https://aistudio.google.com
```

**Option B — Ollama (local, fully offline):**
```bash
# install Ollama from https://ollama.com/download, then:
ollama pull qwen2.5:7b-instruct
```
```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```

**Option C — auto (recommended):**
Same `.env` as A *and* B — the service tries Gemini first, falls back to Ollama on error, and finally to a rule-based responder if both are unreachable.

### 3. Run

```bash
python main.py
```

Open http://127.0.0.1:8000 in your browser.

### 4. Verify

```bash
python -m pytest tests/test_llm_providers.py -v
```

Expected: `14 passed in <2s`.

---

## 📡 API

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/status` | GET | Health check, current provider, available scenarios |
| `/api/setup` | POST | Save user profile (language, level, interests) |
| `/api/chat` | POST | Free-talk message |
| `/api/lesson/start` | POST | Start a scenario by ID |
| `/api/lesson/message` | POST | Continue an active scenario |
| `/api/progress/{user_id}` | GET | Vocabulary, completed scenarios, recent history |
| `/api/test-llm` | GET | Sanity check the currently selected provider |

---

## 🧪 Testing

Unit tests cover the provider abstraction, both real providers (with mocked HTTP), the factory, and `LLMService` fallback paths:

```bash
python -m pytest tests/test_llm_providers.py -v
```

For an end-to-end smoke test against a running Ollama:

```bash
python tests/smoke_ollama.py
```

---

## 📂 Project layout

```
LingMate_MVP_Uni/
├── core/
│   ├── llm/                    # Provider-agnostic LLM layer
│   │   ├── base.py             #   abstract LLMProvider
│   │   ├── gemini_provider.py  #   cloud Gemini implementation
│   │   ├── ollama_provider.py  #   local Ollama implementation
│   │   └── factory.py          #   provider chain builder
│   ├── llm_service.py          # high-level service: prompts, fallback, heuristics
│   ├── scenarios.py            # 24 scripted scenarios across 6 languages
│   ├── storage.py              # JSON persistence for users, history, progress
│   └── models.py               # Pydantic request models
├── static/index.html           # Single-page UI (Russian labels, target-language content)
├── tests/                      # pytest suite
├── data/                       # runtime state (gitignored)
├── main.py                     # FastAPI app
└── requirements.txt
```

---

## 🎓 Background

LingMate was developed as an undergraduate diploma project at ITMO University (2025–2026). The refactor into a provider-agnostic LLM layer was driven by a practical concern: cloud LLM access is unreliable in certain regions and during specific demos, while a local model removes that risk at the cost of quality. The chain-of-providers pattern lets the same code prioritise quality when the cloud is reachable and gracefully degrade to a local model otherwise.

---

## 📌 Author

**Roman Mordovtsev** — [github.com/RomanMordovtsev](https://github.com/RomanMordovtsev)
