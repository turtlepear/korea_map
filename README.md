# 🇰🇷 韓國旅遊地圖

在韓國用的旅遊地圖網頁：中韓英三語搜尋（自動翻譯）、步行／開車／大眾運輸路線、行程規劃、地鐵路線圖、離線地圖、匯率與計程車費估算。不需要任何 API key。

## 檔案說明

| 檔案 | 用途 |
|---|---|
| `index.html` | 網頁本體（地圖程式庫已內嵌） |
| `sw.js` | 離線功能（Service Worker） |
| `manifest.webmanifest` | 讓手機可以「加入主畫面」當 App 用 |
| `icon-*.png`、`apple-touch-icon.png` | App 圖示 |
| `.nojekyll` | 告訴 GitHub Pages 不要處理檔案 |

> 只開 `index.html` 也能用，但**離線地圖、同步連結、手機定位**要放到 https 網站上才會啟用。

## 部署到 GitHub Pages（免費，約 5 分鐘）

### 方法 A：用網頁上傳（不用指令）

1. 登入 [GitHub](https://github.com)，右上角 **＋ → New repository**。
2. Repository name 填 `korea-map`（或任何名字），選 **Public**，按 **Create repository**。
3. 在新 repo 頁面點 **uploading an existing file**，把這個資料夾裡的**所有檔案**拖進去（包含 `.nojekyll`；如果看不到隱藏檔可略過，不影響使用），按 **Commit changes**。
4. 到 repo 的 **Settings → Pages**：
   - Source 選 **Deploy from a branch**
   - Branch 選 **main**、資料夾 **/ (root)**，按 **Save**。
5. 等 1～2 分鐘，網址會是：`https://你的帳號.github.io/korea-map/`

### 方法 B：用 git 指令

```bash
cd korea-map
git init && git add -A && git commit -m "韓國旅遊地圖"
git branch -M main
git remote add origin https://github.com/你的帳號/korea-map.git
git push -u origin main
# 然後照上面第 4 步開啟 Pages
```

## 裝到手機

- **iPhone（Safari）**：打開網址 → 分享按鈕 → **加入主畫面**。
- **Android（Chrome）**：打開網址 → 右上角 ⋮ → **安裝應用程式**（或「加到主畫面」）。

第一次打開會詢問定位權限，請選「允許」。按 📍 時 iPhone 會另外詢問「方向」權限，允許後我的位置會出現方向箭頭。

## 出發前的建議

1. 在電腦上搜尋、收藏景點，用 **☰ → 📅 行程規劃** 排好每天行程。
2. **☰ → 🔄 收藏同步**，用手機掃 QR Code，收藏和行程就會帶到手機。
3. 在手機上（連 Wi-Fi 時）把地圖移到要去的區域，**☰ → 📥 離線地圖 → 下載這個範圍**。可以分區多次下載。
4. **☰ → 🚇 地鐵路線圖** 開一次，路線資料會存在手機裡。

## 更新網頁

改完 `index.html` 後重新上傳。如果改了 `sw.js`，記得把裡面的 `VER = 'kmap-v1'` 改成 `kmap-v2`，手機才會換成新版。

## 資料來源與使用規定

| 功能 | 來源 | 備註 |
|---|---|---|
| 地圖 | [OpenFreeMap](https://openfreemap.org)、OSM France、OpenTopoMap、Esri 衛星圖 | 資料 © [OpenStreetMap](https://www.openstreetmap.org/copyright) 貢獻者 |
| 搜尋 | Nominatim | 每秒最多 1 次查詢 |
| 附近設施、地鐵路線圖 | Overpass API | |
| 步行／開車／腳踏車路線 | [FOSSGIS OSRM](https://routing.openstreetmap.de/about.html) | 每秒最多 1 次查詢 |
| 大眾運輸 | [Transitous](https://transitous.org/sources/) | 限開源、非商業、低用量使用；網頁需附聯絡方式（「關於」頁面會自動顯示這個 GitHub repo 的連結） |
| 翻譯 | Google 翻譯公開端點、MyMemory | 非正式服務，可能失效 |
| 匯率 | [Exchange Rate API](https://www.exchangerate-api.com) | 每日更新 |
| 計程車費率 | 首爾市公告費率 | 估算值 |

所有資訊僅供參考；班次、營業時間、費用請以現場為準。

## 授權

MIT License（見 `LICENSE`）。內嵌的 Leaflet（BSD-2）、MapLibre GL JS（BSD-3）、maplibre-gl-leaflet（ISC）、qrcode-generator（MIT）各依其授權。
