# 建立單場玩法設定

## 1. 場景目的

為特定場次（Game）建立獨立的玩法設定，覆蓋或補充預設的 GameType 或聯賽層級玩法模式。此場景由後台管理人員操作，確保單場賽事可擁有與預設不同的盤口、賠率限制等配置。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/playmodeconfigs/game` | 建立單場玩法設定 |

---

## 3. 流程總覽

1. 接收包含 `businessCode` 與 `gameType` 的 request body（含 `settings` JSON）。
2. 驗證請求者權限（需有效 business account 且 `status=1`）。
3. 驗證 `settings` 欄位是否為合法 JSON 字串。
4. 驗證目標 `businessCode` 是否存在於 `gamesettings.businesses` 表。
5. 建構 `game_settings` 資料列，自動填入 `updater` 與 `updatetime`。
6. 寫入 Cassandra `gamesettings.game_settings` 表。
7. 回傳成功或失敗結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ConfigController.PostPlayModeGame` | 接收請求，轉交 Service |
| 2 | Service | `IConfigService.CreateGamePlayModeConfig` | 業務邏輯協調 |
| 3 | Service | 權限驗證（推測） | 查 `business_accounts` 確認 `status=1` |
| 4 | Service | JSON 驗證 | 檢查 `settings` 是否為合法 JSON |
| 5 | Service | `IBusinessService.GetBusiness` | 確認 `businessCode` 存在 |
| 6 | Provider | Cassandra Provider | `INSERT INTO gamesettings.game_settings` |
| 7 | Controller | - | 回傳 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.businesses` | Read | 驗證 `businessCode` 存在 |
| DB | `gamesettings.business_accounts` | Read (`status=1`) | 權限驗證 |
| DB | `gamesettings.game_settings` | Write (INSERT) | 寫入單場玩法設定 |
| Cache | `gamesettings:game:{id}` (Redis) | *可能需* Delete | 確保前台讀取最新設定（未直接證實，需人工確認） |

---

## 6. 重要規則

- **權限限制**：僅 `status=1` 的 business account 可呼叫此 API（證據：`gamesettingservice-detail.md` 登入檢查）。
- **欄位限制**：
  - `settings`：必須是合法 JSON 字串，不可包含非序列化物件。
  - `updater`：自動填入當前操作者帳號，不接受用戶端傳入。
  - `id`：建立後不可更新（主鍵）。
- **不可暴露資料**：`password`、`authtoken` 不可在 logs 或 response 中出現。
- **Transaction 規則**：Cassandra 不支援多表 transaction；此流程僅涉及單表寫入，無跨 table 一致性問題。
- **狀態值限制**：`enabled` 應預設為 1（啟用），不接受用戶端傳入（需人工確認）。
- **不可修改欄位**：建立後 `id` 不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| `settings` 非合法 JSON | 回傳 400 Bad Request（如「Invalid settings format」） |
| `businessCode` 不存在 | 回傳 404 Not Found |
| 權限不足（`status=0`） | 回傳 401 Unauthorized |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error |
| Redis 快取清除失敗 | 不影響主流程，但可能導致前台暫讀舊資料（需人工確認容錯策略） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| **CF-01** | API Test | 以合法 JSON 建立單場設定 | HTTP 200，`game_settings` 中出現新 record |
| **CF-02** | API Test | `settings` 傳入非法 JSON | HTTP 400 |
| **CF-03** | Permission Test | 以 `status=0` 的帳號呼叫 | HTTP 401 |
| **CF-04** | Flow Test | 建立後用 GET API 查詢 | 能正確查回已寫入的 `settings` JSON |
| **CF-05** | Integration Test | 驗證 `updater` 欄位 | `updater` 為操作者帳號，非請求者傳入值 |
| **CF-06** | API Test | `businessCode` 不存在 | HTTP 404 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.game_settings`，因包含關鍵遊戲設定，錯誤可能影響前台下注。
- **高風險 API**：`POST /api/v1/playmodeconfigs/game`，因直接寫入設定。
- **跨服務資料同步**：前台服務（gamesettingsite）查詢時會依 `enabled=1` 過濾，此處務必確保正確設定。
- **Cache consistency**：需人工確認是否有 Redis 快取需清除，避免前台讀取舊資料。
- **Idempotency**：此 API 為 POST，非 idempotent。重複呼叫會建立多筆 record，可能導致前台設定衝突。

---

## 10. 常見錯誤

- ❌ 更新 `game_settings.settings` 時傳入非 JSON 格式資料。
- ❌ 建立單場設定後未記錄 `updater`，或誤以為此欄位由請求傳入。
- ❌ 忘記驗證 `businessCode` 是否存在於 `businesses` 表。
- ❌ 對已建立的 `id` 再次執行 POST（應使用 PUT 更新）。
- ❌ 認為此 API 會同時更新 Redis（需人工確認當前實作）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | ConfigController (README API 清單) |
| DB | `gamesettings.game_settings` (Cassandra schema) |
| DB 寫入規則 | `gamesettingservice-detail.md § game_settings` |
| 權限驗證 | `gamesettingservice-detail.md § business_accounts` 登入檢查 (`status=1`) |
| 程式流程 | `IConfigService.CreateGamePlayModeConfig` (phase1 code semantics) |
| JSON 驗證 | `gamesettingservice-detail.md § settings` 寫入限制 |