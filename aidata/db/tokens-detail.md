# tokens DB — 完整使用脈絡

> 產出時間：2026-05-30 08:30
> 欄位結構定義：[tokens.md](./tokens.md)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| tokenservice | owner | 讀、寫、更新、刪除（邏輯刪除：停用 token） |
| livechatservice | writer & reader | 讀取 tokens 表進行驗證、透過 TokenProvider 建立 token；唯寫 logs 表（INSERT 操作記錄） |
| ⚠️ 衝突待人工 | | existing 提及 authservice 為 reader，但本次 serviceSummaries 僅提供 tokenservice 與 livechatservice；authservice 角色請人工確認 |

---

## Table：tokens

### Enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     tokenservice / livechatservice       tokenservice / livechatservice
      INSERT                               UPDATE（停用、衝突、管理操作）
     value=1 ──────────────────────────→ value=0
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用（正常狀態） | tokenservice / livechatservice | INSERT 時預設值 |
| 0 | 停用 | tokenservice / livechatservice | 手動停用、衝突時舊 token 被取代、管理操作停用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tokenservice | INSERT Enabled=1 | 建立新 token | 預設啟用 |
| tokenservice | UPDATE Enabled=0 | 手動停用、或建立新 token 時舊 token 衝突（同 CompanyCode + HashKey 且 Enabled=1 已存在） | 先停用舊 token 再新增 |
| tokenservice | SELECT WHERE Enabled=1 | CheckToken、CheckTokenByOriginKey 驗證 | 必須同時滿足 ExpirationTime > NOW() |
| livechatservice | INSERT Enabled=1 | TokenProvider.CreateToken 建立新 token | 預設啟用 |
| livechatservice | UPDATE Enabled=0 | 透過特定管理功能進行停用 | 一般業務流程不得直接修改 |
| livechatservice | SELECT WHERE Enabled=1 | CheckToken 驗證 | 必須同時滿足 HashKey、CompanyCode、ExpirationTime 條件 |

**⚠️ 跨服務限制**：

- 只有 tokenservice 可以直接變更 Enabled 欄位；livechatservice 僅允許在特定管理功能中啟用/停用。
- 一般業務流程不可直接修改 Enabled 欄位。
- 不允許物理刪除 token 記錄，只允許邏輯刪除（Enabled=0）。
- 建立新 token 時若存在同 CompanyCode + HashKey 且 Enabled=1 的紀錄，必須先將該筆設為 0，再新增 token。

---

### ExpirationTime 欄位

**型別**：datetime（UTC，預設 CURRENT_TIMESTAMP）

| 服務 | 操作 | 說明 |
|------|------|------|
| tokenservice | INSERT | 建立 token 時由系統計算過期時間（`CURRENT_TIMESTAMP + 有效秒數`），存入 UTC |
| tokenservice | SELECT | CheckToken 驗證時比較 `ExpirationTime > NOW()`（UTC） |
| livechatservice | INSERT | TokenProvider.CreateToken 根據傳入的 `expirationTime` 參數自動設定（必須由 TokenProvider 計算，外部 API 不可直接指定） |
| livechatservice | SELECT | 驗證 token 時檢查是否過期 |

**⚠️ 注意**：

- 建立 token 後不可 UPDATE 此欄位；若要延長期限，應重新建立 token 並將舊 token 停用（Enabled=0）。
- 所有服務比較過期時間時必須以 UTC 為準，避免時區轉換錯誤。
- livechatservice 的 expirationTime 參數必須由 TokenProvider.CreateToken 根據當前時間和配置計算，不允許從外部 API 直接指定。

---

### HashKey 欄位

**型別**：char(10)

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tokenservice | INSERT | CreateTokenByOriginKey | 由 `originKey` 經雜湊演算法轉換並截斷為前 10 個字元後存入，不可手動指定 |
| tokenservice | SELECT | CheckTokenByOriginKey、CheckToken | 依 HashKey 查詢 |
| livechatservice | INSERT | TokenProvider.CreateToken | 生成邏輯應為不可逆雜湊或隨機字串，不可直接複製或手動指定 |
| livechatservice | SELECT | CheckToken 驗證 | 使用 HashKey 作為主要過濾條件，以提高查詢效率 |

**⚠️ 跨服務限制**：

- 任何對外 API 皆不可回傳 HashKey 欄位值（敏感識別資訊）。
- 僅 `CreateTokenByOriginKey`（tokenservice）或 `TokenProvider.CreateToken`（livechatservice）可寫入 HashKey；`CreateToken` 不操作此欄位。
- livechatservice 的 HashKey 不可直接複製或手動指定，必須透過 TokenProvider 生成。

---

### CompanyCode 欄位

**型別**：char(10)

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tokenservice | INSERT | 建立 token | 由認證請求（`authKey`）或設定檔決定，API 呼叫方不可自由指定 |
| tokenservice | SELECT | CheckToken 驗證 | 依 CompanyCode 過濾 |
| livechatservice | INSERT | TokenProvider.CreateToken | 必須與請求上下文中的公司代碼一致，嚴防跨公司寫入 |
| livechatservice | SELECT | CheckToken 驗證 | CompanyCode 必須匹配請求上下文 |

