# 服務學習卡：MemberService

> 產出日期：2026-05-24 | 學習者：（可填）

---

## 1. 這個服務是做什麼的

MemberService 是整個平台的**會員身份中心**，負責處理所有遊戲會員的註冊、登入、個人資料維護與訂閱狀態管理。
簡單說：「你是誰、能不能進來、你目前買了什麼方案」——這些問題的答案都在這裡。
它不處理金錢流動或排名計算，那些交給 WalletService、SubscriptionService 等下游服務去做。

---

## 2. 在系統架構中的位置

（來源：webapi/_index.md、memberservice-detail.md）

- **類型**：WebAPI
- **技術棧**：C#、Cassandra（member keyspace）、Redis
- **誰呼叫它**：前台站台（PriceCenterSite）、管理後台 BFF（PriceBackendService）、TokenService 驗證流程
- **它呼叫誰**：
  - 寫入 Cassandra `member` keyspace（gameusers、gamesublogs 等）
  - 讀寫 Redis（`editor_cache:{authkey}`、`login_track:{loginTrackId}`）
  - **不直接呼叫**：WalletService、SubscriptionService、SupremeService（由這些服務主動寫入 member 表）

---

## 3. 它負責的資料

（來源：db/_index.md、memberservice-detail.md）

| Table / 資料來源 | 關係 | 說明 |
|---|---|---|
| `member.gameusers` | 主要寫入 | 核心會員資料（帳號、密碼 hash、status、rank、memberships 等） |
| `member.gamesublogs` | 主要寫入 | 訂閱紀錄（由訂閱流程觸發，本服務唯讀為主） |
| `member.gameusers_recommend` | 唯讀/共用 | 推薦人關係查詢（複合鍵：authkey + regdate + recommendaccount） |
| `member.gameusers_banned` | 唯讀/共用 | 封禁紀錄查詢 |
| `member.forbidden_email_domains` | 唯讀 | Email 黑名單，註冊時檢查 |
| `member.gamerobots` | 唯讀 | 機器人帳號清單，報表統計時需排除 |
| `member.subplans` | 唯讀 | 訂閱方案定義（金流由 SubscriptionService 管理） |
| Redis `editor_cache:{authkey}` | 讀寫 | 登入者快取（含 BlackAccounts、FocusAccounts、SubLogs） |
| Redis `login_track:{loginTrackId}` | 讀寫 | 登入追蹤，記錄設備指紋與狀態 |

---

## 4. 主要功能一覽

（來源：memberservice-detail.md）

- **會員註冊**：驗證 Email 格式與黑名單、密碼強度，生成唯一 account 與 authkey，寫入 gameusers，初始 status=0（未啟用）
- **會員登入**：驗證帳密 hash、檢查 status=1，寫登入追蹤到 Redis，回傳 Token
- **個人資料管理**：更新暱稱、大頭貼（僅透過上傳 API）、關注／黑名單清單（互斥），敏感欄位（account、authkey、showcode）不可變更
- **訂閱狀態查詢**：讀取 gamesublogs，回傳訂閱有效期，不暴露支付細節
- **合作夥伴帳號升級**：第三方帳號（site 前綴）可補填 email/password，但 site/siteid 不可覆蓋
- **管理 API**：帳號啟用／凍結（需記錄操作日誌），報表查詢需排除機器人與管理員帳號

---

## 5. 典型業務場景

（來源：scenario-flows/）

### 場景 1：使用者註冊

**入口**：`POST /api/v1/game/user/register`

操作步驟：
1. 前台送出 Email + 密碼
2. 後端先查 `forbidden_email_domains` 確認 Email 不在黑名單
3. 驗證密碼強度，用 `Hash.HashPasswordString` 雜湊
4. 生成 `account`（平台前綴 + Email hash）與 `authkey`（由 Hash.HashAuthString 產生）
5. 寫入 `member.gameusers`，status 預設為 `0`（未啟用）

⚠️ 注意：帳號未啟用前**無法登入**，需等待啟用流程（Email 驗證或管理員操作）。

---

### 場景 2：使用者登入

**入口**：`POST /api/v1/game/user/login`

操作步驟：
1. 接收帳號與密碼
2. 查 `member.gameusers`，比對密碼 hash
3. 檢查 `status=1`（已啟用），否則直接拒絕
4. 寫入 Redis `login_track:{loginTrackId}`，記錄設備指紋
5. 回傳登入成功 Token

⚠️ 注意：`password`、`authkey` 任何情況下都不可對外回傳。

---

### 場景 3：查詢訂閱狀態

**入口**：`GET /api/v1/game/subscription/status`

操作步驟：
1. 以 authKey 驗證會員身份（查 gameusers 確認存在）
2. 查 `member.gamesublogs`（複合鍵：authkey + subtime + tradeno + addtime）
3. 計算訂閱有效期，回傳開始與結束時間

⚠️ 注意：僅回傳時間資訊，不可暴露支付方式等敏感資料。

---

## 6. 新人容易誤解的地方

（來源：memberservice-detail.md 常見錯誤）

- ⚠️ **status 必須是 1 才能登入**：凍結（2）與未啟用（0）帳號不得繞過，光密碼正確還不夠
- ⚠️ **authkey 是內部主鍵，不可對外暴露**：對外識別一律用 account 或 token
- ⚠️ **密碼不可明文儲存**：任何寫入都要先過 `Hash.HashPasswordString`
- ⚠️ **memberships 不可手動直接寫**：由訂閱、活動、競賽服務觸發，MemberService 本身不插入
- ⚠️ **合作夥伴升級不能覆蓋 site/siteid**：升級時只補 email/password，保留原有平台關聯
- ⚠️ **統計報表要排除機器人與管理員**：遺漏 `gamerobots` 過濾會讓報表數字偏差
- ⚠️ **email 不是主鍵**：查詢以 authkey 為主，email 只是輔助索引

---

## 7. 想深入了解，可以看

- 詳細業務規則：[memberservice-detail.md](./memberservice-detail.md)
- 完整 API：[memberservice.json](./memberservice.json)（OpenAPI 3.0）
- 業務場景：[scenario-flows/](./scenario-flows/)
  - [使用者註冊](./scenario-flows/auth-flow/user-registration.md)
  - [使用者登入](./scenario-flows/auth-flow/user-login.md)
  - [查詢訂閱狀態](./scenario-flows/query-flow/query-subscription-status.md)
  - [更新個人資料](./scenario-flows/update-flow/update-user-profile.md)
  - [建立訂單](./scenario-flows/create-flow/create-order.md)
  - [建立 GameEditor](./scenario-flows/create-flow/register-game-editor.md)
- DB Schema：[member keyspace](../../db/member-detail.md)
