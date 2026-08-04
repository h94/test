# stock DB — 完整使用脈絡

> 產出時間：2026-05-30 08:28  
> 欄位結構定義：[stock.json](./stock.json)  
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效  

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| mqservice | owner | 讀、寫（所有表，遵循各欄位限制） |
| tradegameservice | owner | 讀、寫（所有表，遵循各欄位限制） |
| productservice | owner | 讀、寫（所有表，主要負責後台管理、使用者管理、規則設定等，遵循各欄位限制） |
| tradegameresultservice | writer | 讀、寫（所有表，但 users.Password、users.Enabled、rules 定義欄位僅讀取；可寫入 messagelog、sublogs 等） |
| memberservice | reader | 唯讀（users、sublogs） |
| feedbackservice | reader | 唯讀多數表；messagelog 僅限內部後台轉移任務寫入 |

> 註：pricecentersite 不直接存取 stock DB，其會員相關資訊透過 memberservice 間接取得，故不列入本表。  
> ⚠️ **衝突待人工**：productservice 新增為 owner，與現有角色定義可能重疊；後續各表操作明細均已納入，需確認各服務實際職責是否與本表一致。

---

## Table：FavoriteBroker

### User 欄位（複合主鍵）

**型別**：varchar

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選經紀商 | 僅允許對應 User 本人操作 |
| tradegameservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選經紀商 | 僅允許對應 User 本人操作 |
| productservice | INSERT / SELECT / DELETE WHERE User=? | 管理後台或使用者操作 | 支援後台強制維護使用者收藏；同樣遵守使用者隔離 |
| tradegameresultservice | SELECT WHERE User=? | 讀取自選經紀商 | 唯讀，不可寫入 |

### Name 欄位（複合主鍵）

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT | 使用者管理自選經紀商 | 經紀商名稱 |
| tradegameservice | INSERT / SELECT | 使用者管理自選經紀商 | 經紀商名稱 |
| productservice | INSERT / SELECT | 管理後台 / 使用者操作 |  |

### Value 欄位

**型別**：text（須為合法 JSON 陣列字串）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE / SELECT | 使用者管理自選經紀商 | 寫入前須驗證格式為合法 JSON 陣列，並限制陣列長度 |
| tradegameservice | INSERT / UPDATE | 使用者管理自選經紀商 | 同上 |
| productservice | INSERT / UPDATE | 使用者管理或後台操作 | 同上；後台操作時仍需驗證 JSON 格式 |
| tradegameresultservice | SELECT | 讀取設定 | 唯讀 |

**⚠️ 跨服務限制**：
- 僅允許對應 User 本人或具權限的管理後台（productservice）進行寫入，不可由系統批次程序隨意變更
- tradegameresultservice 對此表僅讀取，不可直接 UPDATE 或 DELETE
- Value 欄位寫入前必須驗證 JSON 陣列格式，若格式錯誤應拒絕寫入

---

## Table：FavoriteRule

### User 欄位（複合主鍵）

**型別**：varchar

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選規則 | 僅允許對應 User 本人操作 |
| tradegameservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選規則 | 僅允許對應 User 本人操作 |
| productservice | INSERT / SELECT / DELETE WHERE User=? | 管理後台或使用者管理 | 支援後台強制維護 |
| tradegameresultservice | INSERT / SELECT WHERE User=? | 使用者管理自選規則 | 僅允許對應 User 本人操作 |

### Name 欄位（複合主鍵）

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT | 使用者管理自選規則 | 規則名稱（如 "投信買超+三大法人買超前50名"） |
| productservice | INSERT / SELECT | 使用者管理或後台設定 |  |

### Strategy 欄位（複合主鍵）

**型別**：int

**值定義**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| {策略編號} | 規則策略類型 | mqservice / tradegameservice / productservice | 規則管理 API 寫入，不可由一般偏好設定端點修改 |

### Value 欄位

**型別**：varchar（須為合法 JSON 格式，儲存規則參數）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE / SELECT | 使用者管理自選規則 | 寫入前須驗證 JSON 格式正確 |
| productservice | INSERT / UPDATE / SELECT | 使用者管理或後台設定 | 同上 |

