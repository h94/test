# bussinessmember DB — 完整使用脈絡

> 產出時間：2025-04-14 10:00
> 欄位結構定義：[bussinessmember.json](./bussinessmember.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| adminservice | owner ⚠️ 衝突待人工 | 讀、寫、刪 admins；寫入 admin_login_logs、admin_operation_logs |
| pricecentermanage | owner ⚠️ 衝突待人工（可能與 adminservice 為同一服務） | 讀、寫、刪 admins；寫入 admin_login_logs、admin_operation_logs |
| pricebackendservice | writer | 讀、寫 admins（部分欄位，經由登入/管理流程）；寫入 admin_login_logs（登入記錄） |
| gamesettingsite | writer | 讀、寫 admins（部分欄位，管理員管理）；寫入 admin_login_logs、admin_operation_logs（管理操作記錄） |
| backendservice | reader | 唯讀 admins（身份驗證、權限查詢）；唯讀 admin_login_logs、admin_operation_logs（稽核） |

> ⚠️ adminservice 與 pricecentermanage 皆聲稱為 owner，可能為同一服務的兩個名稱，或存在職責重疊，請人工確認。

---

## Table：admins

### account 欄位

**型別**：text（主鍵）

**值定義與狀態流轉**：

```
     {adminservice / pricecentermanage}
      INSERT
     value=account ──────→ 不可再修改
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 任意字串 | 管理員登入帳號 | adminservice / pricecentermanage | 建立管理員時指定，建立後不可變更 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT account | 建立管理員 | 主鍵，必須唯一 |
| pricecentermanage | INSERT account | 建立管理員 | 同上 |
| pricebackendservice | SELECT account | 登入驗證 | 查詢帳號 |
| gamesettingsite | SELECT account | 管理員查詢 | 後台列表或編輯 |
| backendservice | SELECT account | 權限驗證 | 驗證操作者身份 |

**⚠️ 跨服務限制**：

- account 建立後不可 UPDATE，任何服務皆不可修改。

---

### password 欄位

**型別**：text

**值定義與狀態流轉**：

```
     {adminservice / pricecentermanage}
      INSERT（強雜湊後寫入）
     password=雜湊值 ──────→ 僅密碼修改流程可更新
         ↑
         └── 禁止回傳、禁止明文儲存、禁止記錄於日誌
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| bcrypt 雜湊 | 管理員密碼驗證用 | adminservice / pricecentermanage（經 API） | 建立管理員或密碼變更時，系統雜湊後寫入 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT / UPDATE password=雜湊 | 建立管理員、修改密碼 | 必須經 bcrypt 等強雜湊，禁止明文 |
| pricecentermanage | INSERT / UPDATE password=雜湊 | 同上 | 同上 |
| pricebackendservice | SELECT password（內部比對） | 登入驗證 | 僅供內部密碼比對，不可回傳 |
| gamesettingsite | — | 不可直接讀寫密碼（應透過管理 API） | — |
| backendservice | — | 禁止接觸密碼 | 任何查詢皆不回傳此欄位 |

**⚠️ 跨服務限制**：

- password 絕不可出現在任何 API response 或 log 中。
- 只有負責管理員管理的服務（adminservice / pricecentermanage）可執行密碼更新，且必須確保強雜湊。
- pricebackendservice 僅可進行內部比對，不可回傳密碼值。

---

### level 欄位

**型別**：integer

**值定義與狀態流轉**：

```
     {adminservice / pricecentermanage}
      INSERT / UPDATE
     value=初始等級 ─────────→ value=新等級（不可自行提升）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| ≥0 正整數 | 管理員權限等級 | adminservice / pricecentermanage | 建立或由超級管理員修改 |
| 100 | 超級管理員 | 上述服務 | 僅建立時可設，後續不可降級 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT level=<值> | 建立管理員 | 權限等級由超級管理員決定 |
| adminservice | UPDATE level=<新值> | 修改權限 | 必須由 level≥某閥值的管理員執行，且不可提升自身 |
| pricecentermanage | INSERT / UPDATE level | 同 adminservice | 角色重疊，需確認是否為同一服務 |
| pricebackendservice | UPDATE level（經 API） | 收到有權限的管理員請求時 | 最終寫入由管理服務執行，應用層須校驗權限 |
| gamesettingsite | UPDATE level | 後台管理操作 | 權限控制於應用層 |
| backendservice | SELECT level | 權限判斷 | 決定可訪問的功能範圍 |

**⚠️ 跨服務限制**：

- level 欄位僅可由具備最高管理權限的服務或超級管理員變更。
- 任何服務不得允許管理員自行提升自身 level。
- level=100 的管理員一經建立，所有服務皆不可對其降級。

---

### active 欄位

**型別**：boolean

**值定義與狀態流轉**：

```
     {adminservice etc.}    {adminservice etc.}
      INSERT                UPDATE
     active=true ─────────→ active=false
         ↑                      │
         └──────────────────────┘
              UPDATE（重新啟用）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| true | 啟用 | adminservice / pricecentermanage | 建立時預設；手動啟用 |
| false | 停用 | 同上 | 管理員停用帳號，或多次登入失敗自動觸發 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT active=true | 建立管理員 | 預設啟用 |
| adminservice | UPDATE active=false | 停用帳號 | 管理員後台操作 |
| adminservice | UPDATE active=true | 重新啟用 | 管理員操作 |
| pricecentermanage | 同上 | 同上 | 角色重疊 |
| pricebackendservice | UPDATE active（經 API） | 停用/啟用請求 | 需權限控制 |
| gamesettingsite | UPDATE active | 同上 | 同上 |
| backendservice | SELECT WHERE active=true | 登入驗證、列表查詢 | 過濾已停用帳號 |

**⚠️ 跨服務限制**：

- 查詢管理員時，任何服務都必須加上 `active=true` 條件，避免已停用帳號通過驗證或顯示於列表。
- 停用的帳號不可登入。

---

### deleted_at 欄位

**型別**：timestamp with time zone（儲存 UTC）

**值定義與狀態流轉**：

```
     {adminservice}
      DELETE（軟刪除）
     deleted_at = NULL ─────────→ deleted_at = NOW()
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| NULL | 未刪除 | — | 預設 |
| UTC timestamp | 已軟刪除 | adminservice / pricecentermanage | 管理員執行刪除操作時寫入當前時間 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | UPDATE deleted_at=NOW() | 刪除管理員 | 軟刪除，不物理刪除資料 |
| pricecentermanage | 同上 | 同上 | — |
| pricebackendservice | UPDATE deleted_at（經 API） | 刪除管理員請求 | 需高權限 |
| gamesettingsite | UPDATE deleted_at | 同上 | — |
| backendservice | SELECT WHERE deleted_at IS NULL | 查詢列表 | 必須過濾已刪除帳號 |

**⚠️ 跨服務限制**：

- 任何對 admins 的查詢都必須加上 `WHERE deleted_at IS NULL`，除非有特殊稽核需求。
- 刪除操作不可逆，不能直接將 deleted_at 設回 NULL。
- backendservice 不可直接執行 DELETE 操作。

---

### last_login_at 欄位

**型別**：timestamp with time zone（儲存 UTC）

| 服務 | 操作 | 說明 |
|------|------|------|
| adminservice | UPDATE | 登入成功後自動設置當前 UTC 時間 |
| pricecentermanage | UPDATE | 同上 |
| pricebackendservice | UPDATE（系統自動） | 處理登入驗證成功後更新 |
| gamesettingsite | UPDATE | 若其處理登入流程則更新 |
| backendservice | SELECT | 用於判斷閒置時間、異常登入偵測 |

**⚠️ 注意**：
- 時區一律儲存 UTC，讀取時依前端需求轉換。
- 值為 NULL 表示該管理員從未登入。
- 僅可由系統自動更新，禁止手動賦值。

---

## Table：admin_login_logs

此表為管理員登入的歷史記錄，所有寫入均由服務端在登入驗證流程中自動完成，**禁止任何手動 INSERT / UPDATE / DELETE**。

### success 欄位

**型別**：boolean

**值定義與狀態流轉**：
一經寫入即不可變更。
- `true`：登入成功
- `false`：登入失敗，對應 `failure_reason` 欄位記錄原因

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT success=true/false | 登入驗證結束後 | 系統自動，同時記錄 IP、UserAgent 等 |
| pricecentermanage | INSERT ... | 同上 | 若它也處理登入 |
| pricebackendservice | INSERT ... | 登入 API 處理完成 | 系統自動，不可由請求端傳入參數 |
| gamesettingsite | INSERT ... | 若其處理後台登入 | 系統自動 |
| backendservice | SELECT | 稽核查詢 | 必須指定時間範圍，可依 success 篩選 |

**⚠️ 跨服務限制**：

- 任何服務不得直接對該表執行 UPDATE 或 DELETE。
- 寫入時必須正確設定 `success` 與 `failure_reason`，`failure_reason` 不得包含機敏資訊（如密碼明文、帳號存在性判斷）。
- backendservice 僅有 SELECT 權限，且必須加上時間範圍條件，不允許全表掃描。
- 一般業務 API 不應回傳此表資料，僅供內部稽核與後台管理使用。

---

## Table：admin_operation_logs

此表記錄管理員進行的所有敏感操作，所有寫入均由服務端在操作攔截器或對應流程中自動完成，**禁止手動 INSERT / UPDATE / DELETE**。

### action 欄位

**型別**：text

**值定義與狀態流轉**：
由系統根據實際執行的操作自動填入操作代碼（例如 `admin.create`、`admin.update`、`status.change` 等），不可由調用方指定。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| adminservice | INSERT action=<代碼> | 執行管理操作後 | 同時寫入 before_data / after_data（密碼欄位須排除） |
| pricecentermanage | INSERT ... | 同 adminservice | — |
| pricebackendservice | INSERT（經由管理 API） | 當作為管理操作的執行層時 | 由系統攔截器自動記錄，不可人為插入 |
| gamesettingsite | INSERT | 後台管理操作 | 同上 |
| backendservice | SELECT | 稽核查詢 | 必須指定時間範圍、分頁、依建立時間降序 |

**⚠️ 跨服務限制**：

- 任何服務都不可直接 INSERT 此表，必須透過 ORM 或攔截器機制自動生成記錄。
- before_data 和 after_data 必須為合法 JSON，且不可包含密碼等機敏欄位。
- backendservice 查詢時必須指定時間範圍，避免全表掃描。
- 此表資料僅供內部稽核或受控管後台使用，不可對外開放。

---

## Redis — ⚠️ 衝突待人工

根據 pricecentermanage 摘要，存在 Redis 快取，但詳細內容被截斷。可能涉及管理員 session、token 或權限快取。需人工確認並補充以下資訊：
- Key pattern（如 `admin:session:{account}` 等）
- 各服務的 SET/GET/DEL 操作與 TTL
- 與 admins 表資料同步策略

---

## 常見錯誤（跨服務）

- ❌ 直接對 admins 表執行 UPDATE，跳過管理員服務的權限驗證 → 應通過 adminservice / pricecentermanage API。
- ❌ 查詢 admins 時未加 `active=true` 或 `deleted_at IS NULL` 條件 → 可能導致已停用/已刪除帳號被使用。
- ❌ 在 API 回傳中洩漏 `password` 欄位 → 任何對外 API 絕不可回傳密碼。
- ❌ 手動寫入 admin_login_logs 或 admin_operation_logs → 日誌完整性喪失，可能無法稽核。
- ❌ 管理員操作日誌中記錄了密碼明文或雜湊 → 必須在寫入 before/after 快照時排除密碼欄位。
- ❌ 時間欄位未統一使用 UTC 儲存 → 各服務取用時產生時區不一致問題。
- ❌ backendservice 執行全表掃描 admin_login_logs 或 admin_operation_logs → 應強制使用時間範圍查詢。
- ❌ pricebackendservice 或 gamesettingsite 直接賦值 level 未經權限檢查 → 必須由具有足夠權限的管理員觸發，服務端驗證。