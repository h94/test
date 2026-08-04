# 推送操作日誌至 Kafka

## 1. 場景目的

TokenService 在每次成功執行 Token 操作（建立、驗證、停用）後，將操作內容（公司代碼、時間、動作）組裝為日誌訊息，非同步發佈至 Kafka 指定的 topic。此流程對 API 呼叫端完全透明，供下游日誌收集或其他服務消費，達成集中式紀錄與稽核。

---

## 2. 入口 API

此場景無直接對應的API入口，而是嵌入在以下 Token 操作的內部流程中：

| Method | Path | 說明 |
|---|---|---|
| GET | /api/v1/token/get | 建立 Token 時觸發 |
| GET | /api/v1/token/check | 驗證 Token 時觸發 |
| GET | /api/v1/licence | 建立 license token 時觸發 |
| GET | /api/v1/licence/check | 驗證 license token 時觸發 |
| POST | /api/v1/token/auth/{authKey} | 建立 AuthToken 時觸發 |
| POST | /api/v1/token/auth/{authKey}/verify | 驗證 AuthToken 時觸發 |

---

## 3. 流程總覽

1. Token 操作（建立、驗證、停用）成功執行
2. 組裝 Log 物件，填入 `CompanyCode`、`AccessTime`（目前時間）、`Action`（操作描述）
3. 呼叫 LogService 寫入 DB `logs` 表（同步）
4. 呼叫 LogService 發佈訊息至 Kafka（非同步）
5. 對 API 呼叫端回傳 Token 操作結果（無感知日誌推送）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TokenController.CreateToken` / `CheckToken` 等 | 接收請求，呼叫 Service 層 |
| 2 | Service | `TokenService.CreateToken` / `CheckToken` | 執行 Token 業務邏輯 |
| 3 | Service | `LogService.SetLog` | 將操作寫入 DB `logs` 表 |
| 4 | Service | `LogService.PublishLog` | 將操作序列化後發佈至 Kafka |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `logs` (MySQL) | Write (INSERT) | 同步寫入操作日誌記錄 |
| Kafka | `{topic}` | Publish | 非同步推送操作日誌，供下游消費 |

**注意**：此場景不涉及 Redis 操作。

---

## 6. 重要規則

- **寫入順序**：優先寫入 DB `logs` 表，確保同步日誌不遺失；Kafka 發佈失敗不影響 API 回應
- **欄位限制**：
  - `CompanyCode` 由請求上下文（`authKey` 或設定）決定，API 呼叫方不可指定
  - `AccessTime` 為 UTC 時間
  - `Action` 為操作描述，不可包含敏感資料（如 HashKey）
- **不可暴露資料**：Kafka 訊息中的 `Action` 不可包含 Token 的 `HashKey` 值
- **Transaction 規則**：Kafka 發佈不參與 DB transaction，避免跨系統交易
- **Retry 規則**：需人工確認是否有 Kafka publish retry 機制

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| DB `logs` INSERT 失敗 | Token 操作失敗，API 回傳錯誤，不推送 Kafka |
| Kafka broker unavailable | Token 操作成功，DB 記錄成功，Kafka 推送失敗（需人工確認是否 retry） |
| 訊息序列化失敗 | 需人工確認處理方式 |
| `CompanyCode` 為空 | Token 操作不應成功，因此日誌不會寫入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | Integration Test | Token 建立後，檢查 DB `logs` 表是否新增記錄 | `logs` 表應有對應 `Action` 記錄 |
| T2 | Integration Test | Token 建立後，檢查 Kafka 是否收到訊息 | Kafka consumer 應收到對應訊息 |
| T3 | API Test | 呼叫 Token 建立 API，驗證回應不因 Kafka 延遲而阻塞 | API 回應時間應合理 |
| T4 | Error Test | Kafka broker 不可用時，呼叫 Token API | API 回應成功，DB 記錄存在 |
| T5 | Data Test | 驗證 Kafka 訊息格式與內容 | 訊息應包含 `CompanyCode`、`AccessTime`、`Action`，不包含 `HashKey` |

---

## 9. 高風險區域

- **Kafka 推送失敗**：若無 retry 機制，可能造成最終日誌遺失
- **訊息大小**：`Action` 欄位若寫入過多內容，可能影響 Kafka 訊息大小（需人工確認是否有大小限制）
- **跨服務相依**：下游服務若消費失敗，不應影響 TokenService 本身（已解耦）
- **Idempotency**：需人工確認 Kafka 訊息是否有重複消費可能性，以及下游是否有冪等處理

---

## 10. 常見錯誤

- ❌ 將 Token 操作失敗的流程也推送 Kafka → ✅ 僅推送成功操作
- ❌ `Action` 中寫入 `HashKey` 值 → ✅ 只寫入操作名稱，不包含敏感資訊
- ❌ 推送 Kafka 失敗時回滾 DB 寫入 → ✅ DB 為同步寫入，不可因 Kafka 失敗回滾
- ❌ 阻塞 API 回應等待 Kafka 確認 → ✅ Kafka 發佈應為非同步，不影響回應

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `TokenController.CreateToken`、`CheckToken` |
| DB | `logs` table (MySQL) |
| Kafka | 訊息內容由 `LogService.PublishLog` 發佈 |
| Code | `LogService` 負責 DB 寫入與 Kafka 發佈 |
| Schema | `logs` 表結構包含 `CompanyCode`、`AccessTime`、`Action` |