### NeedSend 欄位

**型別**：int

**值定義與狀態流轉**：

```
     mqservice / tradegameservice / productservice     tradegameservice（排程）
      INSERT                                            UPDATE
     value=0 ───────────────────────────────────────→ value=1
                      （首次匹配觸發或使用者啟用通知）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 不發送通知 | mqservice / tradegameservice / productservice | 使用者設定規則時預設 |
| 1 | 需發送通知 | tradegameservice（排程）或 productservice（管理後台手動調整） | 規則引擎首次匹配成功後自動設為 1，或管理員手動開啟 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE NeedSend=1 | 觸發規則時 | 作為發送通知的篩選條件 |
| tradegameservice | UPDATE NeedSend=1 | 規則引擎或後台排程 | 首次匹配後自動更新，不可由一般偏好設定端點修改 |
| productservice | UPDATE NeedSend=0/1 | 管理後台手動調整 | 管理員可強制開啟或關閉通知；⚠️ 避免與排程自動更新衝突，需有明確權限控制 |
| tradegameresultservice | SELECT WHERE NeedSend=1 | 讀取規則時 | 用於通知準備 |

### FirstMatch 欄位

**型別**：int

**值定義與狀態流轉**：

```
     mqservice / tradegameservice / productservice     tradegameservice（排程）
      INSERT                                            UPDATE
     value=0 ───────────────────────────────────────→ value=1
                      （首次匹配成功後）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 尚未匹配 | mqservice / tradegameservice / productservice | 使用者設定規則時預設 |
| 1 | 已首次匹配 | tradegameservice（排程） | 首次匹配後自動設為 1；不可由前台或一般 API 直接修改 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE FirstMatch=0 | 觸發規則時 | 用於「首次匹配後不再重複發送」邏輯 |
| tradegameservice | UPDATE FirstMatch=1 | 規則引擎或後台排程 | 首次匹配後自動更新，前端不可操作 |
| productservice | SELECT / UPDATE（管理後台） | 特殊情況手動重置 | ⚠️ 手動重置 FirstMatch 可能導致重複發送，需謹慎；預設不可直接修改 |
| tradegameresultservice | SELECT WHERE FirstMatch=? | 讀取規則時 | 不可直接修改此欄位 |

### Industry 欄位

**型別**：varchar，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Industry=? | 篩選特定行業 | 非空時須與標的股票所屬行業匹配才觸發 |
| tradegameresultservice | SELECT WHERE Industry=? | 規則比對 | 同上 |
| productservice | INSERT / UPDATE / SELECT | 管理後台或使用者設定 | 設定行業篩選條件 |

### FilterMarket 欄位

**型別**：varchar，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE FilterMarket=? | 篩選特定市場 | 非空時須與標的股票所屬市場匹配才觸發 |
| tradegameresultservice | SELECT WHERE FilterMarket=? | 規則比對 | 同上 |
| productservice | INSERT / UPDATE / SELECT | 管理後台或使用者設定 | 設定市場篩選條件 |

### Country 欄位

**型別**：varchar，預設值 'tw'

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Country=? | 查詢使用者所屬國家 | 預設 'tw'，與用戶區域匹配 |
| tradegameservice | SELECT WHERE Country=? | 讀取規則時 | 需與用戶所在市場匹配 |
| tradegameresultservice | SELECT WHERE Country=? | 市場限定查詢 | 需與使用者所屬國家一致 |
| productservice | INSERT / UPDATE / SELECT | 管理後台或使用者設定 | 預設 'tw'，可依市場調整 |

**⚠️ 跨服務限制**：
- Strategy、NeedSend、FirstMatch 主要由規則引擎（tradegameservice）自動維護，productservice 僅限管理後台特殊干預，不可開放給一般使用者或 API 任意修改
- FirstMatch 欄位僅 tradegameservice 排程可安全更新為 1；productservice 手動變更需有完整稽核
- 僅允許對應 User 本人或具管理權限的後台進行寫入，不可由系統批次程序跨使用者變更
- 所有寫入前須驗證 Value 為合法 JSON 格式

