# 查詢商家站台設定

## 1. 場景目的
提供後台管理人員或下游服務查詢指定商家（businessCode）所擁有的站台設定清單，或依 GameType 過濾後取得單一站台設定，確保回傳內容遵守公司隔離與權限驗證。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/siteconfigs/{businessCode}` | 查詢指定商家的所有站台設定 |
| GET | `/api/v1/siteconfigs/{businessCode}/{gameType}` | 查詢指定商家某個 GameType 的站台設定 |

---

## 3. 流程總覽

1. 驗證請求者身分與權限（ECFramework 內部驗證）。
2. 以 `businessCode` 查詢 `gamesettings.businesses` 表，確認商家存在。
3. 檢查商家狀態（需人工確認：是否需檢查 `subenddate` 過期或 `status`？目前 `businesses` 表無 `status` 欄位，可能以 `subenddate` 當前日期比對判斷有效性）。
4. 從 `gamesettings.gametype_settings` 表讀取符合 `company = businessCode` 的記錄（若帶 `gameType` 則多加 `gametype` 條件）。
5. 依 `company` + `gametype` 為主鍵的查詢為核心操作，不可跨公司掃描。
6. 組裝回應，排除不可回傳欄位（如 `authtoken`、`password` 等）。
7. 回傳站台設定 JSON。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ConfigController` | 接收 GET 請求，解析 `businessCode` 及可選 `gameType` |
| 2 | Validator | ECFramework 驗證機制 | 檢查身分與授權 Token |
| 3 | Service | `IConfigService.GetSiteConfigs(businessCode, gameType?)` | 呼叫 Provider 進行資料讀取 |
| 4 | Provider | Cassandra Provider (gamesettings) | 執行對 `gamesettings.businesses` 的單點讀取（驗證商家存在） |
| 5 | Provider | Cassandra Provider (gamesettings) | 查詢 `gamesettings.gametype_settings`：<br> - 無 `gameType`：`SELECT * FROM gametype_settings WHERE company = ?`<br> - 有 `gameType`：`WHERE company = ? AND gametype = ?` |
| 6 | Service | `IConfigService` | 組裝回應物件，過濾敏感欄位 |
| 7 | Controller | `ConfigController` | 回傳成功結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.businesses` | Read | 驗證 `businessCode` 有效性 |
| DB | `gamesettings.gametype_settings` | Read | 讀取站台設定（company + gametype 為複合主鍵） |
| Redis | 未直接使用 | - | 目前服務未使用 Redis 快取站台設定（需人工確認後續版本） |

---

## 6. 重要規則

- **權限限制**：所有路由皆需通過 ECFramework 驗證（✅ 需要驗證）。
- **公司隔離**：查詢 `gametype_settings` 時，`company` 欄位必須嚴格等於請求的 `businessCode`，禁止跨公司查詢。
- **不可回傳欄位**：
  - `businesses.authtoken` 不可回傳。
  - `businesses.email` 是否回傳需人工確認（依業務規則遮罩或排除）。
- **businesses 存在性**：若 `businessCode` 不存在於 `businesses` 表，直接回傳 404 或業務錯誤。
- **訂閱有效性**：**需人工確認** — 是否需檢查 `subenddate < today` 則拒絕查詢；目前流程中可能尚未強制，但 `gamesettings-detail.md` 建議必須比對。
- **Transaction 規則**：不涉及寫入，無需交易。
- **TTL 規則**：不適用。
- **狀態值限制**：無直接對應的 `enabled` 欄位在 `gametype_settings`；`showstopplaymode` 為布林值，不影響查詢回傳。
- **不可修改欄位**：本場景僅讀取，無寫入行為。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `businessCode` 不存在 | 回傳 404 或業務錯誤碼（例如 `BusinessNotFound`） |
| 請求未攜帶有效驗證 Token | 回傳 401 Unauthorized |
| 指定 `gameType` 但無此設定資料 | 回傳空物件或對應的 NotFound 狀態 |
| 公司隔離違規（跨 `company`） | 設計上不應出現；若程式誤寫可能洩露其他公司設定 |
| `subenddate` 過期（若實施檢查） | 拒絕請求，回傳「訂閱已過期」錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 提供有效 businessCode，無 gameType | 成功回傳所有 gameType 設定清單 |
| T2 | API Test | 提供有效 businessCode ＋ 有效 gameType | 成功回傳該 gameType 設定 |
| T3 | API Test | 提供不存在之 businessCode | 回傳 404 |
| T4 | API Test | 無效的 gameType | 回傳空結果或 NotFound |
| T5 | Permission Test | 無驗證 Token 直接呼叫 | 回傳 401 |
| T6 | Flow Test | 確認查詢條件嚴格鎖定 company = businessCode | 不可跨 company 讀取 |
| T7 | Integration Test | 模擬 subenddate 過期（若系統有檢查） | 拒絕查詢並回傳錯誤 |

---

## 9. 高風險區域

- **跨公司資料洩漏**：若 `company` 過濾條件被省略或寫死成萬用字元，可能回傳其他商家的站台設定。
- **商家訂閱狀態跳過檢查**：若未比對 `subenddate`，可能讓過期商家繼續取得設定服務。
- **Cassandra 全表掃描**：若錯誤使用 `ALLOW FILTERING` 或無主鍵查詢，將嚴重影響效能。
- **敏感欄位外洩**：`businesses` 表內的 `authtoken` 若被不慎序列化進回應，將造成安全問題。

---

## 10. 常見錯誤

- ❌ 回傳 `businesses.authtoken` 或 `email` 未經遮罩。
- ❌ 寫出跨公司的查詢（例如 `WHERE company IN (...)` 或無條件 ALLOW FILTERING）。
- ❌ 忽略 `businessCode` 不存在的情況，直接查詢 `gametype_settings` 造成空結果被誤認為合法。
- ❌ **AI 容易誤解**：將 `businessCode` 當作操作方帳號而非公司代碼，導致權限模型錯誤。
- ❌ 新增端點時未加入 ECFramework 驗證，導致未授權存取。
- ❌ 直接修改 DB 查詢條件而未遵循 `company` 隔離規則。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README - ConfigController GET `/api/v1/siteconfigs/{businessCode}` 與 `/{businessCode}/{gameType}` |
| DB | `gamesettings.gametype_settings` (company + gametype 複合主鍵) |
| DB | `gamesettings.businesses` (businesscode 主鍵) |
| Code | 推斷：`IConfigService.GetBusinessGameTypePlayModeConfig` 等方法 (source semantics) |
| Rule | `gamesettings-detail.md` 不可回傳 authtoken 與跨公司隔離規則 |
| Flow | README 使用場景 #1 後台設定 GameType 玩法模式，其相關查詢亦遵循相同隔離原則 |

---

> **需人工確認**：
> - 是否已實作 `subenddate` 過期檢查？若未實作，需補充。
> - `gametype_settings` 中無明確啟用/停用旗標，是否所有記錄皆可查詢，或有其他控制機制（如依賴 `settings` JSON 內標記）？
> - 回應物件的確切結構（是否包含 `showstopplaymode`、`swap` 等）需繞過 AI 推測，應以實際 DTO 定義為準。
> - 純查詢流程是否會觸發 `Redis BusinessCache` 的讀取？目前證據指出 Redis 未用於此場景，但若未來導入快取則需納入分析。