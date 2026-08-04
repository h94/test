# PriceFrontEndSite – 前端服務目錄

## 概述

PriceFrontEndSite 為一個價格展示前端應用，提供使用者瀏覽、查詢與互動的介面。專案建置於 Vue 2 生態系，並透過 Docker 映像部署於 Docker Swarm 生產環境中。

## 主要功能

- 價格資訊展示與即時更新（透過 SignalR / WebSocket）
- 支援第三方帳號登入（Facebook、Google）
- 圖片與檔案檢視（v-viewer）
- 多語系支援（vue-i18n）
- 輪播與捲軸優化（vue-carousel、vue-smooth-scrollbar）
- 響應式設計（Bootstrap 4 + BootstrapVue）
- 後端 API 串接（axios）
- 表單與驗證（Bootstrap 表單元件）
- 靜態資源壓縮（Docker 建置時將 img、js、css 打包為 zip）

## 技術棧

- **前端框架**：Vue 2 (v2.6.12)
- **建置工具**：Vue CLI 4.x
- **狀態管理**：Vuex (v3.4.0)
- **路由**：Vue Router (v3.2.0)
- **UI 庫**：Bootstrap 4 + BootstrapVue
- **即時通訊**：@aspnet/signalr / @microsoft/signalr (WebSocket)
- **HTTP 客戶端**：axios (v0.21.1)
- **圖示**：Font Awesome (Free 系列)
- **樣式預處理**：Sass (dart-sass)
- **語言國際化**：vue-i18n
- **容器化**：Docker (base image node:10, 最終 nginx 服務)
- **部署平台**：Docker Swarm (生產環境)
- **版本控制**：GitLab

## 組態與部署注意

- **環境變數**：專案不包含 `.env` 檔案，建置時需透過 CI/CD 注入（Dockerfile 已清除 `.env`）。請確認以下環境變數於建置階段正確設置：
  - `VUE_APP_API_BASE_URL`（後端 API 網址）
  - `VUE_APP_SIGNALR_URL`（SignalR 中樞位址）
  - 其他自訂變數（參考 `process.env` 使用處）
- **Docker 映像**：使用多階段建置，最終映像僅包含 nginx 與前端靜態檔案，並將 `img/`、`js/`、`css/` 目錄額外壓縮為 zip 檔（可能供下載或離線使用）。
- **Nginx 配置**：需自訂 `docker-config/nginx.conf`，建議包含 Gzip 壓縮、靜態檔案快取設定及 SPA 路由 Fallback。
- **部署叢集**：生產環境為 Docker Swarm，Portainer 識別鍵為 `PRD_Docker_Swarm`。服務名稱於 Swarm 中應為 `pricefrontendsite`。
- **注意事項**：
  - Node 版本鎖定於 10，若有升級需求請一併調整建置基礎映像。
  - `vue-cli-service build` 產生的 `dist/` 內容直接複製至 nginx 的 `/app` 目錄。
  - 由於使用 `@aspnet/signalr`（已棄用），建議評估遷移至 `@microsoft/signalr`。

## 相關連結

- **GitLab 倉庫**：[https://git.zbdigital.net/biz/pricefrontendsite.git](https://git.zbdigital.net/biz/pricefrontendsite.git)
- **Portainer 生產環境**：`PRD_Docker_Swarm` 叢集上的 `pricefrontendsite` 服務
- **Nginx 配置範本**：`docker-config/nginx.conf`（存放於倉庫中）
- **CI/CD 管線**：請參考 GitLab CI 配置（若有）