# README 產出提示詞

## WebAPI 專案

```
請分析這個 WebAPI 專案的 codebase，
參考 ./aidata/templates/readme/webapi.md 的格式，
產出這個服務的 README.md。

分析來源：
- Controllers/ → 對外 API 重點、功能分群
- Services/ → 職責說明、常見使用場景
- Entities/ 或 Models/ → 資料庫重要 Table 欄位
- Migrations/ → Table 結構確認（取最新 5 個）
- DbContext.cs → Table 關聯
- appsettings.json → 相依服務的 BaseUrl

注意：
- API 判斷關鍵字要從業務邏輯歸納，不是技術名詞
- 只列對外公開的 endpoint，不列 private method
- 輸出前先告訴我你判斷的服務類型是否正確
```

## 前端 JS 專案

```
請分析這個前端專案的 codebase，
參考 ./aidata/templates/readme/frontend.md 的格式，
產出這個專案的 README.md。

分析來源：
- src/views/ 或 pages/ → 頁面清單和路由
- src/router/ → 路由定義和權限設定
- src/api/ 或 services/ → 呼叫的後端服務和 API 前綴
- src/components/ → 重要共用元件
- src/stores/ 或 store/ → 狀態管理邏輯判斷場景
- .env 或 .env.example → 後端服務的 BaseUrl

注意：
- 頁面清單以使用者看得到的功能為主，不列技術性的 layout 頁
- 後端服務從 api/ 資料夾的 baseURL 設定判斷
- 常見場景要從使用者角度描述，不是技術流程
```

## Background Service 專案

```
請分析這個 Service 專案的 codebase，
參考 ./aidata/templates/readme/service.md 的格式，
產出這個服務的 README.md。

分析來源：
- Workers/ 或 Jobs/ → 排程工作清單和執行頻率
- Consumers/ → 訊息佇列消費邏輯
- Services/ → 業務邏輯和相依服務
- Entities/ → 資料庫 Table
- appsettings.json → Cron 設定、MQ 連線、相依服務

注意：
- 執行頻率從 Cron expression 或 Timer 設定判斷並轉成人看得懂的說明
- 相依方式要區分 HTTP 呼叫、MQ 訊息、還是共用 DB
- 常見場景要說明觸發條件和對業務的影響
```