---

## Table：FavoriteStock

### ID 欄位（自增主鍵）

**型別**：int，AUTO_INCREMENT

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT（不指定值） | 使用者新增自選股 | 由 DB 自動產生，禁止應用層手動指定 |
| tradegameservice | INSERT（不指定值） | 使用者新增自選股 | 同上 |
| productservice | INSERT（不指定值） | 使用者新增自選股或後台操作 | 同上 |

### User 欄位（複合主鍵）

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選股 | 僅允許對應 User 本人操作 |
| tradegameservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理自選股 | 僅允許對應 User 本人操作 |
| productservice | INSERT / SELECT / DELETE WHERE User=? | 使用者管理或後台維護 | 支援後台強制維護 |
| tradegameresultservice | SELECT WHERE User=? | 讀取自選股 | 唯讀，不可跨使用者存取 |

### Name 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / SELECT | 使用者管理自選股 | 股票代號或自選股名稱 |
| productservice | INSERT / SELECT | 使用者管理或後台 |  |

### Value 欄位

**型別**：text（須為合法 JSON 陣列字串）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE / SELECT | 使用者管理自選股 | 寫入前須驗證 JSON 陣列格式，並限制陣列長度 |
| tradegameservice | INSERT / UPDATE | 使用者管理自選股 | 同上 |
| productservice | INSERT / UPDATE | 使用者管理或後台 | 同上 |

### Country 欄位

**型別**：varchar，預設值 'tw'

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Country=? | 查詢使用者所屬國家 | 只載入符合當前市場的組合 |
| tradegameresultservice | SELECT WHERE Country=? | 市場限定查詢 | 預設 'tw' |
| productservice | INSERT / UPDATE / SELECT | 管理後台或使用者 | 預設 'tw' |

**⚠️ 跨服務限制**：
- 僅允許對應 User 本人或具管理權限的後台進行寫入，不可由系統批次程序變更
- tradegameresultservice 僅可讀取，不可執行 INSERT、UPDATE 或 DELETE
- Value 寫入前必須驗證 JSON 陣列格式，若格式錯誤應拒絕寫入

---

## Table：MessageLog

### Date 欄位（分區鍵，複合主鍵）

**型別**：varchar（格式 yyyyMMdd）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT Date | 建立發送任務 | 帶入當天日期，作為分區依據 |
| mqservice | SELECT WHERE Date=? | 查詢發送歷史 | 必須搭配 Date 條件以利分區查詢，無日期範圍時應限制查詢筆數 |
| feedbackservice | INSERT Date | 運動反饋轉移任務 | 僅限特定任務寫入 |
| tradegameservice | INSERT Date | 寫入日誌 | 同日寫入 |
| tradegameresultservice | INSERT Date | 寫入日誌 | 同日寫入 |
| productservice | INSERT Date | 發送通知或後台記錄 | ⚠️ productservice 亦會寫入 messagelog，需確認其發送通知身分是否與 mqservice 重疊 |

### Account 欄位（複合主鍵）

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT Account | 建立發送任務 | 接收者帳號 |
| mqservice | SELECT WHERE Account=? | 查詢發送歷史 | 可依帳號進一步過濾 |
| productservice | INSERT Account | 發送通知 |  |

### SendStatus 欄位

**型別**：int

**值定義與狀態流轉**：

