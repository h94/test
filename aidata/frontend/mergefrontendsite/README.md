# MergeFrontEndSite 服務目錄

## 概述
MergeFrontEndSite 為MergeSite 賽事資料整合平台的網頁前端，提供站台賽事、聯盟、隊伍的合併、編輯、查詢等後台管理功能。目前於 **PRD_Docker_Swarm** 叢集上以容器化方式運作，屬於前端 (frontend) 類型。

## 主要功能
### 業務功能
- **賽事合併**：透過人工合併頁面，可搜尋並選取原始賽事，指定主賽事、合併對象或進行交換操作，支援強制合併模式。
- **聯盟合併**：提供聯盟與站台聯盟的雙側比對與合併，可指定主站台聯盟或將多個站台聯盟合併至既有聯盟。
- **賽事與隊伍管理**：編輯已合併賽事的時間、比數、狀態；編輯原始賽事、聯盟、隊伍的名稱與簡稱，並支援解除合併或批量刪除。
- **操作記錄查詢**：依球種、日期、行為類型等條件過濾系統操作記錄，並檢視每筆記錄的詳細變更內容。
- **使用者認證**：基於靜態帳密對照表的前端登入機制，未登入使用者將強制導向登入頁。

### 技術特性
- **靜態頁面合併與路由管理**：基於 Vue Router 實現多頁面或微前端整合。
- **圖標與字型支援**：整合 Font Awesome 圖示庫。
- **狀態管理**：使用 Vuex 進行全域狀態儲存。
- **HTTP 請求**：透過 Axios 與後端 MergeSite API 通訊。
- **Cookie 管理**：利用 vue3-cookies 處理客戶端 Cookie 操作。
- **單元測試**：內建 Vitest 測試框架，確保元件穩定性。

## 技術棧
| 類別       | 技術                                      |
|------------|-------------------------------------------|
| 框架       | Vue 3 (^3.2.37, Composition API)         |
| 語言       | TypeScript (^4.6.4)                      |
| 建置工具   | Vite (^3.1.0)                            |
| 路由       | Vue Router (^4.1.5)                      |
| 狀態管理   | Vuex (^4.0.2)                            |
| 圖示       | Font Awesome 6 (SVG Core + Vue 元件)      |
| HTTP 客戶端 | Axios (^1.1.3)                           |
| Cookie 工具 | vue3-cookies (^1.0.6)                    |
| CSS 預處理器 | Sass (^1.55.0)                          |
| 測試       | Vitest (^0.25.8) + jsdom + @vue/test-utils (^2.2.6) |
| 型別檢查   | vue-tsc (^0.40.4)                        |

## 組態與部署注意
- **環境變數**：透過 Vite 的 `--mode` 參數切換環境（如開發、生產），生產模式使用 `npm run production`。
- **構建輸出**：執行 `npm run production` 會先透過 `vue-tsc --noEmit` 進行型別檢查，再以 `vite build --mode production` 產生靜態檔案，部署至 Docker Swarm 服務。
- **Docker 部署**：Portainer 管理，服務名稱為 `mergefrontendsite`。建議在 `docker-compose.yml` 中設定 `NODE_ENV` 及後端 API 基礎路徑（如 `API_BASE_URL`）**（需人工確認實際變數名稱與代理設定）**。
- **依賴安裝**：務必執行 `npm ci` 確保鎖定版本，避免因依賴差異導致建置失敗。
- **TypeScript 嚴格模式**：`tsconfig.json` 啟用了 `strict: true`，開發時注意型別正確。
- **後端依賴**：本服務依賴 MergeSite 提供 API（預設路徑為 `/api/v1/`），部署前請確認 MergeSite 服務位址及 CORS 設定正確。

## 開發環境設定
- **推薦編輯器**：[VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 擴充套件。
- **`.vue` 檔案的型別支援**：TypeScript 預設無法處理 `.vue` 的型別資訊。若需要在匯入 `.vue` 時獲取正確的 prop 型別（例如手動使用 `h()` 呼叫時），可啟用 Volar 的接管模式（Take Over Mode）：
  1. 在 VS Code 命令面板執行 `Extensions: Show Built-in Extensions`，找到 `TypeScript and JavaScript Language Features`，右鍵選擇 `Disable (Workspace)`。
  2. 使用 `Developer: Reload Window` 重新載入視窗。
  詳細說明請參考 [Volar 討論串](https://github.com/johnsoncodehk/volar/discussions/471)。

## 常用指令
| 指令                | 說明                                       |
|---------------------|--------------------------------------------|
| `npm run dev`       | 啟動開發伺服器 (Vite)                      |
| `npm run production`| 型別檢查 + 生產環境構建                    |
| `npm run test:unit` | 執行單元測試 (Vitest + jsdom)              |
| `npm run preview`   | 預覽生產構建結果                           |

## 相關連結
- **GitLab 倉庫**：[https://git.zbdigital.net/Biz/mergefrontendsite.git](https://git.zbdigital.net/Biz/mergefrontendsite.git)