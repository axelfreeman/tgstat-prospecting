#!/usr/bin/env python3
"""Extract bots/contacts from channel posts via t.me/s/<u>. No API, no account.
Input: JSON with channels[].username. Output: channels -> bots + contacts."""
import json, re, time, urllib.request, concurrent.futures, os

SRC = os.environ.get("SRC_FILE", "tg_channels_live.json")
OUT = os.environ.get("OUT_FILE", "contacts_from_posts.json")

# junk mentions (common Telegram links and search engines) — add your niche
JUNK = {'telegram', 'durov', 'addlist', 'joinchat', 'share', 'forward', 'embed',
        'tgme', 'tme', 'web', 'channels', 'bots', 'settings', 'proxy', 'premium',
        'wallet', 'username', 'stories', 'catalog'}

def fetch(u):
    url = f"https://t.me/s/{u}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='ignore')

def extract(u):
    html = ""
    for _ in range(2):
        try:
            html = fetch(u); break
        except Exception:
            time.sleep(1.5)
    if not html:
        return (u, "", [], [])
    mentions = set()
    for m in re.findall(r'@([A-Za-z][A-Za-z0-9_]{3,})', html):
        mentions.add(m.lower())
    for m in re.findall(r't\.me/([A-Za-z0-9_]+)', html):
        mentions.add(m.lower())
    clean = {m for m in mentions if m not in JUNK and m != u.lower()}
    bots = sorted({m for m in clean if m.endswith('bot')})
    others = sorted({m for m in clean if not m.endswith('bot')})
    return (u, "", others, bots)

def main():
    d = json.load(open(SRC))
    # accepts both channels[] and {channels: ...}
    chans = d.get("channels", d) if isinstance(d, dict) else d
    if isinstance(chans, dict) and "live_channels" in chans:
        chans = chans["live_channels"]
    usernames = [(c.get("username") or "").lstrip("@") for c in chans]
    usernames = [u for u in usernames if u]
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for u, _, others, bots in ex.map(extract, usernames):
            results[u] = {"other_mentions": others, "bots": bots}
    json.dump({"channels": results}, open(OUT, "w"), ensure_ascii=False, indent=2)
    with_bots = sum(1 for v in results.values() if v.get("bots"))
    print(f"{len(results)} channels, {with_bots} with bots")

if __name__ == "__main__":
    main()
