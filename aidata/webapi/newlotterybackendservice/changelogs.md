# newlotterybackendservice — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-06-10 — MR !33

變更摘要：本次 MR 依據報表、社群討論區及水桶通知三項 Plan 需求，實作後台管理 API。報表模組新增帳號區間注單查詢（R-A3），社群模組提供板塊、主題、回文查詢與刪除，水桶與訊息中心模組完成 CRUD 代理，並加入玩家搜尋。所有資料操作僅透過下游服務（PredictService、communityservice、memberservice），不直連資料庫。此外，為支援後台營運，額外實作了錦標賽排行榜計算、彩池結算與派彩、彩池抽成計算、待開獎資訊生成及錦標賽販售授權名單等排程邏輯，雖超出原計畫範圍，但已整合於本分支。總計新增或修改逾 60 個檔案，涵蓋 Controller、Service、Provider、Validator、Transfer、Model 及相關測試。

主要變更（code）：

| 變更類型 | 檔案路徑 | 變更摘要 |
|----------|----------|----------|
| 新增 | NewLotteryBackEndService.DomainService/ReportService.cs | 實作報表彙總、明細及 R-A3 帳號區間注單查詢邏輯，整合 Predict 與 PriceCenter |
| 新增 | NewLotteryBackEndService.DomainService/CommunityService.cs | 實作社群討論區板塊、主題、回文查詢與刪除，含使用者名稱補齊與開文保護 |
| 新增 | NewLotteryBackEndService.DomainService/BannedService.cs | 提供水桶新增、查詢、更新、解除等 BFF 邏輯 |
| 新增 | NewLotteryBackEndService.DomainService/NotificationService.cs | 實作訊息中心主題與文章 CRUD 轉發 |
| 修改 | NewLotteryBackEndService.DomainService/MemberService.cs | 新增使用者建立、錢包交易處理、彩池抽成計算、玩家搜尋及帳號查詢等多項功能 |
| 修改 | NewLotteryBackEndService.DomainService/ChampionshipService.cs | 加入錦標賽排行榜計算與販售授權名單自動生成排程 |
| 修改 | NewLotteryBackEndService.DomainService/BetPoolService.cs | 新增彩池結算、派彩、得獎名單生成與彩池抽成查詢邏輯 |
| 修改 | NewLotteryBackEndService.DomainService/SystemService.cs | 新增待開獎資訊排程，收集進行中錦標賽用戶並產出 pending 檔案 |
| 修改 | NewLotteryBackEndService.Controllers/ReportController.cs | 新增 R-A3 端點 `GET /api/reports/{gameType}/accounts/{account}/dateRange/bets` 及相關路由 |
| 新增 | NewLotteryBackEndService.Controllers/CommunityController.cs | 實作 `/api/community/forums/*` 六支端點（查詢與刪除） |
| 新增 | NewLotteryBackEndService.Controllers/BannedController.cs | 提供 `/api/banned` 水桶 CRUD 端點 |
| 新增 | NewLotteryBackEndService.Controllers/NotificationController.cs | 提供 `/api/notification/*` 訊息中心端點 |
| 修改 | NewLotteryBackEndService.Controllers/MemberController.cs | 新增 `GET /api/users/search` 玩家搜尋端點 |
| 新增 | NewLotteryBackEndService.Infrastructure/DataAccess/CommunityProvider.cs | 封裝 communityservice Restful 呼叫，含分頁映射與錯誤處理 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataAccess/MemberProvider.cs | 擴充逾十個方法，涵蓋水桶、通知、使用者、彩池抽成與錢包交易等 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataAccess/PredictProvider.cs | 新增報表彙總、錦標賽明細、彩池得獎名單查詢、日期區間注單等多種方法 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataAccess/PriceCenterProvider.cs | 新增 `GetDateRangeGames` 以支援賽事主檔查詢 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataAccess/PaymentProvider.cs | 移除彩池抽成查詢，新增交易訂單建立方法 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataAccess/FileProvider.cs | 新增彩池得獎名單、錦標賽排行榜、待開獎資訊、販售授權等檔案寫入與讀取方法 |
| 新增 | NewLotteryBackEndService.Infrastructure/DataValidator/CommunityValidator.cs | 驗證 community 端點參數（forumId、subjectId、分頁等） |
| 新增 | NewLotteryBackEndService.Infrastructure/DataValidator/ReportValidator.cs | 驗證報表端點參數及日期格式 |
| 修改 | NewLotteryBackEndService.Infrastructure/DataValidator/MemberValidator.cs | 調整錢包交易驗證以支援轉帳交易 |
| 新增 | NewLotteryBackEndService.Infrastructure/Transfer/CommunityTransfer.cs | 將 communityservice 下游模型轉換為 BFF 對外模型，含分頁局部切片 |
| 新增 | NewLotteryBackEndService.Infrastructure/Transfer/ReportTransfer.cs | 將 Predict/PriceCenter 資料組裝為報表回應信封（Envelope） |
| 新增 | NewLotteryBackEndService.Interface/DomainService/IReportService.cs 等 | 對應新增服務之介面定義（含 ICommunityService、IBannedService、INotificationService） |
| 新增 | NewLotteryBackEndService.Interface/Infrastructure/* | 對應 Provider、Validator、Transfer 之介面新增 |
| 新增 | NewLotteryBackEndService.Model/Community/*.cs | 社群相關模型：CommunityForum、CommunitySubject、CommunityComment 等 |
| 新增 | NewLotteryBackEndService.Model/Report/*.cs | 報表相關模型：多種 Envelope 與 Item（含 R-A3 之 AccountDateRangeBetsEnvelope） |
| 新增 | NewLotteryBackEndService.Model/Member/Banned.cs、UserMeiliSearch.cs 等 | 水桶、玩家搜尋模型 |
| 新增 | NewLotteryBackEndService.Model/Notification/NotificationTopic.cs、NotificationMessage.cs | 訊息中心模型 |
| 新增 | UnitTestProject/NewLottery/CommunityServiceTests.cs 等 | 社群服務與 Transfer 單元測試 |
| 新增 | UnitTestProject/NewLottery/Integration/CommunityControllerIntegrationTests.cs 等 | 社群整合測試（含情境 1、2） |
| 新增 | UnitTestProject/Report/ReportServiceTests.cs、ReportControllerIntegrationTests.cs | 報表服務單元測試及 R-A3 整合測試 |

---