**⚠️ 注意**：

- API 呼叫方不可自由指定 CompanyCode，必須由 tokenservice 或設定檔決定。
- livechatservice 假定傳入的 CompanyCode 是有效且已存在的，不負責校驗其合法性；若要強化安全性，建議後續加入校驗。

---

### AddTime 欄位

**型別**：datetime（UTC，預設 CURRENT_TIMESTAMP）

| 服務 | 操作 | 說明 |
|------|------|------|
| tokenservice | INSERT | 建立 token 時自動設定當前 UTC 時間，不可由外部指定 |
| livechatservice | INSERT | TokenProvider.CreateToken 根據當前時間自動設定，不允許從外部 API 直接指定 |

**⚠️ 注意**：

- 此欄位由資料庫預設值或服務自動設定，外部 API 不可直接指定。
- 時區統一為 UTC。

---

## Table：logs

### Action 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tokenservice | INSERT | 每次 token 操作（CreateToken、CheckToken、EnableToken、DisableToken） | 由內部 `SetLog` 方法寫入，不開放任何 API 直接操作 |
| livechatservice | INSERT | TokenProvider 內部執行 CreateToken 和 CheckToken 時 | 唯寫（Write-Only）記錄，僅供 TokenProvider 內部新增 |

**⚠️ 注意**：

- logs 表僅用於稽核與排查，不參與任何線上業務邏輯判斷。
- Action 內容可能包含 Token 明文（如 `Token Validation Request: 7LrHjteaFX`），任何對外 API 皆不可回傳；若須查閱，應由內部管理介面脫敏處理。
- 不允許 UPDATE 或 DELETE 操作。

---

### AccessTime 欄位

**型別**：datetime（UTC，預設 CURRENT_TIMESTAMP）

| 服務 | 操作 | 說明 |
|------|------|------|
| tokenservice | INSERT | 記錄操作發生的時間點，由服務端自動填入 |
| livechatservice | INSERT | 由 TokenProvider 內部在執行操作時自動設定 |

**⚠️ 注意**：

- 時區統一為 UTC，前端展示時需自行轉換。

---

### CompanyCode 欄位

**型別**：char(10)

| 服務 | 操作 | 說明 |
|------|------|------|
| tokenservice | INSERT | 記錄操作所屬的公司代碼，由呼叫方傳入 |
| livechatservice | INSERT | 由 TokenProvider 內部在執行操作時自動寫入 |

**⚠️ 注意**：

- 此欄位僅供稽核用途，不參與業務邏輯。

---

## Redis — TokenCache

### xxx_token_{HashKey}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | tokenservice | CheckToken 驗證通過後 | TTL：`ExpirationTime - 當前時間`（秒），主動更新 token 時須同步刪除舊 key |
| GET | tokenservice | CheckToken 查詢時 | 若存在直接判定 token 有效；Redis miss 才查 DB |
| DEL | tokenservice | 手動停用 token、token 過期、或建立新 token 取代舊 token（衝突處理）時 | 必須主動刪除，不可只靠 TTL 自然過期，以維持最終一致性 |

**⚠️ 注意**：

- 任何服務讀不到此 Key 時必須 fallback 查 DB，不可直接報錯。
- livechatservice 對 tokens 資料庫無 Redis 操作，其快取機制由 livechatservice 自行處理。

---

## 常見錯誤（跨服務）

- ❌ 直接在 SQL 中查 `HashKey = ?` 而忽略 `Enabled` 與 `ExpirationTime` → ✅ 應一律加上 `Enabled = 1 AND ExpirationTime > NOW()` 條件。
- ❌ 手動透過 UPDATE 修改 `ExpirationTime` 延長 token 期限 → ✅ 一律重新建立 token，舊 token 標記為停用 (`Enabled = 0`)。
- ❌ 對外 API 回傳 `HashKey` 值 → ✅ 任何對外回應都應遮蔽或排除該欄位。
- ❌ `CreateTokenByOriginKey` 建立 token 時未檢查舊 token 是否已存在且 `Enabled=1` → ✅ 應先停用舊 token (`Enabled=0`) 再新增。
- ❌ tokenservice 主動更新 Redis 設定後遺漏 DEL 舊 key → ✅ 建立新 token、停用 token 後應立即清除對應 Redis key。
- ❌ 嘗試讀取 `tokens.logs` 來判斷 token 是否有效 → ✅ `logs` 表僅為操作記錄，不具備狀態判斷能力，必須查詢 `tokens.tokens` 表。
- ❌ livechatservice 在一般業務流程中直接修改 `Enabled` 欄位 → ✅ 僅允許透過特定管理功能進行啟用/停用。
- ❌ livechatservice 在 API 回應中因格式化或 Debug 需求而回傳了 `HashKey` → ✅ 應設計專門的、安全的值物件（ViewModel）來排除敏感欄位。
- ❌ 建立 token 時由 API 呼叫方直接指定 `CompanyCode` → ✅ 應由服務端依認證資訊或設定檔決定。