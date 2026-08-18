# TGStat Prospecting — Ready-Made TGStat API Reference for AI Agents

<p align="center">
  <a href="https://github.com/axelfreeman/tgstat-prospecting/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/axelfreeman/tgstat-prospecting/stargazers"><img src="https://img.shields.io/github/stars/axelfreeman/tgstat-prospecting?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/axelfreeman"><img src="https://img.shields.io/badge/author-Axel%20Freeman-0A0A0A?style=flat-square" alt="Author"></a>
</p>

<p align="center"><i>⭐ Star this repo so your agent stops hallucinating the TGStat API.</i></p>

> 🌐 [Russian version →](README.ru.md)

**Give your AI agent the TGStat API — without it hallucinating the endpoints.**

This is a pre-written, agent-ready reference for the TGStat API: exact endpoints, parameters, error codes, rate limits and fallback strategies. Load it into Claude, Cursor, Hermes, Codex or Cline and the agent immediately knows how to search, validate and extract contacts from Telegram channels — no guesswork, no invented URLs.

## The problem it solves

Ask an agent "find Telegram channels about X" and it will invent `channels/search` with wrong params, hit `flood_control`, or burn your quota. This skill gives it the real API, so it calls the right thing the first time.

## What the agent gets

| Capability | Exact endpoint / method |
|------------|------------------------|
| Channel discovery | `channels/search` — keyword + country (10 geos) + language + description search |
| Subscriber + bio inline | returned in the same response — no extra `channels/get` (saves quota) |
| Live/dead validation | HTTP `t.me/<username>` — `og:title` / `og:image` signals |
| Contact extraction | `t.me/s/<username>` — @mentions + bot links from last ~20 posts |
| Quota monitoring | `usage/stat` — spent requests, expiry |
| Error handling | full table: `flood_control_10/60`, `quota_*`, `outdated_statistics`, etc. |
| Advanced search | `=`, `*`, `|`, `""`, `-`, `()` operators |

## Why HTTP, not client libraries

`t.me/` and `t.me/s/` serve public data unauthenticated. Client libraries (Telethon etc.) hit FloodWait for hours on mass requests. This skill routes the agent to the public HTTP endpoints — no account, no bans, no ToS circumvention.

## Works with any agent

- **Claude Code** — drop `SKILL.md` into your skills directory
- **Cursor** — add as a project rule / context file
- **Hermes Agent** — `skill_manage(action='create')` with the `SKILL.md` frontmatter
- **Codex / Cline** — add `SKILL.md` + `AGENTS.md` to the repo

## Quick start (scripts)

```bash
# 1. Search — drop your niche keywords in tgstat_search.py (marked "ЗАМЕНИ")
export TGSTAT_API_KEY=your_key OUT_FILE=channels.json
python3 scripts/tgstat_search.py

# 2. Validate live/dead
export SRC_FILE=channels.json OUT_FILE=live.json
python3 scripts/tgstat_validate_http.py

# 3. Extract contact bots
export SRC_FILE=live.json OUT_FILE=contacts.json
python3 scripts/tgstat_extract_contacts.py
```

## Requirements

- Python 3.8+ (scripts)
- TGStat API token (free tier at [tgstat.ru](https://tgstat.ru))
- Standard library only — `requests` optional

## Safety

- Public data only — no account scraping, no ToS circumvention
- Exclude illegal content (CSAM) — criminal in every jurisdiction
- Parallelism ≤8 workers to avoid false "dead" results

---

**Author:** Axel Freeman — AI-Native Marketer · [axelfreeman.com](https://axelfreeman.com)
