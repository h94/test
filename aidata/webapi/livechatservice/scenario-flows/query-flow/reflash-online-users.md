# 刷新在線用戶

## 1. 場景目的

根據指定的房間（room）和當前連線 ID（connectionId），將使用者的存活時間刷新，並回傳該房間內目前所有在線的使用者列表，用於維護客服聊天室的線上狀態與人數顯示。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/channel/reflash` | 刷新當前使用者在線狀態並回傳房間內所有在線用戶 |

---

## 3. 流程總覽

1. 接收 GET 請求，參數包含 `room` 和 `connectionId`。
2. 使用 `room` 和 `connectionId` 組合為 Redis key，更新該 key 的 TTL（保持使用者在線）。
3. 利用 `room` 取得該房間內所有連線的 Redis key 集合。
4. 遍歷集合中的每個 key，反序列化取得使用者資訊（userid、connectid 等）。
5. 建立並回傳該房間所有在線使用者列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `LiveChatController.Reflash` | 接收 `room`、`connectionId` 參數，呼叫 Service |
| 2 | Service | `LiveChatService.ReflashAsync` | 組合 Redis key，呼叫 Provider 更新 TTL |
| 3 | Provider | `RedisProvider.SetExpireAsync`（推斷） | 對指定 key 設定過期時間（如 60 秒），保持在其內可得在線 |
| 4 | Service | `LiveChatService.ReflashAsync` | 呼叫 Provider 取得房間內所有連線 key |
| 5 | Provider | `RedisProvider.GetSetMembersAsync`（推斷） | 使用 `SMEMBERS` 取得房間集合內所有 key |
| 6 | Service | `LiveChatService.ReflashAsync` | 批量取得每個 key 的值，反序列化為使用者物件 |
| 7 | Service | `LiveChatService.ReflashAsync` | 彙整結果回傳給 Controller |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `online:{room}:{connectionId}` | Write（TTL 刷新） | 設定該使用者的存活時間 |
| Redis | `online:{room}` | Read（SMEMBERS） | 取得房間內所有在線使用者的 key 集合 |
| Redis | 每個 `online:{room}:{connectionId}` | Read（GET） | 取得個別使用者的詳細資訊 |
| DB | 無直接操作 | - | 此場景僅使用 Redis，不涉及 MySQL 或 Cassandra |

---

## 6. 重要規則

- **權限限制**：需人工確認，是否需驗證 Token 或來源 IP，當前 OpenAPI 未標示授權 header。
- **欄位限制**：回傳列表中的使用者資訊應僅包含前端所需欄位（如 `userid`、`connectid`、`room` 等），不應暴露內部機敏資料。
- **不可暴露資料**：不可回傳使用者密碼、內部權限等欄位（若存在）。
- **TTL 規則**：需人工確認 Redis key 的預設 TTL 值，通常設為 60 秒，每次刷新時重設該 TTL。
- **Redis 集合管理**：`online:{room}` 為 Set 資料結構，用於快速取得房間內所有連線。需注意當使用者離線時需透過其他機制移除 key（如 TTL 過期自動刪除與 Set 清理同步）。
- **狀態值限制**：無。
- **不可修改欄位**：此場景僅讀取與設定 TTL，不應修改使用者資料。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `room` 或 `connectionId` 為空 | 回傳參數錯誤或 400 Bad Request |
| Redis 連線失敗或 Timeout | 服務應記錄日志，回傳 500 或適當錯誤碼，不可 crash |
| Redis 中無該房間的 key | 回傳空陣列 `[]`，不拋出異常 |
| key 值反序列化失敗 | 需人工確認處理方式（跳過該筆或記錄錯誤） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| RT-01 | API Test | 正常請求，提供有效 `room`、`connectionId` | 200 OK，回傳在線使用者列表 |
| RT-02 | Flow Test | 刷新後再次查詢，使用者仍在線 | 回傳列表中包含該使用者 |
| RT-03 | Integration Test | 等待 TTL 過期後再查詢 | 使用者從列表中消失 |
| RT-04 | API Test | 缺少 `room` 參數 | 400 Bad Request |
| RT-05 | API Test | 房間內無任何使用者 | 200 OK，回傳空陣列 |

---

## 9. 高風險區域

- **高風險 API**：`/api/v1/channel/reflash` 為頻繁呼叫的 API（每個在線使用者定時刷新），需注意 Redis 連線數與效能，避免 Redis 成為瓶頸。
- **Cache consistency**：Redis `Set` 中的成員與實際 key 存在不一致風險（如 key 過期但未從 Set 移除）。需確認是否有定期清理機制，否則在線列表可能包含已過期但未刪除的 key。
- **Idempotency**：刷新操作本身為冪等，但若前端重複呼叫速度過快，可能導致 Redis 壓力增大。需搭配前端節流或 debounce。

---

## 10. 常見錯誤

- 新人容易犯錯：未理解 Redis Set 與個別 key 的關聯，只刷新自己的 key 而忽略從 Set 讀取列表的正確性。
- AI 容易誤解：把 Redis 操作視為永久存儲，未設 TTL 導致記憶體洩漏。
- 常見漏檢查項目：未檢查 `room` 參數是否為合法值，可能被注入攻擊。
- 常見錯誤流程：因 Redis 集群分片導致 `SMEMBERS` 效能問題，或使用 `KEYS` 命令掃描（應使用 Set）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `LiveChatController.Reflash` |
| Service | `LiveChatService.ReflashAsync` |
| Redis | `online:{room}` (Set)、`online:{room}:{connectionId}` (String with TTL) |
| Code | `LiveChatService.cs`（推斷，需人工確認實際 method 簽名） |
| OpenAPI | `/api/v1/channel/reflash`（GET） |
| README | 線上用戶管理：「記錄每位使用者所屬的房間、連線 ID、服務類型，並提供線上用戶列表刷新」 |

> **需人工確認**：Redis key 的實際命名格式、TTL 數值、Service 內部方法名、權限驗證機制是否已實作。