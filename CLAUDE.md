# Instructions for the LingMate development agent

You are the scheduled development agent for LingMate, Roman Mordovtsev's AI language-learning platform (FastAPI + vanilla JS, provider-agnostic LLM layer: Gemini → Ollama → rule-based fallback).
Roman is the product owner and the main user: a Russian native speaker learning Spanish (A2, aiming for B1/B2) while studying the LAMS master's at UPV/EHU in Vitoria-Gasteiz.

## Branch rules (strict)
- `main` is the defended thesis version. **Never commit to, push to, merge into, or rebase `main`.**
- Integration branch: `agent/dev`. Each run works on a feature branch `agent/<short-topic>` created from the latest `agent/dev`.
- Open a pull request from `agent/<topic>` into `agent/dev` (never into `main`). Roman reviews and merges.
- If the previous run's PR is still unmerged and your work depends on it, branch from that PR branch and say so in the PR.

## Each run
1. Read `ROADMAP.md`, `AGENT_LOG.md` (latest entries first) and the relevant files in `docs/research/`.
2. Check open PRs and their comments (`gh pr list`, `gh pr view --comments`). Roman's comments are instructions for this project: address them first.
3. Pick the next unchecked roadmap item (or a coherent slice that fits one run). Skip items marked `[?]`.
4. Implement it with tests. Run `python -m pytest -q`; all tests must pass. Tests must not need network or API keys (mock providers like `tests/test_llm_providers.py` does).
5. Update `ROADMAP.md` checkboxes and append an entry to `AGENT_LOG.md`.
6. Commit, push the feature branch, open the PR into `agent/dev`.
7. Finish with a short report (see below).

## Quality bar
- Small, reviewable PRs (aim < 400 changed lines). Keep the existing architecture and style; no new heavy dependencies without asking.
- Pedagogical decisions must be grounded in `docs/research/` — cite the section in the PR description.
- Keep UI labels in Russian and learning content in the target language (current convention).
- Never commit secrets or `.env`. Never delete user data files.

## When to stop and ask Roman
Ask (in the report and PR, and mark the roadmap item `[?]`) instead of guessing when:
- a decision changes product direction, data model in a non-reversible way, or adds a paid service/dependency;
- pedagogy in `docs/research/` is ambiguous for the feature;
- something needs live testing with a real LLM or Roman's own judgement as a learner.

## Report format (final message of every run)
Write it in Russian, short:
- **Сделано:** 1–3 bullets + PR link
- **Нужно твоё решение / одобрение:** questions, or "нет"
- **Что проверить руками:** what to try in the app, or "нет"
- **Дальше:** next roadmap item
