# Game Setting Frontend Business - Nuxt 3

## 概述
遊戲設定前端業務 (gamesettingfrontendbusiness_nuxt3) 是一個基於 Nuxt 3 的單頁應用程式，主要提供營運人員進行遊戲相關設定的管理與監控界面。該服務以容器化形式部署於生產環境 Docker Swarm 集群中，對應 Portainer 容器名稱 `gamesettingfrontendbusinessnuxt3`。

## 主要功能
- 遊戲參數設定：提供圖形化界面管理各項遊戲規則、獎項、時間等設定。
- 即時通訊：透過 SignalR 實時接收後端訊息，確保數據同步與通知。
- 多國語系：支援繁體中文及其他語系切換。
- 數據分析圖表：使用 Chart.js (vue-chart-3) 視覺化呈現統計數據。
- 日期與時間處理：結合 dayjs 實現日期選擇與格式化。
- JSON 數據檢視：內嵌 JSON viewer 方便除錯與設定資料瀏覽。
- 通知與提示：使用 toastify 提供操作反饋。

## 技術棧
- **框架**: Nuxt 3 (SSR/CSR 混合模式)
- **前端庫**: Vue 3 + Composition API
- **UI 框架**: Vuetify 3 (Material Design)
- **狀態管理**: Pinia
- **HTTP 客戶端**: Axios
- **即時通訊**: @microsoft/signalr
- **圖表**: vue-chart-3 / Chart.js
- **日期處理**: dayjs
- **壓縮/解壓縮**: pako
- **多語言**: @nuxtjs/i18n
- **圖示**: @iconify-json, @mdi/font
- **樣式**: Sass

## 組態與部署注意
本專案透過 `.env` 檔案區分環境設定，主要環境檔為：
- `.env.local`：本機開發/測試環境
- `.env.prd`：生產環境配置

常用執行指令：
```bash
npm run dev            # 預設開發模式
npm run local          # 使用 .env.local 啟動開發伺服器 (port 8080)
npm run prd            # 使用 .env.prd 模擬生產環境 (port 8080)
npm run build:prd      # 構建生產版本
npm run start          # 啟動已構建的應用程式 (.output/server/index.mjs)
```

部署至 Docker Swarm 時，請確保：
- 正確設定對應的環境變數（如 API 端點、SignalR Hub 位址）。
- 服務名稱須與 Portainer 容器定義一致 (`gamesettingfrontendbusinessnuxt3`)。
- 建置階段使用 `build:prd` 以載入正確的生產環境變數。
- 執行階段使用 `start` 腳本直接啟動 Node.js 伺服器。

## 相關連結
- GitLab 倉庫：[https://git.zbdigital.net/biz/gamesettingfrontendbusiness_nuxt3.git](https://git.zbdigital.net/biz/gamesettingfrontendbusiness_nuxt3.git)
- Nuxt 3 文件：[https://nuxt.com/docs](https://nuxt.com/docs)
- Vuetify 3 指南：[https://vuetifyjs.com/](https://vuetifyjs.com/)