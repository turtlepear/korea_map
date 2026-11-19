#!/usr/bin/env python3
"""
抓取韓國各城市的地鐵路線、車站與出口資料（OpenStreetMap / Overpass API），
存成 data/*.json，讓網頁不必在使用時即時查詢（公開 Overpass 伺服器常滿載）。

由 GitHub Actions 每週執行一次（.github/workflows/update-data.yml）。
只用 Python 標準函式庫。
"""
import json, math, os, sys, time, urllib.parse, urllib.request

UA = "korea_map/1.0 (+https://github.com/turtlepear/korea_map)"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
REGIONS = [  # 與網頁中的 SUBWAY_REGIONS 一致：[south, west, north, east]
    ("seoul",   [37.15, 126.45, 38.0, 127.45]),
    ("busan",   [35.0, 128.8, 35.4, 129.3]),
    ("daegu",   [35.75, 128.4, 36.0, 128.8]),
    ("gwangju", [35.07, 126.75, 35.25, 126.95]),
    ("daejeon", [36.25, 127.25, 36.45, 127.5]),
]
OUT = os.path.join(os.path.dirname(__file__), "..", "data")


def overpass(query, attempts=6):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for i in range(attempts):
        ep = ENDPOINTS[i % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # 429/406/502/逾時：等 30 秒後換下一台
            last = e
            print(f"  {ep} failed: {e}; retrying in 30s", file=sys.stderr)
            time.sleep(30)
    raise RuntimeError(f"all Overpass attempts failed: {last}")


def dist(a_lat, a_lng, b_lat, b_lng):
    r = 6371000
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lng - a_lng)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


LINE_ZH = [  # 韓文路線名（部分比對）→ 中文
    ("공항철도", "機場鐵路"), ("경의", "京義中央線"), ("수인분당", "水仁盆唐線"), ("신분당", "新盆唐線"),
    ("경춘", "京春線"), ("경강", "京江線"), ("서해", "西海線"), ("우이신설", "牛耳新設線"), ("신림", "新林線"),
    ("김포", "金浦黃金線"), ("의정부", "議政府輕軌"), ("용인", "龍仁輕軌"), ("에버라인", "龍仁輕軌"),
    ("GTX-A", "GTX-A"), ("GTX-C", "GTX-C"), ("동해", "東海線"), ("부산김해", "釜山金海輕軌"),
    ("셔틀트레인", "機場航廈電車"), ("자기부상", "仁川機場磁浮"),
]
CITY_ZH = {"인천": "仁川", "부산": "釜山", "대구": "大邱", "광주": "光州", "대전": "大田"}


def line_label(tags):
    import re
    ref = (tags.get("ref") or "").strip()
    name = (tags.get("name:ko") or tags.get("name") or "").split(":")[0].split("(")[0].strip()
    m = re.search(r"(인천|부산|대구|광주|대전)\D*?(\d)\s*호선", name)
    if m:
        return f"{CITY_ZH[m.group(1)]}{m.group(2)}號線"
    if ref.isdigit():
        return ref + "號線"
    for ko, zh in LINE_ZH:
        if ko in name:
            return zh
    if tags.get("name:zh"):
        return tags["name:zh"].split(":")[0].split("(")[0].strip()
    for pre in ("서울 지하철", "서울 도시철도", "수도권 전철"):
        name = name.replace(pre, "")
    return name.strip() or ref


def norm(s):
    s = (s or "").replace(" ", "").lower()
    return s[:-1] if s.endswith("역") else s


def exit_ref(t):
    if t.get("ref"):
        return str(t["ref"]).rstrip("번")
    import re
    for key, pat in (("name", r"(\d+(?:-\d+)?)\s*번\s*출"), ("description:ko", r"(\d+(?:-\d+)?)\s*번\s*출"),
                     ("description", r"(\d+(?:-\d+)?)\s*번\s*출"), ("name:en", r"exit\s*(\d+(?:-\d+)?)"),
                     ("description:en", r"gate\s*(\d+(?:-\d+)?)")):
        m = re.search(pat, t.get(key) or "", re.I)
        if m:
            return m.group(1)
    return None


def station_base(n):
    import re
    n = re.sub(r"\s*\d+(-\d+)?\s*번\s*출\S*.*$", "", n or "")
    n = re.sub(r"\s*(출입구|出口|exit).*$", "", n, flags=re.I)
    return n.strip()


