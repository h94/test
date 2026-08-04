# 前端專案目錄

此目錄包含各前端站台與管理工具的說明，涵蓋使用者面向的前台站台及後台管理工具。

---

## Confluence 業務文件（documents.md）

由 Confluence 整理、經人工審核的業務規範／技術設計摘要。引導師**優先讀此檔**，再讀 README / `ui-context.md`；與程式註解衝突時以 `documents.md` 為準。

> 全域目錄（僅在該站台無 `documents.md` 或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### frontend/{project}` 或關鍵字。

| 專案 | Confluence 摘要 |
|------|----------------|
| gametools | [documents.md](./gametools/documents.md) |
| mergefrontendsite | [documents.md](./mergefrontendsite/documents.md) |
| pricefrontendsite | [documents.md](./pricefrontendsite/documents.md) |
| pricefrontendsite_nuxt3 | [documents.md](./pricefrontendsite_nuxt3/documents.md) |
| stockfrontendsite | [documents.md](./stockfrontendsite/documents.md) |

前端架構（Vue3 / Nuxt3 等）見 [others/_index.md](../others/_index.md) 的 architecture；博彩／股票業務規則見 [game/_index.md](../game/_index.md)、[stock/_index.md](../stock/_index.md)。

---

## 1. 使用者前台（C 端）

面向一般使用者的公開站台。

| 專案 | README | 框架 | 說明 |
|------|--------|------|------|
| pricefrontendsite_nuxt3 | [pricefrontendsite_nuxt3/README.md](./pricefrontendsite_nuxt3/README.md) | Nuxt 3 / TypeScript | **主力前台（現役）**。inplayz 球王運彩分析平台，提供賽事預測、即時比分（SignalR）、排行榜、社群聊天、AI 分析、商城訂閱、會員管理 |
| pricefrontendsite | [pricefrontendsite/README.md](./pricefrontendsite/README.md) | Vue 2 | **舊版前台（已有 Nuxt 3 替代）**。inplayz 早期版本，含 SignalR 即時更新、第三方登入（Facebook/Google）、多語系 |
| stockfrontendsite | [stockfrontendsite/README.md](./stockfrontendsite/README.md) | Vue 3 / TypeScript | 股票資訊展示站台（`stock.zbdigital.net`），提供股票資料頁面與使用者登入，含 SEO 預渲染 |
| leaderboardfrontendsite | [leaderboardfrontendsite/README.md](./leaderboardfrontendsite/README.md) | Vue 3 / TypeScript | 排行榜前台站台，視覺化展示排行榜資料，支援多語系與主題切換 |

---

## 2. 後台管理工具（B 端）

面向內部人員的管理介面與工具。

| 專案 | README | 框架 | 說明 |
|------|--------|------|------|
| gamesettingfrontendsite | [gamesettingfrontendsite/README.md](./gamesettingfrontendsite/README.md) | Vue 2 | 遊戲設定管理後台，提供玩法/聯賽/商家設定的 CRUD 操作，含 SignalR 即時更新 |
| pricefrontendtools | [pricefrontendtools/README.md](./pricefrontendtools/README.md) | Vue 3 / TypeScript | 價格管理內部工具，提供定價查詢、批次更新、促銷設定、圖表統計與權限管理 |
| mergefrontendsite | [mergefrontendsite/README.md](./mergefrontendsite/README.md) | Vue 3 / TypeScript | 賽事合併管理前台，整合多個前端模組為統一入口，使用 Vite 建置 |
| gametools | [gametools/README.md](./gametools/README.md) | **Blazor WebAssembly** (.NET 6) | 賽事/聯盟/隊伍的合併、編輯、分割、翻譯、強制合併內部工具，串接 PriceCenter API |

---

## 技術棧速覽

| 專案 | 框架版本 | 建置工具 | Node | 部署方式 |
|------|---------|---------|------|---------|
| pricefrontendsite_nuxt3 | Nuxt 3 | Vite | 18 | Docker (node:18-alpine)，port 3000 |
| pricefrontendsite | Vue 2 | Vue CLI 4 | 10 | Docker → Nginx |
| stockfrontendsite | Vue 3 | Vue CLI 4 | 14 | Docker → Nginx |
| leaderboardfrontendsite | Vue 3 | Vue CLI 4 | 14 | Docker → Nginx |
| gamesettingfrontendsite | Vue 2 | Vue CLI 4 | 16 | Docker → Nginx |
| pricefrontendtools | Vue 3 | Vue CLI 4 | 14 | Docker → Nginx |
| mergefrontendsite | Vue 3 | Vite 3 | — | Docker → Nginx |
| gametools | Blazor WASM | .NET 6 | — | Docker (Linux) |

---

## 各站台補充文件

部分前端站台下備有 `ui-context.md`，描述該站台的 UI 操作功能清單（頁面、功能入口、操作流程等）。
AI 在處理以下任務時應主動查閱：

- 理解「這個按鈕 / 這個頁面是做什麼的」
- 前端任務分析（task-helper / task-understanding）
- 評估 UI 改動影響範圍

路徑規則：`./aidata/frontend/{serviceName}/ui-context.md`

若該站台目錄下無此檔案，代表尚未建立，可詢問開發者或略過。

---

## 套用原則

處理前端任務時，依使用者類型查閱對應專案：

| 任務類型 | 查閱專案 |
|---------|---------|
| inplayz 前台（賽事/預測/社群/商城） | `pricefrontendsite_nuxt3`（現役 Nuxt 3 版） |
| inplayz 前台（舊有 Vue 2 邏輯參考） | `pricefrontendsite` |
| 股票站台 | `stockfrontendsite` |
| 排行榜嵌入頁 | `leaderboardfrontendsite` |
| 遊戲設定後台 | `gamesettingfrontendsite` |
| 價格管理工具 | `pricefrontendtools` |
| 賽事合併後台 | `mergefrontendsite` |
| 賽事/聯盟/隊伍合併操作工具 | `gametools` |

---

## 後端服務相依（pricefrontendsite_nuxt3）

| 服務 | 用途 | PRD 位址 |
|------|------|---------|
| API Service（PriceCenterSite） | 主 REST API（會員/賽事/預測/社群/商城） | `https://inplayz.com/apiservice/api` |
| Hub Service（SignalR 即時比分） | 即時賽事比分推播，3 節點負載均衡 | `https://inplayz.com/hubservice/hub` |
| Game Live Hub（SignalR 聊天） | 社群聊天室即時通訊（GameLiveService） | `https://inplayz.com/gamelive/gamelivehub` |
| Sport API | 外部運動賽事資料 | `https://sports.zbdigital.net/apiservice/api` |
| NAS | 圖片/靜態資源（頭像、文章圖） | `/nas`（反向代理） |