```
      mqservice / tradegameservice       mqservice（發送回調）/ productservice（發送回調）
      / tradegameresultservice            UPDATE
      / productservice
       INSERT
      value=0（未發送） ──────────────→ value=1（成功）
                                  或
                                ───→ value=2（失敗）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未發送 / 待處理 | mqservice / feedbackservice / tradegameservice / tradegameresultservice / productservice | INSERT 時預設值 |
| 1 | 發送成功 | mqservice / productservice（負責發送調回調的服務） | 發送後回調成功，更新為 1 |
| 2 | 發送失敗 | mqservice / productservice | 發送後回調失敗，或重試後仍失敗 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT SendStatus=0 | 建立發送任務 | 預設未發送 |
| mqservice | UPDATE SendStatus=1 或 2 | 發送回調 | 成功或失敗後更新，不可直接 SET 為其他狀態 |
| mqservice | SELECT WHERE SendStatus=? | 查詢發送歷史 | 可依狀態篩選 |
| feedbackservice | INSERT SendStatus | 運動反饋轉移任務 | 僅限特定任務，不可由外部 API 直接 INSERT / UPDATE |
| tradegameservice | INSERT SendStatus=0 | 寫入日誌 | append-only，已有記錄不可 DELETE |
| tradegameresultservice | INSERT SendStatus=0 | 寫入日誌 | append-only，僅可將 SendStatus 0→1 或 0→2 更新 |
| productservice | INSERT SendStatus=0 | 發送通知 | ⚠️ productservice 是否為主要發送服務？若與 mqservice 分工不同，需明確定義； |
| productservice | UPDATE SendStatus=1/2 | 發送回調 |  |

### MsgContent 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT | 建立發送任務 | 內部儲存完整訊息內容 |
| mqservice | SELECT（內部查詢） | 除錯或重送 | 不可對外回傳，對外查詢時應過濾或僅顯示摘要 |
| productservice | INSERT | 發送通知 |  |

**⚠️ 跨服務限制**：
- 本表為 append-only 日誌，一旦 INSERT 後僅 SendStatus 可更新為 1 或 2，其餘欄位不可修改，且不可 DELETE
- MsgContent 欄位嚴禁任何 API 回傳至前端
- 所有查詢（含 SELECT）必須攜帶 Date 條件以有效利用分區；不得執行全表掃描
- feedbackservice 僅可由內部任務（SportFeedbackTransfer）寫入，不應暴露為公開端點
- tradegameresultservice 寫入的記錄僅可將 SendStatus 從 0 更新為 1 或 2，不可跳級或降級
- ⚠️ **衝突待人工**：productservice 摘要中提及「messagelog：僅發送通知服務寫入」，但現有文檔中多個服務（tradegameservice、tradegameresultservice）亦可寫入。需確認 productservice 所指的「發送通知服務」是否涵蓋這些服務，或者應限制寫入者。

---

## Table：Options

### ID 欄位（自增主鍵）

**型別**：int，AUTO_INCREMENT

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT（不指定值） | 管理後台新增選項 | 由 DB 自動產生，禁止應用層手動指定 |
| tradegameservice | INSERT（不指定值） | 管理後台新增選項 | 同上 |
| productservice | INSERT（不指定值） | 管理後台新增選項 | 同上 |

### Value 欄位

**型別**：varchar（業務上唯一，須為合法 JSON 格式）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE / SELECT | 管理後台 | 寫入時須唯一檢查，避免重複選項；若為 JSON 陣列須正確解析 |
| tradegameservice | INSERT / UPDATE | 管理後台 | 僅管理後台可寫入 |
| productservice | INSERT / UPDATE / SELECT | 管理後台 | 同上；寫入時遵循格式限制 |
| tradegameresultservice | SELECT WHERE Enabled=1 | 讀取系統設定 | 唯讀，確認 Enabled=1 才生效 |

### Enabled 欄位

**型別**：int，預設 1

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | mqservice / tradegameservice / productservice | 管理後台新增時預設 |
| 0 | 停用 | mqservice / tradegameservice / productservice | 管理後台關閉選項 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Enabled=1 | 系統讀取選項 | 僅回傳啟用中的選項 |
| tradegameservice | SELECT WHERE Enabled=1 | 前端讀取選項 | 停用的選項不回傳 |
| tradegameresultservice | SELECT WHERE Enabled=1 | 讀取系統設定 | 取得實際生效的設定 |
| productservice | SELECT WHERE Enabled=1 / UPDATE Enabled | 管理後台讀取和設定 | 僅管理後台可變更 Enabled 狀態 |

**⚠️ 跨服務限制**：
- 僅管理後台可直接寫入 options 表，前端 API 一律不可 INSERT / UPDATE / DELETE
- tradegameresultservice、feedbackservice 等服務僅具讀取權限
- 讀取選項時必須確認 Enabled = 1，以取得實際生效的設定

---

## Table：Rules

### ID 欄位（自增主鍵）

**型別**：int，AUTO_INCREMENT

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT（不指定值） | 管理後台新增規則 | 由 DB 自動產生 |
| tradegameservice | INSERT（不指定值） | 管理後台新增規則 | 同上 |
| productservice | INSERT（不指定值） | 管理後台新增規則 | 同上 |

### Type 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Type=? | 規則匹配時 | 依規則類別（如「技術面」）過濾 |
| tradegameresultservice | SELECT WHERE Type=? | 規則比對 | 依規則類別篩選 |
| productservice | INSERT / UPDATE / SELECT | 管理後台規則設定 | 設定或修改規則類別 |

### Indicator 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Indicator=? | 規則判斷 | 技術指標名稱 |
| productservice | INSERT / UPDATE / SELECT | 管理後台規則設定 | 設定指標名稱 |

### Text 欄位

**型別**：varchar（規則描述）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT Text | 管理後台新增規則 | 規則描述，不可由一般服務修改 |
| tradegameservice | INSERT Text | 管理後台新增規則 | 同上 |
| productservice | INSERT / UPDATE Text | 管理後台規則設定 | 管理員可編輯規則描述 |

### Enabled 欄位

**型別**：int，預設 1

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | mqservice / tradegameservice / productservice | 管理後台設定 |
| 0 | 停用 | mqservice / tradegameservice / productservice | 管理後台設定（關閉規則） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Enabled=1 | 讀取觸發規則清單 | 停用規則不觸發 |
| tradegameservice | SELECT WHERE Enabled=1 | 讀取規則 | 僅讀取啟用規則 |
| tradegameresultservice | SELECT WHERE Enabled=1 | 規則比對 | 僅啟用規則納入計算 |
| productservice | SELECT / UPDATE Enabled | 管理後台管理規則開關 | 停用/啟用規則，直接影響所有服務 |

### Parameter 欄位

**型別**：varchar（須為合法 JSON 格式）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE / SELECT | 管理後台設定 | 規則的參數值，須為 JSON 格式（如 ["2","2","K"]） |
| productservice | INSERT / UPDATE / SELECT | 管理後台規則設定 |  |

### Countries 欄位

**型別**：varchar（須為合法 JSON 陣列）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Countries LIKE ? | 規則判斷 | 支援多國，儲存 JSON 陣列（如 ["tw"]），需與用戶市場匹配 |
| tradegameresultservice | SELECT WHERE Countries LIKE ? | 規則比對 | 同上 |
| productservice | INSERT / UPDATE / SELECT | 管理後台規則設定 | 設定適用國家 |

**⚠️ 跨服務限制**：
- 僅管理後台可寫入 rules 表（Type、Indicator、Text、Parameter、Countries 等定義欄位），前端 API 只能讀取
- 任何服務在讀取規則時，必須附加 WHERE Enabled=1 條件；若未過濾，可能取得停用規則導致錯誤觸發
- tradegameresultservice 僅可讀取，不可新增或修改現有規則的定義欄位

---

## Table：SubLogs

### Account 欄位（複合主鍵）

**型別**：varchar

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT WHERE Account=? | 訂閱記錄寫入 | 記錄用戶訂閱歷程 |
| tradegameservice | INSERT WHERE Account=? | 訂閱交易完成後寫入 | 寫入新的訂閱事件 |
| tradegameresultservice | INSERT WHERE Account=? | 訂閱過期判定或金流回調 | 記錄訂閱狀態變更 |
| productservice | INSERT WHERE Account=? | 訂閱流程建立或續期 | 確認訂閱事件，主鍵欄位寫入後不可變更 |
| memberservice | SELECT WHERE Account=? | 查詢訂閱記錄 | 唯讀，用於檢查訂閱狀態 |

### AddTime 欄位（複合主鍵）

**型別**：bigint（時間戳）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT (系統生成) | 寫入時由系統填充 | 不可手動指定 |
| productservice | INSERT (系統生成) | 寫入時由系統填充 | 同上 |

### TradeNo 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT | 金流交易編號 | 與支付系統對應 |
| productservice | INSERT | 金流交易編號 | 與支付系統對應 |

### SubID 欄位

**型別**：varchar

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT | 訂閱方案 ID |  |
| productservice | INSERT | 訂閱方案 ID |  |

### SubRank 欄位

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT | 訂閱等級 |  |
| productservice | INSERT | 訂閱等級 |  |

### SubTime 欄位

**型別**：varchar（日期時間字串）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT | 訂閱開始時間 | 系統寫入 |
| productservice | INSERT | 訂閱開始時間 | 系統寫入 |

### SubEndTime 欄位

**型別**：varchar（日期時間字串）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 訂閱結束時間，可由排程更新 | 僅訂閱到期排程或續期時可變更 |
| productservice | INSERT / UPDATE | 訂閱結束時間，由訂閱模組計算寫入 | SubEndTime 為訂閱有效期限，更新須有明確業務邏輯 |

**⚠️ 跨服務限制**：
- SubLogs 為 append-only 日誌，寫入後主鍵欄位不可變更；SubEndTime 僅限排程或續期流程更新
- 任何服務在寫入 SubLogs 時，需確保對應的 Users 記錄存在且 Enabled=1（除非特殊訂閱流程）
- productservice 寫入時需確保訂閱方案有效，並正確計算 SubEndTime

---

## Table：Users

### Account 欄位（主鍵）

**型別**：varchar

**值定義與狀態流轉**：註冊後不可更新，為使用者唯一識別碼。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT Account | 使用者註冊 | 寫入帳號，不可變更 |
| productservice | INSERT Account | 使用者註冊或後台建立 | 同上；註冊後不可 UPDATE |
| tradegameservice | SELECT WHERE Account=? | 使用者查詢 | 僅讀取自己的資料 |
| tradegameresultservice | SELECT WHERE Account=? | 使用者驗證 | 唯讀，不可變更 |
| memberservice | SELECT WHERE Account=? | 查詢使用者身份 | 唯讀 |

### Password 欄位

**型別**：varchar（雜湊儲存）

**值定義與狀態流轉**：註冊或密碼修改時經 bcrypt 或 SHA-256 加鹽雜湊後寫入；不可明文儲存，不可透過 API 回傳。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE（密碼變更 API） | 註冊或修改密碼 | 必須雜湊後寫入，禁止直接 UPDATE |
| productservice | INSERT / UPDATE | 註冊或後台重設密碼 | 同上；後台重設密碼須有安全流程 |
| tradegameservice | SELECT（內部驗證） | 登入驗證 | 不可回傳，僅用於比對 |
| tradegameresultservice | 不可讀取 | — | 明文或雜湊皆不可外洩 |
| memberservice | 不可讀取 | — |  |

**⚠️ 注意**：
- 任何對外 API（包含查詢使用者資料）均不可回傳 Password 欄位，即使遮蔽也禁止。
- 寫入 Password 時必須確保已雜湊，若收到明文應在服務端立即雜湊，不可直接入庫。

### Enabled 欄位

**型別**：int，預設 1

**值定義與狀態流轉**：

```
     mqservice / productservice         productservice（管理後台）
      INSERT                             UPDATE
     value=1（啟用） ────────────────→ value=0（停用）
                      （管理員停用帳號）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | mqservice / productservice | 註冊時預設或後台啟用 |
