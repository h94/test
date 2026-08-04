# 建立球種警示來源設定

## 1. 場景目的
為指定球種（game_type）設定主要警示來源（primary_source）與次要警示來源（secondary_sources），以決定該球種的警示資料從哪些數據源處理。

---

## 2. 入口 API
（需人工確認：以下端點為推測，OpenAPI 文件中未完整列出此資源）

| Method | Path | 說明 |
|---|---|---|
| POST | `/alertbackendservice/api/sport_alert_sources` | 建立一筆球種警示來源設定 |
| PUT | `/alertbackendservice/api/sport_alert_sources/{game_type}` | 更新指定球種的警示來源設定 |

若提供 POST，body 需包含 game_type、primary_source、secondary_sources 與 operator_account。

---

## 3. 流程總覽
1. 接收建立請求（game_type、primary_source、secondary_sources、operator_account）
2. 驗證必要欄位不為空
3. 確認 game_type 是否已存在設定（若存在返回 409 或視業務邏輯而定）
4. 寫入 `sport_alert_sources` 資料表
5. 回傳成功（201 Created）
6. （需人工確認）若閥值異動規則適用，寫入 changelog 與同步佇列，否則不進行

---

## 4. 程式流程
（需人工確認：實際 Class／Method 名稱需以原始碼為準）

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportAlertSourcesResource.create | 接收 POST 請求，轉交 Service |
| 2 | Service | SportAlertSourcesService.create | 驗證參數、檢查重複 |
| 3 | Provider | SportAlertSourcesProvider.insert | 執行 INSERT 至 sport_alert_sources |
| 4 | Service | SportAlertSourcesService.create | 若需要，寫入 changelog／同步 |
| 5 | Controller | 回傳 201 | 回傳成功訊息 |

---

## 5. DB / Cache / Queue 使用
（需人工確認）

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sport_alert_sources` | INSERT | 儲存球種警示來源設定 |
| DB | `threshold_changelog` | INSERT（可能） | 記錄異動歷程（若納入閥值稽核） |
| DB | `threshold_sync_pending` | INSERT（可能） | 排入同步佇列供下游消費（若納入） |
| Queue | Kafka | Publish（可能） | 通知下游設定變更（若有實作） |

---

## 6. 重要規則
- **唯一性**：同一 `game_type` 只能有一筆警示來源設定，不可重複建立（PK: game_type）。
- **必要欄位**：`game_type`、`primary_source` 必須提供；`secondary_sources` 可為空陣列或 null。
- **操作者紀錄**：`operator_account` 必填，用於稽核。
- **時區**：所有時間戳記（created_at、updated_at）使用 `Asia/Taipei`。
- **JSON 格式**：`secondary_sources` 必須是有效的 JSON 陣列。
- **權限限制**：需後台管理權限（需人工確認：通常須登入且具備設定管理權限）。
- **不可修改欄位**：`created_at` 由系統自動設定，不可由 API 傳入。
- **Transaction**：單一 INSERT 操作，無跨表事務需求（除非另加 changelog 寫入，則需包在同一 transaction）。

---

## 7. 錯誤情境
（假設 API 設計與其他設定端點一致）

| 情境 | 預期結果 |
|---|---|
| `game_type` 未提供或空白 | 422 Validation Error |
| `primary_source` 未提供或空白 | 422 Validation Error |
| `secondary_sources` 格式非 JSON 陣列 | 422 Validation Error |
| 同一 `game_type` 已存在 | 409 Conflict（或依業務邏輯採用 PUT 行為）|
| `operator_account` 未提供 | 422 Validation Error |
| DB 連線失敗 | 500 Internal Server Error |
| 同時寫入 changelog 失敗（若存在） | 需人工確認：可能 rollback 主設定或僅記錄 log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常建立新球種警示來源 | 201，資料正確寫入 |
| TC02 | Validation Test | 缺少 primary_source | 422，錯誤訊息指明欄位 |
| TC03 | Validation Test | secondary_sources 為非法 JSON | 422 |
| TC04 | Conflict Test | 對已存在 game_type 再建立 | 409 或更新成功（依設計）|
| TC05 | Data Integrity | 檢查 created_at 由系統設定 | 日期格式正確，時區為 TPE |
| TC06 | Permission Test | 無效或遺漏 operator_account | 422 或 401（若需權驗）|

---

## 9. 高風險區域
- **重複建立**：若未正確檢查唯一性，可能導致多筆同一 game_type，影響警示派送邏輯。
- **操作者帳號遺漏**：若未強制填寫，稽核追蹤困難。
- **異動同步**：若須通知下游服務（如 OddAlertService），漏發 queue 可能造成警示來源不一致。
- **cache 一致性**：目前無 Redis cache 使用證據，若後續有加入，須注意清除或更新。
- **Index**：`game_type` 為 TEXT 型別，查詢效能須確保索引存在（通常 migration 會建立 PK）。

---

## 10. 常見錯誤
- 忽略 `game_type` 大小寫問題：應統一使用小寫（參考 alerts 表的 game_type 大小寫處理）。
- 將空的 `secondary_sources` 設為 null 而非空陣列，影響下游解析。
- 忘記填 `operator_account`，導致寫入空值，日後無法追溯操作者。
- （若實作同步）忘記在建立設定後寫入 changelog/sync pending，導致下游無法取得最新設定。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB table | `migrations/001_create_core_tables.sql` → `sport_alert_sources` 定義 |
| OpenAPI 端點 | 未在提供的 OpenAPI 片段中出現，需人工確認實際路由 |
| Code | 推測為 `Resources/sport_alert_sources.py` / `Service/` / `Provider/sport_alert_sources.py`，需人工確認 |
| README | 說明「警示來源設定（sport_alert_sources）：指定各球種的主要與次要警示來源」 |
| 權限與稽核 | README 提到閥值異動寫 changelog 與同步，但警示來源設定是否納入該機制需人工確認 |

- **需人工確認**：實際 API 路徑、HTTP method、是否存在 changelog / sync 邏輯、Kafka 通知、權限驗證機制。
- **建議新增文件**：`db-usage/sport_alert_sources.md` 說明該表用途與下游依賴關係。
- **建議新增測試**：整合 Kafka 或 Queue 的 end-to-end 測試，確認設定變更後下游能正確接收。