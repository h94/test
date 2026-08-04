# 每日清理過期閥值設定

## 1. 場景目的

每日定時清理過期的遊戲閥值設定（`oddthreshold_game_setting`）及已完成的同步暫存記錄（`threshold_sync_pending`），確保資料庫效能並避免堆積。

---

## 2. 入口 API

此場景為背景 Worker 任務，無對外 API。

- 觸發方式：背景 Worker 定時呼叫（每日執行一次）。
- 相關代碼位置：需人工確認（`Tasks.py` 或排程模組）。

---

## 3. 流程總覽

1. 每日觸發清理任務。
2. 刪除 `oddthreshold_game_setting` 中 `gdate` 早於今天的過期設定。
3. 刪除 `threshold_sync_pending` 中 `status='done'` 且 `created_at` 超過保留期限的同步記錄。
4. 追蹤清理結果（DB 刪除筆數 Log）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Worker/Scheduler | 需人工確認 | 定時觸發（每日一次） |
| 2 | Provider | `oddthreshold_game_setting` 相關 Provider | 執行 DELETE 語句，刪除 `gdate < today` 的記錄 |
| 3 | Provider | `threshold_sync_pending` 相關 Provider | 執行 DELETE 語句，刪除 `status='done'` 且 `created_at` 超過保留期限的記錄 |
| 4 | Worker | 需人工確認 | 記錄刪除筆數 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_game_setting` | DELETE | 移除過期遊戲閥值設定 |
| DB | `threshold_sync_pending` | DELETE | 移除已完成且過期的同步暫存記錄 |

> **注意**：此場景未涉及 Redis、Kafka 或 Queue 操作。

---

## 6. 重要規則

- **欄位限制**：
  - `oddthreshold_game_setting.gdate` 為字串格式日期，用於判斷過期。
  - `threshold_sync_pending.status` 必須為 `'done'` 才會被清理。
- **TTL 規則**：
  - 遊戲閥值設定：過期日定義為 `gdate < 今日`。
  - 同步暫存記錄：需人工確認保留期限（例如保留 7 天或 30 天）。
- **不可修改欄位**：此為刪除操作，無欄位修改。
- **時區**：所有時間比較以 `Asia/Taipei` 為準。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| DB 連線失敗或 timeout | 任務失敗，需記錄錯誤並重試（Retry 規則需人工確認） |
| 刪除操作部分失敗 | 需人工確認交易範圍（是否使用 Transaction） |
| 無過期資料 | 正常執行，刪除 0 筆 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T001 | Integration Test | 存在過期遊戲閥值設定 | 僅刪除 `gdate < today` 的記錄 |
| T002 | Integration Test | 存在 `status='done'` 的過期同步記錄 | 僅刪除符合條件的記錄 |
| T003 | Flow Test | 執行兩次清理任務 | 第二次刪除筆數為 0（Idempotency） |
| T004 | API Test | 不存在任何過期資料 | 任務正常完成，刪除筆數 0 |

---

## 9. 高風險區域

- **高風險 Table**：
  - `oddthreshold_game_setting`：誤刪可能影響遊戲層級監控。
  - `threshold_sync_pending`：誤刪可能影響下游同步機制（需確認下游消費邏輯，若僅依賴 `status='pending'` 則風險較低）。
- **Idempotency**：需確保重複執行不會誤刪未過期資料。
- **Transaction**：若兩張表刪除操作未包在同一 Transaction，可能出現部分成功。需人工確認。

---

## 10. 常見錯誤

- 新人容易直接手動執行 SQL 而不透過排程，可能誤刪資料。
- 未注意時區差異，導致過期判斷錯誤。
- 未確認 `threshold_sync_pending` 保留期限，可能過早刪除導致同步異常。
- AI 容易誤解：此任務只清理「已完成」的同步記錄，並非所有舊記錄。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 任務描述 | `README.md`：「每日清理過期的遊戲閥值設定與同步暫存記錄」 |
| DB Table | `migrations/001_create_core_tables.sql` → `oddthreshold_game_setting` |
| DB Table | `migrations/003_create_sync_tables.sql` → `threshold_sync_pending` |
| DB Schema | `oddthreshold_game_setting.gdate`（字串格式日期） |
| DB Schema | `threshold_sync_pending.status`（值包含 `'done'`） |
| 代碼 | 需人工確認（`Provider/` 下 `oddthreshold_*.py` 及 `threshold_sync_pending.py` 中的 DELETE 邏輯） |

---

## 12. 建議新增項目

- 建議新增設定檔明確定義 `threshold_sync_pending` 保留天數。
- 建議新增監控指標（刪除筆數）供日誌或警報使用。
- 建議新增測試腳本驗證 Idempotency 與時區正確性。