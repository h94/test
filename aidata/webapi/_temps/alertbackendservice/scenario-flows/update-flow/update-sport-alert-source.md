# 更新球種警示來源設定

## 1. 場景目的

修改指定球種的主要警示來源與次要警示來源清單，確保後續產生的警示能引用正確的資料來源組合。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/sport_alert_sources/{game_type}` | 更新 `game_type` 對應的警示來源設定 |

---

## 3. 流程總覽

1. 接收 PUT 請求，包含 `game_type` 路徑參數與 request body
2. 驗證 `game_type` 非空
3. 查詢 `sport_alert_sources` 是否已有該 `game_type` 的記錄（若無則視為新增，視業務邏輯決定是否拒絕或創建）
4. 更新 `primary_source`、`secondary_sources`、`operator_account`、`updated_at`
5. 寫入異動紀錄至 `threshold_changelog` 表
6. 將同步任務排入 `threshold_sync_pending` 佇列，供下游消費
7. 回傳成功（200）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Resource | `sport_alert_sources_router.put("/{game_type}")` | 接收 `game_type` 與 body，呼叫 Service |
| 2 | Service | `SportAlertSourcesService.update()`（推測） | 處理業務邏輯，組裝資料 |
| 3 | Provider | `SportAlertSourcesProvider.upsert()`（推測） | 執行 DB upsert |
| 4 | Provider | `ThresholdChangelogProvider.insert()` | 寫入 changelog |
| 5 | Provider | `ThresholdSyncPendingProvider.enqueue()` | 寫入同步 pending 記錄 |

> 注：Resource 與 Service 層具體名稱需人工確認，目前僅由 db 操作反向推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sport_alert_sources` | Upsert（Write / Update） | 儲存警示來源設定 |
| DB | `threshold_changelog` | Insert | 異動稽核 |
| DB | `threshold_sync_pending` | Insert | 同步任務排程 |

---

## 6. 重要規則

- **欄位限制**：`primary_source` 為字串，`secondary_sources` 須為 JSON 陣列（字串清單）
- **不可暴露資料**：無額外敏感欄位要求
- **不可修改欄位**：`created_at` 由系統自動管理，不可從 API 傳入
- **Transaction 規則**：更新 `sport_alert_sources`、寫入 changelog、寫入 sync pending 應包裹在一個交易中（需人工確認實際實作）
- **權限**：`operator_account` 僅記錄操作者，無額外 RBAC 攔截（需人工確認）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不存在 | 依現行規則可能自動建立（需人工確認），或回傳 404 |
| `primary_source` 空白 | 回傳 422 Validation Error |
| `secondary_sources` 格式錯誤（非陣列） | 回傳 422 Validation Error |
| DB 寫入失敗 | 回傳 500，changelog 與 sync 皆不會殘留 |
| 同步佇列寫入失敗 | 觸發回滾，返回 500（若使用 Transaction） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Flow Test | 成功更新既有 `game_type` 的 sources | `sport_alert_sources` 記錄更新，changelog 與 sync pending 正確寫入 |
| UT-02 | Flow Test | 對不存在的 `game_type` 進行 PUT | 依設計決定是否自動建立（需人工確認），否則 404 |
| UT-03 | Permission Test | operator_account 缺失或格式錯誤 | 422 Validation Error |
| UT-04 | Integration Test | 更新後查詢該球種警示是否採用新來源 | 新產生的警示應使用更新後的 `primary_source` 與 `secondary_sources`（由下游服務驗證） |

---

## 9. 高風險區域

- **高風險 table**：`sport_alert_sources` – 直接影響警示產生的資料源選擇邏輯
- **高風險 API**：`PUT /api/sport_alert_sources/{game_type}` – 不當更新可能造成監控失效
- **跨服務資料同步**：寫入 `threshold_sync_pending` 後需確保下游確實消費，否則設定不一致
- **Transaction**：changelog 與 sync pending 必須與主表操作原子化，防止部分成功
- **Cache consistency**：若下游快取來源設定，需設計 cache invalidation（需人工確認）

---

## 10. 常見錯誤

- 忘記傳遞 `operator_account`，導致 DB constraint 或空值
- `secondary_sources` 誤傳字串而非陣列
- 混淆 `primary_source` 與 `secondary_sources` 的順序，導致 source 優先級錯誤
- 未於 Transaction 中包覆 changelog 寫入，造成異動遺失
- AI 容易將此操作誤認為覆蓋所有欄位（實際上應只更新 sources，保留其他欄位；但本表欄位簡單，影響不大）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | Resource 層定義於 `Resources/sport_alert_sources.py`（推測，需人工確認） |
| DB table | `sport_alert_sources` (`migrations/001_create_core_tables.sql`) |
| DB fields | `game_type`, `primary_source`, `secondary_sources`, `operator_account`, `created_at`, `updated_at` (from schema) |
| Changelog | `threshold_changelog` table (semantics from `threshold_changelog.py:insert`) |
| Sync queue | `threshold_sync_pending` table (semantics from `threshold_sync_pending.py:enqueue`) |
| 邏輯關聯 | README: “閥值異動皆寫入 changelog，並將變更排入同步佇列” |

> 部分方法名稱與流程細節尚無完整程式碼證據，標記「需人工確認」。