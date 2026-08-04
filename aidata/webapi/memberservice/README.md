# MemberService WebAPI

- **Git Repository**: [memberservice.git](https://git.zbdigital.net/biz/memberservice.git)

## 概述
MemberService 是平台的會員核心服務，負責管理遊戲會員、股票會員、新運彩會員、排行榜帳號及賽事編輯者的身份，並提供統一的錢包、訂閱、至尊球王競賽與通知等 API。

> **注意**：本服務聚焦於會員身份維護與對外 API 整合；實際錢包結算、訂閱金流、至尊競賽排名等由專門服務處理（詳見「⚠️ 本服務不負責」一節）。
> 本服務已整合新運彩（NewLottery）相關功能，包括會員註冊／驗證、水桶名單管理、通知中心管理、代幣訂閱方案管理及彩池抽成記錄等 API。新運彩的核心業務邏輯（如錢包結算）則由 `newlotterybackendservice` 負責。

## 主要功能
- **會員系統**：提供註冊、登入、實名驗證、封禁、黑名單、關注清單、合作夥伴登入等功能，涵蓋 `member.gameusers` 表的完整生命週期管理。
- **股票會員管理**：管理 `Stock.Users`、`Stock.SubLogs` 等表的股票會員註冊、登入、密碼管理與訂閱記錄查詢。
- **錢包管理**：暴露 Z 幣錢包（`GameUser_Wallet`）、錦標賽積分（`ChampionshipWallet`）、代幣錢包（`CoinWallet`）的查詢與交易記錄 API；實際餘額維護由 `newlotterybackendservice` 負責**並透過專用 API 操作**，本服務寫入時必須配合交易記錄在同一個事務中，禁止直接 UPDATE 餘額欄位。
- **訂閱服務**：管理會員的訂閱記錄（`gamesublogs`、`Stock.SubLogs`、新運彩訂閱記錄），支援查詢與自動續訂狀態追蹤；金流與方案管理由外部服務處理。
- **編輯者管理**：建立賽事小編帳號、記錄登入事件、更新 AI 個性設定（CharacterSetting）、罐頭用語（MantraSetting）及管理可訪問群組權限（VisitGroupSetting）。
- **冠軍賽**：管理至尊球王週期的新增、更新與結算，記錄獲獎者及發放獎勵。
- **新運彩功能**：直接提供新運彩會員註冊／驗證、水桶名單（Banned）的完整 CRUD、通知中心（Notification）的訊息管理（含硬刪除）與過濾（依主題與啟用狀態）、代幣訂閱方案（SubPlan）的建立與查詢，以及彩池抽成（Commission）記錄等 API。

## 技術棧
- **核心技術**：ASP.NET Core (.NET 8.0)
- **資料庫**：
  - Cassandra（主會員資料：`member` keyspace，含 `gameusers`、`gamesublogs`、`gameusers_banned` 等）
  - MySQL（股票會員資料：`Stock` 資料庫，含 `Users`、`SubLogs` 等；**新運彩錢包相關資料：`NewLottery` 資料庫，含 `CoinWallet`、`ChampionshipWallet` 等，MemberService 為 reader / writer**）
  - Redis（快取：編輯者、登入追蹤、錢包、新運彩通知等）
- **工具與框架**：
  - ECFramework.ECService（驗證）
  - Zookeeper（配置管理）
  - MeiliSearch（全文搜尋會員）
  - Cassandra / Kafka（日誌紀錄）

## 組態與部署注意
- 確保 .NET 8.0 執行環境與相依套件（Docker 基礎映像為 `mcr.microsoft.com/dotnet/sdk:8.0`）。
- 正確設定 Cassandra（`member` keyspace）、MySQL（`Stock` 及 `NewLottery` 資料庫）連線字串。
- 配置 Zookeeper 以便動態組態管理。
- 啟用 MeiliSearch 服務並確保索引可透過 API（`/api/v1/system/game/meilisearch/users`、`/api/v1/system/newlottery/meilisearch/users`）進行同步。
- 驗證 Kafka 與 Cassandra 的日誌寫入路徑（如 `logs.logintrack_*`、`logs.loginfail_*`）。
- 容器環境變數：
  - `TZ=Asia/Taipei`（時區設定）。
  - 暴露埠號：`5000`。
  - 工作目錄：`/app`。

## ⚠️ 本服務不負責
| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 訂閱方案管理與付款處理 | SubscriptionService | 本服務僅記錄訂閱結果至 `gamesublogs` 或 `SubLogs`，不處理金流。 |
| Z 幣錢包餘額維護與交易核心邏輯 | WalletService | `GameUsers_Wallet` / `GameUsers_Wallet_Transactions` 的餘額變更由 WalletService 負責。 |
| 至尊競賽週期與排名計算 | SupremeService | 本服務僅管理週期資料與獲獎者。 |
| 排行榜使用者管理 | LeaderboardService | `Leaderboard.Users` 由 LeaderboardService 維護。 |
| 股票行情、技術指標計算、通知發送 | StockService | 本服務僅儲存使用者收藏與規則，實際篩選與通知由 StockService 執行。 |
| 新運彩錢包（代幣/錦標賽）的餘額維護與交易核心邏輯 | `newlotterybackendservice` | 本服務僅提供交易記錄的 API 殼層，**並以 reader/writer 角色配合寫入交易記錄，不可獨立異動餘額**。實際餘額變動需通過 `newlotterybackendservice` 進行，以確保帳務一致性。 |

## 常見錯誤
- ❌ 直接 UPDATE `status=1` 啟用帳號 → ✅ 須透過驗證流程或管理 API，並記錄操作日誌
- ❌ 註冊時直接寫入明文密碼 → ✅ 須先經 `Hash.HashPasswordString` 雜湊
- ❌ 登入時僅檢查密碼正確 → ✅ 須同時驗證 `status=1`，否則凍結 / 未啟用帳號可繞過
- ❌ 使用 email 作為主鍵查詢 → ✅ 以 `authkey` 為主鍵，email 僅作索引輔助查詢
- ❌ 合作夥伴用戶升級時覆蓋 `site` / `siteid` → ✅ 升級時僅補填 `email` / `password`，保留原 `site` / `siteid` 關聯
- ❌ 在 `gameusers` 直接寫入 `memberships` 項目 → ✅ 由訂閱 / 活動 / 競賽服務觸發寫入
- ❌ 統計報表未排除機器人與管理員 → ✅ 須過濾 `gamerobots.account` 與 `memberships` 含 `admin` 的帳號
- ❌ 變更密碼未驗證舊密碼 → ✅ 一般用戶變更需舊密碼；合作夥伴升級例外
- ❌ 直接修改 `Stock.Users.Rank` 而不同時更新 `SubEndTime` → ✅ 須透過 `UpdateUserRank` 同步更新
- ❌ 在 `Stock.SubLogs` 手動新增記錄 → ✅ 應由訂閱付款流程自動寫入
- ❌ 未檢查 `Stock.Rules.Enabled` 或 `Options.Enabled` 就提供給使用者 → ✅ 前端與 API 僅顯示已啟用的規則與選項
- ❌ 直接對 `NewLottery` 錢包表進行餘額變更 → ✅ 所有餘額變動必須透過 `newlotterybackendservice` 的專用 API，本服務不可繞過事務直接寫入。
- ❌ 直接 UPDATE `CoinWallet.Balance` 或 `ChampionshipWallet.Balance` → ✅ 一律透過交易 API 記錄 `_Transactions` 並更新餘額，確保帳務可追溯
- ❌ 跨 `CID` 合併錦標賽餘額 → ✅ `ChampionshipWallet` 以 `Account` + `CID` 為單位隔離，不可相互抵扣或加總
- ❌ 在 member 服務中嘗試寫入 games 表 → ✅ games 表為唯讀，任何新增、更新比賽狀態等操作應由 GameService 負責

## 相關連結
- [GitLab Repository](https://git.zbdigital.net/biz/memberservice.git)
- [服務責任邊界與 DB 操作細節](memberservice-detail.md)
- [業務規範文件摘要](documents.md)
- [變更紀錄](changelogs.md)