| 0 | 停用 | productservice（管理後台）或系統排程（過期未續費等） | 停用帳號，禁止登入及大部分操作 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | SELECT WHERE Enabled=1 | 登入、規則觸發、使用者操作前檢查 | 停用帳號禁止操作 |
| productservice | UPDATE Enabled=0/1 | 管理後台停用/啟用 | 僅後台管理 API 可操作 |
| tradegameservice | SELECT WHERE Enabled=1 | 交易前驗證 | 停用不可交易 |
| tradegameresultservice | SELECT WHERE Enabled=1 | 結算或讀取使用者資料時 | 僅處理啟用帳戶 |
| memberservice | SELECT WHERE Enabled=1 | 查詢使用者狀態 | 僅回傳啟用中帳戶資訊 |

**⚠️ 跨服務限制**：
- Enabled 欄位僅可透過管理後台（productservice）或特定系統流程變更，任何前端 API 或排程（除明確的停用排程外）不可直接 UPDATE。
- 所有涉及使用者驗證、操作授權的查詢，必須強制加上 `WHERE Enabled=1` 條件。

### Rank 欄位

**型別**：int

**值定義與狀態流轉**：會員等級，反映訂閱或活動層級。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE（後台管理） | 初始預設等級或後台調整 | 不可由一般使用者修改 |
| productservice | INSERT / UPDATE | 後台管理或訂閱服務 API | 與 SubEndTime 聯動，過期後可能降級 |
| tradegameservice | SELECT | 交易驗證（如手續費優惠） | 唯讀 |
| tradegameresultservice | SELECT | 結算或紀錄 | 唯讀 |
| memberservice | SELECT | 查詢會員身份 | 唯讀 |

