#!/usr/bin/env python3
"""Собирает vless.json из публичных коллекторов конфигов.

Тянет списки vless://, оставляет только reality + tcp, определяет страну по IP,
берёт по PER_COUNTRY серверов на страну и пишет полные конфиги Xray.
Запускается по крону в GitHub Actions.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/main/sub/mix",
]

PER_COUNTRY = 20
MIN_PER_COUNTRY = 20
OUT = "vless.json"

COUNTRY_NAMES = {
    "AD": "Andorra", "AE": "UAE", "AF": "Afghanistan", "AL": "Albania", "AM": "Armenia",
    "AR": "Argentina", "AT": "Austria", "AU": "Australia", "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina", "BD": "Bangladesh", "BE": "Belgium", "BG": "Bulgaria",
    "BH": "Bahrain", "BR": "Brazil", "BY": "Belarus",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "CN": "China", "CO": "Colombia",
    "CR": "Costa Rica", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DK": "Denmark", "DO": "Dominican Republic", "DZ": "Algeria",
    "EC": "Ecuador", "EE": "Estonia", "EG": "Egypt", "ES": "Spain",
    "FI": "Finland", "FR": "France",
    "GB": "United Kingdom", "GE": "Georgia", "GR": "Greece",
    "HK": "Hong Kong", "HR": "Croatia", "HU": "Hungary",
    "ID": "Indonesia", "IE": "Ireland", "IL": "Israel", "IN": "India", "IQ": "Iraq",
    "IR": "Iran", "IS": "Iceland", "IT": "Italy",
    "JP": "Japan", "KE": "Kenya", "KG": "Kyrgyzstan", "KR": "South Korea", "KW": "Kuwait",
    "KZ": "Kazakhstan", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "MA": "Morocco", "MD": "Moldova", "ME": "Montenegro", "MK": "North Macedonia",
    "MT": "Malta", "MX": "Mexico", "MY": "Malaysia",
    "NG": "Nigeria", "NL": "Netherlands", "NO": "Norway", "NP": "Nepal", "NZ": "New Zealand",
    "OM": "Oman", "PA": "Panama", "PE": "Peru", "PH": "Philippines", "PK": "Pakistan",
    "PL": "Poland", "PT": "Portugal", "PY": "Paraguay",
    "QA": "Qatar", "RO": "Romania", "RS": "Serbia", "RU": "Russia",
    "SA": "Saudi Arabia", "SE": "Sweden", "SG": "Singapore", "SI": "Slovenia",
    "SK": "Slovakia", "TH": "Thailand", "TN": "Tunisia", "TR": "Turkey", "TW": "Taiwan",
    "UA": "Ukraine", "US": "United States", "UZ": "Uzbekistan",
    "VN": "Vietnam", "ZA": "South Africa",
}

RU_DOM = [
    "domain:bank.com", "domain:gov.ru",
    "domain:ru", "domain:su", "domain:рф", "domain:xn--p1ai",
]
LOCAL_IP = [
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "169.254.0.0/16", "224.0.0.0/4", "255.255.255.255",
]

IPV4 = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
UUID = re.compile(r"^[0-9a-f-]{36}$", re.I)


def get(url, timeout=90, attempts=3):
    last = ""
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "happ-sub-builder/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                buf = bytearray()
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
            return buf.decode("utf-8", "replace")
        except Exception as e:
            last = e
            print("fetch retry %d/%d: %s (%s)" % (n + 1, attempts, url, e))
            time.sleep(3)
    print("fetch failed:", url, last)
    return ""


def post_json(url, payload, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "happ-sub-builder/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def collect():
    servers = {}
    for url in SOURCES:
        try:
            body = get(url)
        except Exception as e:
            print("source failed:", url, e)
            continue
        body = body.replace("&amp;", "&")
        for raw in body.splitlines():
            line = raw.strip()
            if not line.startswith("vless://"):
                continue
            try:
                rest = line[len("vless://"):].split("#")[0]
                userhost, _, qs = rest.partition("?")
                uid, _, hostport = userhost.rpartition("@")
                host, _, port = hostport.rpartition(":")
                if not host or not port.isdigit() or not UUID.match(uid):
                    continue
                q = dict(urllib.parse.parse_qsl(qs))
                if q.get("security") != "reality" or q.get("type", "tcp") != "tcp":
                    continue
                pbk, sni = q.get("pbk", ""), q.get("sni", "")
                if not pbk or not sni:
                    continue
                key = host + ":" + port
                if key in servers:
                    continue
                servers[key] = {
                    "host": host, "port": int(port), "id": uid,
                    "pbk": pbk, "sid": q.get("sid", ""), "sni": sni,
                    "fp": q.get("fp") or "chrome", "flow": q.get("flow", ""),
                }
            except Exception:
                continue
    print("unique reality/tcp:", len(servers))
    return list(servers.values())


def geo(ips):
    found = {}
    chunk = 100
    for i in range(0, len(ips), chunk):
        part = ips[i:i + chunk]
        payload = [{"query": ip, "fields": "query,countryCode"} for ip in part]
        res = None
        for attempt in range(3):
            try:
                res = post_json("http://ip-api.com/batch", payload)
                if isinstance(res, dict):
                    res = None
                    raise RuntimeError("rate limited: %s" % res)
                break
            except Exception as e:
                print("geo batch retry %d/3: %s" % (attempt + 1, e))
                time.sleep(8)
        if not res:
            continue
        for item in res:
            cc = item.get("countryCode")
            if cc:
                found[item["query"]] = cc
        print("geo:", len(found), "/", len(ips))
        time.sleep(6)
    return found


def flag(cc):
    if not re.match(r"^[A-Z]{2}$", cc):
        return "🌐"
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in cc)


def build(entry, idx):
    s = entry["server"]
    reality = {
        "fingerprint": s["fp"],
        "publicKey": s["pbk"],
        "serverName": s["sni"],
    }
    if s["sid"]:
        reality["shortId"] = s["sid"]
    reality["show"] = False

    return {
        "remarks": entry["name"],
        "api": {"listen": "[::1]:10085", "services": ["StatsService"], "tag": "api"},
        "dns": {
            "hosts": {"domain:googleapis.cn": "googleapis.com"},
            "queryStrategy": "UseIP",
            "servers": [
                "1.1.1.1",
                {"address": "1.1.1.1", "domains": [], "port": 53},
                {"address": "8.8.8.8", "domains": list(RU_DOM), "port": 53},
            ],
        },
        "inbounds": [{
            "listen": "127.0.0.1",
            "port": 10808,
            "protocol": "socks",
            "settings": {
                "accounts": [{"user": "happ-socks", "pass": "p%d" % idx}],
                "auth": "password",
                "udp": True,
                "userLevel": 8,
            },
            "sniffing": {"destOverride": ["http", "tls", "quic"], "enabled": True},
            "tag": "socks",
        }],
        "log": {
            "access": "/data/user/0/com.happproxy/files/logs/access/access_log.txt",
            "dnsLog": True,
            "error": "/data/user/0/com.happproxy/files/logs/error/error_log.txt",
            "loglevel": "warning",
        },
        "outbounds": [
            {
                "mux": {"concurrency": -1, "enabled": False, "xudpConcurrency": 8, "xudpProxyUDP443": ""},
                "protocol": "vless",
                "settings": {
                    "address": s["host"],
                    "encryption": "none",
                    "flow": s["flow"],
                    "id": s["id"],
                    "level": 8,
                    "port": s["port"],
                    "security": "auto",
                },
                "streamSettings": {
                    "network": "tcp",
                    "realitySettings": reality,
                    "security": "reality",
                    "tcpSettings": {"header": {"type": "none"}},
                },
                "tag": "proxy",
            },
            {"protocol": "freedom", "tag": "direct"},
            {"protocol": "blackhole", "tag": "block"},
        ],
        "policy": {
            "levels": {"8": {"connIdle": 300, "downlinkOnly": 1, "handshake": 4, "uplinkOnly": 1}},
            "system": {"statsOutboundUplink": True, "statsOutboundDownlink": True},
        },
        "routing": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {"ip": ["1.1.1.1"], "outboundTag": "proxy", "port": "53"},
                {"ip": ["8.8.8.8"], "outboundTag": "direct", "port": "53"},
                {"domain": ["geosite:category-ads-all"], "outboundTag": "block"},
                {"domain": list(RU_DOM), "outboundTag": "direct"},
                {"ip": list(LOCAL_IP), "outboundTag": "direct"},
            ],
        },
        "stats": {},
    }


def main():
    servers = collect()
    ips = sorted({s["host"] for s in servers if IPV4.match(s["host"])})
    countries = geo(ips)

    by_country = {}
    for s in servers:
        cc = countries.get(s["host"])
        if not cc:
            continue
        by_country.setdefault(cc, []).append(s)

    picked = []
    for cc in sorted(by_country, key=lambda c: COUNTRY_NAMES.get(c, c)):
        arr = by_country[cc]
        if len(arr) < MIN_PER_COUNTRY:
            continue
        for i, s in enumerate(arr[:PER_COUNTRY], start=1):
            picked.append({
                "cc": cc,
                "name": "%s %s #%d" % (flag(cc), COUNTRY_NAMES.get(cc, cc), i),
                "server": s,
            })

    configs = [build(e, i) for i, e in enumerate(picked)]
    if len(configs) < 20:
        raise SystemExit("too few servers (%d), keeping old file" % len(configs))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)
        f.write("\n")

    summary = {}
    for c in configs:
        cc = c["remarks"].split(" ")[0]
        summary[cc] = summary.get(cc, 0) + 1
    print("written:", len(configs), "configs")
    print("countries:", {COUNTRY_NAMES.get(k, k): v for k, v in sorted(summary.items())})


if __name__ == "__main__":
    main()
