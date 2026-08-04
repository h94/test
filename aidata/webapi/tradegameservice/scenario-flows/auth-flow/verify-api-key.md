# API Key / 內部服務授權驗證

## 1. 場景目的

對所有進入 `tradegameservice` 的請求執行身份驗證與授權攔截。確保請求攜帶合法 API Key，或來自於 TCZB Globals 信任的內部服務，從而保護交易、盤口查詢及重算 API 不被未授權存取。

---

## 2. 入口 API

本場景為**跨 API 共用之攔截層**，非單一入口，涵蓋所有 `tradegameservice` 對外 API。

| Method | Path | 說明 |
|--------|------|------|
| POST | `/trade/{game_type}` | 新增交易 |
| GET | `/trade/{game_type}` | 查詢球種交易資料 |
| GET | `/trade/{game_type}/{account}` | 查詢使用者球種交易資料 |
| GET | `/trade/daily/{account}/{game_type}/{addtime}` | 查詢使用者單日交易資料 |
| GET | `/tradegames/{game_type}/{lid}` | 取得球種聯盟盤口快照列表 |
| POST | `/tradegames` | 批次查詢多球種盤口快照 |
| POST | `/recalculate/{game_type}` | 重算指定球種交易盈虧 |

> **Evidence**：READM 中「對外 API 重點」之全部路由，皆標記「需要驗證 ✅」。

---

## 3. 流程總覽

1. API Gateway / Middleware 攔截所有進入 `tradegameservice` 的 HTTP 請求。
2. 從 Header 中提取 `X-Api-Key` 或內部服務驗證 Token（需人工確認具體 Header 名稱，例如 `X-Internal-Auth`）。
3. 驗證邏輯分歧：
    - 若存在有效 API Key：比對 Key 合法性（比對來源需人工確認，可能為環境變數或 DB）。
    - 若存在內部服務 Token：驗證 Token 簽名與來源 IP 是否在信任白名單（需人工確認）。
4. 任一身分驗證通過，請求放行至對應 Controller。
5. 驗證失敗：攔截請求，記錄告警，並回傳 `401 Unauthorized` 或 `403 Forbidden`。

> **需人工確認**：缺乏 API Gateway / Middleware 的具體代碼證據，流程基於 README「驗證：API Key / 內部服務授權（TCZB Globals）」描述推斷。

---

## 4. 程式流程

> **需人工確認**：以下流程為基於 Flask 常見實踐推斷，缺乏程式碼直接證據。

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware / Before Request | `auth_middleware.check_api_key`（推斷） | 從 Flask `request.headers` 取得認證資訊 |
| 2 | Provider / Util | `auth_provider.validate_key`（推斷） | 載入合法 Key 列表或調用內部驗證服務 |
| 3 | Middleware | `auth_middleware.check_internal_service`（推斷） | 驗證內部服務 Token 與 IP |
| 4 | Middleware | `abort(401)`（推斷） | 驗證失敗時阻斷請求 |
| 5 | Controller | `trade_games.TradeGamesController` 等（推斷） | 驗證通過，正常進入業務邏輯 |

---

## 5. DB / Cache / Queue 使用

> 雖然 API Key 驗證本身不直接操作 DB，但系統層面存在相依性，以下列出相關資源以供完整理解。

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `pricecenter.accounts_*` | Read | 內部驗證使用者 `enabled` 狀態（間接關聯） |
| Redis | `price:acc:verify:{account}` | Get | 快取已驗證帳戶狀態，避免頻繁查詢 DB |
| Kafka / MQService | 告警隊列 | Publish | 多次驗證失敗時推送安全告警（需人工確認） |

> **Rule**：`price:acc:verify:{account}` 的 TTL 為 3600 秒。  
> **Evidence**：`tradegameservice-detail.md` Redis 表格。

---

## 6. 重要規則

- **API Key 驗證**：
    - 合法 API Key 由系統管理員分配，須具備足夠強度（長度／亂度，需人工確認）。
    - 遺失或過期的 API Key 應立即註銷（需人工確認撤銷流程）。
- **內部服務授權**：
    - 僅接受來自 TCZB Globals 信任清單的內部服務請求（IP / Token）。
    - 內部服務 Token 需定期旋轉（需人工確認輪換週期）。
- **不可明文儲存**：
    - API Key 或 Token 在配置檔或 DB 中應以環境變數或加密方式儲存。
- **攔截行為**：
    - 未授權請求一律不回傳任何業務資料，僅回傳標準 HTTP 錯誤碼。
    - 不可在錯誤訊息中洩漏具體驗證邏輯（例如「API Key 格式錯誤」優於「Key 應為 32 位」）。
