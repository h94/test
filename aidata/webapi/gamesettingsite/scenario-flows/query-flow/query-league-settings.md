# 場景：取得聯賽設定

## 1. 場景目的
根據指定的公司（company）與遊戲類型（gametype），從 `gamesettings` Cassandra keyspace 的 `league_settings` 表中，查詢並回傳對應的聯賽設定資料。此設定主要用於動態玩法佈局的映射。

**⚠️ 需人工確認：** 此 API 的具體路由、參數格式及是否為獨立端點或合併於其他接口，在所提供文件中無法確定。以下分析基於服務職責與 DB 操作慣例推導。

---

## 2. 入口 API
**需人工確認**：OpenAPI 與提供的 code evidence 中均未揭露此場景的端點。依據 DB 職責推斷，可能為內部 API。

| Method | Path | 說明 |
|---|---|---|
| GET | 需人工確認 | 需人工確認。預期路徑可能包含 `company` 和 `gametype` 參數 |

---

## 3. 流程總覽
基於本服務的職責與 DB 使用限制，推導的流程如下：

1.  API 接收請求，內含 `company` 與 `gametype` 參數。
2.  驗證參數格式與必要性。
3.  實例化 Cassandra 查詢，指定完整的 keyspace 與 table：`gamesettings.league_settings`。
4.  查詢 `league_settings` 表，以 `company` 和 `gametype` 為完整主鍵條件進行精確查詢。
5.  讀取並組合回傳資料，特別是 `leagues` 和 `settings` 欄位。
6.  根據服務邊界規則，過濾不回傳的機敏欄位（若有）。
7.  回傳成功結果；若查無資料則回傳空或適當的錯誤碼。

---

## 4. 程式流程
因無確切程式碼，以下為基於 .NET 6 服務慣例的推導。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收 HTTP GET 請求，取得 `company`, `gametype`。 |
| 2 | Controller | 需人工確認 | 呼叫對應的 Service 方法。 |
| 3 | Service | 需人工確認 | 商業邏輯層，準備查詢條件。本場景可能直接呼叫 Provider。 |
| 4 | Provider | 需人工確認 (e.g., `GameSettingProvider`) | 實作 Cassandra 查詢。 |
| 5 | Provider | 需人工確認 | 建立 `SELECT` 語句，指定 `company` 與 `gametype` 查詢。 |
| 6 | Provider | 需人工確認 | 執行查詢並將結果映射至 DTO。 |

---

## 5. DB / Cache / Queue 使用
根據 db-usage，本服務僅直接操作 Cassandra，未使用 Redis 或 Kafka。

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `gamesettings.league_settings` | Read | 讀取特定 `company` 與 `gametype` 的聯賽設定。 |

---

## 6. 重要規則
- **查詢規則：** 查詢 `league_settings` 時，必須以 `company`（分區鍵）和 `gametype`（集群鍵）作為完整主鍵條件，**嚴禁**任何形式的全表掃描。
    - **Evidence:** `gamesettingsite-detail.md` 規範：“查詢 `league_settings`：必須帶入 `company` + `gametype`（完整主鍵）”
- **不回傳欄位：** `settings` 欄位為 JSON 字串，回傳前必須確保無機密配置（如內部 API 位址）外洩。若 `league_settings` 表有其他記錄操作者的機敏欄位，亦不可回傳。
    - **Evidence:** `gamesettingsite-detail.md` 規範：“game_settings.settings / gametype_settings.settings 視業務需求決定是否回傳；若回傳，須確認無機密配置外洩。”
- **權限限制：** 此為內部服務 API，需確認是否有額外的內部服務驗證機制。
- **不可修改欄位：** `gamesettingsite` 作為讀取方，**嚴禁**對 `league_settings` 表執行寫入操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `company` 或 `gametype` 參數缺失 | 應回傳 HTTP 400 Bad Request 錯誤，提示缺少必要參數。 |
| 指定的 `company` 或 `gametype` 不存在 | 回傳 HTTP 200 OK，但 body 為空物件或空列表（依實際定義）。 |
| 對 Cassandra 進行全表掃描（缺少 `company` 條件） | 服務端應拒絕此查詢，可能拋出例外並記錄錯誤日誌。不應對外暴露詳細錯誤。 |
| Cassandra 連線逾時或暫時無法使用 | 服務應有重試機制，次數過多則回傳 HTTP 503 Service Unavailable。 |
| `settings` 欄位內容非合法 JSON | 應記錄錯誤並回傳 HTTP 500 Internal Server Error，並將此資料視為損毀。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| LS-01 | API Test | 提供有效的 `company` 和 `gametype` | HTTP 200, body 包含正確的 `leagues` 和 `settings` 資訊。 |
| LS-02 | API Test | 提供有效的 `company` 但無效的 `gametype` | HTTP 200, body 為空或查無資料的標示。 |
| LS-03 | API Test | 缺少 `company` 參數的請求 | HTTP 400, 包含明確的錯誤訊息。 |
| LS-04 | Security Test | 檢查回應中 `settings` 欄位內是否包含內部 IP 或金鑰 | 確認無機敏資訊暴露。 |
| LS-05 | DB Test | 模擬 Cassandra 查詢條件缺乏 `company` | 確認服務內部在執行查詢前正確檢查了完整主鍵。 |

---

## 9. 高風險區域
- **高風險 Table:** `gamesettings.league_settings`。其 `settings` 欄位內容若未經審查直接對外暴露，可能洩漏架構資訊。
- **Cache consistency:** 目前 db-usage 指出本服務無 Redis。若未來為此場景導入快取（例如快取 `league_settings` 結果），必須在設定變更時主動失效快取。否則前端將顯示過期的聯賽配置。
- **跨服務資料同步:** `league_settings` 的寫入應由其他負責服務（如 `syncservice` 或 `gamesettingservice`）管理。`gamesettingsite` 為純讀取方，若讀到不一致的過渡資料，須由寫入方確保 Transaction 或最終一致性。

---

## 10. 常見錯誤
- **新人易錯：** 誤將 `league_settings` 當成 `league_logs` 查詢。`league_logs` 儲存的是聯賽記錄，兩者用途不同。
- **AI 易誤解：** 推斷出一個不存在的 API 路由，或在沒有的情況下假設使用了 Redis 快取。
- **常見漏檢查：** 未檢查 `settings` 欄位的內容就直接序列化回傳，導致敏感配置外洩。
- **常見錯誤流程：** 在 Cassandra 查詢時，嘗試使用 `ALLOW FILTERING` 或未帶入完整主鍵而觸發全表掃描。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 服務角色 | `gamesettingsite-detail.md` (gamesettings: owner / writer / reader) |
| Table 名稱 | `gamesettings.league_settings` (from DB schema truncated section) |
| DB 操作 | `gamesettingsite-detail.md` (league_settings 需完整主鍵查詢) |
| 不可回傳欄位規則 | `gamesettingsite-detail.md` (settings 欄位需確認無機密) |
| API / Service 方法 | **需人工確認** |