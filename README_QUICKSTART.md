# LingMate — Quick Start

1. Create and activate a virtual environment.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Pick one of three modes inside `.env`:
   - **Gemini (cloud):** set `LLM_PROVIDER=gemini` and paste your key into `GEMINI_API_KEY`.
   - **Ollama (local):** install Ollama, run `ollama pull qwen2.5:7b-instruct`, then set `LLM_PROVIDER=ollama`.
   - **Auto (recommended):** set `LLM_PROVIDER=auto` — tries Gemini, falls back to Ollama, then to a rule-based responder.
5. Run: `python main.py`
6. Open http://127.0.0.1:8000
7. (Optional) Verify the LLM layer: `python -m pytest tests/test_llm_providers.py -v`
