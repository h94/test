# ads DB — 完整使用脈絡

> 產出時間：2025-06-30 10:30  
> 欄位結構定義：[ads.json](./ads.json)  
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| advertisingservice | owner | 讀、寫、刪 |
| webpservice | owner / writer / reader ⚠️衝突 | 讀、寫、刪；寫入權限與 advertisingservice 重疊 |
| productservice | owner ⚠️衝突 | 讀、寫、刪；舊版文件宣稱為 owner，本次摘要亦具寫入權限，多服務寫入可能衝突 |
| communityservice | reader | 唯讀 |
| pricecentersite | reader | 唯讀 |
| livechatservice | reader | 唯讀 |
| newlotterysite | reader | 唯讀 |

---

## Table：advertising

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     advertisingservice / webpservice / productservice
            INSERT (enabled=1)
                │
                ▼
          ┌──────────────┐
          │   enabled=1   │ ◄── 啟用狀態（預設）
          └──────┬───────┘
                 │ UPDATE (enabled=0)
                 ▼
          ┌──────────────┐
          │   enabled=0   │ ◄── 禁用狀態
          └──────────────┘
                 │ UPDATE (enabled=1)
                 ▼
          ┌──────────────┐
          │   enabled=1   │ ◄── 重新啟用
          └──────────────┘
