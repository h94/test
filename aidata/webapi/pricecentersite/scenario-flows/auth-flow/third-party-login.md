# 第三方登入

## 1. 場景目的

提供 Apple、Google、Discord、Line、X、Partner 等第三方帳號登入（或自動註冊）流程，使用`site` + `siteid` 關聯 / 建立 `gameusers` 記錄，Apple 登入需額外查詢 `appleinfos_game` 取得使用者信箱與名稱。

---

## 2. 入口 API

> **需人工確認**：以下路徑為推測，OpenAPI 未暴露第三方登入端點，實際 Controller 位置待確認。

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/thirdparty/login` | 接收第三方 token 與 provider 參數 |

---

## 3. 流程總覽

1. 接收請求（`provider`, `site`, `token`, `siteid` 等）
2. 根據 `provider` 呼叫對應第三方 API 驗證 token 有效性
3. 由第三方回應取得唯一識別碼 `siteid` 與可選的使用者資訊（名稱、信箱）
4. 若為 Apple 登入，額外查詢 `member.appleinfos_game` 取得 `email`、`name`
5. 以 `site` + `siteid` 查詢 `member.gameusers` 是否存在
6. 若存在：檢查狀態與封鎖記錄（`gameusers_banned`）
7. 若不存在：自動註冊新使用者
   - 產生 `authkey`（`tryLogin` 流程，SHA256 雜湊）
   - 產生帳號 `account`
   - 寫入 `gameusers`（含 `site`、`siteid`、`status`、必要欄位）
   - Apple 場合可將 `appleinfos_game` 的 `email` 寫入 `gameusers.email`
8. 更新 `lastactiontime`（直接寫 DB 或透過 Redis TTL）
9. 回傳 `authkey`（做為後續 API 身分驗證使用），禁止暴露密碼或完整信箱

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ThirdPartyController.Login` | 接收 DTO，呼叫 Service |
| 2 | Service | `ThirdPartyService.Login` | 驗證第三方 token，協調 Provider |
| 3 | Provider | `AppleProvider.ValidateToken` | 呼叫 Apple 驗證 API |
| 4 | Provider | `GoogleProvider.ValidateToken` | 呼叫 Google 驗證 API（依 provider 選擇） |
| 5 | Service | `ThirdPartyService.Login` | 必要時呼叫 `MemberService.GetAppleInfo(siteid)` |
| 6 | Provider | `MemberProvider.GetGameUserBySite` | 執行 `SELECT * FROM gameusers WHERE site=? AND siteid=?`（Cassandra） |
| 7 | Service | `MemberService.RegisterGameUser` | 若不存在，產生 `authkey`、`account`，寫入 `gameusers` |
| 8 | Service | `ThirdPartyService.Login` | 更新最後活動時間（`GameUserLastActionTime` Redis key） |
| 9 | Controller | — | 回傳 `authkey` 及必要資訊 |

> **需人工確認**：實際類別名稱與依賴注入細節。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read | 查詢 site+siteid 是否存在 |
| DB | `member.gameusers` | Write (INSERT) | 自動註冊新帳號 |
| DB | `member.gameusers` | Write (UPDATE email) | Apple 登入時寫入信箱 |
| DB | `member.gameusers_banned` | Read | 檢查是否封鎖中（`endtime` 仍有效） |
| DB | `member.appleinfos_game` | Read | Apple 登入時取得對應 `email`、`name` |
| Cache | `Redis: GameUserLastActionTime:{authKey}` | Write (SET) | 更新最後活動時間（TTL 300秒，非立即寫入 DB） |
| Queue | 無 | — | 無推估相關訊息 |

> **需人工確認**：是否實際使用 Redis 延遲寫入，或直接更新 `gameusers.lastactiontime`。

---

## 6. 重要規則

