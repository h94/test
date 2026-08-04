# 爬蟲心跳回報

## 1. 場景目的

各爬蟲程序定時向 `pricecentermanage` 服務回報自身執行狀態（心跳）。`pricecentermanage` 負責將心跳時間記錄於對應的爬蟲帳號（`accounts_{source}`）中，以便管理後台監控儀表板能查詢各爬蟲機器的健康狀態與最後活躍時間。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/system/machines/crawler` | 爬蟲心跳回報 |

---

## 3. 流程總覽

1. 爬蟲機器發送 POST 請求至 `/api/v1/system/machines/crawler`，攜帶自訂的 Payload 供後續解析。
2. Controller 層驗證請求合法性（驗證機制由 ECFramework 統一攔截，需為已驗證請求）。
3. Service 層取得 Payload 中的相關欄位（包含 `source`、`account`、`machinename` 等）。
4. Provider 層：
   - 依 `source` 決定目標 Cassandra table（如 `accounts_AU8`、`accounts_HGA` 等）。
   - 讀取該帳號現有 `handler` 欄位（型別為 `map<text, text>`）。
   - 將本次機器的 `machinename` 與當下時間寫入（或更新）至 `handler` map 中。
   - 更新帳號的 `handler` 欄位回 Cassandra。
5. 若帳號不存在或已停用（`enabled != 1`），則拒絕寫入並回傳錯誤。
6. 成功後回傳 200 OK。

> **需人工確認**：OpenAPI/Swagger 定義中，`CrawlerHeartBeat` 的 request body 欄位名與 Provider 端所用 `CrawlerInfo` 物件的實際屬性名，需核對是否完全一致（如 `machinename` 拼寫）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `CrawlerController.HeartBeat` | 接收請求，呼叫 Service。 |
| 2 | Service | `ISysManagerService` (推測) | 轉拋至 Provider，不處理業務邏輯。 |
| 3 | Provider | `ISysManagerProvider.CrawlerHeartBeat` | 執行核心心跳寫入邏輯。 |
| 4 | Provider | 同上 | 查詢 `accounts_{source}`，檢查 `enabled` 狀態。 |
| 5 | Provider | 同上 | 讀取現有 `handler`，更新 target machine 時間戳。 |
| 6 | Provider | 同上 | 寫入 `accounts_{source}` 的 `handler` 欄位。 |
| 7 | Controller | `CrawlerController.HeartBeat` | 回傳成功回應。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `pricecenter.accounts_{source}` | `SELECT`, `UPDATE` | 讀取帳號狀態與 handler，寫入心跳時間。 |

> **證據**：`accounts_{source}.handler` 為 `map<text, text>`，Key 為機器名稱，Value 為心跳時間戳。 (來源: `pricecenter-detail.md` 寫入限制)

---

## 6. 重要規則

- **權限限制**：API 需要驗證。
- **不可變更其他機器狀態**：寫入 `handler` 時「須確保不覆蓋其他機器的 handler 資訊」，僅能對本次回報的 `machinename` 對應的 Key 進行新增或更新。 (來源: `db/pricecenter-detail.md` 寫入限制)
- **帳號狀態驗證**：寫入前必須確認目標帳號 `enabled = 1` 且 `closetime` 為空，已關閉或停用的帳號應拒絕心跳。 (來源: `db/pricecenter-detail.md` 常見錯誤)
- **不可暴露資料**：`accounts_{source}.password` 及 `phone` 不應在此流程的日誌或回應中出現。
- **欄位不可修改**：`account` 為主鍵，不可修改。
- **寫入方式**：更新 `handler` 時，應先讀取現有 map，僅對此次的 `machinename` 進行 put 操作，不可直接 `SET handler = ?` 覆蓋整個 map。 (來源: `db/pricecenter-detail.md` 常見錯誤)

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未通過驗證 | 回傳 401 Unauthorized |
| 目標 `accounts_{source}` 不存在 | 回傳錯誤，拒絕更新 |
| 目標帳號 `enabled = 0` 或 `closetime` 非空 | 回傳錯誤（例如帳號已停用或關閉） |
| Payload 缺少必要欄位 | 回傳 400 Bad Request |
| Cassandra 寫入失敗或超時 | 回傳 500 或對應錯誤訊息 |
| 同一 `handler` 中同時有多個機器寫入 | 依序讀後寫，後寫者可能覆蓋先寫者（需注意並發控制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| HB-01 | API Test | 提供合法 payload，正常心跳 | 200 OK；對應 `handler` 中 `machinename` 時間戳被更新 |
| HB-02 | Permission Test | 無效 token 呼叫 | 401 Unauthorized |
| HB-03 | Flow Test | 目標帳號 `enabled=0` | 拒絕寫入，返回錯誤 |
| HB-04 | Integration Test | 多台機器對同一帳號先後心跳 | `handler` map 中各自 Key 均保留，未被覆蓋 |
| HB-05 | API Test | 重複發送心跳（相同 `machinename`）| 時間戳更新為最新值，不會產生多餘 Key |

---

## 9. 高風險區域

- **高風險 Table**：`pricecenter.accounts_{source}`，寫入衝突可能導致 `handler` 欄位資料遺失。
- **並發寫入**：`handler` 為 map 類型，沒有 Transaction 保護，多機器同時心跳時可能因 read-before-write 競爭而互相覆蓋。建議對單一帳號的寫入進行排隊（如 Actor 模型或分布式鎖）。
- **Idempotency**：此為單純心跳時間記錄，業務上具備冪等性（重複寫入只更新時間戳），但需避免因殘留錯誤邏輯而將整個 map 重置。

---

## 10. 常見錯誤

- **新人容易犯錯**：使用 `UPDATE table SET handler = ?` 直接覆蓋 map，導致其他機器的 Key 全部遺失。正確做法是應用層讀取、修改對應 Key、再寫回。
- **AI 容易誤解**：以為心跳回報會寫入 `machines` table，但實際上此流程是更新爬蟲**帳號** (`accounts_*`) 的 `handler` 欄位，與物理機器管理表 (`machines`) 不同。
- **常見漏檢查項目**：未檢查帳號 `enabled` 與 `closetime` 狀態就直接寫入。
- **常見錯誤流程**：未過濾 `handler` 中已存在但本次心跳無關的 Key，導致 update 語句不當而造成覆蓋。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/system/machines/crawler` (README.md, OpenAPI) |
| DB | `pricecenter.accounts_{source}` (pricecenter-detail.md, dbSchema) |
| Code | `ISysManagerProvider.CrawlerHeartBeat` (phase1 batch semantics) |
| Code | `PriceCenterManage.Model.Accounts` (semantics: handler 為 `map<text,text>`, Key=提供者, Value=心跳時間) |
| Code | `CrawlerController.HeartBeat` (phase1 batch-1) |