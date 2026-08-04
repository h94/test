# feedback DB — 完整使用脈絡

> 產出時間：2025-09-16 16:00
> 欄位結構定義：[feedback.json](./feedback.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| feedbackservice | owner | 讀、寫、刪（所有 Table） |
| livechatservice | writer & reader | 讀、寫（⚠️ 衝突待人工，具體操作範圍待確認：livechatservice 對 feedback keyspace 有寫入權限，但各表操作細節尚未定義，詳見各表跨服務限制） |
| pricebackendservice | reader | 讀取 feedbacks_sport, feedbacks_stock, topics_sport, topics_stock, questions_sport, questions_stock |
| pricecentersite | reader | 讀取 topics_sport, topics_stock, questions_sport, questions_stock（僅用於前台顯示主題分類、常見問題） |

---

## Table：businessmessages

**完整名稱**：`feedback.businessmessages`  
**Primary Key**：(site) clustering: (datetime, id)  
**備註**：所有 id 由系統自動生成，API 不得指定或覆蓋。

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
 feedbackservice     feedbackservice
      INSERT              UPDATE
     status=0 ────────→ status=1
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未回覆 | feedbackservice | INSERT 時預設值 |
| 1 | 已回覆 | feedbackservice | 管理員透過後台提交回覆內容後 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT status=0 | 收到新商業訊息 | 預設未回覆 |
| feedbackservice | UPDATE status=1 | 管理員填寫 respcontent 後 | 只能由 0→1，不可反向 |

**⚠️ 跨服務限制**：

- 僅 feedbackservice 可寫入，其他服務無法操作此欄位。
- status 僅允許值 0 或 1，任何其他值將被拒絕。
- ⚠️ livechatservice 對本表的讀寫規則待確認，目前不應進行任何直接操作。

---

### site 欄位

**型別**：text

**值定義**：站點代碼，用於區分不同產品線的商業訊息。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| sport | 運動站點 | feedbackservice | 寫入時由 API 帶入，需通過枚舉校驗 |
| stock | 股票站點 | feedbackservice | 同運動站點 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE site | 建立或修改訊息時 | 必須為 `sport` 或 `stock`，否則拒絕寫入 |

**⚠️ 跨服務限制**：

- 站點代碼嚴格限於 `sport`、`stock`，不可擴充或接受其他值。

---

### datetime 欄位

**型別**：text

**說明**：訊息建立時間，格式如 `2023-09-19 10:19`。由系統自動填入當前時間，不接受 API 傳入值。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT datetime | 建立訊息時 | 系統自動產生，API 傳入值將被忽略 |

---

### updatetime 欄位

**型別**：bigint

**說明**：最後更新時間的 Unix timestamp（秒）。每次對該筆記錄進行任何修改時，系統會自動刷新。不接受 API 傳入。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | UPDATE updatetime | 任何更新發生時 | 系統自動設定，API 傳入值無效 |

---

### respcontent 欄位

**型別**：text

**說明**：管理員針對此商業訊息的回覆內容。僅管理後台可寫入。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | UPDATE respcontent | 管理員提交回覆時 | 同時更新 status 為 1 |

---

### 其他欄位

- **sendcontent**：發送者輸入的訊息內容，由 API 傳入。
- **sendermail**：發送者留下的聯絡信箱，格式需驗證。
- **id**：系統自動產生的唯一識別碼，不可手動指定。

⚠️ **livechatservice 對 businessmessages 的操作待補充**，目前不可進行任何 INSERT/UPDATE/DELETE。

---

## Table：feedbacks_sport

**完整名稱**：`feedback.feedbacks_sport`  
**Primary Key**：(tid) clustering: (datetime, account, id)  
**備註**：id、account 等欄位由系統管理，API 不可覆蓋。

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
 feedbackservice     feedbackservice     feedbackservice
      INSERT              UPDATE              UPDATE
     status=0 ────────→ status=1 ────────→ status=2
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未處理 | feedbackservice | INSERT 時預設值 |
| 1 | 已處理 | feedbackservice | 管理員查看或回覆後 |
| 2 | 已結案 | feedbackservice | 管理員標記結案 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT status=0 | 用戶提交反饋 | 預設未處理 |
| feedbackservice | UPDATE status=1 | 管理員第一次處理（加入回覆或查看） | 只能由 0→1 |
| feedbackservice | UPDATE status=2 | 管理員確認結案 | 只能由 1→2，不可直接從 0→2 |
| pricebackendservice | SELECT status | 後台查詢反饋狀態 | 用於報表或客服 |

**⚠️ 跨服務限制**：

- 狀態必須嚴格遞進，不可跳級或降級（例如 2→1 或 0→2 皆不被允許）。
- 任何服務均不得直接設定 status 值，必須由業務邏輯依照流程變更。
- ⚠️ livechatservice 對本表的讀寫規則待確認，目前不應進行任何寫入；若有讀取需求需確認 WHERE 條件。

---

### tid 欄位

**型別**：text

**說明**：對應至 `topics_sport.id`，表示該反饋所屬的主題分類。為 partition key，所有查詢必須提供此欄位。

**值定義**：必須存在於 `topics_sport` 且該主題的 `enabled = 1`。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE tid | 建立或變更反饋主題時 | 寫入前驗證主題存在且啟用，否則拒絕寫入 |
| pricebackendservice | SELECT tid | 後台查詢反饋分類 | 用於報表 |
| pricecentersite | — | — | 不直接操作此表 |

---

### problem 欄位

**型別**：list<text>

**說明**：用戶提交的問題內容清單。存入前須將每項序列化為 JSON 字串，格式為 `{"DateTime":"...","Message":"..."}`，若反序列化失敗則拒絕寫入。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE problem | 用戶提交或管理員補充問題 | 存入前需完成序列化校驗 |
| pricebackendservice | SELECT problem | 後台查看反饋內容 |  |

---

### respcontent 欄位

**型別**：list<text>

**說明**：管理員回覆內容列表，格式同 problem（JSON 字串列表）。僅管理後台可寫入，普通用戶 API 無權修改。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | UPDATE respcontent | 管理員透過後台回覆 | 寫入前需序列化校驗，並同時推進 status 狀態 |
| pricebackendservice | SELECT respcontent | 後台查看回覆記錄 |  |

---

### adminimgpath 欄位

**型別**：list<text>

**說明**：管理員上傳的圖片路徑列表，僅能由管理後台 API `UpdateSportFeedbackMessageRespImage` 更新。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | UPDATE adminimgpath | 管理員上傳圖片後 | 普通用戶 API 不可寫入 |
| pricebackendservice | SELECT adminimgpath | 後台查詢附件 |  |

---

### imgpath 欄位

**型別**：list<text>

**說明**：使用者建立反饋時可上傳的圖片路徑列表，需為有效的路徑字串。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT imgpath | 用戶提交反饋時 | 可選，非必填；不可後續由使用者修改 |
| pricebackendservice | SELECT imgpath | 後台查看用戶上傳圖片 |  |

---

### datetime / updatetime 欄位

| 欄位 | 型別 | 說明 |
|------|------|------|
| datetime | text | 建立時間，由系統自動填入，不接受 API 傳入 |
| updatetime | bigint | 最後更新時間戳，任何修改時自動刷新，API 傳入值無效 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| feedbackservice | INSERT datetime / UPDATE updatetime | 系統自動處理 |
| pricebackendservice | SELECT datetime, updatetime | 查詢時間資訊用於報表 |

---

## Table：feedbacks_stock

**完整名稱**：`feedback.feedbacks_stock`  
**Primary Key**：(id)  
**備註**：與 `feedbacks_sport` 結構相似，但主鍵僅為 id，無 clustering columns。

### status 欄位

**型別**：int

**值定義與狀態流轉**：同 `feedbacks_sport.status`（0→1→2）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT status=0 | 用戶提交反饋 | 預設未處理 |
| feedbackservice | UPDATE status=1 | 管理員第一次處理 | 只能由 0→1 |
| feedbackservice | UPDATE status=2 | 管理員確認結案 | 只能由 1→2 |
| pricebackendservice | SELECT status | 後台查詢狀態 |  |

---

### tid 欄位

**型別**：text

**說明**：對應 `topics_stock.id`，表示主題分類。寫入前需確認主題存在且啟用。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE tid | 建立或變更主題 | 寫入前驗證主題存在且 enabled=1 |
| pricebackendservice | SELECT tid | 後台查詢 |  |
| pricecentersite | — | — | 不直接操作此表 |

---

### problem 欄位

**型別**：list<text>

**說明**：與 `feedbacks_sport.problem` 相同，需 JSON 序列化校驗。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE problem | 用戶提交或管理員補充 | 序列化校驗 |
| pricebackendservice | SELECT problem | 後台查看問題內容 |  |

---

### respcontent 欄位

**型別**：list<text>

**說明**：回覆內容，僅管理後台可寫入。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | UPDATE respcontent | 管理員回覆 | 同時推進 status |
| pricebackendservice | SELECT respcontent | 後台查看 |  |

---

### adminimgpath / imgpath 欄位

**型別**：list<text>（兩者相同）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE | 管理員上傳或用戶上傳 |  |
| pricebackendservice | SELECT | 後台查看圖片 |  |

---

### datetime / updatetime 欄位

同 `feedbacks_sport`，由系統自動管理。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| feedbackservice | 自動寫入 |  |
| pricebackendservice | SELECT | 用於時間查詢 |

---

## Table：questions_sport

**完整名稱**：`feedback.questions_sport`  
**Primary Key**：(id)  
**備註**：id 由系統生成，不可手動指定。

### enabled 欄位

**型別**：int

**值定義**：0 = 停用，1 = 啟用。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE enabled | 管理後台新增或異動問題 | 僅後台 API 可修改；用戶端查詢時僅回傳 enabled=1 的項目 |
| pricebackendservice | SELECT enabled | 後台查詢常見問題狀態 |  |

---

### sort 欄位

**型別**：int

**值定義**：排序順序，數值越小越靠前。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE sort | 管理後台調整排序 | 用戶端不可修改 |
| pricebackendservice | SELECT sort | 查詢排序 |  |

---

### question / answer 欄位

**型別**：map<text, text>

**說明**：多語言內容，key 為語系代碼（如 `zh-TW`、`en-US`），value 為對應語言的文字。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE question, answer | 管理後台編輯常見問題 | 語系代碼必須合法，寫入前校驗 |
| pricebackendservice | SELECT question, answer | 後台查看常見問題內容 |  |

---

### tid 欄位

**型別**：text

**說明**：關聯的主題 ID，用於將問題歸類至某個 `topics_sport`。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE tid | 管理後台設置關聯主題 |  |
| pricebackendservice | SELECT tid | 後台查詢 |  |

---

## Table：questions_stock

**完整名稱**：`feedback.questions_stock`  
**Primary Key**：(id)

### enabled / sort 欄位

規則與 `questions_sport` 完全相同，僅管理後台可修改。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE | 管理後台操作 |  |
| pricebackendservice | SELECT | 後台查詢狀態或排序 |  |
| pricecentersite | SELECT enabled=1, sort | 前台查詢常見問題 | 只取啟用中的問題，依 sort 排序 |

---

### question / answer 欄位

**型別**：text（單語言）

**說明**：股票反饋的常見問題僅支援單一語言文字，不採用 map。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE | 管理後台編輯 |  |
| pricebackendservice | SELECT | 後台查看問題內容 |  |
| pricecentersite | SELECT | 前台顯示問題與答案 |  |

---

## Table：topics_sport

**完整名稱**：`feedback.topics_sport`  
**Primary Key**：(id)

### enabled 欄位

**型別**：int

**值定義**：0 = 停用，1 = 啟用。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE enabled | 管理後台新增或開關主題 | 停用的主題不會出現在用戶端選項中 |
| pricebackendservice | SELECT enabled | 後台查詢主題狀態 |  |
| pricecentersite | SELECT enabled=1 | 前台查詢主題分類 | 僅回傳啟用中的主題供用戶選擇反饋類別 |

---

### sort 欄位

**型別**：int

**值定義**：排序順序，影響用戶端顯示順序。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE sort | 管理後台修改排序 |  |
| pricebackendservice | SELECT sort | 後台查詢排序 |  |
| pricecentersite | SELECT sort | 前台顯示主題列表時使用 | 依 sort 升冪排列 |

---

### name 欄位

**型別**：map<text, text>

**說明**：多語言主題名稱，key 為語系代碼，value 為名稱字串。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE name | 管理後台編輯主題名稱 | 語系代碼需合法 |
| pricebackendservice | SELECT name | 後台查看主題名稱 |  |
| pricecentersite | SELECT name | 前台顯示主題名稱 | 依使用者語系選擇對應語言 |

---

## Table：topics_stock

**完整名稱**：`feedback.topics_stock`  
**Primary Key**：(id)

### enabled / sort 欄位

規則與 `topics_sport` 相同。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE | 管理後台操作 |  |
| pricebackendservice | SELECT | 後台查詢 |  |
| pricecentersite | SELECT enabled=1, sort | 前台查詢啟用中的主題 | 依 sort 升冪排列顯示 |

---

### name 欄位

**型別**：text

**說明**：股票反饋主題名稱，僅支援單一語言文字。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| feedbackservice | INSERT / UPDATE | 管理後台編輯 |  |
| pricebackendservice | SELECT | 後台查看名稱 |  |
| pricecentersite | SELECT name | 前台顯示主題名稱 |  |

---

## Redis — 無

本 DB 不使用 Redis 快取。

---

## 常見錯誤（跨服務）

由於 feedback DB 主要只有 feedbackservice 寫入，pricebackendservice 與 pricecentersite 僅讀取，跨服務寫入衝突較少，但仍須注意以下操作錯誤：

- ❌ 在 `feedbacks_sport` 查詢時未帶入 `tid`（partition key） → 應強制要求 `tid` 參數，或改用 `id` 主鍵查詢，避免全表掃描。
- ❌ 直接將 `feedbacks_sport.status` 或 `feedbacks_stock.status` 由 0 跳至 2 → 狀態必須依序遞進，後端邏輯應攔截非法變更。
- ❌ 寫入 `feedbacks_sport.tid` 或 `feedbacks_stock.tid` 前未檢查對應主題是否存在且啟用 → 應先校驗 `topics_*.id` 的 enabled 狀態。
- ❌ 提交 `problem` 或 `respcontent` 時未將內容序列化為正確的 JSON 字串 → 後端須在儲存前驗證格式，並拒絕不符的請求。
- ❌ 嘗試由普通用戶 API 寫入 `respcontent` 或 `adminimgpath` → 這類欄位僅限管理後台 API，權限管控必須落實。
- ❌ 手動設定 `datetime` 或 `updatetime` → 這些欄位一律由系統自動產生與更新，API 傳入值應被忽略，避免時間不一致。
- ❌ 在 `businessmessages` 中寫入 site 值為 `sport` 以外的字串 → 寫入前需通過枚舉校驗，確保只接受已定義的站點代碼。
- ❌ 未過濾 `topics_sport.enabled=0` 或 `topics_stock.enabled=0` 的主題即顯示給用戶 → 查詢時應加上 `enabled=1` 條件（pricecentersite 查詢 topics 時需特別注意）。
- ❌ pricebackendservice 或 pricecentersite 試圖寫入任何 feedback 表 → 這兩個服務僅有 SELECT 權限，任何 INSERT / UPDATE / DELETE 都將被拒絕。
- ❌ pricebackendservice 或 pricecentersite 查詢時未考慮分頁或 partition key → 可能導致全表掃描，影響效能，需優化查詢條件。
- ⚠️ **livechatservice 角色衝突**：服務摘要指出 livechatservice 對 Cassandra feedback 有 writer & reader 權限，但現有文件未定義其操作範圍。所有對於 feedback 表的寫入規則（如 status 流轉、必填校驗、序列化等）必須在 livechatservice 實作時同步確認，避免越權寫入或破壞業務邏輯。建議由資深工程師審核後，明確定義 livechatservice 可操作的表、欄位、以及與 feedbackservice 的職責邊界。