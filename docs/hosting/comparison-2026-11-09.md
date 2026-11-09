# C.8 Step 1: hosting + database for multi-device sync (2026-11-09)

Goal (ROADMAP C.8): one hosted backend + database as the single source of truth, so profile, progress, SRS queue and chat history are the same on laptop, phone and tablet. The client is a PWA. Login comes first for Roman, then for more users. This document only compares options. **Roman picks; nothing is deployed yet.**

## What LingMate needs from a host
- **Small app.** One FastAPI process (uvicorn) with static files. No GPU: the LLM runs outside (Gemini API or another free tier, 5.8). Local Ollama can't run on a cheap host. 256–512 MB RAM is enough.
- **Data.** Today it is one SQLite file (`core/storage.py`, `LINGMATE_DB_PATH`). Hosts with a **persistent disk** keep SQLite as it is. Hosts with an ephemeral filesystem need a hosted Postgres plus a `PostgresStore` with the same interface as `SqliteStore`, which is roughly one PR.
- **Keys.** `GEMINI_API_KEY` and the future 5.8 keys live in the host's secret env vars. They are never in the repo or the browser.
- **Users.** At the start only Roman, a few requests a day. Later several learners (C.7), which first needs 5.5 (consent, export/delete).
- **EU data location.** Learner texts are personal data, so a Frankfurt/Amsterdam/Paris/Helsinki region is preferred.
- **Cold starts matter on a phone.** If the server sleeps, the first tap waits. The PWA can show the cached UI and queue reviews, but chat needs the server.

## Options

Facts were collected on 2026-11-09 from vendor docs and 2026 third-party write-ups, with links below. Free tiers change often. Hetzner and Oracle changed theirs in 2026. **Re-check the pricing page before signing up.**

| # | Option | Cost | Card needed | Sleeps? | Data stays | EU | Backups | Code changes | Ops effort |
|---|---|---|---|---|---|---|---|---|---|
| A | **Render free web service + Neon free Postgres** | €0 | Render: not stated; Neon: no (card only for extras) | Render sleeps after 15 min idle, **~1 min cold start**; Neon scales to zero after 5 min (fast resume) | Neon: 1 GB/project, 100 CU-h/month | Neon Frankfurt; Render EU region not verified | Neon free: 6 h restore window + 1 manual snapshot, no scheduled backups → we add a nightly `pg_dump` export ourselves | `PostgresStore` (~1 PR) | Low |
| B | **Small EU VPS (Hetzner CPX02 1 vCPU/1 GB) + SQLite on disk + Caddy (HTTPS)** | ≈ €6.49 + €1.20 backups ≈ **€7.7/month** (+VAT) | Yes (card/SEPA/PayPal, ID check possible) | **Never** | SQLite file as today | Germany / Finland | Daily server backups (7 slots) + our SQLite copy | None for storage; deploy script | Medium: Roman owns a Linux server (updates, firewall) |
| C | **Fly.io machine + volume (Frankfurt) + SQLite** | ~$2.2 (256 MB) to ~$7.7 (1 GB, fra) / month + $0.15/GB volume | Yes (after a $1 / 7-day trial) | Optional auto-stop (cheaper, cold start) or always on | SQLite on a volume | Frankfurt, Amsterdam, Paris | Volume snapshots (first 10 GB/month free) | Dockerfile + `fly.toml` | Low-medium |
| D | **Oracle Cloud Always Free (Ampere ARM VM) + SQLite** | €0 | Yes (real credit/debit card, auth hold; no prepaid/virtual) | Never, but **idle VMs can be reclaimed** (CPU/network/memory < 20 % for 7 days), and that is exactly LingMate's load | SQLite on 200 GB block storage | Home region chosen at sign-up (EU possible) | 5 free volume backups | Same as B | Medium-high; ARM allowance was cut from 4 OCPU/24 GB to 2/12 on 2026-06-15 without notice; capacity often "out of host" |
| E | Render web + **Supabase** free Postgres | €0 | not stated | Render as in A; **Supabase pauses the project after 1 week without activity** (manual restore) | 500 MB DB | Frankfurt | Free: none (daily backups = Pro $25) | `PostgresStore` | Low, but the weekly pause breaks "open the app after a holiday" |
| F | Koyeb (free Postgres 0.25 vCPU) | €0 DB / Pro $29+ for apps | not stated | DB sleeps after 5 min | 1 GB | Frankfurt | ? | `PostgresStore` | Free hours unclear (the pricing page says 5 h, the blog says 50 h); no free web instance → not a fit |