```
> ⚠️ 狀態之間可雙向轉換，但僅限特定啟用／停用 API，不可透過一般 UPDATE 直接設定。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 禁用 | advertisingservice / webpservice / productservice | 後台停用廣告（特定 API） |
| 1 | 啟用 | advertisingservice / webpservice / productservice | INSERT 時預設值，或後台啟用廣告（特定 API） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT enabled=1 | 建立廣告 | 預設啟用 |
| advertisingservice | UPDATE enabled=0/1 | 後台啟用／停用 API | 僅能透過 `/ad/enable/{id}` 或 `/ad/disable/{id}` 變更 |
| webpservice | INSERT enabled=1 | 管理後台建立廣告 | 預設啟用 |
| webpservice | UPDATE enabled=0/1 | 後台啟用／停用 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT enabled=1 | 後台廣告管理 | 前端不可直接修改啟用狀態 |
| productservice | UPDATE enabled=0/1 | 後台啟用／停用 API | 僅後台廣告管理 API 可寫入（⚠️衝突） |
| communityservice | SELECT WHERE enabled=1 | 查詢啟用中的廣告 | 對外一律過濾啟用狀態 |
| pricecentersite | SELECT WHERE enabled=1 | 前台廣告展示 | 僅回傳啟用廣告 |
| livechatservice | SELECT WHERE enabled=1 | 聊天頁廣告展示 | 僅回傳啟用廣告 |
| newlotterysite | SELECT WHERE enabled=1 | 廣告查詢 | 同時需滿足時間範圍條件 |

**⚠️ 跨服務限制**：
- 只有 advertisingservice、webpservice 與 productservice 可修改 `enabled`，其他服務僅能讀取且必須加 `enabled=1` 條件。
- ⚠️ 三個寫入服務可能發生競態寫入，需透過分散式鎖或明確責任歸屬解決。

---

### starttime 欄位

**型別**：bigint（Unix 時間戳，秒級，UTC）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改廣告 | 強制校驗 `starttime < closetime`；若 `closetime` 早於當前時間，新增時應拒絕 |
| webpservice | INSERT / UPDATE | 後台設定廣告開始時間 | 同 advertisingservice，須校驗（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台廣告管理 | 校驗 `starttime < closetime`（⚠️衝突） |
| communityservice | SELECT | 過濾目前有效廣告 | 條件：`starttime <= NOW() < closetime` |
| pricecentersite | SELECT | 前台廣告展示 | 同上，確保只顯示時間範圍內的廣告 |
| livechatservice | SELECT | 聊天頁廣告展示 | 同上 |
| newlotterysite | SELECT | 廣告查詢 | 條件：`starttime <= UNIX_TIMESTAMP(NOW()) <= closetime` |

**⚠️ 跨服務限制**：
- 各服務對時間戳單位必須一致（秒級），若某服務內部使用毫秒級 epoch，需轉換後再比對。
- `starttime` 值不得大於 `closetime`，寫入前需校驗。

---

### closetime 欄位

**型別**：bigint（Unix 時間戳，秒級，UTC）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改廣告 | 強制校驗 `closetime > starttime` |
| webpservice | INSERT / UPDATE | 後台設定廣告結束時間 | 同 advertisingservice，需校驗（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台廣告管理 | 校驗 `starttime < closetime`（⚠️衝突） |
| communityservice | SELECT | 過濾條件 `NOW() < closetime` | 超過結束時間的廣告不應顯示 |
| pricecentersite | SELECT | 過濾條件 `NOW() < closetime` | 同上 |
| livechatservice | SELECT | 過濾條件 `NOW() < closetime` | 同上 |
| newlotterysite | SELECT | 時間範圍過濾 | 與 starttime 共同決定廣告有效期 |

**⚠️ 跨服務限制**：
- 若 `closetime` 早於當前時間，任何 SELECT 查詢都不應回傳該記錄；寫入時應避免建立已過期的廣告。

---

### lang 欄位

**型別**：text

**值定義**：以 `&` 分隔的語言代碼組合，例如 `zh-TW&en-US`；空字串表示全語言適用。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改廣告 | 僅允許寫入預定義的語言代碼，禁止非法值；格式須為 `&` 分隔字串 |
| webpservice | INSERT / UPDATE | 後台設定語言 | 前端傳入單一語言代碼，服務端組合成 `&` 分隔字串後寫入，需驗證代碼合法性（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台廣告管理 | 應遵守相同規則（⚠️衝突） |
| communityservice | SELECT | 篩選語言 | 檢查 `lang` 是否為空或包含請求語系代碼 |
| pricecentersite | SELECT | 同 communityservice | 若無匹配語言則不回傳該廣告 |
| livechatservice | SELECT | 同 communityservice | 依請求語言過濾 |
| newlotterysite | SELECT ⚠️ 待人工確認 | 依請求語言過濾 | 應檢查 `lang` 是否匹配；若無匹配語言應不回傳（部分服務可能交由前端過濾，此處需人工確認） |

**⚠️ 跨服務注意**：
- webpservice 與 productservice 對語言過濾的實現方式可能存在差異（服務端過濾 vs. 前端過濾），為避免遺漏或重複，建議統一由服務端在 SELECT 時進行語言匹配。

---

### seq 欄位

**型別**：int

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或排序調整 | 同一 `type` 內 `seq` 不可重複 |
| webpservice | INSERT / UPDATE | 後台設定排序 | 同 advertisingservice，需確保同 type 不重複（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定排序 | 同 advertisingservice（⚠️衝突） |
| pricecentersite | SELECT | 前台顯示 | 查詢結果依 `seq` 遞增排序 |
| livechatservice | SELECT | 聊天頁顯示 | 同 `seq` 遞增排序 |
| newlotterysite | SELECT | 廣告排序 | 依 `seq` 遞增排序 |

---

### createdby 欄位

**型別**：text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立廣告（`CreateAds`） | 僅首次寫入，後續更新不可修改 |
| webpservice | INSERT | 管理後台建立廣告 | 由後台自動設定（例如操作者），不可由前端傳入（⚠️衝突） |
| productservice | INSERT | 後台廣告建立 | 僅系統內部寫入，前端不可指定或修改（⚠️衝突） |
| pricecentersite | SELECT | – | **不可回傳**，僅內部管理資訊 |
| livechatservice | SELECT | – | **不可回傳** |
| newlotterysite | — | — | **禁止選取此欄位**，對外 API 不得暴露 |

---

### id 欄位（主鍵）

**型別**：text (PK)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立廣告 | 應用層生成（建議 UUID），**API 不可傳入自訂值**；建立後不可修改 |
| webpservice | INSERT | 建立廣告 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT | 建立廣告 | 同 advertisingservice（⚠️衝突） |
| newlotterysite | SELECT | – | 僅作識別用途，無特別限制 |

---

### 其他欄位

- **type**：僅限後台從預定義類型中選取寫入（如 `right`），API 不可任意代入新值。由 advertisingservice、webpservice、productservice 寫入時需校驗枚舉。
- **action**：廣告點擊行為，須為系統支援的枚舉值（如 `blank`）。僅後台可設定。
- **path**：廣告圖片相對路徑，由圖片上傳 API 回傳並寫入，後台不可手動填入。
- **url**：目標網址，應為合法 URL 格式，寫入前需校驗。
- **title**：廣告標題文字，無特殊限制。

---

## Table：advertising_sport

### adarea 欄位（分割區鍵）

**型別**：text (PK)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立體育廣告 | 建立後**不可更新** |
| webpservice | INSERT | 後台建立體育廣告 | 由管理後台透過預設選項寫入，建立後不可修改（⚠️衝突） |
| productservice | INSERT | 後台建立體育廣告 | 建立後不可修改（⚠️衝突） |
| pricecentersite | SELECT | 前台讀取 | **必須帶入 `adarea` 作為 WHERE 條件**，禁止跨分區掃描 |
| livechatservice | SELECT | 聊天頁讀取 | 同上 |
| newlotterysite | SELECT | 體育廣告查詢 | 同上述限制，務必指定 `adarea` 條件 |

---

### id 欄位（聚簇鍵）

**型別**：text (CK)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立廣告 | 系統自動生成（UUID），**建立請求不可傳入**；建立後不可修改 |
| webpservice | INSERT | 建立廣告 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT | 建立廣告 | 同 advertisingservice（⚠️衝突） |
| newlotterysite | SELECT | – | 僅作識別用途，無特別限制 |

---

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：同 advertising 表，由 advertisingservice、webpservice 與 productservice 共同控制。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 禁用 | advertisingservice / webpservice / productservice | 後台停用體育廣告（特定 API） |
| 1 | 啟用 | advertisingservice / webpservice / productservice | INSERT 時預設值，或後台啟用（特定 API） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT enabled=1 | 建立體育廣告 | 預設啟用 |
| advertisingservice | UPDATE enabled=0/1 | 後台管理 | 僅限特定 API |
| webpservice | INSERT enabled=1 | 後台建立體育廣告 | 預設啟用（⚠️衝突） |
| webpservice | UPDATE enabled=0/1 | 後台啟用／停用 | （⚠️衝突） |
| productservice | INSERT enabled=1 | 後台建立體育廣告 | 預設啟用（⚠️衝突） |
| productservice | UPDATE enabled=0/1 | 後台啟用／停用 | 僅後台體育廣告管理 API 可寫入（⚠️衝突） |
| communityservice | SELECT WHERE enabled=1 | 查詢啟用中的體育廣告 | – |
| pricecentersite | SELECT WHERE enabled=1 | 前台體育版位展示 | – |
| livechatservice | SELECT WHERE enabled=1 | 聊天室體育廣告 | – |
| newlotterysite | SELECT WHERE enabled=1 | 體育廣告查詢 | 同時限定日期區間 |

---

### startdate 欄位

**型別**：text（格式固定 `yyyy-MM-dd`）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改廣告 | 校驗 `startdate ≤ closedate`，格式必須為 `yyyy-MM-dd` |
| webpservice | INSERT / UPDATE | 後台設定開始日期 | 同 advertisingservice，需校驗（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定開始日期 | 校驗 `startdate ≤ closedate`（⚠️衝突） |
| communityservice | SELECT | 過濾有效廣告 | 將字串解析為日期物件比對，避免字串字典序錯誤 |
| pricecentersite | SELECT | 過濾有效廣告 | 同上 |
| livechatservice | SELECT | 過濾有效廣告 | 同上 |
| newlotterysite | SELECT | 有效日期過濾 | 必須轉為日期物件，確定當前伺服器日期在 [startdate, closedate] 範圍內 |

---

### closedate 欄位

**型別**：text（格式固定 `yyyy-MM-dd`）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改廣告 | 校驗 `startdate ≤ closedate` |
| webpservice | INSERT / UPDATE | 後台設定結束日期 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定結束日期 | 校驗 `startdate ≤ closedate`（⚠️衝突） |
| communityservice | SELECT | 過濾條件：當前日期在 [startdate, closedate] 內 | 必須轉為日期物件比對 |
| pricecentersite | SELECT | 同上 | 同上 |
| livechatservice | SELECT | 同上 | 同上 |
| newlotterysite | SELECT | 同上 | 同上 |

**⚠️ 跨服務限制**：
- 日期欄位為字串，直接字串比對可能因字典序誤判（如 `'2025-10-01' < '2025-9-30'`），各讀取服務務必先解析為日期物件。

---

### supportlangs 欄位

**型別**：list<text>

**值定義**：語言代碼清單，例如 `['zh-TW', 'en-US']`。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 寫入廣告時 | 必須**全量覆蓋**，每個元素須為有效語言代碼 |
| webpservice | INSERT / UPDATE | 後台寫入 | 同 advertisingservice，須驗證代碼合法性（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台寫入 | 同 advertisingservice（⚠️衝突） |
| communityservice | SELECT | 語言過濾 | 檢查 `supportlangs` 是否包含請求語系代碼 |
| pricecentersite | SELECT | 語言過濾 | 同上 |
| livechatservice | SELECT | 語言過濾 | 同上 |
| newlotterysite | SELECT ⚠️ 待人工確認 | 語言過濾 | 應檢查 `supportlangs` 是否包含使用者語系；若摘要未明確，仍需實作以保證多語系正確性 |

**⚠️ 跨服務限制**：
- 禁止對 `supportlangs` 進行增量追加（如 `list + ['newlang']`），必須全量替換，防止舊語言殘留。

---

### adclass 欄位

**型別**：text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 後台設定廣告分類 | 須為系統預定義分類（如 `self`） |
| webpservice | INSERT / UPDATE | 後台操作（⚠️衝突） | 同 advertisingservice，內部管理欄位，不應回傳給前端 |
| productservice | INSERT / UPDATE | 後台操作（⚠️衝突） | 廣告分類內部標記，僅後台寫入，前端不可操作 |
| pricecentersite | SELECT | 後台統計 | **不可對外回傳**，對外 API 須遮蔽此欄位 |
| livechatservice | SELECT | 後台統計 | **不可對外回傳** |
| newlotterysite | — | – | **禁止選取或回傳此欄位**，僅為管理資訊 |

---

### seq 欄位

**型別**：int

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 設定排序 | 寫入時需確保分區內不重複 |
| webpservice | INSERT / UPDATE | 設定排序 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT / UPDATE | 設定排序 | 同 advertisingservice（⚠️衝突） |
| pricecentersite | SELECT | 前台排序 | 依 `seq` 遞增排序 |
| livechatservice | SELECT | 聊天頁排序 | 同上 |
| newlotterysite | SELECT | 排序 | 依 `seq` 遞增排序 |

---

### 其他注意事項

- **tageturl**（欄位名拼寫錯誤，實際為 `tageturl` 而非 `targeturl`）：所有服務必須使用正確欄位名，避免查詢失敗。寫入前需校驗為合法 URL。
- **imgpath**、**mobileimgpath**：圖片相對路徑，由圖片上傳 API 回傳並寫入，不可手動填寫。
- **title**：廣告標題文字，無特殊跨服務約束。

---

## Table：bulletinboard_sport

### aid 欄位（分割區鍵）

**型別**：text (PK)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立公告 | 建立後**不可修改** |
| webpservice | INSERT | 後台建立公告 | 建立後不可修改（⚠️衝突） |
| productservice | INSERT | 後台建立公告 | 建立後不可修改（⚠️衝突） |
| newlotterysite | SELECT | – | 無特殊限制 |

---

### addtime 欄位（聚簇鍵）

**型別**：bigint（Unix 秒級時間戳，UTC）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT | 建立公告 | 自動填入伺服器當前時間戳，**API 不可傳入** |
| webpservice | INSERT | 建立公告 | 同 advertisingservice，由系統自動填入（⚠️衝突） |
| productservice | INSERT | 建立公告 | 同 advertisingservice（⚠️衝突） |
| communityservice | SELECT | 排序 | 常用於降冪排序取得最新公告 |
| newlotterysite | SELECT | – | 可用於排序或過濾，但主要篩選條件為 status 與時間區間 |

---

### announcementmethod 欄位（聚簇鍵）

**型別**：int

**值定義**：

| 值 | 意義 | 由誰設定 |
|----|------|---------|
| 1 | 模式一 | advertisingservice / webpservice / productservice |
| 2 | 模式二 | 同上 |
| 3 | 模式三 | 同上 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改公告 | 僅接受 1、2、3 三種值，非法值應拒絕 |
| webpservice | INSERT / UPDATE | 後台設定公告模式 | 同 advertisingservice，須驗證取值範圍（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定公告模式 | 同 advertisingservice（⚠️衝突） |
| communityservice | SELECT | 讀取 | – |
| newlotterysite | SELECT | – | 僅讀取，無寫入權限 |

---

### status 欄位

**型別**：int

**值定義與狀態流轉**（⚠️ 存在衝突，參見說明）：

```
     advertisingservice / webpservice / productservice
            INSERT (status=0)
                │
                ▼
          ┌──────────────┐
          │   status=0    │ ◄── 未公告／草稿（預設）
          └──────┬───────┘
                 │ UPDATE (status=1)
                 ▼
          ┌──────────────┐
          │   status=1    │ ◄── 已公告
          └──────────────┘