### SendAction 欄位

**型別**：varchar，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 使用者偏好設定 | 通知方式（如 SMS、LINE、Email 等） |
| productservice | INSERT / UPDATE | 後台設定或使用者綁定 | 格式驗證 |
| tradegameservice | SELECT | 發送通知時讀取 | 唯讀 |

### Phone 欄位

**型別**：varchar，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 使用者綁定手機 | 寫入前驗證格式 |
| productservice | INSERT / UPDATE | 後台綁定或使用者設定 | 需脫敏儲存？寫入明文，但回傳時須遮罩 |
| tradegameservice | SELECT（自身查詢或通知發送） | 發送 SMS 時使用 | 不可對其他使用者回傳完整號碼 |
| memberservice | SELECT（內部） | 可能用於驗證 | 不可回傳給前端 |

**⚠️ 注意**：
- Phone 欄位屬於個資，對外 API 回傳使用者自身資料時，應僅回傳尾碼（如後四碼），管理後台可看完整。
- 任何服務在無明確業務需求時不可將其回傳至前端。

### Email 欄位

**型別**：varchar，不可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 註冊或綁定 Email | 格式驗證，禁止一次性信箱網域 |
| productservice | INSERT / UPDATE | 後台綁定或使用者設定 |  |
| tradegameservice | SELECT | 登入或發送郵件通知 | 僅限自身帳號下可取得完整 Email |
| tradegameresultservice | SELECT | 可能用於通知 | 不可回傳給前端 |
| memberservice | SELECT | 查詢使用者 | 回傳時須遮罩（如 a***@example.com） |

