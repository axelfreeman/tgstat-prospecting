#!/usr/bin/env python3
"""Валидация каналов жив/мёртв через HTTP t.me/<u>. Без API, без аккаунта.
Вход: JSON с channels[].username. Выход: живые + мёртвые."""
import json, time, re, urllib.request, concurrent.futures, os

SRC = os.environ.get("SRC_FILE", "tg_channels.json")
OUT = os.environ.get("OUT_FILE", "tg_channels_live.json")

def fetch(username):
    url = f"https://t.me/{username}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='ignore')

def check(username):
    title, html = "", ""
    for _ in range(3):
        try:
            html = fetch(username)
        except Exception:
            time.sleep(2); continue
        for m in re.findall(r'og:title" content="([^"]+)"', html):
            title = m; break
        if title:
            break
        time.sleep(1.5)
    alive = bool(title) and not title.startswith("Telegram: Contact @")
    desc = ""
    for m in re.findall(r'og:description" content="([^"]+)"', html):
        desc = m; break
    return (username, alive, title, desc)

def main():
    d = json.load(open(SRC))
    ch = d.get("channels", [])
    usernames = [c.get("username", "").lstrip("@") for c in ch]
    usernames = [u for u in usernames if u]
    live, dead = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for u, alive, title, desc in ex.map(check, usernames):
            c = next(x for x in ch if x.get("username", "").lstrip("@") == u)
            c["_title"], c["_desc"] = title, desc
            (live if alive else dead).append(c)
    json.dump({"live_count": len(live), "dead_count": len(dead),
               "live_channels": live, "dead_channels": dead},
              open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Живых {len(live)}, мёртвых {len(dead)} из {len(usernames)}")

if __name__ == "__main__":
    main()
