## 概述

PriceFrontendTools 為公司內部**價格管理與工具操作平台**之前端應用程式，提供業務團隊查詢、編輯及分析價格資料的統一操作介面。  
系統基於 Nuxt 3 框架實作，整合即時通訊、圖表可視化、富文本編輯等多項前端服務，並以 Docker Swarm 模式部署於正式環境。

## 主要功能

- **價格資料管理**  
  支援價格項目的查詢、新增、修改，並具備版本歷程與審核流程提示。
- **即時狀態推送**  
  透過 SignalR 連線，實現價格變更、任務狀態等資料的即時更新，無需手動重整頁面。
- **圖表分析儀表板**  
  使用 vue-chart-3 繪製價格趨勢、分佈等統計圖表，協助快速掌握數據變化。
- **富文本編輯器**  
  整合 Tiptap、Jodit 與 Vue Quill 編輯器，提供結構化的備註、公告或價格說明內容編寫。
- **日曆與排程**  
  基於 @vuepic/vue-datepicker 的日期範圍選擇器，方便設定價格生效區間與排程作業。
- **檔案上傳與色彩輔助**  
  支援拖放上傳（vue3-dropzone）附件，並提供無障礙色彩挑選器（vue-accessible-color-picker）以自訂標記顏色。
- **即時通知**  
  使用 vue3-toastify 提供操作回饋與事件提示，確保使用者即時掌握系統狀態。
- **引導式操作教學**  
  使用 intro.js 實作新功能導覽，降低內部使用者學習門檻。

## 技術棧

- **核心框架**：Nuxt 3 (Vue 3 Composition API)
- **UI 元件庫**：Vuetify 3
- **圖標**：@fortawesome/vue-fontawesome（搭配 Solid、Regular、Brands 圖標集）
- **狀態管理**：Pinia（搭配 @pinia/nuxt 模組）
- **即時通訊**：@microsoft/signalr、@microsoft/signalr-protocol-msgpack
- **HTTP 客戶端**：Axios
- **日期處理**：Day.js（透過 dayjs-nuxt 模組整合）
- **圖表**：vue-chart-3（Chart.js 封裝）
- **文字編輯器**：nuxt-tiptap-editor、jodit-vue（Jodit）、@vueup/vue-quill
- **檔案上傳**：vue3-dropzone
- **通用工具**：@vueuse/nuxt、mitt（事件總線）、pako（壓縮）、cheerio（HTML 解析）
- **建置工具**：Vite、Sass（SCSS）
- **容器化部署**：Docker Swarm（Portainer 管理）

## 組態與部署注意

### 環境變數

- 依部署環境選用對應的 `.env` 檔案：
  - **開發環境**：`.env.dev`
  - **正式環境**：`.env.production`
- 必要環境變數包含 API 端點、SignalR Hub 位址等，請確認與後端服務一致。

### 本地開發

```bash
# 安裝依賴
npm install

# 啟動開發伺服器（使用 .env.dev 環境變數，監聽 8081 port）
npm run dev

# 以 production 環境變數進行本地測試（同樣監聽 8081 port）
npm run prd
```

### 正式建置與執行

```bash
# 建置（使用 .env.production 環境變數）
npm run build:production

# 啟動 Node 伺服器（讀取 .output/server/index.mjs）
npm run start
```

### Docker Swarm 部署

- 本服務以 `pricefrontendtoolsnuxt3_PriceFrontendTools` 為服務名稱運行於 Swarm 叢集，由 Portainer 管理堆疊。
- 映像檔建置時需一併複製 `.env.production` 並執行建置指令，容器啟動命令為 `node .output/server/index.mjs`。
- 對外暴露 port 與網路設定請參考對應的 Docker Compose / Stack 配置，確保服務可被反向代理（如 Traefik）正確路由。

## 相關連結

- 原始碼倉庫：[GitLab - pricefrontendtools_nuxt3](https://git.zbdigital.net/biz/pricefrontendtools_nuxt3.git)
- Nuxt 3 官方文件：[https://nuxt.com/docs](https://nuxt.com/docs)

---

> **需人工確認**：@microsoft/signalr 與 @microsoft/signalr-protocol-msgpack 版本差異（8.0.0 vs 7.0.11）是否為預期組合；若出現相容性問題，請調整版本對齊。