**⚠️ 注意**：
- Email 欄位屬個資，對外 API 回傳時應遮罩處理；管理後台可看完整。

### ChatID 欄位

**型別**：varchar，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 綁定 LINE 或其他通訊平台 | 內部通訊用，不回傳前端 |
| productservice | INSERT / UPDATE | 後台綁定 | 同上 |

### AddTime 欄位

**型別**：datetime

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT（系統寫入） | 註冊時自動填入 | 不可由應用程式手動指定 |
| productservice | INSERT（系統寫入） | 註冊或後台建立時自動填入 | 同上 |

### SubEndTime 欄位

**型別**：datetime，可為 NULL

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mqservice | INSERT / UPDATE | 訂閱模組更新 | 記錄訂閱到期時間，過期後視為一般用戶 |
| productservice | INSERT / UPDATE | 訂閱服務寫入 | 與 SubLogs 聯動 |
| tradegameservice | SELECT WHERE SubEndTime > NOW() | 交易前驗證訂閱有效性 | 過期用戶可能限制功能 |
| tradegameresultservice | SELECT | 查詢訂閱狀態 | 唯讀 |
| memberservice | SELECT | 查詢會員到期日 | 唯讀 |

### LastUpdateTime 欄位

**型別**：timestamp，預設 CURRENT_TIMESTAMP，ON UPDATE 自動更新

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| **所有服務** | 不可手動寫入 | DB 自動維護 | 任何 UPDATE 操作時自動刷新，應用程式不可直接設定 |

