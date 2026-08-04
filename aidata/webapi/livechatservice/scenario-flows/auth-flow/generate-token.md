# 生成Token

## 1. 場景目的

為第三方服務建立一組具備時效性的存取令牌（Token），存放於後端儲存層，並回傳 Token 字串以供後續驗證與整合使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/token/get?expirationtime={seconds}` | 產生一個 Token 並寫入儲存層 |

- `expirationtime`（query 參數）：單位為秒，最小值 0，最大值 432000（5 天），預設值 60 秒。
- 回傳：HTTP 200 並於 body 回傳 Token 字串（text/plain 或 application/json）。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，提取 `expirationtime` 參數。
2. 若未傳遞，採用預設值 60 秒。
3. 驗證範圍：`0 <= expirationtime <= 432000`。
4. 生成唯一 Token 字串。
5. 計算過期時間點（當前時間 + expirationtime 秒）。
6. 將 Token 與過期時間寫入儲存層。
7. 回傳 Token 字串給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `LiveChatController`（推測） | 接收 `expirationtime` 參數，呼叫 Service |
| 2 | Service | `TokenService`（推測） | 驗證範圍、生成 GUID 或隨機字串作為 Token |
| 3 | Provider | `TokenRepository`（推測） | 將 Token 與過期時間寫入儲存層（MySQL 或 Redis） |
| 4 | Controller | - | 回傳 Token 字串 |

> ⚠️ 需人工確認：具體的 Controller、Service、Provider 類別名稱與方法簽章。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Storage（MySQL 或 Redis） | `token` 表或快取鍵 | Write | 儲存 Token 與其過期時間 |
| Storage（MySQL 或 Redis） | 同上 | Read（驗證時） | Token 檢查用途（由 `/api/v1/token/check` 使用） |

> ⚠️ 需人工確認：OpenAPI 摘要為「生成一個token並加入數據庫」，但未指定儲存媒介為 MySQL 還是 Redis（或兩者皆有）。需補充實際儲存設計文件。

---

## 6. 重要規則

- **參數限制**：`expirationtime` 必須為非負整數，最大值為 432000（5 天）。
- **預設行為**：未提供參數時，採用 60 秒。
- **唯一性**：生成的 Token 須保證唯一（可能使用 GUID v4）。
- **不可回傳欄位**：無，Token 字串本身即為回傳值。
- **寫入失敗**：寫入儲存層失敗時，不應回傳 Token（需人工確認目前實作是否具備此事務保護）。
- **無權限限制**：API 看似公開，但可能需內部網路或特定驗證（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `expirationtime` 超過 432000 | 回傳 HTTP 400 或自訂錯誤碼（OpenAPI 未明確定義） |
| `expirationtime` 為負數 | 同上，拒絕請求 |
| Token 寫入儲存層失敗 | 回傳 HTTP 500，不回傳 Token（需人工確認目前錯誤處理方式） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TOKEN-01 | API Test | 未提供 `expirationtime`，取得預設 60 秒的 Token | 回傳有效 Token，並在 60 秒內可透過 `/check` 驗證成功 |
| TOKEN-02 | API Test | `expirationtime=300` | 回傳 Token，並在 5 分鐘內有效 |
| TOKEN-03 | Validation | `expirationtime=432001`（超出上限） | 回傳 400 或拒絕 |
| TOKEN-04 | Validation | `expirationtime=-1` | 回傳 400 |
| TOKEN-05 | Flow Test | 生成後立刻用 `/check` 驗證 | 應回傳有效（正常狀況回傳 >0 的值） |
| TOKEN-06 | Flow Test | 等待過期後再 `/check` | 應回傳無效 |
| TOKEN-07 | Storage | 寫入儲存層失敗（模擬不可用） | 不回傳 Token，並回報錯誤 |

---

## 9. 高風險區域

- **儲存層一致性**：寫入失敗時若仍回傳 Token，將導致用戶拿到無效憑證，造成第三方服務誤判。
- **無明確 Idempotency 機制**：重複請求會產生不同 Token，若有重試情境，呼叫方需自行處理重複。
- **無驗證權限**：API 若未限制存取來源，可能被惡意大量調用，需依賴基礎設施防護（如內部網路、API Gateway 驗證）。

---

## 10. 常見錯誤

- 誤解 `expirationtime` 單位為毫秒（實際為秒）。
- 忽略 `expirationtime=0` 的合法情境，應可用於產生「立即過期」的 Token 作為測試或特殊用途。
- 漏加儲存層失敗的錯誤處理，導致回傳無效 Token。
- 未確認 Token 存儲介質，直接假設為某種快取而忽略持久性需求。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `/api/v1/token/get` |
| 參數定義 | OpenAPI: `expirationtime` 查詢參數，最小值0，最大值5天，預設60 |
| 功能描述 | README: 「Token 服務：提供建立與驗證 Token」 |
| 關聯驗證 API | OpenAPI `/api/v1/token/check` |
| 儲存層描述 | OpenAPI summary：「生成一個token並加入數據庫」 |

> 需人工確認：
> - 儲存媒介與具體表結構（MySQL 表或 Redis key 格式）。
> - 寫入失敗的回應行為。
> - 是否具備 API 層級認證或限流。
> - Token 生成演算法（GUID、隨機數等）。
> - Token 檢查（`/api/v1/token/check`）的回傳值定義。