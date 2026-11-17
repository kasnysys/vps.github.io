# vless · happ (json)

Конфиги для [Happ](https://happ.su) (Xray-core): VLESS + Reality, TCP, 3 сервера.
Только JSON — ссылок `vless://` здесь нет.

## Ссылка подписки

```
https://kasnysys.github.io/vps.github.io/vless.json
```

Happ → **Подписки** → «+» → **Ссылка** → вставить → «Обновить».

Если Pages не работает или Happ не ест json по ссылке — тот же файл напрямую с GitHub:

```
https://raw.githubusercontent.com/kasnysys/vps.github.io/main/vless.json
```

Или скачай `vless.json` и импортируй файлом: Happ → «+» → **Из файла**.

## Файлы

- `vless.json` — массив из трёх полных конфигов Xray (NL, FI, CH). Это и есть подписка.
- `index.html` — страница со ссылкой подписки и кнопками «JSON» (копируют конфиг одного сервера в буфер).
- `README.md` — этот файл.

Если Happ ругается на массив — вырежи нужный блок `{ ... }` в отдельный `.json`.

## Серверы

| # | Сервер | Адрес | Порт |
|---|---|---|---|
| 0 | 🇳🇱 Нидерланды | nl-s-2-b1.pythonmakemigreat.wiki | 443 |
| 1 | 🇫🇮 Финляндия | fi-b2.golangwikito.cfd | 443 |
| 2 | 🇨🇭 Швейцария | 85.155.183.228 | 443 |

Все: `tcp`, `security=reality`, `fp=firefox`, `flow=xtls-rprx-vision`, socks-инбаунд `127.0.0.1:10808`.

## Обход

В `routing` российские домены и IP идут **напрямую**, мимо прокси:

- `domain:ru`, `domain:su`, `domain:рф`, `domain:xn--p1ai`
- `domain:gov.ru`, `domain:bank.com`
- локальные сети `10/8`, `172.16/12`, `192.168/16`, `169.254/16`

Остальное — через VPN. Реклама (`geosite:category-ads-all`) — в блок.

> Категорий `geosite:ru` / `geoip:ru` в конфигах нет специально: в geosite.dat,
> который идёт с Happ, секции `RU` не бывает, и ядро падает с ошибкой
> «отсутствует секция RU». Обход по России сделан обычными доменами `.ru`, `.su`, `.рф`.

> В конфигах лежат реальные `id` и `publicKey`. Кто увидит файл — сможет подключиться к серверам. Держи репозиторий приватным, если серверы боевые.
