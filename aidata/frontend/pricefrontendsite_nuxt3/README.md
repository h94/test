# pricefrontendsite_nuxt3 前端專案

- **Git Repository**：[https://git.zbdigital.net/biz/pricefrontendsite_nuxt3.git](https://git.zbdigital.net/biz/pricefrontendsite_nuxt3.git)

## 職責

提供會員在 **inplayz（球王運彩分析即時比分）** 平台進行賽事預測、即時比分追蹤、排行榜、社群聊天、商城訂閱、會員管理的 Web 介面。目標使用者為體育博彩愛好者與預測高手。

---

## 技術棧

| 類別 | 技術 |
|---|---|
| 框架 | Nuxt 3（`^3.11.2`），純 SPA 模式（`ssr: false`） |
| 語言 | TypeScript |
| 狀態管理 | Pinia（`^2.1.6`）+ pinia-plugin-persistedstate |
| HTTP 客戶端 | Nuxt `$fetch` + Axios（上傳用） |
| 即時通訊 | Microsoft SignalR（`@microsoft/signalr ^8.0.0`）+ msgpack 壓縮 |
| UI 元件 | 自製元件 + Nuxt Icon（mdi / tabler / material-symbols 等多套圖示集） |
| 圖片處理 | `@nuxt/image`、`vue-cropper`、WebP 自動轉換 |
| 圖表 | Chart.js + vue-chart-3 |
| 樣式 | SCSS（`sass ^1.63.3`） |
| 多語系 | `@nuxtjs/i18n ^8.1.1`，語系資料由 Google Sheets 同步 |
| 其他套件 | nuxt-swiper、mitt（事件匯流排）、pako（Gzip 解壓）、timeago.js、qs |
| 打包 | Vite（Nuxt 3 內建） |
| 容器化 | Docker（node:18-alpine），port 3000 |
| GA / 廣告 | Google Tag Manager（`G-BFYFCWH3GH`）、Google AdSense |

---

## 專案結構重點

```
pricefrontendsite_nuxt3/
├── apis/               # 所有 API 呼叫模組（依業務領域分檔）
│   ├── index.ts        # 共用 $priceCenterSite / $http 封裝
│   ├── game.ts         # 賽事資料
│   ├── predict.ts      # 預測相關
│   ├── user.ts         # 會員
│   ├── chat.ts         # 聊天室 / 社群
│   ├── ai.ts           # AI 分析報告
│   ├── odd.ts          # 賠率
│   ├── payment.ts      # 付款 / 訂閱
│   └── ...（共 20+ 模組）
├── components/         # 全域共用元件（Header、Footer、廣告欄、側邊欄等）
├── composables/        # 業務邏輯 Composables
│   ├── game/           # HubSocket（SignalR）、LiveGame、GameOdd...
│   ├── chat/           # Room、Moderator、Identity
│   ├── predict/        # 預測邏輯
│   └── global/         # Cookie、LocalStorage、Device、Debounce...
├── config/             # 靜態設定常數
│   ├── global/Http.ts  # API Domain 切換邏輯（依環境 cookie）
│   ├── global/WebSocket.ts  # HubService URL（3 個 load-balanced 節點）
│   └── global/GameType.ts   # 賽事類型定義
├── layouts/            # 各頁面佈局（home、main、chat、shop、user...）
├── middleware/         # Nuxt Middleware
│   ├── user.global.ts  # 全域使用者驗證
│   ├── setSeoData.global.ts # 全域 SEO 設定
│   └── router-record.global.ts
├── pages/[country]/    # 頁面路由（country 為動態地區前綴）
├── plugins/            # Nuxt Plugin（directive、domain、timeago）
├── store/              # Pinia Store（user、game、hub、chat、predict、payment...）
├── types/              # TypeScript 型別定義
├── I18n/locales/       # 多語系 JSON（由 Google Sheets 同步）
├── assets/icons/       # 自訂 inplayz 圖示集
├── dockerfile          # Docker 建置設定
└── .env.{local|dev|pre|prd}  # 各環境變數
```

---

## 環境設定

### 環境變數說明（`.env.*`）

| 變數 | 用途 |
|---|---|
| `VITE_APP_ENV` | 環境識別（local / dev / pre / prd） |
| `VITE_APP_API_DOMAIN` | 主 API 服務網址 |
| `VITE_APP_CHAT` | SignalR Chat Hub 網址 |
| `VITE_APP_API_SPORT` | 外部運動賽事資料 API |
| `VITE_APP_IMG_URL` | NAS 圖片伺服器路徑（`/nas`） |
| `VITE_APP_DOCS_URL` | 文件伺服器路徑（`/docs`） |
| `VITE_APP_FB_ID` | Facebook App ID |

### 各環境 API Domain

| 環境 | API Domain |
|---|---|
| local | `http://localhost:5000/api` |
| dev | `http://192.168.9.233:22307/api` |
| pre | `https://test.inplayz.com/apiservice/api` |
| prd | `https://inplayz.com/apiservice/api` |

---

## 本地開發

### 安裝相依套件
```bash
npm install
```

### 啟動開發伺服器（port 8080）
```bash
npm run local   # 使用 .env.local
npm run dev     # 使用 .env.dev
npm run pre     # 使用 .env.pre
npm run prd     # 使用 .env.prd
```

### 多語系同步（從 Google Sheets 拉取）
```bash
npm run i18n-sync
```

---

## 建置與部署

### 建置
```bash
npm run build:local
npm run build:dev
npm run build:pre
npm run build:prd
```

### 啟動 Production Server
```bash
npm run start    # node .output/server/index.mjs
```

### Docker 建置
```bash
docker build --build-arg ENV_MODE=prd -t pricefrontendsite_nuxt3 .
# 容器開放 port 3000
```

---

## 主要頁面路由

所有頁面皆以 `/:country/` 開頭（地區動態前綴，例如 `/tw/`）：

| 路由 | 功能 |
|---|---|
| `/` | 首頁 |
| `/:country/live-game` | 即時比賽 |
| `/:country/pre-game` | 未來賽事 |
| `/:country/result-game` | 賽事結果 |
| `/:country/predict-game` | 預測玩法 |
| `/:country/predict-popular` | 熱門預測 |
| `/:country/leaderboard` | 排行榜 |
| `/:country/master` | 大師排行 |
| `/:country/king` | 球王榜 |
| `/:country/community` | 社群討論區 |
| `/:country/chat` | 聊天室 |
| `/:country/analysis/...` | 賽事深度分析 |
| `/:country/article` | 文章專區 |
| `/:country/news` | 新聞 |
| `/:country/ai-report` | AI 分析報告 |
| `/:country/event/...` | 活動（各聯盟連勝挑戰） |
| `/:country/shop` | 商城 / 訂閱方案 |
| `/:country/users/...` | 會員中心（個人資料、追蹤、訂閱記錄、提款等） |
| `/:country/notification` | 通知 |
| `/:country/feedback` | 意見回饋 |
| `/:country/uwin` | UWin 活動 |

---

## 後端服務相依

| 服務名稱 | 說明 | PRD 位址 | DEV 位址 |
|---|---|---|---|
| **API Service**（主後端） | REST API，涵蓋用戶、預測、賽事、社群、商城等所有業務 | `https://inplayz.com/apiservice/api` | `http://192.168.9.233:22307/api` |
| **Hub Service**（SignalR 即時比分） | WebSocket，負載平衡 3 節點（`hubservice` / `hubservice2` / `hubservice3`） | `https://inplayz.com/hubservice/hub` | 同 PRD |
| **Game Live Hub**（SignalR 聊天） | 社群聊天室即時通訊 | `https://inplayz.com/gamelive/gamelivehub` | `http://192.168.9.232/gamelivehub/hub` |
| **Sport API**（外部運動資料） | 外部賽事資料來源 | `https://sports.zbdigital.net/apiservice/api` | 同 PRD |
| **NAS**（圖片檔案伺服器） | 用戶頭像、文章圖片等靜態資源 | `/nas`（反向代理） | 同 PRD |
| **Docs 服務** | 文件資源 | `/docs`（反向代理） | 同 PRD |
| **Forum Service** *(備用，已停用)* | 論壇服務 | — | `http://192.168.9.232/forumservice` |
| **Python Service** *(備用，已停用)* | AI / 分析後端 | — | `http://192.168.9.233:22331/api/v1` |

---

## i18n 多語系管理

語系 JSON 由 Google Sheets 統一管理，透過腳本同步至 `I18n/locales/`：

- Google Sheets：`https://docs.google.com/spreadsheets/d/1-5859KlCCkpdxP8lK-CDjDlsFNoqetYPU9uneq7yDu0`
- 同步指令：`npm run i18n-sync`

---

## 即時通訊架構

使用 **Microsoft SignalR** 建立 WebSocket 連線，分兩條通道：

1. **Game Hub**（即時比分）：3 個 load-balanced 節點，由 `tokenSum % 3` 自動選擇線路
2. **Chat Hub**（聊天室）：用於社群聊天室即時訊息推送