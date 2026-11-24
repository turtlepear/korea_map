# 🇰🇷 韓國旅遊地圖

🌐 網站：https://turtlepear.github.io/korea_map/

給台灣旅客在韓國用的旅遊地圖網頁，像 Google Map 一樣方便：中韓英三語搜尋（自動翻譯）、路線導航、地鐵、行程規劃、記帳、滑雪……全部免費，**不需要任何 API key**，可以加入手機主畫面當 App 用，也能離線使用。

## 功能

### 🔍 搜尋與地圖
- 中／韓／英三語搜尋，自動翻譯；地址找不到會自動放寬找附近
- 打字時立即列出常用地點（熱門景點、全韓國約 1.4 萬個景點、地鐵站、收藏、滑雪場），繁簡字都對得到；搜尋結果存在手機 7 天，再搜一次立刻出現
- 搜尋結果顯示「營業中／即將打烊／已打烊」
- 附近設施快捷鍵（地鐵站、便利商店、餐廳、咖啡廳、ATM、藥局、廁所……），下方有拉條可以左右滑動
- 地圖語言切換：中韓雙語、中文、韓文、英文、英韓、韓文＋羅馬拼音、中日
- 標準、明亮、地形、衛星地圖；深色模式；離線地圖下載
- 定位與方向箭頭

### 🧭 交通
- 步行、開車、腳踏車、大眾運輸路線，含語音導航
- 地鐵路線圖、最近的地鐵站與出口（首爾、釜山、大邱、光州、大田）
- 計程車費估算、「給司機看」的大字韓文地址、叫車
- 機場交通指南（仁川 T1／T2、金浦）

### 📅 行程
- 行程規劃：自動排順序、每站抵達時間、營業時間檢查
- 每小時天氣、幾點開始下雨、戶外景點的雨天備案（推薦附近室內景點）
- 韓國國定假日提醒、天氣與空氣品質
- 回程倒數：算出最晚幾點要出發去機場，可加入手機行事曆提醒

### ⛷️ 滑雪
- 14 個滑雪場：交通、接駁巴士、雪道數量
- 雪道地圖（依難度上色）與纜車路線
- 山頂／山腳分開看的山上天氣（強風、凍傷、能見度、新雪提醒）
- 滑雪紀錄：用 GPS 算趟數、總落差、最高速度
- 雪具尺寸換算、滑雪韓文句卡、滑雪行前清單

### 🎬 探索
- 附近美食、咖啡廳、景點的短影音：用在地人習慣的關鍵字（例如「성수 맛집」）一鍵打開 YouTube Shorts、Instagram、TikTok、Naver、小紅書
- 熱門景點、收藏（可分類）、搜尋紀錄

### 🗣️ 語言
- 韓文句卡（點餐、購物、交通、過敏、緊急、滑雪……），可放大給對方看並唸出來
- 對話翻譯（可語音輸入）、拍照翻譯（韓文文字辨識）

### 💰 花錢
- 旅費記帳（多人分帳）、每日預算、換匯紀錄與平均匯率
- 退稅計算、購物清單、匯率換算
- 入境台灣免稅額度提醒（購物 3 萬 5 千元、菸酒）與豬肉製品禁帶提醒

### 📔 紀念
- 旅行日記：打卡、照片；可一次匯入相簿照片，依照片的 GPS 或拍攝時間自動定位
- 今日足跡（GPS 軌跡）
- 旅程回顧：每天去了哪、走多少、花多少、照片，可匯出網頁或複製文字版

### 🧳 其他
- 緊急醫療資訊卡（中韓對照，只存在手機裡）
- 行前清單、尺寸換算、韓國常用 App 介紹
- 收藏、行程、記帳用 QR Code 同步到另一支手機

## 裝到手機

- **iPhone（Safari）**：打開網址 → 分享按鈕 → **加入主畫面**。
- **Android（Chrome）**：打開網址 → 右上角 ⋮ → **安裝應用程式**（或「加到主畫面」）。

第一次打開會詢問定位權限，請選「允許」。按 📍 時 iPhone 會另外詢問「方向」權限，允許後我的位置會出現方向箭頭。

## 出發前的建議

