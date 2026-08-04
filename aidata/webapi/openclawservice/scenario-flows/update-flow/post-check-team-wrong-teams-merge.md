# 寫入異常合併隊伍

## 1. 場景目的
將前端辨識出「被錯誤合併」的隊伍資料寫入 Redis 暫存，供後續對帳、人工覆核或重新比對使用。寫入時會附帶過期時間（TTL），避免永久佔用記憶體。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/check-team/wrong-teams-merge/{game_type}` | 接收指定球種的異常合併隊伍資料，寫入 Redis |

- **game_type**：球種代碼，如 `SC`, `BK`, `BS`, `FL`, `HL`, `ES`, `TN` 等。
- **Request Body**：需人工確認（推測為 JSON，包含合併錯誤的隊伍映射或標記資料）。

---

## 3. 流程總覽

1. 接收 POST 請求，根據 `game_type` 路由至對應處理單元。
2. 驗證 `game_type` 是否為系統支援的球種（依賴 Enum 或對照表）。  
   ⚠️ **需人工確認**：驗證方式與不合法時的錯誤處理。
3. 解析請求本體，提取異常合併隊伍資訊。  
   ⚠️ **需人工確認**：是否包含多筆隊伍、站台來源等結構。
4. 將資料結構化（key 可能包含 `game_type` 與特定識別碼），設定 TTL（例如 86400 秒或由配置決定），寫入 Redis（db=3）。
5. 回傳成功狀態（200 / 201）或錯誤訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Router | `app/api/check-team` | 路由 `POST /check-team/wrong-teams-merge/{game_type}` |
| 2 | Controller | **需人工確認** | 接收請求，呼叫 Service |
| 3 | Service | **需人工確認** (可能為 `CheckTeamService.store_wrong_teams`) | 1. 驗證 game_type 合法性<br>2. 轉換資料結構<br>3. 呼叫 Redis Provider 寫入 |
| 4 | Provider | `project/Provider/redis_provider.py`（推測） | 與 Redis 互動（SET with TTL） |

⚠️ 上述 Class 與 Method 名稱均為推測，需人工確認實際實作。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `wrong_teams:{game_type}:*` 或類似 key | **Write** (SET) | 儲存異常合併的隊伍清單（含 TTL） |

- **Redis 連線**：`192.168.55.80:6379`，db=3。
- **TTL**：需人工確認（可能來自環境變數或常數設定，建議為 7 天或依業務決定）。
- **無 Cassandra / Kafka 寫入**：此流程不操作 Cassandra 與 Kafka。

---

## 6. 重要規則

- **權限限制**：此 API 應為後台管理功能，需驗證操作者權限（如 token 或 IP 白名單）。⚠️ **需人工確認** 是否有實作。
- **不可暴露資料**：寫入 Redis 的內容不應包含明文密碼或個人隱私；若包含隊伍資料，無敏感問題。
- **TTL 規則**：必須設定 TTL，不可永久留存，避免記憶體洩漏。
- **Idempotency**：若重複寫入同一 key，應以最新資料覆蓋（SET 直接覆蓋），無額外防護。
- **game_type 驗證**：只接受指定的球種列表，非法值應拒絕並回傳 400。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不合法（如 `XX`） | 回傳 400 Bad Request，包含錯誤訊息 |
| Request body 格式錯誤或缺少必要欄位 | 回傳 422 Unprocessable Entity |
| Redis 連線失敗或寫入 timeout | 回傳 503 Service Unavailable，記錄錯誤日誌（透過 Kafka） |
| Redis 寫入成功但後續流程中斷 | 無特殊回滾（已寫入 Redis） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WT-01 | API Test | 提供合法球種與正確 JSON | 200/201，Redis 中可讀取到對應資料且含 TTL |
| WT-02 | Permission Test | 無權限呼叫 | 需人工確認是否攔截（若無實作則跳過） |
| WT-03 | Flow Test | 提供非法 game_type | 400，寫入未發生 |
| WT-04 | Flow Test | Redis 不可用（模擬連線失敗） | 503，錯誤日誌產出 |
| WT-05 | Integration Test | 寫入後查詢 Redis 並驗證 TTL | TTL 設定正確，逾時後 key 自動消失 |

---

## 9. 高風險區域

- **Redis 單點故障**：服務依賴單一 Redis 節點，若 Redis 故障，此 API 直接不可用。
- **無 Transaction**：僅 Redis 寫入，無分佈式事務問題，成功即寫入，失敗則回傳錯誤。
- **Cache consistency**：寫入後無後續清理機制，僅靠 TTL 淘汰，不存在一致性問題。
- **資料格式**：若寫入的資料結構變更，需考慮舊 key 的相容性或直接讓其過期。
- **記憶體壓力**：若無 TTL 或 TTL 過長，大量異常隊伍可能佔滿 Redis 記憶體。目前有 TTL 可緩解，但仍需監控。

---

## 10. 常見錯誤

- 誤用 Cassandra 寫入異常隊伍，實則應寫入 Redis。  
- 未設定 TTL 導致 Redis 資料永久留存。  
- 忽略 `game_type` 驗證，任意字串傳入可能導致 Redis key 混亂。  
- 將敏感資訊（如帳號密碼）寫入異常隊伍資料，雖然此場景僅存隊伍，但仍應避免。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | `project/main.py` 或路由模組中定義 `/api/check-team/wrong-teams-merge/{game_type}` |
| Redis 使用 | README.md：「Redis（db=3）用於異常隊伍快取」 |
| 錯誤日誌 | README.md：「日誌使用 TCZB 套件經 Kafka 傳送」 |
| 技術棧 | README.md：「Redis: 192.168.55.80:6379, db=3」 |

---

⚠️ **需人工確認**：  
- 實際 Controller / Service / Provider 名稱與路徑  
- Request body schema  
- TTL 具體數值與設定方式  
- 權限驗證機制是否存在  
- 異常隊伍寫入的 Redis key 規則  
- 是否有對應的查詢 API 以讀取這些異常資料