# AGENTS.md — TGStat Prospecting

## What this is

A skill for collecting, validating and enriching Telegram channels via the TGStat API, with HTTP scraping as a quota-free fallback. Universal — any niche, any language.

## When to use

- User wants to find Telegram channels by topic/keyword
- User needs to validate which channels are still alive
- User wants to extract contact bots / @mentions from channel posts
- User asks about Telegram lead generation or channel prospecting

## How it works (3-stage pipeline)

1. **Search** — `channels/search` by keyword + country + language → returns channels with `username`, `title`, `about`, `participants_count`
2. **Validate** — HTTP `GET t.me/<username>` → check `og:title` (live) vs `Telegram: Contact @username` (dead)
3. **Extract** — HTTP `GET t.me/s/<username>` → pull @mentions and bot links from last ~20 posts

## Key facts for agents

- TGStat API base: `https://api.tgstat.ru/`, auth via `token` query param
- `channels/search` requires `country` param (10 geos: ru ua by uz kz ir kg in cn et)
- `channels/search` returns subscriber count + bio inline — no extra `channels/get` needed (saves quota)
- Quota check: `usage/stat` → `spentChannels`, `spentRequests`, `expiredAt`
- ~40-50% of niche channels die fast — always validate before pitching
- Public HTTP endpoints (`t.me/`, `t.me/s/`) need no auth and no account

## Critical rules (never violate)

1. **Use HTTP (`t.me/`, `t.me/s/`), not client libraries** (Telethon etc.) — client libs hit FloodWait for hours on mass requests
2. **Parallelism ≤8 workers** — beyond that Telegram rate-limits and returns empty og-tags (false "dead")
3. **Exclude illegal content (CSAM) hard** — criminal in every jurisdiction
4. **Check niche terms per language** — short terms have false friends (numbers, other meanings)

## Scripts

| Script | Purpose | Env vars |
|--------|---------|----------|
| `scripts/tgstat_search.py` | channel discovery | `TGSTAT_API_KEY`, `OUT_FILE` |
| `scripts/tgstat_validate_http.py` | live/dead check | `SRC_FILE`, `OUT_FILE` |
| `scripts/tgstat_extract_contacts.py` | bots/contacts from posts | `SRC_FILE`, `OUT_FILE` |


## Repo conventions

- README.md and AGENTS.md are English-only (matches author's GitHub convention)
- SKILL.md is the source of truth for the methodology
- Scripts use stdlib `urllib` with optional `requests` fallback
- No tokens, usernames, or niche identifiers in committed files — placeholders only
