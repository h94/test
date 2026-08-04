# NewLotteryBackEndService（新彩票後端服務）

## 概述

NewLotteryBackEndService 為基於 .NET 8 的 Web API 服務，負責彩票業務後端邏輯，涵蓋投注池管理、錦標賽運作、會員錢包交易、充值計畫、訂單處理、後台報表、社群討論區管理、水桶（封禁）管理及通知訊息中心。本服務作為 owner / writer / reader，對 Cassandra `member`、`payment`、`predict`、`newlottery`（MySQL）等 keyspace 具有完整讀寫權限，並可唯讀 `pricecenter` keyspace。部署於生產環境之 Docker Swarm 叢集，透過內部 Gateway 與其他微服務協作。

## 主要功能

- **投注池管理（BetPool）**：建立、更新、查詢各遊戲類型之彩池群組與個別彩池；支援週／月／季彩池，包含基本利潤、紅利及抽成獎勵計算；並提供彩池結算、派彩與得獎名單生成（xxl-job 排程）。
- **錦標賽管理（Championship）**：建立、更新與查詢錦標賽，自動產生門票資訊（於結束前兩日停止販售）；提供錦標賽排行榜計算、販售授權名單自動生成（xxl-job 排程）。
- **遊戲資料查詢（Game）**：依遊戲類型與語系取得聯賽名稱對映。
- **會員與錢包（Member）**：會員帳號查詢、建立；錢包交易記錄建立；會員搜尋（支援模糊查詢）；彩池抽成記錄建立（xxl-job 排程）；後台重製會員密碼。
- **付款與訂單（Payment）**：充值計畫 CRUD、交易訂單查詢與更新。
- **通知訊息（Notification）**：通知主題與訊息之新增、查詢、更新、刪除；訊息列表支援快取與依主題過濾。
- **水桶管理（Banned）**：水桶名單之新增、查詢（含歷史與活躍封禁）、更新（解除或延長）、刪除（解除最新一筆封禁）。
- **報表（Report）**：提供依錦標賽 gid 彙總、依帳號日期區間注單查詢（R-A3）等多種後台報表，整合 Championship、Predict 與 PriceCenter 服務資料。
- **社群管理（Community）**：後台討論區板塊、主題、回文查詢與刪除；支援分頁、排序與開文保護。
- **系統服務（System）**：服務啟動、基礎配置入口；提供錦標賽待開獎會員資訊排程（xxl-job）。

> 以上功能中的結算、派彩、佣金計算等排程邏輯，由本服務內部的 `BetPoolService` 與 `ChampionshipService` 領域服務實作，並非外部微服務。

## 技術棧

- **運行時**：.NET 8（ASP.NET Core Web API）
- **容器化**：Docker（Linux 容器）
- **內部框架**：ECFramework、ECCore 自研依賴注入與服務底座
- **日誌**：Kafka Logger
- **快取**：Redis（用於會話管理、用戶快取、域名黑名單、機器人清單、支付方式、充值方案等）
- **通訊**：RESTful API（經由 Gateway 路由至 MemberService、PredictService、PaymentService、PriceCenter、CommunityService）
- **部署平台**：Docker Swarm（Portainer 管理）

## 組態與部署注意

- **環境設定**：使用 `appsettings.{Environment}.json` 區分 Local 與 PRD；PRD 環境 `appsettings.PRD.json` 已配置。
- **容器端口**：`Dockerfile` 中 `EXPOSE 5000`，容器內以 `dotnet NewLotteryBackEndService.dll` 啟動。
- **時區**：固定為 `Asia/Taipei`（於 Dockerfile 中設定）。
- **外部依賴服務**：

| 服務 | 用途 |
|------|------|
| MemberService | 會員註冊、登入、封禁、錢包交易底層操作 |
| PredictService | 投注池遊戲、錦標賽、注單查詢與管理 |
| PaymentService | 充值方案、交易訂單、佣金記錄底層操作 |
| PriceCenter | 第三方遊戲廠商帳戶資訊查詢 |
| CommunityService | 討論區板塊、主題、回文底層操作 |

