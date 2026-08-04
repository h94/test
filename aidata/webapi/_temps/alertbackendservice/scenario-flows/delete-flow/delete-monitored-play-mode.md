# 刪除監控玩法設定

## 1. 場景目的
移除指定球種（game_type）的監控玩法設定，使該球種不再觸發對應玩法的賠率異常監控。

---

## 2. 入口 API
**需人工確認**：現有 OpenAPI 文件與已知路由中均未揭露監控玩法的刪除端點，可能為
- `DELETE /api/monitored_play_modes/{game_type}`（未公開），或
- 透過 `PUT /api/monitored_play_modes/{game_type}` 傳入空設定達成邏輯刪除。

---

## 3. 流程總覽
1. 接收目標球種代碼 `game_type`（路徑參數）。
2. 驗證該球種的監控玩法設定是否存在（若不存在則回應 404）。
3. **（推測）** 執行資料庫刪除，移除 `monitored_play_modes` 中對應記錄。
4. 寫入稽核記錄至 `threshold_changelog`（記錄 table_name=monitored_play_modes、old_value 等）。
5. 將同步任務排入 `threshold_sync_pending`，供下游服務同步變更。
6. 回傳成功（204 或 200）。

---

## 4. 程式流程（推測）

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `Resources/MonitoredPlayModes.py` 的 `delete_monitored_play_modes` | 接收 `game_type`，呼叫 Service 刪除 |
| 2 | Service | `Service/MonitoredPlayModesService.py` 的 `delete_monitored_play_modes` | 檢查記錄存在、執行刪除、寫入 changelog、觸發同步 |
| 3 | Provider | `Provider/monitored_play_modes.py` 的 `delete_by_game_type` | 對資料庫執行 `DELETE FROM monitored_play_modes WHERE game_type = ?` |
| 4 | Provider | `Provider/threshold_changelog.py` 的 `insert` | 記錄異動至 `threshold_changelog` |
| 5 | Provider | `Provider/threshold_sync_pending.py` 的 `enqueue` | 寫入同步佇列 `threshold_sync_pending` |

*備註：以上 Layer 方法名稱僅為推測，需人工確認實際程式碼結構。*

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `monitored_play_modes` | Delete | 移除指定球種的監控玩法設定 |
| DB | `threshold_changelog` | Write | 稽核刪除操作，保留舊值 |
| DB | `threshold_sync_pending` | Write (INSERT) | 通知同步模組，有設定變更 |
| Redis | 未使用 | - | 本次流程未直接快取相關設定（**需人工確認**：查詢階段可能使用 Redis 快取？） |
| Kafka/Queue | 未直接使用 | - | 同步是透過 `threshold_sync_pending` 表，而非 Kafka，後續排程 Worker 會讀取並發佈至 Kafka（根據 README，但本場景只負責寫入 pending 表） |

---

## 6. 重要規則

- **記錄存在性檢查**：若 `game_type` 不存在於 `monitored_play_modes` 表，應回傳 404（**需人工確認**目前實作是否如此）。
- **權限限制**：需驗證操作者 `operator_account`，避免未授權刪除（**需人工確認**權限驗證點，可能由 API Gateway 或 Middleware 處理，或從 request body 中取得 account）。
- **不可回復**：刪除為破壞性操作，未發現軟刪除或備份機制；一旦刪除，該球種將不再產生相關警示（直到重新建立）。
- **稽核不可遺漏**：務必寫入 `threshold_changelog`，並保留完整 `old_value`（**需人工確認**對應 `record_key` 的格式，應包含 `{"game_type": "xxx"}`）。
- **同步保證**：刪除成功後，`threshold_sync_pending` 表必須包含一筆 `status='pending'` 的記錄，以確保下游能感知變更；若寫入失敗，應視為操作失敗或進行重試。
- **Transaction**：刪除主表、寫入 changelog 與同步 pending 應在同一個 DB transaction 中，以保證資料一致性（**需人工確認**實際是否使用 asyncpg 的 transaction 管理）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `game_type` 不存在 | 回傳 404 Not Found（或 409 若使用特定設計） |
| 操作者帳號未提供或無權限 | 回傳 403 Forbidden |
| 資料庫刪除失敗（例如連線逾時） | 回傳 500 Internal Server Error，記錄錯誤日誌 |
| 寫入 changelog 失敗 | 整筆操作應該 rollback，回傳 500 |
| 寫入 `threshold_sync_pending` 失敗 | 整筆操作 rollback，回傳 500，保證主表與同步狀態一致 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| DEL-01 | API Test | 刪除已存在的球種設定（例如 "soccer"） | 返回 200/204，查詢該球種不再存在 |
| DEL-02 | API Test | 刪除不存在的球種 | 返回 404 |
| DEL-03 | API Test | 無效的 game_type（特殊字元…） | 返回 422 或 400 |
| DEL-04 | Flow Test | 刪除成功後檢查 changelog | `threshold_changelog` 有一筆 table_name='monitored_play_modes'，record_key 對應該 game_type，old_value 不為空 |
| DEL-05 | Flow Test | 檢查同步 pending | `threshold_sync_pending` 狀態為 pending，table_name 為 monitored_play_modes |
| DEL-06 | Transaction Test | 模擬 changelog insert 失敗 | 主表應未被刪除，回傳 500 |
| DEL-07 | Permission Test | 缺少 operator_account | 返回 403（若實作有驗證） |

---

## 9. 高風險區域

- **直接刪除無備份**：`monitored_play_modes` 中 game_type 一經刪除，立刻影響所有相應的即時監控，可能錯失異常賠率行為。
- **同步機制依賴 DB 表**：如果同步排程 Worker 異常，下游可能長時間未更新，導致資料不一致。
- **Transaction 範圍**：若未將 changelog 與 pending 寫入包在一起，可能出現主表已刪除但同步通知未送出的情形。
- **權限控制**：若刪除動作未嚴格限制角色（例如僅限管理員），可能遭誤刪。

---

## 10. 常見錯誤

- **新人誤解**：以為透過 PUT 更新成空陣列即可達到刪除效果，但實際上可能仍存在一筆記錄（若系統未實作 DELETE，則需確認正確做法）。**
- **AI 誤解**：可能自行生成 DELETE 端點的實作，但實際上該服務未提供，需嚴格依照既有 API。
- **漏檢查**：刪除後未驗證同步 pending 是否寫入，導致下游永遠不知道設定已刪除。
- **錯誤處理不足**：只處理 HTTP 層成功，未留意 changelog 寫入失敗可能導致稽核缺失。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| OpenAPI 缺少 DELETE | `openapi.json` 中未定義，路徑 `_reference` 未出現刪除端點 |
| 資料表結構 | `migrations/001_create_core_tables.sql`：`monitored_play_modes` 包含 `game_type`, `play_mode`, `operator_account` 等 |
| 稽核表 | `threshold_changelog` 設計可記錄所有閥值異動，包括 `monitored_play_modes` |
| 同步機制 | `threshold_sync_pending` 負責通知同步，READM.md 提及「閥值異動皆寫入 changelog，並將變更排入同步佇列供下游消費」 |
| 現有操作方法 | Provider 文件 `monitored_play_modes.py` 已知有 `list_all`、`create`，推測存在 `delete` 方法（**需人工確認**） |

**建議補充**：  
- 確認刪除 API 的實際路由與方法。  
- 補齊 API 權限驗證規則。  
- 增加 `DELETE /api/monitored_play_modes/{game_type}` 的 OpenAPI 定義（若尚未有）。  
- 提供整合測試腳本 `Tests.py` 中有關刪除的案例（若已有）。