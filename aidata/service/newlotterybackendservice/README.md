## 概述

newlotterybackendservice 是新運彩後端服務，負責處理錦標賽、彩池、會員錢包、交易記錄、通知、討論區稽核、儲值方案管理與報表彙整等核心業務。服務透過 MySQL（NewLottery）儲存錢包與交易資料，並以 Cassandra（payment）儲存儲值方案與佣金資訊，同時使用 Redis 作為餘額快取。對外提供 RESTful API，並透過 xxl-job 定時排程執行錦標賽排行榜、門票快取、彩池結算等作業。

## 主要功能

- **會員與錢包**
  - 會員新增與搜尋
  - 錢包交易（代幣轉帳），包含交易記錄與原子餘額更新
  - 錢包餘額查詢（代幣錢包、錦標賽錢包）
- **錦標賽管理**
  - 錦標賽 CRUD、門票快取、排行榜、投注權限
- **彩池群組與派彩**
  - 彩池群組建立/修改、彩池管理
  - 彩池資訊更新與結算、派彩（xxl-job）
- **水桶名單**
  - 新增、查詢、更新、解除水桶
- **通知系統**
  - 通知主題 CRUD
  - 通知訊息管理（支援快取）
- **討論區稽核**
  - 板塊列表、主題分頁、單筆查詢、回文查詢
  - 主題與回文刪除
- **支付與儲值方案**
  - 儲值方案新增/修改/查詢
  - 交易訂單查詢與更新（依帳號、時間區間）
- **報表**
  - 錦標賽下注彙總（依 gid、cid、帳號）
  - 帳號日期區間下注明細（含賽事）
  - 帳號／cid 彙總報表
- **遊戲資訊**
  - 依球種取得聯盟名稱
- **系統工具**
  - 心跳檢測、版本資訊
  - 錦標賽預測待處理名單產出（xxl-job）

## 技術棧

- **執行環境**：.NET 8（容器化部署）
- **框架**：ASP.NET Core（REST API）
- **資料庫**
  - MySQL（NewLottery）：錢包（`ChampionshipWallet`、`CoinWallet`）與交易記錄
  - Cassandra（payment）：儲值方案、活動商品、佣金、支付方式
- **快取**：Redis（錢包餘額快取，TTL 5 分鐘，交易發生時主動失效）
- **內部相依服務**
  - `communityservice`（討論區實際寫入）
  - `paymentservice`（支付主邏輯）
  - `PriceCenter`（賽事主檔）
  - `Predict`（注單與彙總查詢）
  - `MemberService`（會員基礎資料）
- **排程**：xxl-job 觸發（彩池結算、門票、排行榜、待處理檔案等）
- **容器**：Docker，時區設定為 `Asia/Taipei`，監聽埠 `5000`

## 組態與部署注意

- **資料庫連線**
  - MySQL（NewLottery）：由 `ECCore` 管理連線，需正確設定連線字串
  - Cassandra（payment）：需設定 Contact Points 與 Keyspace
- **Redis 快取**
  - `coin_wallet:{Account}` 與 `championship_wallet:{Account}:{CID}`，TTL 300 秒
  - 交易發生時**必須主動 DEL 對應快取**，不可只靠 TTL 自然過期
- **錢包與交易紀律**
  - 所有餘額變動**必須透過交易 API**（原子操作），不可直接 UPDATE `Balance` 欄位
  - 變動時須同步寫入對應 `_Transactions` 表，確保稽核軌跡
  - `T_Detail`、`T_UID` 等欄位由服務端控制，嚴禁接收前端任意字串
  - 對外查詢時，敏感欄位（如 `T_Detail`、`Point`、`Coin`、`T_Type`）應過濾或語意化摘要
- **交易安全**
  - 查詢交易記錄**必須帶入時間範圍**（`AddTime` / `T_Date`），避免全表掃描
  - 查詢錢包不可 JOIN 交易表；餘額變動前應使用 `SELECT ... FOR UPDATE` 鎖行或樂觀鎖確認
- **容器部署**
  - `ENTRYPOINT ["dotnet", "NewLotteryBackEndService.dll"]`
  - 務必掛載正確的 `appsettings.json` 或使用環境變數注入組態
  - `Version` 與 `Environment` 資訊來自組態，版本號讀取 `Version` section
- **排程任務**
  - 服務對外暴露 API 端點（如 `/api/betpoolgroups/betpools/result`），由 xxl-job 定時調用
  - 需確保 xxl-job 排程依業務需求正確配置執行頻率與順序

## 相關連結

- GitLab 存放庫：`https://git.zbdigital.net/Biz/newlotterybackendservice.git`
- 服務邊界與資料庫操作限制詳見 `service/_temps/newlotterybackendservice-detail.md`
- DB Schema 與使用脈絡請參考 `db/newlottery.json` / `db/newlottery-detail.md` 及 `db/payment.json` / `db/payment-detail.md`