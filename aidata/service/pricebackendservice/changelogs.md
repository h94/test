# pricebackendservice — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-07-16 — MR !362

變更摘要
本次合併請求依據 TCZB-4463 與 TCZB-4439 規劃，實作賽事交易所設定管理之 14 個 API 端點，涵蓋球種聯盟設定、股票上限規則與分數防禦規則的新增、查詢、更新及刪除操作；同時整合了 TCZB-4439 的聯盟篩選機制，確保賽事列表僅顯示已啟用聯盟。主要程式變更包括 Controller、Service、Provider、Transfer、Validator 層的對應邏輯，以及檔案快取的更新。惟 aidata OpenAPI 與 README 文件尚未更新，建議後續補充。

主要變更（code）

| 檔案路徑 | 變更摘要 |
|----------|----------|
| PriceBackendService/Controllers/TradeGameController.cs | 新增 14 個設定管理 API 端點（含 POST、GET、PUT、DELETE）與對應的 Admin 驗證。 |
| PriceBackendService.DomainService/TradeGameService.cs | 新增球種聯盟 CRUD、股票上限/分數防禦設定處理、聯盟名稱對照、檔案快取更新及 TCZB-4439 賽事列表聯盟篩選整合。 |
| PriceBackendService.Infrastructure/DataAccess/TradeGameProvider.cs | 實作對 tradegameservice 的設定 CRUD 呼叫（新增、儲存、查詢、刪除）。 |
| PriceBackendService.Infrastructure/Transfer/TransferTradeGame.cs | 新增 StockLimitSetting / ScoreDefenseSetting 與對應 DTO 之間的轉換方法。 |
| PriceBackendService.Infrastructure/Validator/ValidatorTradeGame.cs | 新增驗證器，包含球種驗證、股票上限規則與分數防禦規則的格式與邏輯校驗。 |
| PriceBackendService.Model/TradeGame/StockLimitSetting.cs | 新增股票上限設定內部模型與 DTO（含層級、GID/GDate 等欄位）。 |
| PriceBackendService.Model/TradeGame/ScoreDefenseSetting.cs | 新增分數防禦設定內部模型與 DTO（含玩法規則字典）。 |
| PriceBackendService.Model/TradeGame/TradeGameSetting.cs | 新增球種聯盟設定、更新請求與快取結構（TradeGameTypeSetting、TradeGameTypeSupSetting、TradeGameTypeSettingCache）。 |
| PriceBackendService.Interface/DomainService/ITradeGameService.cs | 擴充介面，加入所有設定管理方法簽章。 |
| PriceBackendService.Interface/Infrastructure/DataAccess/IAppSettingDataProvider.cs | 新增 GetSupportGameTypes、GetTradeGameLayers 方法簽章。 |
| PriceBackendService.Interface/Infrastructure/DataAccess/IFileDataProvider.cs | 新增 SaveTradeGameSettingsJson 方法簽章以支援設定快取存放。 |
| PriceBackendService.Interface/Infrastructure/DataAccess/ITradeGameProvider.cs | 擴充介面，加入設定相關的 Provider 方法簽章。 |
| PriceBackendService.Interface/Infrastructure/Transfer/ITransferTradeGame.cs | 擴充轉換介面，加入股票上限與分數防禦設定的轉換方法簽章。 |
| PriceBackendService.Interface/Infrastructure/Validator/IValidatorTradeGame.cs | 新增 Validator 介面，定義球種及規則驗證方法簽章。 |
| PriceBackendService.Infrastructure/DataAccess/AppSettingDataProvider.cs | 實作支援球種清單與交易層級清單的回傳邏輯。 |
| PriceBackendService.Infrastructure/DataAccess/FileDataProvider.cs | 新增 SaveTradeGameSettingsJson 方法以提供檔案快取寫入功能。 |
| PriceBackendService.DomainService/SystemService.cs | 改用 IAppSettingDataProvider 提供的支援球種清單，移除硬編碼。 |
| PriceBackendService.DomainService/MemberService.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/DataAccess/ArticleDataProvider.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/DataAccess/FeedbackProvider.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/DataAccess/GameLiveProvider.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/DataAccess/MqProvider.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/DataAccess/PaymentProvider.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/Transfer/TransferPayment.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/Transfer/TransferPredict.cs | 修正命名空間宣告（無功能變更）。 |
| PriceBackendService.Infrastructure/Validator/ValidatorPredict.cs | 修正命名空間宣告（無功能變更）。 |

---
