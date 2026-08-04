# 查詢球隊列表

## 1. 場景目的

後台管理員或內部工具查詢指定遊戲類型的球隊列表，用於聯賽與球隊名稱對照維護、手動拆分球隊等管理功能。  
此 API 供內部管理端使用，不直接面向終端玩家。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/teams/{gameType}` | 查詢指定遊戲類型的球隊列表 |

來源：README「聯賽與球隊管理」表格。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，路徑含 `gameType` 參數
2. 通過 ECFramework.ECService 內部驗證框架驗證呼叫端權限
3. Controller 接收請求，調用 Service 層查詢
4. Service 透過 Provider 查詢 MySQL Sport 資料庫的 `bk_siteplayers` 表
5. 依據 `gameType` 對應的條件過濾
6. 回傳整理後的球隊列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `TeamsController.GetTeams` | 接收 `gameType` 參數，調用 Service |
| 2 | Service | `MergeService.GetTeams` | 根據 `gameType` 決定查詢條件，調用 Provider |
| 3 | Provider | 資料存取層 | 查詢 `sport.bk_siteplayers` 表，依條件過濾 |
| 4 | Service | `MergeService.GetTeams` | 整理查詢結果為 `Team` 物件列表 |
| 5 | Controller | `TeamsController.GetTeams` | 回傳 JSON 格式球隊列表 |

來源：Phase1 batch-1 `TeamsController.cs`、`MergeService.cs` 程式碼分析。  
需人工確認：確切 Provider 類別名稱與查詢邏輯細節。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL `sport.bk_siteplayers` | Read（查詢`Team`, `TeamID`, `Site`） | 取得指定遊戲類型的球隊資料 |

### 資料來源說明

`bk_siteplayers` 表的 `Site` 欄位儲存站台來源（如 bet365、pinnacle），`gameType` 路徑參數對應到特定站台或遊戲類型。  
Service 層依據業務邏輯篩選對應 `Site` 的資料。

來源：  
- README「資料庫重要 Table」列舉 MySQL Sport `Team` 表  
- `sport-detail.md` 對 `bk_siteplayers` 的讀取規則：`pricecenterservice` 僅讀取，查詢時以 `Site + SiteID + Year` 複合條件  
- 實際查詢邏輯需參照 `MergeService.cs` 程式碼（Phase1 分析中）

---

## 6. 重要規則

### 權限限制
- 此 API 需要通過內部驗證框架驗證（來源：README 路由表格標註 `✅`）

### 欄位限制
- `SiteID` 對外 API 不可回傳，僅內部用（來源：`sport-detail.md` 的 `bk_siteplayers` 不可回傳欄位說明）
- 回傳欄位以 `Team`（球隊名稱）、`TeamID` 為主，不應暴露 `Record`（球員數據 JSON）

### 不可修改欄位
- `pricecenterservice` 對 `bk_siteplayers` 表**僅有讀取權限**，嚴禁 INSERT / UPDATE / DELETE（來源：`pricecenterservice-detail.md` 寫入限制）

### 狀態值限制
- 無特定狀態過濾需求（此場景查詢球隊列表，不涉及 `Enabled` 等業務狀態）

### 遊戲類型對應
- `gameType` 值定義參數對應的運動種類（如 `BS` 棒球、`BK` 籃球），需與系統中遊戲類型註冊表一致  
- 需人工確認：`gameType` 與 `bk_siteplayers.Site` 的對應關係

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過權限驗證 | 回傳 HTTP 401 Unauthorized |
| `gameType` 參數為空或不存在 | 回傳 HTTP 400 Bad Request 或空列表 |
| MySQL 連線失敗或查詢逾時 | 回傳 HTTP 500 Internal Server Error |
| 指定 `gameType` 無對應球隊資料 | 回傳空陣列 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T-01 | API Test | 有效 `gameType`（如 `BS`） | 回傳 200 與球隊列表 |
| T-02 | API Test | 無效 `gameType`（不存在） | 回傳 200 與空陣列 `[]` |
| T-03 | Permission Test | 未帶驗證 Token | 回傳 HTTP 401 |
| T-04 | Integration Test | MySQL 資料庫有資料，驗證回傳欄位 | 回傳欄位僅含 `Team`、`TeamID`，不含 `SiteID`、`Record` |
| T-05 | Flow Test | 連續查詢不同遊戲類型 | 各自回傳正確對應的球隊列表，無資料混雜 |

---

## 9. 高風險區域

- **跨服務資料讀取**：`bk_siteplayers` 表由 `gameliveservice` 同步寫入，若同步延遲或失敗，查詢結果可能過時。
- **資料外洩**：`SiteID` 為內部識別碼，對外回傳可能暴露站台資料結構；需確保 API 回傳時過濾。
- **讀取權限界線**：pricecenterservice 對此表僅有唯讀權限，不應在任何流程中嘗試寫入。

---

## 10. 常見錯誤

- ❌ 直接回傳 `bk_siteplayers` 的完整 row（包含 `SiteID`、`Record`）→ ✅ 應在 Service 層映射為 `Team` DTO，僅回傳必要欄位。
- ❌ 誤用 `GameType` 作為 SQL 查詢條件直接對應 `bk_siteplayers` 欄位 → ✅ `gameType` 需透過業務邏輯轉換為 `Site` 或特定過濾條件。
- ❌ 在查無資料時回傳 HTTP 404 → ✅ 應回傳空陣列 `[]` 與 HTTP 200，表示查詢成功但無符合資料。
- ❌ 試圖在此 API 中加入寫入邏輯（如快取更新）→ ✅ pricecenterservice 對 `bk_siteplayers` 僅唯讀，寫入由 `gameliveservice` 等負責。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README「聯賽與球隊管理」表格 `/api/v1/teams/{gameType}` |
| DB | MySQL `sport.bk_siteplayers`（from `sport-detail.md`） |
| Code | `TeamsController.cs`、`MergeService.cs`（Phase1 batch-1） |
| 權限規則 | `pricecenterservice-detail.md` 寫入限制（bk_siteplayers 唯讀） |
| 不可回傳欄位 | `sport-detail.md` 的 `bk_siteplayers` 區段（SiteID 不可對外） |
| 服務責任 | README「服務相依」與 `pricecenterservice-detail.md`「本服務不負責」 |