Not compared in depth: Render **free Postgres**, because it is deleted 30 days after creation and has no backups, so it doesn't fit; Railway, Google Cloud Run, PythonAnywhere and Turso (hosted SQLite), because there was no time to verify their 2026 terms. They can be checked in a follow-up if A–C don't suit.

## Where the API keys live
In every option the keys are host-side **secret environment variables**: the Render/Fly dashboard secrets, or an `.env` with `chmod 600` on the VPS. The browser never sees them. Once the app is public, `/api/*` must require login, otherwise anyone could spend Roman's free quota. That is part of the implementation step: a simple session login, a single user first. The 09.11 quota fix (PR #9) already keeps the app from hammering an exhausted provider.

## If it grows
- A: Neon Launch is pay-per-use ($0.106/CU-hour, $0.35/GB-month), a few € for a handful of learners. Render's paid instance (from ~$7) removes the cold start.
- B: the same server easily handles dozens of learners. A bigger plan costs a few € more. Hetzner raised prices twice in 2026, so expect more increases.
- C: pay per machine size. Managed Postgres ($38/month) is only needed much later.

## Recommendation
1. **To start (Roman only, €0, no card): option A.** Render free web service + Neon free Postgres in Frankfurt, plus a nightly `pg_dump` / JSON export as our own backup.
   - Cost: one `PostgresStore` PR. SQLite stays for local dev and tests.
   - Downside: about a 1 min wait on the first tap after 15 min idle. Workarounds: the PWA shows the cached home screen and SRS queue while the server wakes, or a free uptime ping. The ping is a grey area under Render's terms, so we wouldn't rely on it.
2. **If the cold start annoys you, or once there are more learners: option B or C** (≈ €3–8/month). Always on, SQLite stays and no DB code is needed. B is cheapest per GB and fully EU; C is less server admin. Both are paid, so they need your decision.
3. **Not recommended:**
   - D: free but fragile. Idle VMs get reclaimed and the terms were cut without notice in 2026.
   - E: Supabase pauses the project after a week without activity.
   - F: the free hours are unclear.
   - Render free Postgres: deleted after 30 days.

## Questions for Roman
1. €0 with a cold start (A), or ≈ €3–8/month always on (B/C)?
2. Is a card sign-up OK (needed for B, C, D)?
3. Is EU-only data location a hard requirement? It matters later for other learners (5.5).
4. Login: email + password, or a magic link by email (needs an email service, 2.4c)?

After your choice the implementation goes in slices: (a) login + per-user data; (b) `PostgresStore` (only for A/E); (c) deploy config + secrets docs; (d) PWA manifest + service worker; (e) offline queue for reviews.

## Sources (checked 2026-11-09)
- Render free tier: https://render.com/docs/free
- Fly.io pricing 2026 (third-party, competitor): https://temps.sh/blog/fly-io-pricing-2026
- Supabase free tier 2026 (secondary, May 2026 data): https://automationatlas.io/answers/supabase-free-tier-limits-2026/
- Neon free plan: https://neon.com/faqs/free-plan-limits-and-quotas, https://neon.com/docs/introduction/plans
- Oracle Always Free: https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm, https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/
- Hetzner 2026 prices (third-party, from Hetzner's price API): https://agentdeals.dev/hetzner-pricing-2026
- Koyeb: https://www.koyeb.com/blog/top-postgresql-database-free-tiers-in-2026, https://www.koyeb.com/pricing
