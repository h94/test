# 概述

本服務為內部**價格管理前端工具**，提供直覺化的網頁介面，供團隊進行價格資料的查詢、設定與分析。服務以容器形式運行於生產環境 Docker Swarm 集群，前端資源由 Nginx 提供靜態服務。

# 主要功能

- 價格資訊查詢與快速瀏覽
- 多維度價格比對與歷史記錄展示
- 管理員批次編輯、匯入價格資料
- 整合內部 API，實現即時數據同步與更新

# 技術棧

- **前端框架**：Vue 3（Composition API + TypeScript）
- **路由與狀態管理**：Vue Router 4、Vuex 4
- **HTTP 客戶端**：Axios
- **UI 輔助**：FontAwesome 圖示、mitt 事件匯流排、vue-picture-cropper
- **建構工具**：Vue CLI 4.5
- **執行環境**：Node.js 14（建置階段）、Nginx（生產環境靜態伺服器）

# 組態與部署注意

1. **環境變數**：專案需透過 `.env` 檔設定後端 API 端點等參數；生產部署前請確保已寫入正確的環境變數並重新建置。
2. **Docker 多階段建構**：採用 `node:14` 進行 `npm run build`，再將產出的 `dist` 目錄與自訂 Nginx 設定複製至 `nginx` 映像，最終容器僅包含靜態檔案及網頁伺服器。
3. **Nginx 設定**：自訂配置位於 `docker-config/nginx.conf`；若有路由重寫、快取策略或安全標頭需求，請編輯該檔案後重新建置映像。
4. **Swarm 部署**：服務由 Portainer 管理，Stack 名稱為 `PRD_Docker_Swarm`，容器名稱為 `pricefrontendtools`；更新映像後可於 Portainer 觸發 rolling update 進行無停機部署。
5. **本地開發**：執行 `npm run serve` 啟動開發伺服器，支援熱重載；提交前請使用 `npm run lint` 檢查程式碼風格，並以 `npm run build` 確認生產建置無誤。

# 相關連結

- GitLab 存放庫：[https://git.zbdigital.net/Biz/pricefrontendtools.git](https://git.zbdigital.net/Biz/pricefrontendtools.git)
- Vue CLI 設定文件：[Configuration Reference](https://cli.vuejs.org/config/)