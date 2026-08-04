# community DB — 完整使用脈絡

> 產出時間：2026-05-30 15:00  
> 欄位結構定義：[community.json](./community.json)  
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| communityservice | owner | 讀、寫、刪（對 newlottery_forums 所有欄位；控制 status 切換） |
| gameliveservice | writer | 讀取、插入新論壇、更新部分欄位（names, edit_timestamp）；不可修改 status、country_code、icon 欄位（創建時可設定初始值） |
| pricebackendservice | reader | 僅 SELECT，常用於後台數據查詢與匯出 |
| pricecentersite | reader / writer（⚠️ 衝突待人工） | 前台 API 僅 SELECT；後台管理 API 可執行 INSERT / UPDATE（需與 communityservice 權責劃分確認） |

> ⚠️ 衝突待人工：  
> - `pricecentersite` 的角色從 reader 變更為 reader / writer，其後台管理 API 可寫入，但前台 API 僅讀取。需確認與 `communityservice` 的權責劃分，避免重複寫入或競爭狀況。

---

## Table：newlottery_forums

### id 欄位

**型別**：text

**值定義與狀態流轉**：  
主鍵，建立後即不可變更（immutable），由插入該記錄的服務設定一次後鎖定。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 任意唯一文字 | 論壇唯一識別碼 | communityservice, gameliveservice, pricecentersite（後台） | INSERT 時產生或指定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| communityservice | INSERT | 後台建立論壇 | 產生或指定唯一識別碼 |
| gameliveservice | INSERT | 遊戲直播等場景觸發建立關聯論壇 | 產生或指定 id，寫入後不可變更 |
| pricecentersite | INSERT | 後台管理 API 建立論壇 | 產生或指定 id，建立後不可變更 |
| communityservice | SELECT WHERE id = ? | 查詢特定論壇 | 一般讀取 |
| gameliveservice | SELECT WHERE id = ? | 讀取特定論壇資訊 | 用於顯示關聯內容 |
| pricebackendservice | SELECT WHERE id = ? | 後台查詢或匯出 | 透過 id 定位特定論壇 |
| pricecentersite | SELECT WHERE id = ? | 前台或後台查詢論壇 | - |

**⚠️ 跨服務限制**：
- 任何服務都不可對已存在的 `id` 執行 UPDATE 或 DELETE。
- `gameliveservice` 和 `pricecentersite` 插入時應確保 `id` 在全表唯一，避免主鍵衝突。

---

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
         communityservice/pricecentersite    communityservice/pricecentersite
         INSERT (status=0)                     UPDATE status=1
     ┌─→ status=0 (隱藏) ──────────────────────────→ status=1 (啟用)
     │          │                                         │
     │          │ communityservice/pricecentersite        │
     │          │ UPDATE status=0 (隱藏)                  │
     │          └─────────────────────────←──────────────┘
     │                    (可從啟用回到隱藏)
     │
     │ communityservice/pricecentersite
     │ UPDATE status=2
     └──────────→ status=2 (封存)