> ⚠️ BetPoolService 與 ChampionshipService 為本服務內部領域服務，非外部微服務，故不列入上表。
> 本服務負責後台管理 API 及部分排程觸發，核心業務邏輯（如結算、派彩、佣金計算）由上述專責服務執行，請勿繞過服務直接寫入底層資料表。

- **部署映像**：目前 PRD 使用映像標籤 `newlotterybackendservice:latest`，容器 ID `eb051c313711`。
- **注意事項**：
  - `Dockerfile` 直接複製已編譯之 `bin/Debug/net8.0/` 目錄，非一般多階段建構流程；部署前請確認二進位檔已正確產生。
  - 服務啟動依賴 `ECServiceStartup` 基底類別，自動注入路由與中介軟體。
  - 資料操作應遵循 Cassandra 與 MySQL 寫入限制，部分欄位為 immutable 或僅允許特定寫入/更新（如 `betpool_bets` 不可修改、`gameusers_banned` 的 `endtime` 僅允許延長或設為空、`gameusers.memberships` 僅可 APPEND 等）；變更前請參閱服務邊界文件 `newlotterybackendservice-detail.md`。
  - 任何金額相關欄位發生錯誤時，應透過新增沖正記錄處理，而非直接修改原始記錄（如 `betpool_bets.betzcoin`、`profitzcoin` 不可事後修改；`ChampionshipWallet_Transactions.Point` 與 `CoinWallet_Transactions.Coin` 亦同）。
  - 封禁用戶務必同步寫入 `gameusers_banned` 並記錄原因（`description`）與時長（`endtime`，設為空表示永久封禁），不可單獨修改 `status`；登入驗證須同時檢查 `status=1` 及封禁狀態（`endtime` 為空或大於當前時間視為封禁中）。
  - 查詢支付方式、充值方案時必須過濾 `enabled=1` 及有效時間範圍（`starttime <= now() AND endtime >= now()`），避免前台顯示已停用或過期項目。
  - 排行榜對外回傳時應對帳號進行脫敏處理，不可暴露內部主鍵（如 `authkey`、`account`）。

- **常見錯誤**：
  - ❌ 直接 UPDATE `gameusers.status = 0` 封禁用戶 → ✅ 必須同時在 `gameusers_banned` 新增記錄並註明原因與結束時間
  - ❌ 註冊時未檢查 `forbidden_email_domains` → ✅ 先查詢黑名單，匹配時拋出 `400 Invalid Email Domain`
  - ❌ 登入查詢時僅檢查 `email` 與 `password` → ✅ 必須加上 `status = 1` 條件，避免封禁用戶登入
  - ❌ 改名時直接 UPDATE `gameusers.username` → ✅ 需同時 +1 `renamecount` 並檢查是否超過上限（通常 3 次）
  - ❌ `gamesublogs` 使用 DELETE 刪除歷史記錄 → ✅ Cassandra 複合主鍵不支援部分刪除，且訂閱日誌需永久保留供稽核
  - ❌ 查詢 `gameusers_banned` 時未判斷 `endtime` → ✅ 空值或大於當前時間才為「封禁中」，否則為「已解封」
  - ❌ `memberships` 使用 SET 覆寫整個列表 → ✅ 使用 `list APPEND` 操作僅追加新訂閱 ID，保留歷史
  - ❌ Redis `session:{authkey}` 過期後仍嘗試查詢 Cassandra → ✅ 優先檢查 …（需人工確認後續內容）

## 相關連結

- GitLab 原始碼倉庫：[https://git.zbdigital.net/biz/newlotterybackendservice.git](https://git.zbdigital.net/biz/newlotterybackendservice.git)
- 服務邊界與 DB 操作規範：`newlotterybackendservice-detail.md`
- 變更紀錄：`changelogs.md`
- Confluence 技術設計：
  - [TCZB-4119 NewLotteryBackEndService 錦標賽、彩池 API](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467346)
  - [TCZB-4224 NewLotteryBackEndService 交易管理 API](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468577)
- 業務規範：[TCZB-4118 NewLotteryTools 錦標賽、彩池管理](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467392)