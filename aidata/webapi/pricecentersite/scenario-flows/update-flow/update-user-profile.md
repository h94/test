# 更新會員資料

## 1. 場景目的
允許已驗證的使用者更新自己的基本資料（如顯示名稱、頭像路徑），禁止修改系統核心欄位（密碼、授權金鑰、信箱、狀態、會員資格）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/member/profile/{authKey}` | 更新會員資料（推測） |

> ⚠️ 需人工確認：實際 API 路徑未在提供的 OpenAPI 片段中明確出現，本文件基於常見 RESTful 慣例推導。

---

## 3. 流程總覽

1. 接收 PUT 請求，路徑中包含 `authKey` 與 JSON body（含欲更新的欄位）。
2. 驗證 `authKey` 格式與存在性。
3. 查詢 `member.gameusers` 取得使用者完整紀錄。
4. 驗證帳號狀態（`status=1`）且未被封禁（查詢 `gameusers_banned`）。
5. 過濾請求 body，僅保留白名單欄位（如 `username`、`headshotpath`）；拒絕 `authkey`、`password`、`email`、`status`、`memberships` 等欄位。
6. 對允許欄位進行內容驗證（如長度、格式、不可為空）。
7. 執行 Cassandra UPDATE 寫入 `member.gameusers` 表。
8. 主動刪除 Redis 快取 `GameUser:{authKey}`，確保下次讀取為最新資料。
9. 回傳更新後的會員資料（排除 `password`、`authkey` 等敏感欄位）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `MemberController.UpdateProfile` | 接收請求，提取 `authKey` 與 body |
| 2 | Service | `MemberService.UpdateProfile` | 呼叫驗證邏輯與更新寫入 |
| 3 | Provider | `MemberProvider.GetUserByAuthKey` | 查詢 `gameusers` 表 (SELECT WHERE authkey=?) |
| 4 | Service | `MemberService.UpdateProfile` | 檢查 `status==1` 與封禁狀態；過濾 request 欄位 |
| 5 | Provider | `MemberProvider.UpdateUserFields` | 執行 Cassandra UPDATE（SET username=?, headshotpath=? 等） |
| 6 | Service | `CacheService.RemoveUserCache` | DEL Redis key `GameUser:{authKey}` |
| 7 | Controller | `MemberController.UpdateProfile` | 將更新後的 DTO 回傳給客戶端 |

> ⚠️ 需人工確認：實際的類別名稱與方法簽名需依程式碼調整，此處為基於架構慣例的推導。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read + Update | 讀取完整紀錄並寫入允許變更的欄位 |
| DB | `member.gameusers_banned` | Read | 確認使用者是否仍在封禁中 |
| Cache | Redis `GameUser:{authKey}` | Delete | 清除舊快取，確保下一次查詢取得最新資料 |

---

## 6. 重要規則

- **權限限制**：僅能更新使用者自己的資料（由 `authKey` 身份決定）；不可跨帳號操作。
- **欄位限制**（白名單）：僅允許更新 `username`、`headshotpath` 等非敏感欄位；禁止修改 `authkey`、`password`、`email`、`status`、`memberships`。
- **不可暴露資料**：回應中絕對不可包含 `password`、`authkey` 欄位。
- **TTL 規則**：無直接對此次寫入設定 TTL，但 Redis 快取 `GameUser:{authKey}` 在資料變更後須立刻刪除（不等它自然過期）。
- **Transaction 規則**：Cassandra 不支援多表交易，因此更新 gameusers 與刪除快取分兩步執行；若 Redis DEL 失敗不應回滾 DB，但需記錄錯誤並允許重試。
- **Retry 規則**：一般 DB 寫入失敗應回傳 5xx 讓客戶端重試；Redis DEL 失敗可非同步重試或標記為警告。
- **狀態值限制**：僅有 `gameusers.status=1` 且 `closetime` 為空/未過期的帳號可執行更新；`memberships`、`status` 等欄位不可經由此 API 變更。
- **不可修改欄位**：`site`、`siteid`（註冊後不可變更）、`focus_account`/`follow_account`/`black_account`（僅能透過專屬 API 操作，禁止整組覆寫）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| `authKey` 不存在 | 回傳 401 Unauthorized |
| `gameusers.status != 1`（停用/凍結） | 回傳 403 Forbidden（帳號已停用） |
| 查詢 `gameusers_banned` 存在有效封禁 | 回傳 403 Forbidden（帳號已停用） |
| Request body 包含禁止修改的欄位（如 `password`） | 回傳 400 Bad Request，提示禁止修改的欄位 |
| `username` 為空字串或超過長度限制 | 回傳 400 Bad Request，附帶校驗訊息 |
| Cassandra 寫入失敗（timeout 等） | 回傳 500 Internal Server Error |
| Redis 刪除快取失敗 | 仍回傳 200 OK，但記錄錯誤 log，後續請求可能讀到舊資料直到 TTL 過期 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| UP-01 | API Test | 正常更新 `username` 與 `headshotpath` | 200，回應不含敏感欄位，DB 已更新 |
| UP-02 | API Test | 嘗試更新 `password` | 400，錯誤訊息指出欄位不允許 |
| UP-03 | Permission Test | 使用無效的 `authKey` | 401 |
| UP-04 | Flow Test | 停用帳號嘗試更新 | 403 |
| UP-05 | Flow Test | 更新後立刻以相同 `authKey` 查詢使用者資料 | 取得最新資料（快取已清除） |
| UP-06 | API Test | 傳送空白 `username` | 400 |

---

## 9. 高風險區域

- **高風險 table**：`member.gameusers` — 誤改 `password`、`authkey`、`email` 將導致帳號安全問題或關聯錯誤。
- **高風險 API**：若白名單過濾邏輯疏漏，可能允許用戶越權修改訂閱狀態（`memberships`）或狀態（`status`）。
- **Cache consistency**：更新 DB 後若未正確刪除 Redis 快取，前端顯示資料為舊值，影響使用者體驗與資料正確性。
- **Idempotency**：本操作為冪等更新，重複送出相同請求不會造成錯誤，但需注意併發寫入可能造成欄位氧化（如 username 重複修改），因無樂觀鎖可考慮加入 `IF EXISTS` 條件。

---

## 10. 常見錯誤

- ❌ 忘記過濾請求 body，直接將整個 JSON 塞入 UPDATE，導致 `password`、`email` 被覆寫。
- ❌ 更新後未清除 Redis 快取 `GameUser:{authKey}`，導致其他服務持續使用舊使用者資料。
- ❌ 回傳時包含了 `authkey` 或 `password` 欄位。
- ❌ 沒有檢查 `gameusers_banned`，讓被封禁使用者仍能修改資料。
- ❌ 對 `username` 沒做內容驗證，存入空白或超長字串。
- ❌ 使用覆寫整個 list 的方式更新 `focus_account` 等欄位，應透過專屬 API 操作，因此此端點不應提供這些欄位的寫入。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 入口推測 | 基於 REST 設計通用模式（無直接證據） |
| DB 寫入限制 | `member-detail.md` — gameusers.password 僅註冊等 API 可寫入；memberships 僅訂閱成功後同步 |
| 白名單欄位 | `member-detail.md` — username, headshotpath 為可寫入欄位 |
| 不可修改欄位 | `pricecentersite-detail.md` — 不可回傳 authkey, password；不可直接修改 memberships |
| Redis 快取清除 | `member-detail.md` — GameUser:{authkey} 在資料變更後必須 DEL |
| 封禁檢查 | `member-detail.md` — 登入驗證須查 gameusers_banned |
| 狀態檢查 | `member-detail.md` — gameusers.status=1 才可使用 |