# 列出 Webhook 組態

## 1. 場景目的

提供後台管理人員查詢所有已設定的 Webhook 端點組態，包含名稱、URL、啟用狀態、觸發事件、速率限制與重試設定等，以便進行後續維護或除錯。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/webhooks（需人工確認） | 列出所有 Webhook 組態記錄 |

---

## 3. 流程總覽

1. 接收 GET 請求
2. 執行 Provider 層查詢 `webhooks` 資料表，取得全部記錄
3. 將資料庫回傳的 row 清單轉為回應格式
4. 回傳 JSON 陣列，每個元素包含 Webhook 完整欄位

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | WebhooksResource.list（需人工確認） | 接收請求，呼叫 Service |
| 2 | Service | WebhookService.list_all | 呼叫 Provider 取得全部資料 |
| 3 | Provider | WebhookProvider.list_all | 執行 `SELECT * FROM webhooks` |
| 4 | Service | WebhookService.list_all | 回傳 raw 資料清單 |
| 5 | Controller | WebhooksResource.list | 將結果序列化為 JSON 並回傳 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | webhooks | Read（SELECT） | 讀取所有 Webhook 組態 |

> 本場景單純查詢，不使用 Redis、Kafka 或 Queue。

---

## 6. 重要規則

- 無特殊權限限制（僅後台操作，前端校驗由閘道負責，需人工確認）
- 回傳所有欄位，無需濾除敏感資訊（url 可能包含密鑰，需人工確認是否需遮蔽）
- 查詢結果按 `id` 排序（依 Provider 實作，預設可能依 id ASC）
- 無分頁：一次回傳全部記錄（若後續量體增大，應考慮分頁，需人工確認）
- 不使用 Cache，每次查詢直接讀取 DB
- 無 Transaction 需求

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 資料庫連線失敗 | 回傳 HTTP 500，並記錄錯誤 |
| 查詢語法異常 | 回傳 HTTP 500，並記錄錯誤 |
| 尚無任何 Webhook 設定 | 回傳 HTTP 200，空陣列 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WH-LIST-01 | API Test | 資料庫有 2 筆 Webhook 記錄 | 回傳 200，陣列長度 2，欄位正確 |
| WH-LIST-02 | API Test | 資料庫無任何記錄 | 回傳 200，空陣列 |
| WH-LIST-03 | Integration Test | 模擬 DB 異常 | 回傳 500 |
| WH-LIST-04 | Flow Test | 連續多次 request | 每次回傳一致（無快取干擾） |

---

## 9. 高風險區域

- **DB 壓力**：若 Webhook 數量極大且無分頁，可能造成查詢緩慢，影響效能。建議監控並規劃分頁。（需人工確認）
- **敏感資訊洩漏**：`url` 欄位可能包含 API Key 或 Token，回傳時未遮蔽恐造成安全風險。（需人工確認）
- **並發讀取**：無鎖定需求，讀取一致性依賴 PostgreSQL 隔離層級，風險低。

---

## 10. 常見錯誤

- 以為命中快取（Redis），實際本場景無快取，導致 stale data 預期錯誤。
- 忘記處理空結果集，前端可能出現 undefined 錯誤。
- 開發環境直接寫死測試資料，遞交時未切換 Provider 查詢。
- AI 可能誤會存在 `status` 或 `is_deleted` 欄位，需明確 `webhooks` 表無軟刪除。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 需人工確認，OpenAPI 未包含；README 提及「管理 Webhook 組態」 |
| DB | `webhooks` 表格（source code semantics, webhooks.py:list_all） |
| Code | Service: WebhookService.list_all（需人工確認） |
| Provider | WebhookProvider.list_all 讀取 `webhooks`（source code semantics） |
| Schema | migrations/002_create_supplement_tables.sql 中 `webhooks` 表定義 |

> **需人工確認**：確切 API 路徑、是否需要遮蔽 URL 中的敏感資訊、是否需要分頁與權限控制。