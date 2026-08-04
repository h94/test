# 每月警示資料自動封存

## 1. 場景目的

每月定期將符合時間門檻的舊警示資料從 `alerts` 表搬移至 `alerts_archive` 表，並清理原表資料，以維持主要警示表的查詢效能與儲存空間。

---

## 2. 入口 API

本場景為背景排程任務，無對外 API。透過 `Tasks.py` 中的排程器於每月 1 日觸發。

---

## 3. 流程總覽

1. 排程器啟動封存任務（每月 1 日，時間點需人工確認）
2. 計算「封存基準時間」（如有設定保留月數，則以**需人工確認**的規則決定）
3. 查詢 `alerts` 表中 `created_at` 早於基準時間的所有記錄
4. 以分批方式（**需人工確認**批次大小）將符合條件資料 INSERT 至 `alerts_archive`
5. 批次寫入與刪除交錯進行（使用 DB Transaction）
6. 從 `alerts` 表刪除已成功搬移至封存表的記錄
7. 記錄執行結果（成功／失敗）至日誌（可能寫入特定監控表或僅輸出至容器日誌，**需人工確認**）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Task | `Tasks.archive_old_alerts` (推測) | 觸發排程，確定執行週期為每月 1 日 |
| 2 | Service | `AlertArchiveService` (推測) | 計算封存時間窗，呼叫 Provider 進行查詢與搬移 |
| 3 | Provider | `AlertProvider.move_to_archive` (推測) | 執行 SQL：`INSERT INTO alerts_archive SELECT ... FROM alerts WHERE created_at < $1`，後接 `DELETE FROM alerts WHERE ...` |
| 4 | Provider | `AlertProvider.delete_batch` (推測) | 根據已搬移的 ID 批次刪除原表資料 |
| 5 | Logger | — | 記錄搬移筆數、執行耗時、錯誤訊息 |

註：實際類別與方法名稱需人工確認原始碼 `Tasks.py` 及相關 Service / Provider。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `alerts` | Read → Delete | 讀取舊資料、搬移後刪除 |
| DB | `alerts_archive` | Write | 寫入封存資料 |
| DB | — | 可能使用 `SELECT ... FOR UPDATE` 或 `COPY` | 避免搬移過程中的競爭（若排程非獨佔） |
| Redis | 可能使用鎖定 | Write（`SETNX`） | 確保多實例環境下只有一份排程執行（**需人工確認**） |
| Queue | — | — | 此場景未使用 Kafka 或 Queue |

---

## 6. 重要規則

- **保留期間**：基準時間的計算規則（例如保留最近 6 個月）**需人工確認**
- **資料寫入策略**：應使用 `INSERT INTO ... SELECT` 批次進行，避免一次性大量載入導致長時間鎖表
- **刪除策略**：必須在確認 `INSERT` 成功後才進行 `DELETE`，可使用單一事務確保一致性；若搬移失敗，原表資料不應被刪除
- **批次大小**：單批次處理筆數需根據資料量由環境變數或組態決定（**需人工確認**）
- **排程鎖定**：若服務採多 Pod 部署，需採用 Redis 或資料庫鎖確保同時只有一個排程實例執行（**需人工確認**）
- **索引與效能**：`alerts` 表的 `created_at` 應有索引，`alerts_archive` 如表體積龐大亦需考慮分區或索引策略（**需人工確認**）
- **不可修改欄位**：搬移至封存表後，所有欄位皆應為唯讀，僅供查詢，不可再變更

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 搬移 SQL 執行超時或失敗 | 整批事務回滾，原表資料保留，下一次排程重新嘗試 |
| 刪除 SQL 失敗 | 若與搬移在不同事務中，可能導致重複搬移（需依實作判斷）；應確保同一個事務內執行或具備冪等性 |
| 排程執行期間服務重啟 | 任務中斷，遺留資料待下次觸發再次處理；需確保搬移邏輯可重入 |
| 封存表缺乏足夠磁碟空間 | 搬移失敗，日誌記錄錯誤，管理人員需介入處理 |
| 跨日執行（處理大量資料跨越 0 點） | 對查詢條件無影響，因使用的基準時間在任務啟動時即固定 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ARCH-01 | Integration Test | 插入一批 3 個月前與 1 個月前的 alerts，執行封存只搬移 3 個月前資料 | 僅舊資料寫入 alerts_archive 且自 alerts 刪除，近期資料保留 |
| ARCH-02 | Flow Test | 模擬搬移過程中斷 DB 連線 | 無人為介入前，alerts 資料未被刪除，alerts_archive 無部分資料 |
| ARCH-03 | DB Test | 重複執行相同任務兩次 | 第二次無新資料搬移，不致重複寫入封存表（依實作需具冪等性） |
| ARCH-04 | Permission Test | 確認封存任務使用的 DB 帳號具備 `INSERT`, `SELECT`, `DELETE` 權限 | 操作成功，權限不足則應有明確錯誤 |

---

## 9. 高風險區域

- **alerts 表誤刪**：若搬移邏輯有誤，可能刪除不該刪的記錄；需嚴格以 `created_at` 與基準時間比對
- **交易邊界**：搬移與刪除需在同一 DB Transaction 或確保原子性；若分批無事務保護，可能因中途失敗導致部分搬移成功但原表未刪，造成後續重複搬移
- **長時間表鎖**：大量資料 `INSERT` 與 `DELETE` 可能造成 `alerts` 表長時間鎖定，影響前檯查詢；必須使用分批與適當隔離層級
- **時區一致性**：`created_at` 為 `TIMESTAMPTZ`，容器時區設為 `Asia/Taipei`，基準時間需明確以台灣時間計算

---

## 10. 常見錯誤

- 假設所有記錄都應被搬移，未正確過濾 `created_at`，導致誤刪近期資料
- 搬移與刪除未包在相同交易中，中斷後留下不一致狀態
- 未實作冪等性，排程重啟後重複搬入相同資料（若封存表無唯一約束）
- 忽略 `alerts` 表的外鍵關聯（如有，例如 `alert_change_log`）；搬移前需確認相關子表處理策略（**需人工確認**）
- 未記錄任何執行日誌，故障時難以追查

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 功能描述 | `README.md` - 定時排程：「每月 1 日執行警示資料自動封存」 |
| DB 表結構 | `migrations/002_create_supplement_tables.sql` - alerts_archive 定義 |
| 時區設定 | `README.md` - 容器時區設為 `Asia/Taipei` |
| 排程機制推斷 | `README.md` - 專案結構含 `Tasks.py`，負責背景 Worker |
| 缺乏直接 code 證據 | 本場景具體實作（Service/Provider）未出現在提供的程式語意分析中，相關方法與確切 SQL 需人工確認 `project/Tasks.py` 及 `project/Provider/` |