---

## Redis — StockCache

### `stock:user:verify:{account}`

**用途**：快取使用者基本驗證狀態（Enabled、Rank、SubEndTime），避免交易前頻繁查詢 MySQL。

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | tradegameservice | 交易前查詢且快取未命中時，從 DB 載入並設定 TTL | TTL：3600 秒 |
| GET | tradegameservice | 交易前驗證使用者狀態 | 若快取不存在，需 fallback 查詢 Users 表 |
| DEL | tradegameservice / productservice | 使用者狀態變更（如 Enabled 由 1→0、Rank 變更、SubEndTime 更新）或使用者登出時 | 主動失效，確保資料一致性 |

**⚠️ 注意**：
- 任何變更 Users 表中 Enabled、Rank、SubEndTime 的服務（包括 productservice 的管理後台操作）都必須主動 DEL 該使用者的快取鍵。
- tradegameresultservice 等服務若讀取使用者狀態，應優先查詢此快取，若不存在再查 DB，不可直接報錯。

### `stock:rules:enabled`

**用途**：快取全局啟用中的規則清單，供規則引擎快速讀取。

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | tradegameservice | 規則引擎啟動或快取過期後從 DB 載入 | TTL：300 秒 |
| GET | tradegameservice / mqservice / tradegameresultservice | 規則匹配時讀取 | 若快取未命中，須查詢 Rules 表（附加 Enabled=1） |
| DEL | productservice / tradegameservice | 規則變更（新增、修改、啟用/停用）時 | 主動失效，可透過管理後台手動觸發或排程清除 |

**⚠️ 注意**：
- 規則管理後台（productservice）在變更 Rules 表任何記錄（尤其 Enabled、Parameter、Type 等）後，**必須**執行 `DEL stock:rules:enabled`，否則其他服務可能繼續使用過期快取。
- 若快取刪除失敗（例如網路問題），可仰賴 TTL 自然過期，但可能導致短暫不一致。

---

## 常見錯誤（跨服務）

- ❌ **未過濾 `Users.Enabled=1` 進行操作** → 所有服務在進行使用者驗證、交易、發送通知前，必須強制加上 `Enabled=1` 條件，否則停用帳號仍可進行操作。
- ❌ **直接回傳 `Users.Password` 或 `Users.Phone`、`Users.Email` 完整內容給前端** → 密碼欄位在任何情況下都不可回傳；Phone、Email 需依場景遮罩或限制回傳範圍。
- ❌ **非管理後台的服務直接修改 `Users.Enabled`、`Users.Rank`** → 只有 productservice 的管理後台或明確的排程流程可以變更這些欄位，其他服務（如 tradegameservice）不可直接 UPDATE。
- ❌ **寫入 `FavoriteStock.Value` 或 `FavoriteRule.Value` 時未驗證 JSON 格式** → 可能造成後續解析錯誤，必須在服務端驗證。
- ❌ **查詢 `MessageLog` 時未帶 `Date` 分區鍵，導致全表掃描** → 所有查詢必須包含 `Date` 條件，否則效能會極差。
- ❌ **`MessageLog` 寫入者過多，權責不清** → ⚠️ 需釐清哪些服務真正負責寫入 messagelog，避免重複寫入或競爭。目前 mqservice、tradegameservice、tradegameresultservice、productservice 皆有寫入權限，可能導致記錄混亂。
- ❌ **變更 `Rules` 表後未清除 `stock:rules:enabled` 快取** → 導致規則引擎使用過期的規則清單。
- ❌ **使用者訂閱到期（`SubEndTime < NOW()`）後未禁用相關功能** → 服務必須在每次操作前檢查 `SubEndTime`，過期用戶應限制操作。
- ❌ **跨服務直接操作 `FavoriteRule.FirstMatch` 或 `NeedSend` 欄位** → 這些欄位應主要由 tradegameservice 排程維護，其他服務手動修改可能造成重複發送或漏發，需有嚴格控制。

---