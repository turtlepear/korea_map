#!/usr/bin/env python3
"""
抓取全韓國有名稱的景點範圍（景點、古蹟、公園、市場、商場、博物館、百貨公司、電影院），
存成 data/poi-kr.json。網頁用它來：
  1) 幫匯入的照片取地名（照片在哪個景區裡、附近有什麼景點）
  2) 雨天備案：找附近的室內景點
不必在使用時即時查詢 Overpass（公開伺服器常常很慢或滿載）。

由 GitHub Actions 每週執行一次（.github/workflows/update-data.yml）。只用 Python 標準函式庫。

輸出格式：{"time":..., "fields":[...], "items":[[lat,lng,s,w,n,e,zh,ko,kind,oh], ...]}
  s,w,n,e：範圍（只有面狀的景點才有，點狀為 null）
  kind：t 景點／主題樂園／動物園、u 博物館／水族館、g 美術館、v 觀景點、h 古蹟、
        p 公園／庭園、m 傳統市場、l 購物中心、d 百貨公司、c 電影院
  oh：營業時間（只有室內類才保留）
"""
import json, math, os, sys, time, urllib.parse, urllib.request

UA = "korea_map/1.0 (+https://github.com/turtlepear/korea_map)"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

QUERY = """[out:json][timeout:900];
area["ISO3166-1"="KR"][admin_level=2]->.kr;
(
  nwr["tourism"~"^(attraction|museum|theme_park|zoo|aquarium|gallery|viewpoint)$"]["name"](area.kr);
  nwr["historic"~"^(castle|palace|fort|city_gate|citywalls|monument|memorial|archaeological_site|tomb|ruins|manor)$"]["name"](area.kr);
  nwr["leisure"~"^(park|garden)$"]["name"](area.kr);
  nwr["amenity"="marketplace"]["name"](area.kr);
  nwr["shop"~"^(mall|department_store)$"]["name"](area.kr);
  nwr["amenity"="cinema"]["name"](area.kr);
);
out tags bb;
"""
MAJOR_T = {"attraction", "theme_park", "zoo"}
MUSEUM = {"museum", "aquarium"}
SMALL_PARK = ("어린이공원", "소공원", "쌈지공원", "근린공원")


def overpass(query, attempts=6):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for i in range(attempts):
        ep = ENDPOINTS[i % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=960) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # 429/406/502/逾時：等 60 秒後換下一台
            last = e
            print(f"  {ep} failed: {e}; retrying in 60s", file=sys.stderr)
            time.sleep(60)
    raise RuntimeError(f"all Overpass attempts failed: {last}")


def diag_m(s, w, n, e):
    dy = (n - s) * 111320
    dx = (e - w) * 111320 * math.cos(math.radians((n + s) / 2))
    return math.hypot(dx, dy)


def kind_of(t):
    tour, hist = t.get("tourism", ""), t.get("historic", "")
    if tour in MAJOR_T: return "t"
    if tour in MUSEUM: return "u"
    if hist: return "h"
    if tour == "gallery": return "g"
    if t.get("shop") == "department_store": return "d"
    if t.get("amenity") == "cinema": return "c"
    if t.get("shop") == "mall": return "l"
    if t.get("amenity") == "marketplace": return "m"
    if t.get("leisure") in ("park", "garden"): return "p"
    if tour == "viewpoint": return "v"
    return None


def r5(x):
    return None if x is None else round(x, 5)


def main():
    t0 = time.time()
    d = overpass(QUERY)
    items, seen = [], set()
    for el in d.get("elements", []):
        t = el.get("tags", {})
        k = kind_of(t)
        if not k:
            continue
        ko = t.get("name:ko") or t.get("name")
        zh = t.get("name:zh-Hant") or t.get("name:zh-TW") or t.get("name:zh") or t.get("name:en")
        if not ko:
            continue
        if el["type"] == "node":
            lat, lng, bb = el["lat"], el["lon"], (None, None, None, None)
        else:
            b = el.get("bounds")
            if not b:
                continue
            s, w, n, e = b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]
            lat, lng, bb = (s + n) / 2, (w + e) / 2, (s, w, n, e)
            size = diag_m(s, w, n, e)
            if k == "p" and (size < 150 or ko.endswith(SMALL_PARK) and size < 400):
                continue  # 太小的社區公園不算景點
            if size > 30000:
                bb = (None, None, None, None)  # 範圍太大（跨城市）的只當成一個點
        key = (ko, round(lat, 3), round(lng, 3))
        if key in seen:
            continue
        seen.add(key)
        oh = t.get("opening_hours") if k in ("t", "u", "g", "d", "c", "l", "m") else None
        items.append([r5(lat), r5(lng), *[r5(x) for x in bb], zh if zh and zh != ko else None, ko, k, oh])
    if len(items) < 1000:
        raise RuntimeError(f"too few items ({len(items)}), keeping old data")
    items.sort(key=lambda x: (x[0], x[1]))
    os.makedirs(OUT, exist_ok=True)
    out = {"time": int(time.time() * 1000), "fields": ["lat", "lng", "s", "w", "n", "e", "zh", "ko", "kind", "oh"], "items": items}
    path = os.path.join(OUT, "poi-kr.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    counts = {}
    for x in items:
        counts[x[8]] = counts.get(x[8], 0) + 1
    print(f"poi-kr.json: {len(items)} items {counts}, {os.path.getsize(path)//1024} KB, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
