# 新彩票工具前端 (newlotterytools)

## 概述
本專案為新版彩票管理工具的前端應用，採用 Nuxt 3 框架構建，整合即時通訊、富文本編輯及 Material Design 介面，提供營運人員直覺且高效的操作體驗。服務以容器化形式部署於內部 SRV84。

## 主要功能
- 📊 **即時數據儀表板**：透過 SignalR 實現開獎資訊、銷售狀態的即時推送與顯示。
- 📅 **彈性日期時間操作**：結合 vue-datepicker 與 dayjs，支援多時區、日期範圍快速篩選。
- ✏️ **富文本公告管理**：內建 Jodit 編輯器，方便產出格式化的活動文案或系統公告。
- 🎨 **一致性 UI 體驗**：基於 Vuetify 3 Material Design 組件庫，確保 RWD 與無障礙操作。
- 🗃️ **集中狀態管理**：使用 Pinia 管理全域狀態，降低跨組件資料同步複雜度。
- 🔔 **通知與引導**：整合 vue3-toastify 與 intro.js 提供操作回饋及新功能導覽。

## 技術棧
- **框架**：Nuxt 3 (Vue 3 + TypeScript)
- **UI 套件**：Vuetify 3, @mdi/font, intro.js
- **狀態管理**：Pinia（搭配 @pinia/nuxt 模組）
- **即時通訊**：@microsoft/signalr, signalr-protocol-msgpack
- **日期處理**：dayjs（封裝為 dayjs-nuxt 模組）
- **編輯器**：jodit, jodit-vue
- **工具庫**：pako（壓縮）, @vueuse/nuxt（組合式實用函式）
- **樣式**：Sass

## 組態與部署注意
- 本專案採用 **SSR 部署模式**，構建後透過 `node .output/server/index.mjs` 啟動。
- **環境變數**需依目標環境準備對應檔案：
  - 本機開發：`.env.local`
  - 生產模式：`.env.prd`
- 常用指令：
  - `npm run local`：啟動本地開發伺服器並進行型別檢查（使用 `.env.local`）。
  - `npm run prd`：模擬生產環境開發（使用 `.env.prd`）。
  - `npm run build:prd`：為生產環境構建。
  - `npm run start`：運行已構建的服務。
- **容器部署**（SRV84）：確保 Dockerfile 中複製 `.output` 目錄，並以 Node.js 環境執行 `start` 指令。設定 Portainer 時請對應好網路埠號及環境變數注入。

## 相關連結
- GitLab 儲存庫：[https://git.zbdigital.net/Biz/newlotterytools.git](https://git.zbdigital.net/Biz/newlotterytools.git)
- Portainer 服務：SRV84 (newlotterytools 容器)
- 內部文件：參閱團隊 Wiki 或專案管理平台