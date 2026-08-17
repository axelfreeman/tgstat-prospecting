#!/usr/bin/env python3
"""TGStat channels/search — сбор каналов по ключам, всем странам/языкам.
Токен из env TGSTAT_API_KEY. Ключи в COUNTRIES — пример, замени на свою нишу."""
import json, time, urllib.parse, urllib.request, os

TOKEN = os.environ.get("TGSTAT_API_KEY", "")
BASE = "https://api.tgstat.ru/channels/search"
OUT = os.environ.get("OUT_FILE", "tg_channels.json")

# страна -> (язык, [ключевые слова ниши]) — ЗАМЕНИ на свои
COUNTRIES = {
    "ru": ("russian", ["ключ1", "ключ2"]),
    "cn": ("chinese", ["ключ1", "ключ2"]),
}

def search(q, country, language, peer_type="all", search_by_description=1, limit=100):
    params = {
        "token": TOKEN, "q": q, "country": country, "language": language,
        "peer_type": peer_type, "search_by_description": search_by_description, "limit": limit,
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    if not TOKEN:
        print("Задай TGSTAT_API_KEY в окружении")
        return
    db = {}
    for country, (lang, kws) in COUNTRIES.items():
        for kw in kws:
            try:
                d = search(kw, country, lang)
            except Exception as e:
                print(f"[{country}] '{kw}' ОШИБКА: {e}"); time.sleep(3); continue
            if d.get("status") != "ok":
                err = d.get("error")
                if err in ("flood_control_10", "flood_control_60"):
                    time.sleep(65); continue
                if err == "quota_requests_reached":
                    print("КВОТА ИСЧЕРПАНА"); return
                print(f"[{country}] '{kw}' → {err}"); continue
            items = d.get("response", {}).get("items", [])
            for it in items:
                u = it.get("username", "").lstrip("@")
                if u and u not in db:
                    db[u] = it
            print(f"[{country}] '{kw}' → {len(items)}, база {len(db)}")
            time.sleep(2.5)
    ranked = sorted(db.values(), key=lambda x: x.get("participants_count", 0) or 0, reverse=True)
    json.dump({"total": len(ranked), "channels": ranked}, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"ГОТОВО: {len(ranked)} каналов → {OUT}")

if __name__ == "__main__":
    main()
