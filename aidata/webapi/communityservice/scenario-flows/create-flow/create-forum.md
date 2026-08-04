# 建立新彩票論壇看板

## 1. 場景目的

提供管理員後台建立新彩票討論看板（Forum）的完整流程。管理員指定看板名稱、國家代碼、圖示後，系統將資料寫入Cassandra `community.newlottery_forums` 表，預設狀態為隱藏（status=0），由後台確認後另行啟用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/newlottery/forums` | 建立新彩票論壇看板 |

- **認證**：需要驗證（auth/user service 驗證 authkey）
- **權限**：僅管理員可呼叫（需人工確認管理員權限檢查點）

---

## 3. 流程總覽

1. 接收建立論壇 request（authkey 已由上層驗證）
2. 參數驗證（`names` 非空、至少一個語系、格式正確）
3. 查詢 `community.newlottery_forums` 現有看板，確認 `names['zh-TW']` 唯一性
4. 若重複，拒絕請求（409 Conflict 或自訂錯誤）
5. 生成論壇 ID（UUID 或自訂格式）
6. 組合寫入資料：`id`、`country_code`、`icon`、`names`、`status=0`、`edit_timestamp`
7. 寫入 Cassandra `community.newlottery_forums`
8. 回傳成功 response（含新建論壇資料）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewLotteryController.create_forum` | 接收 POST body，轉交 Service |
| 2 | Service | `NewLotteryService.create_forum` | 驗證參數、檢查唯一性、呼叫 Provider 寫入 |
| 3 | Provider | `NewLotteryForumProvider` | 封裝 Cassandra 操作（SELECT 唯一性檢查、INSERT） |
| 4 | Validator | `ForumSchema` | 驗證 `names` 格式（map<text, text>）、`country_code` 可選、`icon` 可選 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `community.newlottery_forums` | SELECT | 檢查 `names['zh-TW']` 唯一性 |
| DB | `community.newlottery_forums` | INSERT | 寫入新論壇看板 |

- **本場景無使用 Redis / Kafka / Queue**
- **MeiliSearch 不涉及**：論壇看板為靜態資料，不建立搜尋索引

---

## 6. 重要規則

- **權限限制**：僅管理員可建立看板（需人工確認後台 auth 檢查邏輯）
- **欄位限制**：
  - `id`：由系統生成，不可由 client 指定
  - `names`：至少需提供一個語系名稱（如 `zh-TW`），不可為空 map
  - `names['zh-TW']`：必須唯一，不可與現有啟用或隱藏看板重複
  - `status`：強制設為 0（隱藏），client 不可指定
  - `edit_timestamp`：由系統寫入當前 UTC timestamp（毫秒級）
- **不可暴露資料**：無特別遮蔽需求（論壇名稱、圖示為公開資訊）
- **TTL 規則**：無（Cassandra 無 TTL 設定）
- **Transaction 規則**：Cassandra 無跨 partition 交易，寫入為單一 INSERT
- **Retry 規則**：若 Cassandra 寫入失敗，回傳 500；client 可重試，但需確保 idempotency（相同 `names['zh-TW']` 第二次會失敗）
- **狀態值限制**：`status` 僅允許 0 或 1（此場景固定為 0）
- **不可修改欄位**：`id` 寫入後不可變更

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `names` 為空 map | 422 Unprocessable Entity |
| `names['zh-TW']` 與現有看板重複 | 409 Conflict 或自訂錯誤（如 `FORUM_NAME_DUPLICATE`） |
| 未登入或 authkey 無效 | 401 Unauthorized（由 auth service 攔截） |
| 非管理員角色 | 403 Forbidden（需人工確認檢查點） |
| Cassandra INSERT 失敗（timeout/unavailable） | 500 Internal Server Error；client 可重試 |
| Cassandra SELECT 失敗（timeout） | 500 Internal Server Error（無法確認唯一性） |
| 請求 body 格式錯誤（非 JSON） | 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常建立論壇，提供 `names.zh-TW` 和 `icon` | 201 Created，回傳論壇資料，`status=0` |
| TC02 | API Test | 建立論壇時僅提供 `names.zh-TW` | 201 Created（最小必要欄位） |
| TC03 | Permission Test | 一般使用者呼叫 API | 403 Forbidden（若實作權限檢查） |
| TC04 | Validation Test | `names` 為空 map | 422 錯誤 |
| TC05 | Flow Test | 建立兩個相同 `names.zh-TW` 的論壇 | 第二個請求回傳 409 或錯誤訊息 |
| TC06 | Integration Test | Cassandra 不可用 | 500 錯誤；確認不寫入髒資料 |

---

## 9. 高風險區域

- **高風險 table**：`community.newlottery_forums`（寫入失敗或重複名稱導致前台顯示異常）
- **高風險 API**：`POST /api/newlottery/forums`（無 idempotency key，重複請求可能建立多個看板，但因唯一性檢查僅第一個成功）
- **跨服務資料同步**：無（論壇看板僅 communityservice 寫入）
- **Transaction**：無跨 partition 交易；唯一性檢查依賴應用層 SELECT + INSERT 順序（Cassandra 無原生唯一約束）
- **Cache consistency**：無快取（後續若實作快取，需在建立時失效 `forums:list` 快取）
- **Queue retry**：無佇列
- **Idempotency**：天然保證 idempotent（`names['zh-TW']` 唯一性檢查確保相同名稱不會重複建立）

---

## 10. 常見錯誤

- ❌ **未檢查 `names['zh-TW']` 唯一性** → 造成兩個看板使用相同中文名稱，前台顯示混亂（db-usage 明確禁止）
- ❌ **允許 client 指定 `status`** → 可能建立時直接設為 `status=1`（啟用），繞過後台審核流程（db-usage 限制：status 僅 0 或 1，且需管理員權限）
- ❌ **未提供 `names` 任一語系名稱** → 資料庫寫入空 map，前台無法顯示任何名稱（db-usage 限制：至少需提供一個語系名稱）
- ❌ **直接覆蓋 `names` map 寫入** → 若後續更新時使用此模式，可能遺失其他語系名稱（應使用 `SET names['zh-TW'] = ?`）
- ❌ **忽略 Cassandra write timeout 後續重試機制** → client 可能無限重試，應搭配 backoff
- ❌ **誤用 Redis 快取** → communityservice 目前無 Redis，若未來實作需注意主動失效

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | NewLotteryController.create_forum（POST `/api/newlottery/forums`） |
| DB | `community.newlottery_forums`（Cassandra） |
| DB Schema | `CREATE TABLE community.newlottery_forums (...)` |
| 寫入限制 | `community-detail.md`：`names` 唯一性檢查、`status` 限制、`names` 至少一個語系 |
| 服務角色 | `community-detail.md`：communityservice 為 owner，可讀寫刪 |
| 權限驗證 | `communityservice-detail.md`：auth/user service 驗證 authkey，communityservice 不處理登入 |
| 常見錯誤 | `communityservice-detail.md`：建立新論壇時未檢查唯一性、直接暴露 account |