# NewLottery 新彩券前台

## 概述
本服務為**內部彩券系統**的前端應用，負責呈現開獎畫面、即時開獎狀態、歷史紀錄及相關動態內容，並透過 SignalR 與後端保持即時通訊，確保資訊同步更新。

## 主要功能
- 即時開獎直播：透過 WebSocket（SignalR）接收開獎號碼與狀態，動態渲染開獎動畫。
- 歷史開獎查詢：提供日期、彩種篩選，以圖表（Chart.js）與虛擬列表呈現大量紀錄。
- 輪播廣告/公告：整合 Swiper 輪播模組，展示行銷訊息或系統公告。
- 響應式設計：適配桌面與行動裝置，提供流暢的操作體驗。
- 多環境設定：支援本地開發、測試、預發布及正式環境，透過 `--dotenv` 載入對應變數。

## 技術棧
- **框架**：Nuxt 3（Vue 3 Composition API、TypeScript）
- **狀態管理**：Pinia
- **即時通訊**：@aspnet/signalr（WebSocket）
- **圖表**：Chart.js
- **虛擬捲動**：@tanstack/vue-virtual
- **輪播**：nuxt-swiper
- **工具庫**：@vueuse/core、pako（資料壓縮）
- **樣式**：Sass
- **型別檢查**：vue-tsc
- **並行開發**：concurrently（dev + type-check）

## 組態與部署注意
### 環境變數
專案使用多個 `.env.*` 檔案區分環境，指令已綁定對應模式：
- `.env.local`：本地開發 → `npm run local`
- `.env.dev`：開發伺服器 → `npm run dev`
- `.env.pre`：預發布 → `npm run pre`
- `.env.prd`：正式環境 → `npm run build:prd` 後再 `npm start`

變數內容需包含後端 API 端點、SignalR Hub 位址等，請根據環境正確設定。

### 本地開發
```bash
npm install
npm run local    # 啟動 Nuxt dev server + 型別檢查，載入 .env.local
```
瀏覽器開啟 `http://localhost:3000`

### 建置與部署
- **正式建置**：`npm run build:prd`，輸出至 `.output/`。
- **啟動服務**：`npm start`（執行 `.output/server/index.mjs`）。
- **容器化部署**：本服務於 Portainer 以容器運行（Key: `SRV84`），建置時可依據 `Dockerfile`（如存在）產生映像檔，並確保環境變數正確注入。

### 注意事項
- SignalR 連線需後端 Hub 可用，確認防火牆及 CORS 設定。
- 開獎資料若經 pako 壓縮傳輸，前端解壓後再使用。
- 使用 `nuxt generate` 可產生靜態檔案，但即時功能無法運作，建議以 SSR 模式部署。

## 相關連結
- [GitLab 儲存庫](https://git.zbdigital.net/Biz/newlottery.git)
- [Portainer 容器管理](https://portainer.zbdigital.net)（搜尋 SRV84 或 newlottery）
- [Nuxt 3 官方文件](https://nuxt.com/docs)
- 內部文件：請參閱團隊 Confluence / Wiki 頁面