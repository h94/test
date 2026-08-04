# gamesettingsite — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-07-18 — MR !56

本次 MR 實作兩大功能模組：ExportLog 匯出 API 與 Background Worker（TCZB-4418），以及整合 AlertBackendService 的 37 支警示管理 API（TCZB-4465）。ExportLog 新增 Controller、Service、Provider 與 Worker，支援以 site/gameType/sitegid 提交工作，背景從 Loki 與 Kafka 撈取資料合併輸出 CSV，並提供查詢、下載、刪除等端點。Alert 模組新增四個 Controller 與對應 DomainService，轉發下游 ABS 端點，並注入操作者帳號、補充賽事名稱與資料源顯示名，支援匯出任務管理及 NAS 檔案下載。此外修正 GameSettingTransfer 中空值判斷與 LeagueNameMap 取值邏輯。

| 檔案路徑 | 變更說明 |
|----------|----------|
| GameSettingSite/Controllers/ExportLogController.cs | 新增 ExportLog 四端點 (POST/GET/DELETE/download) |
| GameSettingSite.DomainService/ExportLogService.cs | 實作 ExportLog 業務邏輯、驗證、檔案管理 |
| GameSettingSite.DomainService/ExportLogWorker.cs | 實作 BackgroundService 執行 Loki/Kafka 資料匯出 |
| GameSettingSite.Infrastructure/DataAccess/LokiProvider.cs | 新增 Loki query_range 查詢與結果轉換 |
| GameSettingSite.Infrastructure/DataAccess/KafkaExportProvider.cs | 新增 Kafka 消費邏輯 (gamedata/processedgamedata) |
| GameSettingSite.Infrastructure/DataAccess/ExportLogJobStore.cs | 管理 in-memory 匯出工作佇列 (上限 5 筆 Running) |
| GameSettingSite.Model/ExportLog/ExportLogJob.cs | 匯出工作資料模型 |
| GameSettingSite.Model/ExportLog/ExportLogEntry.cs | 統一座標項目（時間戳、來源、原始內容） |
| GameSettingSite.Model/ExportLog/ExportLogCsvFormatter.cs | 扁平化輸出 CSV |
| GameSettingSite.Model/ExportLog/ExportLogContentFlattener.cs | 三種資料源欄位對照拆解 |
| GameSettingSite/Controllers/Alert/AlertController.cs | 新增警示列表、單筆、狀態更新、Webhook 重送端點 |
| GameSettingSite/Controllers/Alert/AlertExportController.cs | 新增警示匯出建立、列表、查詢、下載端點 |
| GameSettingSite/Controllers/Alert/AlertConfigController.cs | 新增 22 支設定 CRUD 端點 |
| GameSettingSite/Controllers/Alert/AlertWebhookController.cs | 新增 7 支 Webhook 管理端點 |
| GameSettingSite.DomainService/Alert/AlertService.cs | 實作警示查詢、名稱補全、狀態更新邏輯 |
| GameSettingSite.DomainService/Alert/AlertExportService.cs | 實作警示匯出任務管理與 NAS 檔案下載 |
| GameSettingSite.DomainService/Alert/AlertConfigService.cs | 實作設定 CRUD、存在性檢查、操作者注入 |
| GameSettingSite.DomainService/Alert/AlertWebhookService.cs | 實作 Webhook CRUD、日誌、測試、重試、警報重送 |
| GameSettingSite.DomainService/Alert/AlertIntegrationHelper.cs | 共用認證、名稱解析、DTO 轉換 Helper |
| GameSettingSite.Infrastructure/DataAccess/AlertBackendProvider.cs | 實作轉發 ABS 所有端點，處理 204/單多筆正規化 |
| GameSettingSite.Model/Alert/AlertRecord.cs | ABS 警示紀錄 raw model |
| GameSettingSite.Model/Alert/AlertRecordDto.cs | 整合層回傳前端警示紀錄 DTO (含 Source/Market/GameInfo) |
| GameSettingSite.Model/Alert/AlertExportCreate.cs, AlertExportTask.cs 等 | 匯出相關請求/回傳 DTO |
| GameSettingSite.Model/Alert/AlertWebhookDto.cs 等 | Webhook 相關模型 |
| GameSettingSite.DomainService/GameSettingService.cs | 修正 processCache 背景執行緒例外處理與 RemoveAll 索引問題 |
| GameSettingSite.DomainService/Transfer/GameSettingTransfer.cs | 修正空值判斷、LeagueNameMap 取值、MainSpread/SiteGID 空陣列處理 |
| GameSettingSite.Infrastructure/DataAccess/AuthProvider.cs | 新增 GetLoginInfo 方法以 uid 取 Account (Alert 模組用) |

---
