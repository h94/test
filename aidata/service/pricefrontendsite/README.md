# PriceFrontendSite

## 概述
PriceFrontendSite 為面向終端客戶的前端網站，負責報價資訊展示、商品瀏覽與即時價格更新。服務以容器化形式部署於 Docker Swarm 叢集，是業務報價流程中的關鍵互動介面。

## 主要功能
- 即時價格與行情展示，透過 SignalR 維持雙向通訊
- 商品圖片與多媒體檢視 (v-viewer)
- 多語系介面 (vue-i18n)，支援在地化內容
- 社群帳號登入 (Facebook、Google) 整合
- 流暢的滾動與輪播式內容呈現 (vue-carousel、perfect-scrollbar)
- 用戶端指紋採集 (FingerprintJS) 輔助安全與追蹤

## 技術棧
- **前端框架**：Vue 2.x，搭配 Vue Router 與 Vuex 狀態管理
- **UI 元件**：Bootstrap-Vue、vue-carousel、vue-sweetalert2、vue-emoji-picker
- **即時通訊**：@aspnet/signalr + @microsoft/signalr-protocol-msgpack
- **HTTP 客戶端**：axios，並搭配 aes-js 與 jsonwebtoken 進行部分加解密
- **建置工具**：Vue CLI 4，Sass/SCSS 預處理器
- **容器化**：多階段 Docker 構建，最終以 Nginx 提供靜態資源服務

## 組態與部署注意
- 開發時透過 `npm run serve` 啟動本地開發伺服器
- 正式版構建執行 `npm run build`，輸出目錄為 `dist/`
- Docker 構建分為兩階段：
  1. 使用 `node:10` 安裝依賴並執行構建
  2. 以 `nginx` 為基礎映像，複製構建產物與自訂 nginx 設定檔（`docker-config/nginx.conf`）
  3. 將靜態資源（圖片、JS、CSS）壓縮為 zip，供部署端彈性使用
- **環境變數**：映像中刻意移除 `.env`（`rm -rf .env`），所有執行期組態應由 Docker Swarm 的環境變數或 secrets 注入，不可寫入映像
- Nginx 設定需確保 Vue Router history 模式的正確 fallback，並視需求配置反向代理至後端 API 或 SignalR Hub
- 部署目標為 Docker Swarm 生產環境，服務標籤：`PRD_Docker_Swarm|container|pricefrontendsite`

## 相關連結
- 原始碼倉庫：https://git.zbdigital.net/Biz/pricefrontendsite.git
- Docker Swarm 服務識別：`Key=PRD_Docker_Swarm|container|pricefrontendsite`