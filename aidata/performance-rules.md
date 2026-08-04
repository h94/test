# 效能規範（Performance Rules）

**版本**：v1.0  
**最後更新**：2026-06-03

本文件為團隊程式碼效能品質標準，供 `@perf-review` 引導師與 pr-review 效能快掃使用。

---

## 1. 通用原則

- 優先選擇正確的演算法與資料結構，再考慮微調
- 避免 Premature Optimization，但必須避免明顯的反模式
- 所有高頻路徑（Hot Path）必須經過審核
- 可觀測性優先：重要功能必須能方便監控

---

## 2. 程式碼層級規範

### 2.1 複雜度控制

- 單一函數圈複雜度（Cyclomatic Complexity）≤ 12（建議 ≤ 10）
- 單一檔案不超過 800 行（不含註解與空行）；C# Service 層若超過可評估是否拆分 partial class 或抽出 helper
- 避免深度巢狀（最多不超過 4 層）

### 2.2 資料庫

- **禁止 N+1 Query**：必須使用 JOIN、Batch Query 或 DataLoader
- 高頻查詢必須建立適當索引
- 禁止在迴圈中執行 SQL
- 分頁查詢必須使用 LIMIT + OFFSET 或 Cursor-based Pagination
- 交易（Transaction）範圍越小越好

### 2.3 API 與外部呼叫

- 所有 HTTP Client 必須設定 Timeout（預設 5 秒，最大 15 秒）
- 外部呼叫建議使用 Circuit Breaker + Retry 機制
- 高頻外部呼叫必須實作 Cache（至少 Local Cache）

### 2.4 記憶體與物件

- 避免在 Hot Path 中建立大量臨時物件
- 大檔案或大型物件處理必須使用 Streaming
- 禁止在迴圈中做字串 `+` 拼接（使用 StringBuilder 或 join）

### 2.5 並行與非同步

- I/O 密集型操作優先使用 Async
- 避免在 Async 方法中混用 Blocking Call
- 共享資源存取必須正確使用 Lock 或 Concurrent 結構

---

## 3. 風險等級

| 等級 | 描述 | 處理要求 |
|------|------|----------|
| 🔴 High | 會明顯影響系統穩定性或效能 | Merge 前必須修正 |
| 🟡 Medium | 存在明顯優化空間 | 本 Sprint 內建議處理 |
| 🟢 Low | 輕微問題或可接受 | 記錄即可，後續追蹤 |

---

## 4. 常見反模式

- 在迴圈中呼叫資料庫 / API
- 使用 `SELECT *` 而非明確欄位
- 未使用索引的模糊查詢（`LIKE '%xxx'`）
- 大量使用 Reflection 或 Dynamic SQL（除非必要）
- 未做快取的使用者權限 / 配置資訊查詢

---

## 5. 建議模式

- Repository Pattern + Query Builder
- Cache-Aside Pattern
- Event-Driven 架構（非同步處理）
- Bulk Operation（Batch Insert / Update）
- 讀寫分離（Read Replica）

---

## 6. 監控與觀測性

- 所有外部呼叫與資料庫查詢必須記錄耗時
- 關鍵功能需埋入 Metrics（Prometheus）
- 重要流程需記錄 Trace ID
