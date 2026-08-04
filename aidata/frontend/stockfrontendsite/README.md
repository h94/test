# Stockfrontendsite 內部服務目錄

## 概述
Stockfrontendsite 是一個前端網站服務，部署於 Production 環境的 Docker Swarm 叢集。提供股票相關資訊的展示與使用者登入功能，主要對應網域為 `stock.zbdigital.net` 及 `www.zbdigital.net`。採用 Vue 3 框架建構，透過 Nginx 提供靜態資源服務。

## 主要功能
- **股票資訊頁面**：呈現股票相關資料（配置於 `stock.zbdigital.net`）
- **使用者登入**：提供 `/login` 路由進行身份驗證
- **SEO 支援**：內含 `sitemap.xml` 及 `prerender-spa-plugin`（預渲染 SPA 頁面）
- **社交登入整合**：透過 `auth-social` 套件支援第三方登入
- **圖示系統**：採用 Font Awesome 6 免費圖示庫

## 技術棧
| 類別       | 技術                                      |
|------------|-------------------------------------------|
| 前端框架   | Vue 3 (Composition API)                   |
| 語言       | TypeScript 4.1                            |
| 狀態管理   | Vuex 4                                    |
| 路由       | Vue Router 4                              |
| HTTP 客戶端| Axios 0.26                                |
| CSS 預處理 | Sass (dart-sass) + node-sass 6            |
| 建置工具   | Vue CLI 4.5 (webpack 4)                   |
| 容器化     | Docker (Node 14 建置 → Nginx 執行)        |
| 部署平台   | Docker Swarm (Production)                 |

## 組態與部署注意

### 建置流程
- **多階段 Dockerfile**：
  - 第一階段使用 `node:14` 安裝依賴、修正 Debian stretch 套件源（因 oldstable 已封存），執行 `npm run build`。
  - 第二階段使用 `nginx` 作為基底，將建置產物 `dist/` 複製至 `/app`，並掛載自訂 Nginx 配置 (`docker-config/nginx.conf`)。
- **注意**：Dockerfile 中強制修改 `sources.list` 為 `archive.debian.org`，並刪除 `stretch-updates`，確保建置環境可獲取套件。

### 環境變數
- 專案無 `.env` 檔案，建置時由 Dockerfile 移除 `.env`（`RUN rm -rf .env`），環境變數應於執行階段注入（如 Nginx 反向代理或容器環境變數）。

### 依賴相容性
- `node-sass` 版本 6 需對應 Node 14。
- `sass-loader` 使用 10 版，與 Vue CLI 4 相容。
- 若在 Windows 本機開發，需設定 `NODE_OPTIONS=--openssl-legacy-provider`（已於 script 中定義 `build-set` 與 `start`）。

### 部署注意
- Portainer 標籤：`PRD_Docker_Swarm|swarm|stockfrontendsite|stockfrontendsite_Stockfrontendsite`，表示此服務對應的 Stack 名稱為 `stockfrontendsite`。
- 需確保 Docker Swarm 服務名稱與 Portainer 群組一致。
- 自訂 Nginx 配置文件 `docker-config/nginx.conf` 需存在於專案根目錄（Dockerfile 中複製至 `/etc/nginx/nginx.conf`）。

## 相關連結
- **GitLab 儲存庫**：[https://git.zbdigital.net/biz/stockfrontendsite.git](https://git.zbdigital.net/biz/stockfrontendsite.git)
- **正式環境網站**：
  - [https://stock.zbdigital.net](https://stock.zbdigital.net)
  - [https://www.zbdigital.net](https://www.zbdigital.net)