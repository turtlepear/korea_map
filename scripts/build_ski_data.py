#!/usr/bin/env python3
"""
抓取韓國滑雪場的範圍、雪道（含難度）與纜車，存成 data/ski-kr.json。
網頁用它來：在地圖上畫雪道、列出滑雪場、判斷足跡是不是在滑雪場裡（滑雪紀錄）。

由 GitHub Actions 每週執行一次（.github/workflows/update-poi.yml）。只用 Python 標準函式庫。

輸出格式：
{
  "time": ...,
  "resorts": [{"ko":..., "zh":..., "en":..., "lat":..., "lng":..., "bb":[s,w,n,e]}],
  "pistes":  [[difficulty, name, [[lat,lng], ...]], ...],   # difficulty：novice/easy/intermediate/advanced/expert/freeride/""
  "lifts":   [[type, name, [[lat,lng], ...]], ...]          # type：OSM aerialway 值
}
"""
import json, math, os, sys, time, urllib.parse, urllib.request

UA = "korea_map/1.0 (+https://github.com/turtlepear/korea_map)"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

QUERY = """[out:json][timeout:600];
area["ISO3166-1"="KR"][admin_level=2]->.kr;
nwr["landuse"="winter_sports"](area.kr);
out tags bb center;
way["piste:type"="downhill"](area.kr);
out tags geom;
way["aerialway"~"^(cable_car|gondola|chair_lift|mixed_lift|drag_lift|t-bar|j-bar|platter|rope_tow|magic_carpet)$"](area.kr);
out tags geom;
"""


def overpass(query, attempts=6):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for i in range(attempts):
        ep = ENDPOINTS[i % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=660) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            print(f"  {ep} failed: {e}; retrying in 60s", file=sys.stderr)
            time.sleep(60)
    raise RuntimeError(f"all Overpass attempts failed: {last}")


def _perp(p, a, b):
    """點 p 到線段 ab 的距離（公尺，近似平面）"""
    k = math.cos(math.radians(p[0]))
    ax, ay, bx, by, px, py = a[1] * k, a[0], b[1] * k, b[0], p[1] * k, p[0]
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay) * 111320
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy)) * 111320


def simplify(pts, tol=4.0):
    """Douglas–Peucker 化簡，容許誤差約 4 公尺"""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        best, idx = 0, -1
        for m in range(i + 1, j):
            d = _perp(pts[m], pts[i], pts[j])
            if d > best:
                best, idx = d, m
        if best > tol:
            keep[idx] = True
            stack += [(i, idx), (idx, j)]
    return [p for p, k in zip(pts, keep) if k]


def geom(el):
    g = [(round(p["lat"], 5), round(p["lon"], 5)) for p in el.get("geometry", []) if p]
    return [list(p) for p in simplify(g)]


def main():
    t0 = time.time()
    d = overpass(QUERY)
    resorts, pistes, lifts, seen = [], [], [], set()
    for el in d.get("elements", []):
        t = el.get("tags", {})
        if t.get("landuse") == "winter_sports":
            ko = t.get("name:ko") or t.get("name")
            if not ko:
                continue
            b = el.get("bounds")
            c = el.get("center") or ({"lat": el["lat"], "lon": el["lon"]} if "lat" in el else None)
            if not c:
                continue
            key = (ko, round(c["lat"], 2), round(c["lon"], 2))
            if key in seen:
                continue
            seen.add(key)
            resorts.append({
                "ko": ko,
                "zh": t.get("name:zh-Hant") or t.get("name:zh") or None,
                "en": t.get("name:en") or None,
                "lat": round(c["lat"], 5), "lng": round(c["lon"], 5),
                "bb": [round(b["minlat"], 5), round(b["minlon"], 5), round(b["maxlat"], 5), round(b["maxlon"], 5)] if b else None,
            })
        elif t.get("piste:type") == "downhill":
            g = geom(el)
            if len(g) >= 2:
                pistes.append([t.get("piste:difficulty", ""), t.get("piste:name") or t.get("name") or "", g])
        elif t.get("aerialway"):
            g = geom(el)
            if len(g) >= 2:
                lifts.append([t["aerialway"], t.get("name") or "", g])
    if len(pistes) < 50:
        raise RuntimeError(f"too few pistes ({len(pistes)}), keeping old data")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "ski-kr.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"time": int(time.time() * 1000), "resorts": resorts, "pistes": pistes, "lifts": lifts},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"ski-kr.json: {len(resorts)} resorts, {len(pistes)} pistes, {len(lifts)} lifts, "
          f"{os.path.getsize(path)//1024} KB, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