1. 在電腦上搜尋、收藏景點，用 **☰ → 📅 行程規劃** 排好每天行程。
2. **☰ → 🔄 收藏同步**，用手機掃 QR Code，收藏和行程就會帶到手機。
3. 在手機上（連 Wi-Fi 時）把地圖移到要去的區域，**☰ → 📥 離線地圖 → 下載這個範圍**。可以分區多次下載。
4. **☰ → ✅ 行前清單** 逐項確認；要滑雪的話按「⛷️ 加入滑雪清單」。
5. **☰ → ✈️ 回程倒數** 輸入回程航班，並「加入行事曆提醒」。

## 檔案說明

| 檔案 | 用途 |
|---|---|
| `index.html` | 網頁本體（地圖程式庫已內嵌） |
| `sw.js` | 離線功能（Service Worker） |
| `manifest.webmanifest`、`icon-*.png`、`apple-touch-icon.png` | 讓手機可以「加入主畫面」當 App 用 |
| `data/subway-*.json`、`data/exits-*.json` | 各城市地鐵路線、車站、出口 |
| `data/poi-kr.json` | 全韓國景點、古蹟、公園、博物館、商場的位置與範圍（搜尋、照片地名、雨天備案用） |
| `data/ski-kr.json` | 滑雪場範圍、雪道（含難度）與纜車 |
| `scripts/` | 產生 `data/` 的程式（只用 Python 標準函式庫） |
| `.github/workflows/` | 每週自動更新 `data/` 的 GitHub Actions |
| `.nojekyll` | 告訴 GitHub Pages 不要處理檔案 |

> 只開 `index.html` 也能用，但**離線地圖、同步連結、手機定位**要放到 https 網站上才會啟用。

## 資料自動更新

`data/` 由 GitHub Actions 每週一從 OpenStreetMap（Overpass API）重新抓取，有變更才會提交：

| 工作 | 檔案 | 腳本 |
|---|---|---|
| 更新地鐵路線與出口資料 | `data/subway-*.json`、`data/exits-*.json`、`data/index.json` | `scripts/build_transit_data.py` |
| 更新景點範圍與滑雪場資料 | `data/poi-kr.json`、`data/ski-kr.json` | `scripts/build_poi_data.py`、`scripts/build_ski_data.py` |

也可以到 **Actions** 頁面手動執行（Run workflow）。抓取失敗時會保留舊資料。

## 更新網頁

改完 `index.html` 後提交即可，GitHub Pages 約一分鐘內更新。如果改了要讓手機一定換成新版，把 `sw.js` 裡的 `VER = 'kmap-v…'` 數字加一；離線地圖圖塊放在另一個快取，不會因此被刪掉。

## 資料來源與使用規定

| 功能 | 來源 | 備註 |
|---|---|---|
| 地圖 | [OpenFreeMap](https://openfreemap.org)、OSM France、OpenTopoMap、Esri 衛星圖 | 資料 © [OpenStreetMap](https://www.openstreetmap.org/copyright) 貢獻者 |
| 搜尋、地名 | Nominatim | 每秒最多 1 次查詢；結果會快取 |
| 附近設施、地鐵、景點、雪道 | Overpass API | `data/` 每週預先抓好 |
| 步行／開車／腳踏車路線 | [FOSSGIS OSRM](https://routing.openstreetmap.de/about.html) | 每秒最多 1 次查詢 |
| 大眾運輸 | [Transitous](https://transitous.org/sources/) | 限開源、非商業、低用量使用；網頁需附聯絡方式（「關於」頁面會自動顯示這個 GitHub repo 的連結） |
| 天氣、空氣品質、高度 | [Open-Meteo](https://open-meteo.com) | 免費、非商業使用 |
| 翻譯 | Google 翻譯公開端點、MyMemory | 非正式服務，可能失效 |
| 文字辨識 | [tesseract.js](https://github.com/naptha/tesseract.js)（jsDelivr） | 第一次使用時下載 |
| 匯率 | [Exchange Rate API](https://www.exchangerate-api.com) | 每日更新 |
| 計程車費率 | 首爾市公告費率 | 估算值 |
| 入境免稅額度 | 財政部關務署、農業部動植物防疫檢疫署 | 規定可能變動，以官方公告為準 |
| 短影音 | YouTube、Instagram、TikTok、Naver、小紅書 | 只開啟各平台的搜尋頁，不擷取內容 |

所有資訊僅供參考；班次、營業時間、費用、滑雪場營運狀況請以現場或官方公告為準。

## 授權

MIT License（見 `LICENSE`）。內嵌的 Leaflet（BSD-2）、MapLibre GL JS（BSD-3）、maplibre-gl-leaflet（ISC）、qrcode-generator（MIT）各依其授權。
