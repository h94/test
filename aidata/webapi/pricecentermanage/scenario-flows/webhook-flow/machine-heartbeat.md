# 機器心跳回報

## 1. 場景目的
爬蟲機器定時回報自身健康狀態，更新對應帳號在 `pricecenter.accounts_*` 表中的 `handler` 欄位，以便監控後台即時追蹤各機器的最後心跳時間。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/system/machines/crawler` | 爬蟲心跳回報，需要驗證 |

---

## 3. 流程總覽

1. 爬蟲機器定期發送心跳 request，包含機器名稱與程式資訊
2. 驗證 request 的簽章（Token / AuthKey）
3. 依請求內容判斷目標品牌（brand）與帳號（account）
4. 讀取 `pricecenter.accounts_{brand}` 表中對應帳號的現有 `handler` map
5. 將此次回報的機器名稱及當前時間戳（UTC）加入 `handler` map
6. 更新 `pricecenter.accounts_{brand}` 的 `handler` 欄位（map 局部更新）
7. 回傳成功狀態

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SysManagerController.CrawlerHeartbeat` | 接收 HTTP POST 請求，轉交 Service |
| 2 | Validator | `ECFramework.ECService` | 驗證 JWT / API Key 合法性 |
| 3 | Service | `CrawlerHeartbeatService` | 解析請求，決定目標 keyspace/table 與 account |
| 4 | Provider | `ISysManagerProvider` | 讀取 Cassandra `accounts_{brand}` 取得現有 `handler` |
| 5 | Service | `CrawlerHeartbeatService` | 合併新的心跳資訊到 `handler` map |
| 6 | Provider | `ISysManagerProvider` | 寫入 Cassandra 更新 `handler` 欄位 |
| 7 | Controller | `SysManagerController` | 回傳 2xx 成功 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `pricecenter.accounts_{brand}` | Read | 讀取現有 `handler` map |
| DB | Cassandra `pricecenter.accounts_{brand}` | Write | 局部更新 `handler` map，寫入最新心跳時間 |
| Redis | 無 | - | 本場景未使用 Redis |
| Kafka | 無 | - | 本場景未使用 Queue/Kafka |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，使用內部機器的 API Token（非一般用戶 Token）
- **handler map 必須局部更新**：不可直接 `SET handler = ...` 覆蓋整個 map，應先讀取現有值，僅新增或更新指定 Key
  - 來自：`pricecenter-detail.md` - 「寫入時須確保不覆蓋其他機器的 handler 資訊」
- **account 主鍵不可變更**：僅查詢已存在的帳號，不可新建
  - 來自：`pricecenter-detail.md` - 「主鍵，一旦由 INSERT 建立後，不可更新，不可刪除」
- **不可回傳欄位**：任何 API 不可回傳 `accounts_{brand}.password`、`accounts_{brand}.phone`
- **CC（Cassandra Consistency）規則**：使用 `QUORUM` 進行讀寫以確保強一致性
- **時間格式**：`handler` value 中的時間戳應為 UTC 格式字串（如 `2025-01-22T10:30:00Z`）
- **帳號有效性檢查**：寫入前需確認帳號 `enabled = 1` 且 `closetime` 為空
  - 來自：`pricecenter-detail.md` - 「enabled=1 是所有服務進行登入、交易、爬蟲等操作的唯一前提」

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 找不到對應 account | 回傳 404 Not Found 或特定的業務錯誤碼 |
| account 已關閉（enabled=0 或 closetime 非空） | 拒絕寫入，回傳 400/403 錯誤 |
| 必要欄位缺失（如 machine name 為空） | 回傳 400 Bad Request |
| Cassandra 連線失敗 / timeout | 重試 1 次，仍失敗則回傳 503 Service Unavailable |
| handler map 已滿（極端情況） | 需人工確認：目前無明確 map 大小限制規範 |
| 驗證 Token 無效 | 回傳 401 Unauthorized |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|--------|------|------|---------|
| HB-01 | API Test | 正常心跳回報，帶入合法 machine name 與 account | 成功更新 handler map，返回 200 |
| HB-02 | API Test | 不存在的 account | 返回 4xx 錯誤 |
| HB-03 | API Test | 缺少必要參數（如未帶 machine name） | 返回 400 |
| HB-04 | Flow Test | 同一帳號連續兩台不同機器回報心跳 | handler map 中保留兩筆 Key，不被覆蓋 |
| HB-05 | Flow Test | 帳號已停用或關閉 | 返回 4xx，handler 未被修改 |
| HB-06 | Integration Test | Cassandra 暫時無法連線 | Service 正確重試並回傳 503 |

---

## 9. 高風險區域

- **高風險 table**：`pricecenter.accounts_{brand}`（直接更新 `handler` map 涉及併發安全性）
- **handler map 更新**：若未做 partial update，可能覆蓋其他機器的心跳記錄，導致監控數據遺失
- **Cache consistency**：本場景未使用 Redis，無 cache 一致性問題
- **權限控制**：需確保此 API 僅能被內部爬蟲機器群調用，防止外部惡意寫入

---

## 10. 常見錯誤

- ❌ **直接 `UPDATE ... SET handler = ?` 整個 map** → ✅ 需讀取現有 map，只針對此次回報的機器 Key 做更新
- ❌ **未檢查 `enabled` 與 `closetime` 就直接寫入** → ✅ 需先確認帳號為有效狀態
- ❌ **誤用一般用戶 Token 呼叫此 API** → ✅ 需使用內部機器的 Service Token
- ❌ **handler value 使用 non-UTC 時間或格式不一致** → ✅ 統一使用 ISO 8601 UTC 格式

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md - 系統監控與 Bet365 爬蟲管理 > POST `/api/v1/system/machines/crawler` |
| DB | `pricecenter-detail.md` - Table：accounts_{brand} > handler 欄位 |
| 寫入規則 | `pricecentermanage-detail.md` - pricecenter > 寫入限制 > 「handler 寫入時須確保不覆蓋其他機器的 handler 資訊」 |
| 服務角色 | `pricecentermanage-detail.md` - pricecenter > 資料來源與角色 > pricecentermanage 為 reader（註：此場景為爬蟲心跳更新，pricecentermanage 實際上扮演 writer 角色更新 handler） |
| 程式碼 | Phase0/1 code semantics - `PriceCenterManage.Model.Accounts.handler` |