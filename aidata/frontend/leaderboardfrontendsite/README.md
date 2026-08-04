# Leaderboard Frontend Site 服務目錄

## 概述
Leaderboard Frontend Site 為一個 Vue 3 前端應用，提供排行榜前端頁面。採用 TypeScript 開發，透過 Vue CLI 建置，最終以靜態檔案形式部署於 Nginx 容器中。目前運行於 **PRD_Docker_Swarm** 叢集，作為 Docker Swarm 服務（`leaderboardfrontendsite`）。

## 主要功能
- 排行榜資料視覺化與展示
- 支援多語系與主題切換（透過 Vuex 狀態管理） *（多語系支援需人工確認，方案後端或前端未發現明確 i18n 依賴）*
- 與後端 API 透過 Axios 非同步通訊
- 使用 Vue Router 實現前端路由
- 整合 Font Awesome 圖示庫
- 支援 Cookie 處理（js-cookie、vue3-cookies）
- 建構於 Vue CLI 4.5，搭配 TypeScript 嚴格模式

## 技術棧
| 類別 | 技術 |
|------|------|
| 框架 | Vue 3 + TypeScript |
| 建置工具 | Vue CLI 4.5 |
| 狀態管理 | Vuex 4 |
| 路由 | Vue Router 4 |
| HTTP 客戶端 | Axios |
| 圖示 | Font Awesome 6 (free) |
| UI 樣式 | Sass (node-sass v6 + sass-loader v10) |
| 容器化 | Docker (Node 14 建置 → Nginx 運行) |
| 部署平台 | Docker Swarm (Production) |

## 組態與部署注意
- **環境變數**：透過 `ENV_MODE` 建置參數切換環境模式（dev/prod）。Dockerfile 內實際執行 `npm run build --mode=${ENV_MODE}`。請留意：package.json 的預設建置腳本使用 `$npm_config_mode`，兩者不一致，實際生效行為需人工確認，建議於 CI/CD 明確設定。
- **Node 版本相容性**：專案 README.md 標注 v14 與 v16 均可，但 Dockerfile 明確使用 `node:14`，生產環境應以 Dockerfile 為準，請勿隨意更動基礎映像。
- **Nginx 組態**：客製化配置檔案位於 `docker-config/nginx.conf`，為靜態檔案服務基礎設定。
- **Docker 多階段建置**：第一階段使用 Node 14 編譯前端資源，第二階段以 Nginx 映像提供 `/app` 目錄中的 dist 內容。
- **開發環境**：執行 `npm run serve` 啟動開發伺服器（固定 mode=dev）。
- **程式碼檢查**：使用 ESLint + TypeScript 規則，執行 `npm run lint`。

## 相關連結
- **原始碼倉庫**：[GitLab – leaderboardfrontendsite](https://git.zbdigital.net/biz/leaderboardfrontendsite.git)
- **Docker Swarm 服務**：`leaderboardfrontendsite`（PortainerKey: PRD_Docker_Swarm）
- **文件**：專案內附 `README.md`，包含基本開發指令與 Node 版本提示。