# GameSettingFrontEndSite

## 概述
此專案為遊戲設定功能之前端網站，部署於 Docker Swarm 叢集中，提供使用者圖形化介面進行遊戲相關設定之操作與管理。採用 Vue 2 框架開發，並透過 Nginx 提供靜態資源服務。

## 主要功能
- **儀表板（Dashboard）**：即時檢視各遊戲類型與站台的數據更新狀態，逾時自動標示警告。
- **即時賠率監看（Hub）**：透過 SignalR 接收各站台賽事賠率變動，支援球種、站台、賽事狀態篩選，並可瀏覽詳細賠率、比分及操作記錄。
- **多層級遊戲設定管理**：
  - **比賽設定（Game）**：搜尋賽事、套用設定模板、修改玩法參數，並查閱設定歷程。
  - **聯盟設定（League）**：建立與調整聯盟層級的遊戲規則。
  - **範本設定（Template）**：管理可重複使用的設定樣板，加速比賽設定流程。
  - **系統設定（System）**：維護系統預設的遊戲參數。
  - **站台設定（Site）**：批次切換各站台於不同遊戲類型的啟用狀態。
- **賠率比對（Spread）**：橫向對比多個站台對同一賽事的賠率差異，輔助營運判斷。
- **詳細資料頁（Details）**：提供聯賽、隊伍等關聯資訊的查詢入口。
- 多國語系支援（vue-i18n）、響應式 Bootstrap 4 介面、與後端 API 非同步通訊（axios），並整合 Font Awesome 圖示。

## 技術棧
- **前端框架**：Vue 2 (Vue CLI 4.5)
- **狀態管理**：Vuex 3
- **路由**：Vue Router 3
- **UI 元件庫**：Bootstrap 4 + BootstrapVue
- **HTTP 客戶端**：axios
- **即時通訊**：@microsoft/signalr
- **其他**：vue-cookies, vue-sweetalert2, vue-json-viewer, date-fns, @fortawesome 系列
- **建置工具**：Node 16 (Alpine), Webpack, Babel
- **運行環境**：Docker (Nginx 靜態伺服器)
- **部署平台**：Docker Swarm (PRD 環境)

## 組態與部署注意
- 使用多階段 Docker 建置（`Dockerfile`）：第一階段以 `node:16-alpine` 安裝依賴並編譯，第二階段以 `nginx` 執行映像檔。
- Docker 建置過程中會自動移除 `.env` 檔案（`RUN rm -rf .env`），避免機敏設定意外滲入映像檔；但仍建議開發者確認 `.gitignore` 排除 `.env`，且不將含密鑰的 `.env` 提交至儲存庫。
- 部署至 Docker Swarm 時，Portainer 中的服務標籤 (PortainerKey) 應設為 `PRD_Docker_Swarm|container|gamesettingfrontendsite`，對應的服務名稱為 `gamesettingfrontendsite`。原先使用的堆疊路徑 `swarm/gamesettingfrontendsite/gamesettingfrontendsite_GameSettingFrontEndSite` 可能需隨環境調整，需人工確認。
- Nginx 設定檔位於 `docker-config/nginx.conf`，可依需求調整靜態資源快取與反向代理規則。
- 正式環境建置指令：`npm run build`，並透過 CI/CD 產出 Docker 映像。
- 本地開發可執行 `npm run serve`（標準模式）或 `npm run prd`（模擬 PRD 環境的開發伺服器）。

## 相關連結
- **GitLab 儲存庫**：<https://git.zbdigital.net/Biz/gamesettingfrontendsite.git>
- **UI 功能脈絡詳細說明**：請參閱 `ui-context.md`（記錄各頁面之操作邏輯、狀態顯示與錯誤處理）