```
> 根據 **advertisingservice 摘要**，狀態僅有 0 與 1，且 0→1 後不可逆轉。  
> 但 **productservice 摘要** 指出存在 `status=2`（下架），且需先設為下架才能刪除。此衝突需人工確認最終狀態模型。本文件暫以 advertisingservice 為準，`status=2` 不納入合法值。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未公告 | advertisingservice / webpservice / productservice | INSERT 時預設值 |
| 1 | 已公告 | 同上 | 後台公告發布 API（0→1 唯一轉換） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT status=0 | 建立公告 | 預設未公告 |
| advertisingservice | UPDATE status=1 | 後台發布 | 合法流程 0→1；禁止從 1 改回 0 |
| webpservice | INSERT status=0 | 後台建立公告 | 預設未公告（⚠️衝突） |
| webpservice | UPDATE status=1 | 後台發布公告 | 僅允許 0→1（⚠️衝突） |
| productservice | INSERT status=0 | 後台建立公告 | 預設未公告（⚠️衝突，若需下架則狀態模型需調整） |
| productservice | UPDATE status=1 | 後台發布公告 | 僅允許 0→1（⚠️衝突） |
| communityservice | SELECT WHERE status=1 | 查詢已發布公告 | 僅讀取已發布 |
| livechatservice | SELECT WHERE status=1 | 聊天頁公告展示 | 僅讀取已發布 |
| pricecentersite | SELECT WHERE status=1 | 前台公告展示 | 僅讀取已發布 |
| newlotterysite | SELECT WHERE status=1 | 前台／API 公告查詢 | 必須過濾 `status=1`，並搭配時間範圍條件 |

**⚠️ 跨服務限制**：
- `status=1` 不可逆向，任何服務不得將其改為 0。
- 僅 advertisingservice、webpservice 與 productservice 可執行 0→1 更新，且必須透過特定發布 API。
- 所有對外服務必須過濾 `status=1`，不可露出未公告內容。

---

### starttime 欄位

**型別**：text（格式 `yyyy-MM-dd HH:mm:ss`）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改公告 | 強制校驗 `starttime < endtime`，格式必須為 `yyyy-MM-dd HH:mm:ss` |
| webpservice | INSERT / UPDATE | 後台設定開始時間 | 同 advertisingservice，需校驗（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定開始時間 | 校驗 `starttime < endtime`（⚠️衝突） |
| communityservice | SELECT | 過濾有效公告 | 當前時間應 ≧ starttime |
| pricecentersite | SELECT | 過濾有效公告 | 同上 |
| livechatservice | SELECT | 過濾有效公告 | 同上 |
| newlotterysite | SELECT | 有效時間過濾 | 必須轉為時間物件比對，不可直接字串比較 |

---

### endtime 欄位

**型別**：text（格式 `yyyy-MM-dd HH:mm:ss`）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改公告 | 強制校驗 `starttime < endtime` |
| webpservice | INSERT / UPDATE | 後台設定結束時間 | 同 advertisingservice（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台設定結束時間 | 校驗 `starttime < endtime`（⚠️衝突） |
| communityservice | SELECT | 過濾條件：當前時間 < endtime | 公告過期後不顯示 |
| pricecentersite | SELECT | 過濾條件：當前時間 < endtime | 同上 |
| livechatservice | SELECT | 過濾條件：當前時間 < endtime | 同上 |
| newlotterysite | SELECT | 有效時間過濾 | 必須轉為時間物件比對 |

**⚠️ 跨服務限制**：
- 時間比較時，務必將字串解析為日期時間物件，避免簡單字串字典序比對造成錯誤。

---

### sequence 欄位

**型別**：int

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 設定排序 | 可由後台指定，或服務端自動產生（例如 max(sequence)+1） |
| webpservice | INSERT / UPDATE | 設定排序 | 同 advertisingservice，需確保不衝突（⚠️衝突） |
| productservice | INSERT / UPDATE | 設定排序 | 同 advertisingservice（⚠️衝突） |
| communityservice | SELECT | 排序 | 依 `sequence` 升冪排列 |
| pricecentersite | SELECT | 排序 | 同上 |
| livechatservice | SELECT | 排序 | 同上 |
| newlotterysite | SELECT | 排序 | 依 `sequence` 升冪排列 |

---

### maintopic / text1 / text2 / text3 欄位

**型別**：map<text, text>

**值定義**：多語言內容映射，key 為語言代碼，value 為對應文字。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| advertisingservice | INSERT / UPDATE | 建立或修改公告 | 寫入時**必須**包含 `zh-TW`、`zh-CN`、`en-US` 三個 key |
| webpservice | INSERT / UPDATE | 後台寫入 | 前端依語系傳入文字，服務端組裝為 map 後寫入；不可由 API 直接傳入完整 map 結構（⚠️衝突） |
| productservice | INSERT / UPDATE | 後台寫入 | 每個 key 須為有效語言代碼，不可空 map；至少有一個語言條目（⚠️衝突） |
| communityservice | SELECT | 讀取多語言公告 | 應依請求 `Accept-Language` 取出對應語系內容；若無匹配則回退至預設語系（如 `en`） |
| pricecentersite | SELECT | 讀取多語言公告 | 同上 |
| livechatservice | SELECT | 讀取多語言公告 | 同上 |
| newlotterysite | SELECT | 讀取多語言公告 | 同上 |

**⚠️ 跨服務限制**：
- 寫入時，不同服務的 map 組裝規則不一致（完整 map vs. 單一語系組裝），可能導致資料遺漏。建議統一為「接受完整 map，並校驗必要語系」。
- 多語言欄位更新時，需注意是替換整個 map 還是合併 key，避免遺失其他語系內容。

---

### 其他欄位

- **lastup_time**（bigint）：系統自動記錄最後更新時間（Unix 秒級），API 不可覆寫。
- **text1/text2/text3**：格式與 maintopic 相同，讀寫規則一致。

---

## 常見錯誤（跨服務）

- ❌ **廣告狀態同時被多個服務寫入** → 可能造成資料不一致，應明確指定單一 owner 或使用分散式鎖。
- ❌ **日期字串直接用字串比對**（如 `startdate <= '2025-9-30'`）→ ✅ 必須解析為日期物件再比對。
- ❌ **廣告時間範圍過濾時，遺漏 `enabled=1` 條件** → ✅ 對外查詢務必同時檢查啟用狀態與時間區間。
- ❌ **`supportlangs` 使用追加方式寫入** → ✅ 必須全量替換，避免舊語言殘留。
- ❌ **對外 API 回傳了 `createdby` 或 `adclass`** → ✅ 這些為內部管理欄位，必須排除。
- ❌ **公告 `status=1` 之後被意外改回 0** → ✅ 狀態轉換應為不可逆，且僅能透過發布 API 執行。
- ❌ **不同服務對公告 map 欄位寫入方式不一致** → ✅ 應統一接受完整 map 並校驗必要語系。
- ❌ **`bulletinboard_sport` 時間比較使用字串** → ✅ 必須轉為日期物件。
- ❌ **未指定 `adarea` 查詢體育廣告** → ✅ 分割區鍵必須帶入，避免全表掃描。