# vless · happ (json)

Конфиги для [Happ](https://happ.su) (Xray-core): VLESS + Reality, TCP.
Только JSON — ссылок `vless://` здесь нет.

## Ссылка подписки

```
https://kasnysys.github.io/vps.github.io/vless.json
```

Happ → **Подписки** → «+» → **Ссылка** → вставить → «Обновить».

Страница со списком серверов и кнопками:

```
https://kasnysys.github.io/vps.github.io/
```

**Pages пока не включён в репозитории** (отдаёт 404). Пока не включишь, страница
работает через raw.githack:

```
https://raw.githack.com/kasnysys/vps.github.io/main/index.html
```

Включить Pages: Settings → Pages → Source: `Deploy from a branch` → `main` / `/ (root)` → Save.

Если Pages не поднялся, работает напрямую с GitHub:

```
https://raw.githubusercontent.com/kasnysys/vps.github.io/main/vless.json
```

Или скачай `vless.json` и импортируй файлом: Happ → «+» → **Из файла**.

## Серверы

| Сервер | Адрес | Flow | Reality SNI |
|---|---|---|---|
| 🇬🇧 Великобритания | 203.57.82.107 | — | api-io-mgr.galioncc.com |
| 🇳🇱 Нидерланды | 5.253.86.3 | vision | nl3.gofizz.in |
| 🇫🇷 Франция | 163.245.42.85 | vision | mother-earth.fyi |
| 🇸🇪 Швеция | 88.216.60.73 | — | ns-api-gw.galioncc.com |
| 🇷🇺 Родина | 94.139.250.226 | — | net-api-ctl.galioncc.com |

Все на `443`, `tcp`, `security=reality`, `fp=firefox`. Нидерланды, Франция и Родина — с `flow=xtls-rprx-vision`, остальные без flow.

## Обход

В `routing` российские домены идут **напрямую**, мимо прокси:

- `domain:ru`, `domain:su`, `domain:рф`, `domain:xn--p1ai`
- `domain:gov.ru`, `domain:bank.com`
- локальные сети `10/8`, `172.16/12`, `192.168/16`, `169.254/16`, `224/4`

Реклама (`geosite:category-ads-all`) — в блок.

> Категорий `geosite:ru` / `geoip:ru` нет специально: в geosite.dat от Happ секции
> `RU` не бывает, и ядро падало с ошибкой «отсутствует секция RU». Поэтому обход
> по России сделан обычными доменами `.ru`, `.su`, `.рф`.

## Файлы

- `vless.json` — массив конфигов Xray. Это и есть подписка.
- `index.html` — страница: читает `vless.json`, рисует серверы, кнопки «JSON» копируют конфиг одного сервера в буфер.
- `README.md` — этот файл.

> В конфигах лежат реальные `id` и `publicKey`. Кто увидит файл — сможет подключиться к серверам. Держи репозиторий приватным, если серверы боевые.
