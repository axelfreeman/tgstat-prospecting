---
name: tgstat-prospecting
description: "Use TGStat API inside AI agents (Claude, Cursor, Hermes, Codex) to search, validate and extract contacts from Telegram channels. Ready-made API reference so agents don't hallucinate endpoints."
version: 1.0.0
---

# Telegram Channel Collection & Validation — TGStat API + HTTP

**Готовое описание TGStat API для AI-агентов.** Агент (Claude, Cursor, Hermes, Codex, Cline) подгружает этот скилл и сразу знает: какие эндпоинты дёргать, какие параметры передавать, какие ошибки ловить и как обходить квоты. Не выдумывает API сам — берёт готовую методологию.

Сбор и валидация Telegram-каналов/ботов через TGStat API, с HTTP-скрейпингом как альтернативой (когда кончилась квота API или валидация через API долгая). Универсально — любая тематика, любой язык, любой агент.

## 1. TGStat API — основной способ

**База:** `https://api.tgstat.ru/`
**Авторизация:** параметр `token` в каждом запросе (постоянный, берётся в Личном кабинете tgstat.ru).

### Три API-сервиса

| Сервис | Что | Методы |
|--------|-----|--------|
| **Stat API** | аналитика каналов | channels/get, channels/stat, channels/posts, channels/subscribers, channels/views, channels/avg-posts-reach, channels/er/err/err24 |
| **Search API** | поиск по базе публикаций | posts/search, words/mentions-by-period, words/mentions-by-channels |
| **Callback API** | уведомления в реальном времени | callback/subscribe-channel, callback/subscribe-word |

### Ключевой метод сбора — `channels/search`

```
GET https://api.tgstat.ru/channels/search
  ?token=XXX
  &q=ключевое_слово    # мин 3 символа
  &country=XX          # 10 стран: ru ua by uz kz ir kg in cn et
  &language=YYY        # код языка (см. database/languages)
  &peer_type=all       # channel/chat/all
  &search_by_description=1   # искать также в описаниях
  &limit=100           # макс 100
```

**Возвращает** `Channel[]` с полями: `username`, `title`, `about`, `participants_count`, `link`. Подписчики и описание приходят сразу — отдельный `channels/get`/`stat` не нужен (экономит квоту).

### Справочники (бесплатно, вне тарификации)

- `database/categories` — категории каналов
- `database/countries` — доступные страны (ru ua by uz kz ir kg in cn et)
- `database/languages` — доступные языки (коды)

### Контроль квоты

```
GET https://api.tgstat.ru/usage/stat?token=XXX
→ spentChannels, spentRequests, expiredAt
```

### Тарификация

- Квота: общее число запросов/мес + уникальные каналы (Stat) + уникальные ключевые слова (Search).
- `channels/search`, `subscribers`, `views`, `er/err/err24`, `add` — тариф S и выше.
- `channels/get`, `stat`, `posts`, `mentions`, `forwards`, `posts/get`, `posts/stat` — все тарифы.

### Ошибки

| Код | Значение |
|-----|----------|
| `flood_control_10` / `flood_control_60` | слишком часто — добавить паузу |
| `quota_requests_reached` | кончилась квота запросов |
| `quota_channel_reached` | кончилась квота уникальных каналов |
| `param country required` | `country` обязателен для search |
| `param q is too short` | ключ < 3 символов |
| `outdated_statistics` | повторить через 15 мин |

### Расширенный синтаксис поиска

Операторы: `=` точное, `*` часть слова, `|` ИЛИ, `""` фраза, `-` минус-слово, `()` группировка. Параметр `extendedSyntax=1`.

## 2. HTTP-валидация — альтернатива / фолбэк

Когда квота API кончилась или валидация через API слишком медленная — проверять жив/мёртв можно напрямую по публичной странице канала, без API и без аккаунта:

```
GET https://t.me/<username>
```