```

> **補充說明**：  
> - `gameliveservice` 僅能在 INSERT 時設定 status=0，**嚴禁**之後進行任何 `UPDATE status` 操作。  
> - `communityservice` 與 `pricecentersite` 可執行所有狀態轉換，但必須在業務流程上避免衝突。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 隱藏（不對前台顯示） | gameliveservice (僅 INSERT), communityservice, pricecentersite（後台） | INSERT 預設值；或後台手動設為隱藏 |
| 1 | 啟用（前台正常顯示） | communityservice, pricecentersite（後台） | 後台審核後啟用 |
| 2 | 封存（歸檔，不可顯示於前台，僅後台保留） | communityservice, pricecentersite（後台） | 後台手動設定（通常不可還原） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| communityservice | INSERT status=0 | 後台建立論壇 | 預設隱藏，由後台確認後啟用 |
| communityservice | UPDATE status=1 | 管理員啟用 | 前台可查詢到此論壇 |
| communityservice | UPDATE status=0 | 管理員隱藏 | 前台不可查詢到此論壇 |
| communityservice | UPDATE status=2 | 管理員封存 | 封存後僅後台可見 |
| communityservice | SELECT status IN (0,1,2) | 後台管理查詢 | 全部論壇 |
| gameliveservice | INSERT status=0 | 建立關聯論壇 | 預設隱藏，等待後台審核；不可擅自設為 1 或 2 |
| gameliveservice | SELECT WHERE status=1 | 讀取啟用的論壇 | 關聯顯示 |
| gameliveservice | SELECT status IN (0,1,2) | 其後台功能（若有） | 可能查詢全部 |
| pricebackendservice | SELECT WHERE status=1 | 後台特定功能（非管理後台） | 僅回傳啟用論壇，避免匯出隱藏資料 |
| pricebackendservice | SELECT status IN (0,1,2) | 特殊管理需求 | 需更高權限，通常用於資料審計 |
| pricecentersite | INSERT status=0 | 後台 API 建立論壇 | 預設隱藏，須後續審核 |
| pricecentersite | UPDATE status=1 | 後台 API 啟用 | 前台可查詢 |
| pricecentersite | UPDATE status=0 | 後台 API 隱藏 | 前台不可查詢 |
| pricecentersite | UPDATE status=2 | 後台 API 封存 | 歸檔處理 |
| pricecentersite | SELECT status IN (0,1,2) | 後台管理查詢 | 視權限顯示全部 |
| pricecentersite | SELECT WHERE status=1 | 前台 API | 僅回傳啟用論壇 |

**⚠️ 跨服務限制**：
- `status` 欄位的寫入權限同時開放給 `communityservice` 與 `pricecentersite`（後台 API）；必須確保業務流程明確（例如誰負責審核啟用），避免競爭條件或重複操作。
- `gameliveservice` 可 INSERT 時設定 `status=0`，但**嚴禁**執行任何 `UPDATE status` 操作（含直接設定為 0、1、2 或任何其他值）。
- `pricecentersite` 的前台 API 一律只能 `SELECT status=1`，不可寫入。
- `pricebackendservice` 預設僅 SELECT `status=1` 的論壇，除非具有特殊管理權限才可讀取全部狀態。

---

### country_code 欄位

**型別**：text（可為 null）

**值定義**：  
論壇所屬國家代碼（如 `US`、`TW`），`null` 表示不限制國家。

| 服務 | 操作 | 說明 |
|------|------|------|
| communityservice | INSERT / UPDATE | 後台建立或修改國家代碼 |
| gameliveservice | INSERT（僅建立時） | 建立論壇時可指定國家代碼；⚠️ **禁止**後續 UPDATE |
| pricecentersite | INSERT / UPDATE（後台） | 後台 API 建立論壇時設定國家代碼，後續一般不可變更（例外需審核） |
| pricecentersite | SELECT WHERE country_code = ? | 前台依國家篩選顯示論壇 |
| pricebackendservice | SELECT WHERE country_code = ? | 後台數據篩選與匯出 |

**⚠️ 注意**：
- `null` 表示通用（不限國家）；前端需正確提示。
- `gameliveservice` **不可**在建立後修改 `country_code`，此權限僅限管理後台（communityservice, pricecentersite 後台 API）。
- `pricecentersite` 後續不應透過一般 API 變更 `country_code`，若需修改須走特殊審核流程。

---

### names 欄位

**型別**：map<text, text>

**值定義**：
- key：語言代碼（如 `zh-TW`、`en-US`）
- value：該語言對應的論壇名稱

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| communityservice | INSERT / UPDATE | 後台管理多語言名稱，避免遺失其他語系 |
| gameliveservice | INSERT / UPDATE | 建立或更新論壇時設定／修改多語言名稱；更新時必須使用 `UPDATE ... SET names['key'] = 'value'` 方式逐 key 更新，**嚴禁**直接覆蓋整個 map，以避免遺失其他語系；不可出現空值 |
| pricecentersite | INSERT / UPDATE | 後台編輯 API 寫入或修改多語言名稱，應逐 key 更新，避免覆蓋整個 map |
| pricecentersite | SELECT | 前台根據使用者語言選取對應名稱 |
| pricebackendservice | SELECT | 後台列表可能需要預設語言（如 `en-US`），或用於匯出多語系資料 |

**⚠️ 注意**：
- 若查詢時使用者語言對應的 key 不存在，前端應有 fallback 機制（例如顯示第一個可用的名稱，或顯示預留字串）。
- `gameliveservice` 和 `pricecentersite` 更新時若造成既有語言 key 遺失，將導致前端顯示異常，需嚴格遵循「只更新指定 key」的原則。
- `pricebackendservice` 讀取時可能需要一次取得所有語言版本，用於後台報表或管理。

---

### icon 欄位

**型別**：text（可為 null）

**值定義**：圖示的 URL 或代碼。

| 服務 | 操作 | 說明 |
|------|------|------|
| communityservice | INSERT / UPDATE | 管理員設定圖示 |
| gameliveservice | INSERT（僅建立時） | 建立論壇時可設定初始 icon；⚠️ **禁止**後續 UPDATE |
| pricecentersite | INSERT / UPDATE | 後台上傳或更換圖示 |
| pricecentersite | SELECT | 前台顯示論壇圖示 |
| pricebackendservice | SELECT | 後台查詢或匯出時可能讀取圖示 URL |

**⚠️ 注意**：
- 可為 `null`，前端應提供預設圖示。
- `gameliveservice` 不具備管理員權限，因此只能於 INSERT 時設定 icon，不得更新。

---

### edit_timestamp 欄位

**型別**：bigint（儲存 Unix 毫秒時間戳，UTC）

**值定義**：記錄最後一次寫入操作的時間戳，由系統自動設定，不可手動指定。

| 服務 | 操作 | 說明 |
|------|------|------|
| communityservice | INSERT / UPDATE 時自動寫入 | 任何欄位變更時設為當前 UTC 毫秒時間戳 |
| gameliveservice | INSERT / UPDATE 時必須同步更新 | 每次對本筆記錄的任一欄位進行 INSERT 或 UPDATE 時，都必須將此欄位更新為當前毫秒時間戳，不可手動設定非當前時間 |
| pricecentersite | INSERT / UPDATE 時自動寫入 | 後台寫入操作時由系統自動更新，不可手動設定 |
| pricebackendservice | SELECT | 判斷資料最後異動時間，用於增量同步或審計 |

**⚠️ 注意**：
- 所有服務必須以 **UTC 時間戳**寫入；前端顯示時再由客戶端轉換為當地時間。
- 若僅執行 SELECT 操作，則不需更新此欄位。

---

## Redis — （無）

目前 community keyspace 沒有快取機制。若後續加入快取，建議命名空間前綴為 `community:forum:{forumId}`。

---

## 常見錯誤（跨服務）

- ❌ `gameliveservice` 直接修改 `status` 為 1、2 或任意值 → 僅 `communityservice` 或 `pricecentersite`（後台）可變更狀態；`gameliveservice` 僅能在 INSERT 時設為 0，之後嚴禁任何 UPDATE。
- ❌ `gameliveservice` 嘗試 UPDATE `country_code` 或 `icon` → 建立後這些欄位僅管理後台可變更；`gameliveservice` 只能於 INSERT 時設定初始值。
- ❌ `gameliveservice` 在更新 `names` 時直接覆蓋整個 map → 應使用 `UPDATE ... SET names['key'] = 'value'` 方式逐 key 更新，避免遺失其他語系。
- ❌ `gameliveservice` 建立論壇時忘記設置 `status=0` 或誤設為 1 → 必須設為 0，並填入正確的 `edit_timestamp`。
- ❌ 任何寫入操作後未更新 `edit_timestamp` → 導致後台或報表無法判斷最後異動時間。
- ❌ 任一服務直接對記錄執行 DELETE → 此表目前無刪除機制，僅透過 `status` 隱藏或封存。
- ❌ `pricecentersite` 前台 API 直接執行 INSERT / UPDATE → 前台僅有 SELECT 權限，寫入必須透過後台管理 API。
- ❌ `pricecentersite` 後台更新 `country_code` 未走審核 → 國家代碼建立後一般不可變更，除非特殊流程。
- ❌ `pricecentersite` 後台寫入 `names` 時覆蓋整個 map → 應逐 key 更新。
- ❌ `pricecentersite` 或 `communityservice` 後台在未協調的情況下同時變更同一筆記錄的 `status` → 可能導致非預期的狀態切換或覆蓋，需制定明確的業務責任歸屬。
- ❌ `gameliveservice` 嘗試變更已存在的 `id` → `id` 不可變更。
- ❌ `pricebackendservice` 在無特殊權限下 SELECT `status=0` 或 `status=2` 的資料 → 應遵守讀取權限，僅讀取 `status=1` 的論壇。