def build_region(rid, bbox):
    b = ",".join(str(x) for x in bbox)
    print(f"[{rid}] lines + stations", file=sys.stderr)
    j = overpass(
        f'[out:json][timeout:240];relation["route"~"^(subway|light_rail)$"]({b});out geom;'
        f'node["railway"="station"](if:t["station"]=="subway"||t["subway"]=="yes"||t["station"]=="light_rail"||t["light_rail"]=="yes")({b});out;'
    )
    lines, stops, seen = [], [], set()
    for el in j["elements"]:
        if el["type"] != "relation":
            continue
        tags = el.get("tags", {})
        col, lab = tags.get("colour") or tags.get("color") or "#888", line_label(tags)
        for m in el.get("members", []):
            if m["type"] == "way" and m.get("geometry") and m["ref"] not in seen:
                seen.add(m["ref"])
                g, last = [], None
                for p in m["geometry"]:
                    if last is None or abs(p["lat"] - last["lat"]) + abs(p["lon"] - last["lon"]) > 0.00015:
                        g.append([round(p["lat"], 5), round(p["lon"], 5)]); last = p
                end = m["geometry"][-1]; g.append([round(end["lat"], 5), round(end["lon"], 5)])
                lines.append({"c": col, "l": lab, "g": g})
            elif m["type"] == "node" and m.get("lat") is not None and any(k in (m.get("role") or "") for k in ("stop", "platform")):
                stops.append((m["lat"], m["lon"], lab, col))
    stations = []
    for e in j["elements"]:
        if e["type"] != "node" or not e.get("tags", {}).get("name"):
            continue
        t = e["tags"]; ls = {}
        for s in stops:
            if abs(s[0] - e["lat"]) < 0.004 and abs(s[1] - e["lon"]) < 0.005 and dist(s[0], s[1], e["lat"], e["lon"]) < 300:
                ls[s[2]] = s[3]
        stations.append({"lat": e["lat"], "lng": e["lon"], "ko": t.get("name:ko") or t["name"],
                         "zh": t.get("name:zh-Hant") or t.get("name:zh"), "en": t.get("name:en"),
                         "lines": [{"l": k, "c": v} for k, v in ls.items()]})

    time.sleep(10)
    print(f"[{rid}] exits", file=sys.stderr)
    k = overpass(
        f'[out:json][timeout:240];(node["railway"="subway_entrance"]({b});node["railway"="train_station_entrance"]({b}););out;'
        f'node["railway"="station"]({b});out;'
    )
    st_nodes = [{"lat": e["lat"], "lng": e["lon"], "ko": e["tags"].get("name:ko") or e["tags"]["name"],
                 "zh": e["tags"].get("name:zh-Hant") or e["tags"].get("name:zh")}
                for e in k["elements"] if e.get("tags", {}).get("railway") == "station" and e["tags"].get("name")]
    exits = []
    for e in k["elements"]:
        t = e.get("tags", {})
        if "entrance" not in (t.get("railway") or ""):
            continue
        ref = exit_ref(t)
        base = station_base(t.get("name") or t.get("description:ko") or t.get("description"))
        st = None
        if base:
            st = next((s for s in st_nodes if norm(s["ko"]) == norm(base)), None)
        if not st:
            best = 450
            for s in st_nodes:
                d = dist(s["lat"], s["lng"], e["lat"], e["lon"])
                if d < best:
                    best, st = d, s
        if not ref and not st and not base:
            continue
        el = t.get("wheelchair") == "yes" or "엘리베이터" in (t.get("name") or "") + (t.get("description") or "")
        exits.append([round(e["lat"], 6), round(e["lon"], 6), ref or "",
                      (st or {}).get("ko") or base or "", (st or {}).get("zh") or "", 1 if el else 0])

    return {"time": int(time.time() * 1000), "lines": lines, "stations": stations}, {"time": int(time.time() * 1000), "exits": exits}


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {}
    for rid, bbox in REGIONS:
        try:
            sub, ex = build_region(rid, bbox)
        except Exception as e:
            print(f"[{rid}] FAILED, keeping previous data: {e}", file=sys.stderr)
            continue
        with open(os.path.join(OUT, f"subway-{rid}.json"), "w", encoding="utf-8") as f:
            json.dump(sub, f, ensure_ascii=False, separators=(",", ":"))
        with open(os.path.join(OUT, f"exits-{rid}.json"), "w", encoding="utf-8") as f:
            json.dump(ex, f, ensure_ascii=False, separators=(",", ":"))
        index[rid] = {"stations": len(sub["stations"]), "segments": len(sub["lines"]), "exits": len(ex["exits"])}
        print(f"[{rid}] {index[rid]}", file=sys.stderr)
        time.sleep(15)
    if index:
        prev = {}
        p = os.path.join(OUT, "index.json")
        if os.path.exists(p):
            prev = json.load(open(p, encoding="utf-8")).get("regions", {})
        prev.update(index)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"updated": time.strftime("%Y-%m-%d", time.gmtime()), "regions": prev}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