| Сигнал | Живой | Мёртвый (удалён/переименован) |
|--------|-------|-------------------------------|
| `og:title` | реальное имя | `Telegram: Contact @username` |
| `og:image` | `cdn.telesco.pe/...` или `data:image/svg` | `telegram.org/img/t_logo_2x.png` (дефолтный логотип) |
| `og:description` | текст | пусто |

**Правило:** живой ⇔ `og:title` не пустой и не начинается с `Telegram: Contact @`. Либо — `og:image` не содержит `t_logo_2x.png`.

Выживаемость каналов в нишевых тематиках ~40-50% — валидация обязательна перед рассылкой.

## 3. Извлечение контактов/ботов из постов

Контакты часто не в описании, а в постах (закрепы, «жми → бот», inline-кнопки). Достаётся через публичный превью:

```
GET https://t.me/s/<username>
```

`t.me/s/` рендерит ~15-20 последних постов серверно (HTML). Оттуда извлекаются:
- `@упоминания` и `t.me/ссылки` в тексте постов
- ссылки на ботов (username оканчивается на `bot`)

Боты = продукты операторов = точки контакта.

## 4. Фильтр по тематике

Фильтруй каналы по своим ключам и минус-словам. Подставь слова своей ниши:

```
ключи:      <ключевые_слова_ниши>
минус-слова: <нерелевантные_слова_для_исключения>
```

Совет: составь списки на каждом языке целевых стран (локальные термины ищутся лучше, чем английские).

## 5. Пайплайн целиком

```
1. TGStat channels/search (по ключам, всем нужным странам/языкам)
2. + сторонние каталоги (GitHub-коллекции, директории) при необходимости
3. Дедуп против своей базы контактов + прошлых дампов
4. Валидация жив/мёртв (HTTP t.me/<u> — если квота кончилась, либо channels/get)
5. Фильтр по тематике (ключи + минус-слова)
6. Извлечение ботов/контактов из постов (t.me/s/<u>)
7. → финальный список операторов + их боты
```

## 6. ⚠️ Критические правила

1. **HTTP вместо клиентских библиотек**: `t.me/` и `t.me/s/` отдают публичные данные без авторизации — используй их для массовой валидации и скрейпа. Любые клиентские библиотеки при массовых запросах ловят FloodWait на часы.
2. **Параллелизм ≤8 потоков** — при большем числе потоков Telegram режет IP и возвращает пустые og-теги (ложные «мёртвые»). При 6-8 воркерах добавляй ретрай на пустой ответ.
3. **Ложные друзья в языках** — короткие термины могут совпадать с другими значениями (например, слово со значением числа или названием другой модели). Проверяй реальные термины ниши в каждом языке перед поиском.
4. **Нелегальный контент** (детский/CSAM) — исключать жёстко, это уголовка в любой юрисдикции.

## 7. Скрипты (вшиты в скилл, `scripts/`)

| Скрипт | Что делает | Env-параметры |
|--------|-----------|---------------|
| `scripts/tgstat_search.py` | сбор каналов через `channels/search` | `TGSTAT_API_KEY`, `OUT_FILE` |
| `scripts/tgstat_validate_http.py` | валидация жив/мёртв (HTTP) | `SRC_FILE`, `OUT_FILE` |
| `scripts/tgstat_extract_contacts.py` | боты/контакты из постов (`t.me/s/`) | `SRC_FILE`, `OUT_FILE` |

Порядок запуска: `search` → `validate` → `extract`. Ключи ниши и минус-слова подставляются в самих скриптах (помечены комментарием «ЗАМЕНИ»).

Пример:
```bash
export TGSTAT_API_KEY=xxx
export OUT_FILE=channels.json
python3 scripts/tgstat_search.py

export SRC_FILE=channels.json OUT_FILE=live.json
python3 scripts/tgstat_validate_http.py

export SRC_FILE=live.json OUT_FILE=contacts.json
python3 scripts/tgstat_extract_contacts.py
```
