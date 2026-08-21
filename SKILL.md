---
name: tgstat-prospecting
description: "Use TGStat API inside AI agents (Claude, Cursor, Hermes, Codex) to search, validate and extract contacts from Telegram channels. Ready-made API reference so agents don't hallucinate endpoints."
version: 1.0.0
---

# Telegram Channel Collection & Validation — TGStat API + HTTP

**A ready-made TGStat API reference for AI agents.** An agent (Claude, Cursor, Hermes, Codex, Cline) loads this skill and immediately knows which endpoints to call, which parameters to pass, which errors to catch, and how to work around quotas. It never hallucinates the API — it uses this methodology.

Collect and validate Telegram channels/bots via the TGStat API, with HTTP scraping as a fallback (when the API quota runs out or validation via the API is too slow). Universal — any niche, any language, any agent.

## 1. TGStat API — primary method

**Base:** `https://api.tgstat.ru/`
**Auth:** a `token` query parameter on every request (permanent, from the tgstat.ru dashboard).

### Three API services

| Service | What it does | Methods |
|--------|-----|--------|
| **Stat API** | channel analytics | channels/get, channels/stat, channels/posts, channels/subscribers, channels/views, channels/avg-posts-reach, channels/er/err/err24 |
| **Search API** | search across the post database | posts/search, words/mentions-by-period, words/mentions-by-channels |
| **Callback API** | real-time notifications | callback/subscribe-channel, callback/subscribe-word |

### Key collection method — `channels/search`

```
GET https://api.tgstat.ru/channels/search
  ?token=XXX
  &q=keyword        # min 3 chars
  &country=XX       # 10 countries: ru ua by uz kz ir kg in cn et
  &language=YYY     # language code (see database/languages)
  &peer_type=all    # channel/chat/all
  &search_by_description=1   # also search descriptions
  &limit=100        # max 100
```

**Returns** `Channel[]` with fields: `username`, `title`, `about`, `participants_count`, `link`. Subscribers and description come inline — no separate `channels/get`/`stat` call needed (saves quota).

### Reference tables (free, outside billing)

- `database/categories` — channel categories
- `database/countries` — available countries (ru ua by uz kz ir kg in cn et)
- `database/languages` — available languages (codes)

### Quota control

```
GET https://api.tgstat.ru/usage/stat?token=XXX
→ spentChannels, spentRequests, expiredAt
```

### Billing

- Quota: total requests/month + unique channels (Stat) + unique keywords (Search).
- `channels/search`, `subscribers`, `views`, `er/err/err24`, `add` — plan S and above.
- `channels/get`, `stat`, `posts`, `mentions`, `forwards`, `posts/get`, `posts/stat` — all plans.

### Errors

| Code | Meaning |
|-----|----------|
| `flood_control_10` / `flood_control_60` | too frequent — add a pause |
| `quota_requests_reached` | request quota exhausted |
| `quota_channel_reached` | unique-channel quota exhausted |
| `param country required` | `country` is required for search |
| `param q is too short` | key < 3 chars |
| `outdated_statistics` | retry in 15 min |

### Advanced search syntax

Operators: `=` exact, `*` partial word, `|` OR, `""` phrase, `-` minus-word, `()` grouping. Parameter `extendedSyntax=1`.

## 2. HTTP validation — alternative / fallback

When the API quota runs out or API validation is too slow, check live/dead directly on the public channel page, no API and no account:

```
GET https://t.me/<username>
```

| Signal | Live | Dead (deleted/renamed) |
|--------|-------|------------------------|
| `og:title` | real name | `Telegram: Contact @username` |
| `og:image` | `cdn.telesco.pe/...` or `data:image/svg` | `telegram.org/img/t_logo_2x.png` (default logo) |
| `og:description` | text | empty |

**Rule:** live ⇔ `og:title` non-empty and not starting with `Telegram: Contact @`. Or — `og:image` doesn't contain `t_logo_2x.png`.

Channel survival in niche topics is ~40-50% — validation is mandatory before outreach.

## 3. Extracting contacts/bots from posts

Contacts are often not in the description but in posts (pinned, "tap → bot", inline buttons). Pulled via the public preview:

```
GET https://t.me/s/<username>
```

`t.me/s/` server-renders ~15-20 recent posts (HTML). Extract from there:
- `@mentions` and `t.me/links` in post text
- bot links (username ending in `bot`)

Bots = the operators' products = contact points.

## 4. Niche filtering

Filter channels by your own keys and minus-words. Substitute your niche words:

```
keys:        <niche_keywords>
minus-words: <irrelevant_words_to_exclude>
```

Tip: build lists in each target country's language (local terms search better than English ones).

## 5. Full pipeline

```
1. TGStat channels/search (by keys, all target countries/languages)
2. + external directories (GitHub collections, directories) if needed
3. Dedup against your own contact base + past dumps
4. Validate live/dead (HTTP t.me/<u> — if quota ran out, or channels/get)
5. Filter by niche (keys + minus-words)
6. Extract bots/contacts from posts (t.me/s/<u>)
7. → final list of operators + their bots
```

## 6. ⚠️ Critical rules

1. **HTTP instead of client libraries**: `t.me/` and `t.me/s/` serve public data without auth — use them for mass validation and scraping. Any client libraries hit FloodWait for hours on mass requests.
2. **Parallelism ≤8 workers** — beyond that Telegram rate-limits the IP and returns empty og-tags (false "dead"). At 6-8 workers, add a retry on empty response.
3. **False friends across languages** — short terms can collide with other meanings (e.g. a word that means a number or another model name). Check the real niche terms in each language before searching.
4. **Illegal content** (child/CSAM) — exclude hard; it's criminal in every jurisdiction.

## 7. Scripts (bundled in the skill, `scripts/`)

| Script | What it does | Env params |
|--------|-----------|---------------|
| `scripts/tgstat_search.py` | collect channels via `channels/search` | `TGSTAT_API_KEY`, `OUT_FILE` |
| `scripts/tgstat_validate_http.py` | live/dead validation (HTTP) | `SRC_FILE`, `OUT_FILE` |
| `scripts/tgstat_extract_contacts.py` | bots/contacts from posts (`t.me/s/`) | `SRC_FILE`, `OUT_FILE` |

Run order: `search` → `validate` → `extract`. The exact invocation and env vars are in the README.