- **防暴力破解**：
    - 需對短時間內連續驗證失敗的來源 IP 進行速率限制或短暫封鎖（需人工確認現有機制）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 缺少 API Key 且非內部服務來源 IP | HTTP `401 Unauthorized`，不回傳任何業務資料 |
| API Key 合法 | 請求放行，正常進入 Controller |
| API Key 非法（格式不符或已註銷） | HTTP `403 Forbidden`，記錄告警 |
| API Key 過期（若存在 TTL 機制） | HTTP `403 Forbidden`，訊息「API Key expired」 |
| 內部服務 Token 無效（簽名錯誤或過期） | HTTP `401 Unauthorized` |
| 內部服務 Token 有效但來源 IP 不在白名單 | HTTP `403 Forbidden` |
| Redis 連線失敗（不應直接影響驗證） | 降級為直接查詢 DB 或記錄錯誤後放行（需人工確認降級策略） |
| 驗證服務本身不可用 | HTTP `503 Service Unavailable`（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| AUTH-01 | Integration Test | 請求附帶有效 API Key | 成功進入 Controller，回傳對應業務資料 |
| AUTH-02 | API Test | 請求缺少任何授權標頭 | HTTP `401 Unauthorized` |
| AUTH-03 | Permission Test | 請求附帶無效 API Key | HTTP `403 Forbidden` |
| AUTH-04 | Flow Test | 內部服務請求攜帶合法 Token 與白名單 IP | 請求放行 |
| AUTH-05 | Permission Test | 內部服務 Token 合法但 IP 非法 | HTTP `403 Forbidden` |
| AUTH-06 | Security Test | 暴力猜測 API Key | 達到速率限制後觸發 HTTP `429` 或被暫時封鎖（需人工確認） |
| AUTH-07 | Integration Test | 驗證通過後請求交易 / 盤口 API | API 正常返回資料，個資（password、phone）絕不回傳 |
| AUTH-08 | Flow Test | `enabled=0` 的使用者請求 API | API Key 驗證通過，但業務邏輯拒絕交易並回傳相關錯誤（業務層驗證） |

---

## 9. 高風險區域

- **API Key 管理**：
    - 明文 Key 在不安全管道傳遞或儲存，可能導致洩漏。
    - 缺乏 Key 輪換機制，導致長期有效 Key 增大風險。
- **IP 白名單欺騙**：
    - 若僅依賴 IP 驗證內部服務，攻擊者可能偽造 IP 請求頭（如 `X-Forwarded-For`），需確保在可信代理後取得真實來源 IP。
- **防刷**：
    - 若無速率限制，攻擊者可對驗證端點進行高頻嘗試。
- **錯誤訊息洩漏**：
    - 回傳過於詳細的錯誤訊息（如指出 IP 不在白名單）可能成為攻擊者資訊來源。

---

## 10. 常見錯誤

- **新人**：在 Postman 或測試腳本中忘記附加 `X-Api-Key` Header，導致請求被攔截，卻花時間排查業務邏輯。
- **新人**：誤以為內部服務呼叫不需驗證，未設定適當的 Token 或 IP 白名單。
- **AI**：可能在生成測試或用戶端程式碼時，忽略或寫死無效的 API Key。
- **常見漏查**：未驗證 `X-Forwarded-For` 的可信度，導致 IP 白名單被繞過。
- **錯誤流程**：驗證失敗後未記錄任何 Security Log，導致事件無法溯源。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 所有 README「對外 API 重點」路由皆標記 ✅ |
| DB | `tradegameservice-detail.md` 寫入限制與 Redis 表格 |
| Redis | `tradegameservice-detail.md` 中 `price:acc:verify:{account}` |
| 文件 | README「驗證：API Key / 內部服務授權（TCZB Globals）」 |

---

## 12. 建議新增文件／規則／測試

- **建議新增文件**：
    - 「API Key 生命週期管理流程」：說明 Key 的生成、派發、啟用、停用、輪換。
    - 「內部服務授權標準」：列出所有信任的內部服務及其 Token 格式、IP 白名單。
- **建議新增規則**：
    - PLAN_SPEC 中應明確寫入「所有對外 API 必須在 API Gateway / Middleware 層強制驗證」。
    - 定義 API Key 格式規則（長度、組成）。
- **建議新增測試**：
    - 定期壓測驗證模組的效能開銷。
    - 自動化測試定期輪換的 API Key 是否仍有效。