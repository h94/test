# memberservice — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-07-07 — MR !159

變更摘要：
本次 MR 實作 Plan TCZB-4397 新運彩水桶（banned）完整 CRUD 及通知中心（notification）過濾與刪除功能，新增 Banned Model、Provider、Service、Controller 共五支 API，並擴充既有 Notification 端點支援 tid 與 enabled 查詢參數及 Message 硬刪除，同步更新 Redis 快取。另包含 Plan 範圍外的調整：頭像路徑強制改為 PRD 域名（https://www.rankball.net/）、Program.cs 啟動改寫為 WebHostBuilder，以及 GameWalletService 空白字元格式修正，請一併確認這些異動對部署環境的影響。

主要變更（code）：
| 檔案路徑 | 變更說明 |
|----------|----------|
| MemberService.Model/NewLottery/NewLotteryBanned.cs | 新增水桶模型類別，定義 Account、AddTime、EndTime、Description、UserName 欄位。 |
| MemberService.Model/NewLottery/NewLotteryNotificationMessage.cs | 為訊息模型加入 XML 註解與預設值，強化欄位說明。 |
| MemberService.Model/NewLottery/NewLotteryNotificationTopic.cs | 為主題模型加入 XML 註解與預設值，保留既有物件結構。 |
| MemberService.Interface/DomainService/NewLottery/INewLotteryBannedService.cs | 新增水桶服務介面，定義 CreateBanned、GetAllBanned、GetActiveBan、UpdateBanned、DeleteLatestBan 方法。 |
| MemberService.Interface/DomainService/NewLottery/INewLotteryNotificationService.cs | 擴充通知服務介面：GetNotificationTopics 增加 enabled 參數、GetNotificationMessages 增加 tid 參數、新增 DeleteNotificationMessage 方法。 |
| MemberService.Interface/Infrastructure/DataAccess/NewLottery/INewLotteryBannedDataProvider.cs | 新增水桶資料提供者介面，定義 CRUD 及 CreateTables 方法。 |
| MemberService.Interface/Infrastructure/DataAccess/NewLottery/INewLotteryCacheDataProvider.cs | 擴充快取提供者介面，加入 DeleteNotificationMessageCache 方法。 |
| MemberService.Interface/Infrastructure/DataAccess/NewLottery/INewLotteryNotificationDataProvider.cs | 擴充通知資料提供者介面：加入 GetNotificationMessagesByTid、DeleteNotificationMessage 方法。 |
| MemberService.Interface/Infrastructure/Validator/INewLotteryValidator.cs | 擴充驗證器介面，加入 BannedValidate 與 BannedUpdateValidate 方法。 |
| MemberService.DomainService/NewLottery/NewLotteryBannedService.cs | 實作水桶服務邏輯：建立時驗證使用者存在與重複啟用、自動帶入 UserName 與 AddTime、查詢 active ban、更新與刪除最新一筆。 |
| MemberService.DomainService/NewLottery/NewLotteryNotificationService.cs | 實作通知新功能：enabled 過濾主題、tid 過濾訊息（支援快取與 DB 兩種來源）、硬刪除訊息並清除 Redis 快取。 |
| MemberService.DomainService/NewLottery/NewLotteryUserService.cs | 頭像路徑強制改為 PRD 域名 https://www.rankball.net/，移除原本 PRE 路徑註解。 |
| MemberService.DomainService/SysManagerService.cs | 注入 INewLotteryBannedDataProvider 並於 CreateTables 流程加入新表建立呼叫。 |
| MemberService.DomainService/GameWalletService.cs | 無業務邏輯變動，僅格式微調（_setTransactionThread.Start(); 後多一個空白字元）。 |
| MemberService.Infrastructure/DataAccess/NewLottery/NewLotteryBannedDataProvider.cs | 實作水桶資料存取：建表、INSERT、全表查詢、依帳號查詢、UPDATE、DELETE。 |
| MemberService.Infrastructure/DataAccess/NewLottery/NewLotteryCacheDataProvider.cs | 實作 DeleteNotificationMessageCache，透過 Redis HashDeleteAsync 刪除指定快取鍵。 |
| MemberService.Infrastructure/DataAccess/NewLottery/NewLotteryNotificationDataProvider.cs | 擴充通知資料存取：修正 GetNotificationMessage 查詢條件加入 tid 和 id、新增 GetNotificationMessagesByTid 與 DeleteNotificationMessage 方法。 |
| MemberService.Infrastructure/Validator/NewLotteryValidator.cs | 實作水桶驗證：endTime 格式驗證、必填檢查、時效性檢查。 |
| MemberService/Controllers/NewLottery/NewLotteryBannedController.cs | 新增水桶控制器，定義 POST/GET/PUT/DELETE 五支 API 路由與 Swagger 註解。 |
| MemberService/Controllers/NewLottery/NewLotteryNotificationController.cs | 擴充通知控制器：GET topics 新增 enabled 參數、GET messages 新增 tid 參數、新增 DELETE messages/{tid}/{id} 端點。 |
| MemberService/Program.cs | 啟動流程改寫為使用 CreateWebHostBuilder 並呼叫 Build().Run() 替代原本 Bootstrap 寫法。 |
| XUnitTestProject/TestNewLotteryBannedService.cs | 新增水桶服務單元測試，涵蓋建立、重複檢查、帳號不存在、active 查詢、更新驗證等場景。 |
| XUnitTestProject/TestNewLotteryNotificationService.cs | 新增通知服務單元測試，涵蓋 enabled 過濾、tid 過濾、空結果、刪除與快取清除、主題不存在等場景。 |

---
