# PredictService

## 概述
PredictService 為內部賽事預測服務，提供預測注單、彩池、殺手系統、錦標賽、報表及活動排行榜等核心功能。服務以 ASP.NET Core Web API 建置，部署於 Docker Swarm，配合 Portainer 進行容器管理。主要服務對象為前臺應用與後臺管理，支援傳統運彩與新運彩（NewLottery）兩種業務模式。

## 主要功能
- **預測注單管理**  
  建立、查詢、更新、刪除賽事預測注單，支援單場、串關、合併注單，以及以帳號、聯盟、日期、賽事等維度過濾。
- **彩池系統**  
  管理彩池遊戲、注單、開獎結果與派彩狀態；新運彩另包含彩池群組與得獎名單。
- **新運彩錢包**  
  管理金幣錢包（CoinWallet）與錦標賽積分錢包（ChampionshipWallet），支援餘額查詢、交易記錄、加減幣操作，變動強制寫入交易流水，確保帳務可稽核。（需人工確認：錢包快取 Redis `coin_wallet:{Account}` 與 `championship_wallet:{Account}:{CID}` 的實際使用情況）
- **莊家殺手**  
  查詢會員殺手紀錄、聯盟期數殺手，支援週期結算與排行榜生成。
- **新運彩**  
  包含錦標賽建立、賣牌資格、注單解鎖、報表（依 GID / 帳號 / CID 彙總）等專屬功能。
- **報表與篩選**  
  提供預測篩選報表（含主推連勝）、週結算紀錄、計算日誌查詢與重算。
- **系統排行榜與排程**  
  冥燈榜、殺手殿堂、勝率榜、最受歡迎會員、熱門賽事快取等多項定時任務（xxl-job 觸發）。
- **設定管理**  
  球種預測設定、玩法設定、殺手條件與期數設定、活動期數設定等。
- **特殊活動**  
  站台活動紀錄、主推連勝排行榜、勝率排行榜、獲獎會員派彩等。

## 技術棧
- **後端框架**：.NET 8 / ASP.NET Core Web API
- **資料庫**：
  - **需人工確認**：既有 README 記載為 Cassandra（依程式碼中 CQL 與 `ALLOW FILTERING` 推測），但依 `newlottery` 資料庫 schema（`newlottery.json`），`ChampionshipWallet`、`ChampionShipWallet_Transactions`、`CoinWallet`、`CoinWallet_Transactions` 四張表引擎均為 **MySQL**。實際整體儲存層架構（傳統運彩是否仍使用 Cassandra、新運彩是否完全遷移至 MySQL）待資深工程師確認。
- **容器化**：Docker（基於 `mcr.microsoft.com/dotnet/sdk:8.0` 映像）
- **排程**：xxl-job 整合
- **日誌與監控**：自訂心跳 `/api/heart` 與版本 `/api/version` 端點（心跳回傳伺服器當前時間 `yyyy-MM-dd HH:mm:ss.fff`，版本回傳組態版號與組建時間）
- **時區**：Asia/Taipei（強制設定於容器內）

## 組態與部署注意
- 服務預設監聽 **5000** 端口，Dockerfile 已定義 `EXPOSE 5000`。
- 容器內設定時區為 `Asia/Taipei`，確保所有時間相關邏輯一致。
- 環境變數或 `appsettings` 中須提供資料庫連線資訊、ZCoin 相關配置、站台識別（如 `inplayz` / `newLottery`）與 xxl-job 回呼位址。
- 初次部署或新環境需執行 **自動建表** API：`POST /api/v1/system/tables` 與 `POST /api/v1/system/tables/newlottery`。
- 使用 Portainer 管理時，Portainer Key 為 `PRD_Docker_Swarm`，容器類型 `container`，服務名稱為 `predictservice`。
- 部分 Controller（如 `BetPoolController`、`NewLotteryChampionshipController`、`ReportController`）路由前綴為 `api/`（無前導 `/`），與其他 Controller 使用 `/api` 不同，呼叫時請注意路徑是否正確對應。

## 相關連結
- GitLab 原始碼：[https://git.zbdigital.net/Biz/predictservice.git](https://git.zbdigital.net/Biz/predictservice.git)