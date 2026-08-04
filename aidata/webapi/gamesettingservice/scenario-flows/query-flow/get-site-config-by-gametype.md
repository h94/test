# 查詢指定 GameType 站台設定

## 1. 場景目的
供已通過驗證的後台客戶端，以 `businessCode` 與 `gameType` 為條件，讀取該商家在其餘遊戲類型上的完整站台設定（JSON 內容）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/siteconfigs/{businessCode}/{gameType}` | 查詢特定商家下特定遊戲類型的站台設定（ConfigController） |

---

## 3. 流程總覽

1. API 層接收 GET 請求，取得路徑參數 `businessCode` 與 `gameType`。
2. 框架（ECFramework.ECService）先完成 Token 驗證（所有 `/api/v1/siteconfigs/*` 皆需驗證）。
3. Controller 呼叫對應的 Service 方法（如 `IConfigService.GetSiteConfig`，因目標為站台設定）。
4. Service 層直接對 Cassandra 的 `gametype_settings` 表執行單行查詢。
5. 若結果存在，取出 `settings` 欄位（JSON 字串）；若不存在，返回空或預設值（需人工確認）。
6. 將 `settings` 內容回傳給客戶端（不含任何敏感欄位）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | ConfigController.GetSiteConfigByGameType | 接收 `businessCode`、`gameType`，轉送參數。 |
| 2 | Service | ConfigService.GetSiteConfig(businessCode, gameType) | 查詢 `gametype_settings` 表。 |
| 3 | Provider | Cassandra data provider（如 `ICassandraProvider`） | 執行 CQL 查詢。 |
| 4 | Transfer | DTO 轉換 | 取出 `settings` 回傳，排除 `showstopplaymode`、`swap` 等系統欄位（如需）。 |

> ⚠️ 上述 Class / Method 名稱為基於現有 `IConfigService` 命名慣例推斷；若不存在對應函數，需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `gamesettings.gametype_settings` | Read | 透過 Composite Key `(company, gametype)` 讀取該商家的站台設定。 |

- 本服務**未**直接使用 Redis（所有查詢均直接存取 Cassandra）。
- 無 Queue / Kafka 消費。

---

## 6. 重要規則

- **權限限制**：必須持有有效 Token（所有 ConfigController 端點標記 ✅）。
- **公司隔離**：查詢時強制使用 `company`（即 `businessCode`）作為 Partition Key 條件，不允許跨公司查詢（全表掃描為禁止行為）。
- **不可暴露資料**：`gametype_settings` 回傳的 `settings` 為純設定 JSON，不得夾帶 `password`、`authtoken` 等敏感欄位。
- **欄位限制**：`settings` 須為合法 JSON 字串；若值異常（NULL 或非 JSON），服務應記錄錯誤並回傳安全預設值。
- **不可修改欄位**：此為查詢流程，`updater`、`updatetime` 等欄位僅供內部記錄，不可被前端修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| Token 無效或過期 | 401 Unauthorized |
| `businessCode` 不存在於 `gametype_settings` 的 Partition Key | 返回空 `{}` 或 `404`（取決於 Service 設計） |
| `gameType` 在該 `company` 下不存在 | 返回空 `{}`（Cassandra 單行查詢為空結果） |
| Cassandra 資料庫不可用 | 500 Internal Server Error（依框架 retry/fallback 設定） |
| `settings` 欄位值為損毀的 JSON | 500 Internal Server Error 或返回空設定並記錄 log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-SITE-01 | API Test / Permission | 無 Token 呼叫 GET | 401 |
| TC-SITE-02 | API Test / Flow | `businessCode` 存在 & `gameType` 存在 | 200，body 為有效 JSON 設定 |
| TC-SITE-03 | Flow Test | `businessCode` 存在但 `gameType` 不存在 | 200 / 404，body 為 `{}`（視設計） |
| TC-SITE-04 | API Test | `businessCode` 不存在 | 200 / 404，body 為 `{}` |
| TC-SITE-05 | Integration Test | Cassandra 強制延遲／拒絕連線 | 500，記錄 error log |
| TC-SITE-06 | API Test | 回傳內容確認 | 無 `password` 或 `authtoken` 等敏感欄位 |

---

## 9. 高風險區域

- **公司隔離失效**：若查詢條件未包含 `company` 或使用範圍掃描，可能回傳非該商家的設定。
- **JSON 解析崩潰**：若 `settings` 字串損壞，解析時可能拋出例外導致 API 崩潰。
- **快取一致性**：本服務不直接使用 Redis，但若上游（如 syncservice）有快取 `gamesettings:company:{company}:gametypes` 而在更新站台設定後未 purge，可能導致回傳舊資料。

---

## 10. 常見錯誤

- ❌ 未檢查 Token 有效性 → API 應由 ECFramework 攔截，但不小心放行會洩露設定。
- ❌ 使用全表掃描查詢 `gametype_settings`（未指定 company）→ 正確做法是 always 帶上 Partition Key。
- ❌ 將 `settings` 內容與其他業務欄位混雜再轉為 DTO → 應保持純設定傳輸。
- ❌ 查詢不存在記錄時拋出 exception 而非回傳空 body → 應處理 Cassandra `RowSet` 為空的狀況。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/siteconfigs/{businessCode}/{gameType}` 於 OpenAPI / README |
| DB | Cassandra `gamesettings.gametype_settings` (Composite Key `company, gametype`) |
| DB Schema | db/gamesettings.md（`company text, gametype text, settings text...`） |
| 服務依賴 | gamesettingservice 直接存取 Cassandra，不透過 Redis |
| Company 隔離規則 | gamesettings-detail.md：`gametype_settings` 讀取須確保 `company` 為該業務所屬公司 |
| Code 推斷 | `IConfigService.GetBusinessGameTypePlayModeConfig` 命名慣例映射本查詢模式 |