- **帳號可重複登入**：同一 `site` + `siteid` 組合可在不同時間登入，但註冊後 `site` / `siteid` 不可變更
- **authkey 產生**：使用 `tryLogin` 方法，透過 SHA256 雜湊特定欄位組成，不可由客戶端指定，不可預測
- **status 初值**：第三方登入自動註冊時，`status` 應設為 `1`（已啟用）；除非特定站台政策要求 `0` 再驗證（本流程推定直接啟用）
- **Apple email 更新**：`pricecentersite` 允許在 Apple 第三方登入時更新 `email` 欄位
- **email 不可重複**：註冊 / 寫入 email 前不需檢查唯一性（目前無唯一約束），但應記錄；若業務規則要求，需人工訂定
- **appleinfos_game 為輔助資訊**：僅用於取得 Apple 帳戶對應的信箱與名稱，不影響主要登入流程
- **封禁檢查**：必須查詢 `gameusers_banned WHERE authkey=?`，若存在且 `endtime` 為空或大於現在時間，拒絕登入
- **authkey 不可對外回傳**（除登入回應）：首次登入成功回傳一次，後續查詢用戶資訊不可暴露

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 第三方 token 驗證失敗 | 回傳 401，登入拒絕 |
| `site` + `siteid` 不存在 | 觸發自動註冊 |
| 帳號已存在但 `status != 1` | 拒絕登入，回傳「帳號已停用」 |
| 帳號已存在且被封鎖（`gameusers_banned` 有效） | 拒絕登入，回傳「帳號已停用」 |
| 自動註冊時 `account` 產生碰撞（極低機率） | 需重試或記錄錯誤；目前帳號產生規則需確認 |
| Redis 寫入失敗（最後活動時間） | 不應影響登入主流程，僅記錄警告 |
| Apple `appleinfos_game` 查無資料 | 不中斷登入，但 `email` 可能不寫入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TP-01 | Flow Test | Google 新用戶首次登入 | 回傳 authkey，DB 新增一筆 gameusers（status=1） |
| TP-02 | Flow Test | 已存在用戶再次登入（同 site+siteid） | 回傳相同 authkey，不再新建記錄 |
| TP-03 | Permission Test | 被封鎖用戶登入 | 回傳錯誤，不允許登入 |
| TP-04 | API Test | Apple 登入且 `appleinfos_game` 中有 email | `gameusers.email` 更新成功 |
| TP-05 | Integration Test | 第三方 token 無效 | 回傳 401 |
| TP-06 | Flow Test | 自動註冊後立即登入 | 正常可操作後續 API |
| TP-07 | Audit Test | 登入後 `lastactiontime` 是否更新 | 在觀察期內會更新（或 Redis 有記錄） |

---

## 9. 高風險區域

- **高風險 table**：`member.gameusers`（帳號大量建立）、`member.gameusers_banned`（封鎖檢查疏漏）
- **高風險 API**：第三方 token 回調驗證，可能被偽造（需確保使用官方 SDK 或標準 OAuth 驗證）
- **跨服務資料同步**：`appleinfos_game` 與 `gameusers` 的 email 更新，若不同步可能導致帳號資訊不一致
- **Transaction**：無關聯式 Transaction，Cassandra 寫入與查詢無法保證強一致性；自動註冊前後可能有多餘記錄（需靠程式邏輯防範）
- **Cache consistency**：`GameUserLastActionTime` 快取失效或未更新，不影響核心功能，但活動紀錄可能不即時
- **Idempotency**：重複登入請求不應建立重複帳號；透過 `site+siteid` 唯一性保證

---

## 10. 常見錯誤

- ❌ 未檢查 `status` 就接受登入 → 已停用帳號仍可操作
- ❌ 未檢查 `gameusers_banned` → 被封禁帳號仍登入成功
- ❌ 自動註冊時直接拿第三方 token 作為 `authkey` → 安全漏洞，必須經過系統產生
- ❌ Apple 登入時未發現 `appleinfos_game` 缺失，仍宣告成功但漏了 email → 使用者資料不完整
- ❌ 回傳使用者資料時洩漏 `authkey`（非登入回應） → 資安問題
- ❌ 忽略 `lastactiontime` 更新，導致使用者活躍度統計錯誤
- ❌ 註冊時將 `site` 或 `siteid` 留空，造成後續無法關聯

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB 寫入規則 | `pricecentersite-detail.md` – `member` 寫入限制：`gameusers.site/siteid` 第三方登入寫入 |
| DB 表結構 | `member.md` – `gameusers` 欄位定義 |
| Apple 額外查詢 | `member-detail.md` – 第三方帳號關聯：WHERE site=? AND siteid=? … Apple 額外查詢 appleinfos_game |
| Apple info 表 | `member.md` – `appleinfos_game` (id, email, name) |
| authkey 產生 | `pricecentersite-detail.md` – 第三方登入透過 tryLogin 產生 |
| email 寫入權限 | `pricecentersite-detail.md` – pricecentersite 可 UPDATE email（Apple 登入） |
| Redis 使用 | `pricecentersite README` – `GameUserLastActionTime:{authKey}` TTL 300 秒 |
| OpenAPI 缺失 | 無對應入口路徑（需人工確認 Controller） |