# product DB — 完整使用脈絡

> 產出時間：2025-06-14 10:30（基於現有 detail 更新，補充 pricecentersite 夜間批次觸發情境）
> 欄位結構定義：[product.json](./product.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| productservice | owner | 讀、寫、刪、管理商品、兌換記錄、庫存、活動；唯一可變更 redeem logs 終態 |
| pricecentersite | writer | 讀取商品資訊；可寫入 `products_activity` 表（夜間批次同步活動資料，如狀態、價格、庫存） |
| currencyservice | writer | 可寫入 `products_activity_redeem_logs` 與 `product_store_redeem_logs`（INSERT 初始狀態），讀取庫存與商品資訊 |
| inplayzsubscriptionsystem | writer | 可寫入 `products_activity_redeem_logs` 與 `product_store_redeem_logs`（INSERT 初始狀態），管理 Redis 快取 |
| cryptoflowservice | writer | 可寫入 `product_store_redeem_logs` 與 `products_activity_redeem_logs`（INSERT 初始狀態） |
| priceclientsystem | writer | 讀取兌換記錄、庫存、商品資訊；可 INSERT redeem logs 初始狀態 |
| paymentservice | reader | 唯讀，查詢商品與活動資訊供支付流程使用 |
| pricebackendservice | reader | 唯讀，查詢所有表的記錄供後台管理、報表及客服使用 |

---

## Table：products_store

### status 欄位

**型別**：text（`"0"` / `"1"`）

**值定義與狀態流轉**：

```
     productservice          productservice
      INSERT/UPDATE          UPDATE
     "0"（下架） ──────────→ "1"（上架）
         ↑                       │
         │                       │
         └───────────────────────┘
              productservice UPDATE（下架）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| `"0"` | 下架 | productservice | 建立商品時預設；管理員手動下架 |
| `"1"` | 上架 | productservice | 管理員確認庫存充足後，透過 `UpdateStoreProductStatus` 上架 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT status=`"0"` | 建立商品 | 預設下架 |
| productservice | UPDATE status=`"1"` | 管理員上架 | 需確認庫存 > 0 |
| productservice | UPDATE status=`"0"` | 管理員下架 | — |
| currencyservice | SELECT WHERE status=`"1"` | 前台查詢商品列表 | 僅顯示上架商品 |
| priceclientsystem | SELECT WHERE status=`"1"` | 前台查詢商品列表 | 僅顯示上架商品；`"active"` 等同 `"1"` |
| pricebackendservice | SELECT WHERE status=`"1"` | 後台商品列表查詢 | 過濾上架商品 |
| paymentservice | SELECT WHERE status=`"1"` | 支付流程讀取商品資訊 | 唯讀，用於計算支付金額 |

**⚠️ 跨服務限制**：
- `status` 僅能透過 productservice 的 `UpdateStoreProductStatus` 方法寫入，其他服務不可直接 UPDATE。
- 下架後若要重新上架，需確認庫存量充足（由 `product_store_stock_logs` 加總計算）。

---

### price / originalprice 欄位

**型別**：int（分單位）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT | 建立商品 | 一次寫入，後續不允許單一欄位更新 |
| currencyservice | SELECT | 前台讀取價格 | 唯讀 |
| pricebackendservice | SELECT | 後台價格檢視、報表 | 唯讀 |
| paymentservice | SELECT | 支付流程讀取商品金額 | 唯讀 |

**⚠️ 注意**：
- 修改價格需整筆重建商品記錄，不可直接 UPDATE；避免造成歷史訂單金額不一致。

---

### pnames / description / image_path 欄位

**型別**：map<text, text>

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT / UPDATE | 商品管理後台 | key 須為標準語言代碼（如 `zh-TW`, `en-US`），不可為空 map |
| currencyservice | SELECT | 前台多語言顯示 | 對外輸出時應根據 Accept-Language 只回傳對應單一語系 value |
| pricebackendservice | SELECT | 後台顯示商品名稱 | 可回傳完整 map 供管理員編輯 |
| pricecentersite | SELECT | 活動獎品清單顯示 | 唯讀，用於展示兌換獎品名稱 |

**⚠️ 注意**：
- 任何服務更新此 map 欄位時，都應確保不遺失既有語系資料（建議先 GET 再 MERGE）。
- 不可由前端 API 直接操作 map 鍵值，以免遺失多語言資料。

---

### popular / sequence 欄位

**型別**：boolean（popular）、int（sequence）

| 服務 | 操作 | 說明 |
|------|------|------|
| productservice | INSERT / UPDATE | 管理後台設定熱門標記與排序值 |
| currencyservice | SELECT WHERE popular=true ORDER BY sequence | 前台列表查詢，優先顯示熱門商品 |
| pricebackendservice | SELECT ORDER BY sequence | 後台商品列表排序 | 唯讀 |

---

## Table：product_store_redeem_logs

### status 欄位

**型別**：text（枚舉值，依據 `StoreProductRedeemLogStatus`）

**值定義與狀態流轉**：

```
     productservice/priceclientsystem/currencyservice/inplayzsubscriptionsystem/cryptoflowservice
      INSERT
     UnderReview(2) ──────────→ ReviewSuccesful(3) ──────────→ InTransit(4)
         │                         productservice               productservice
         │                              UPDATE                     UPDATE
         │                                                            │
         │                                                            ├─→ Delivered(5) → Received(6) / UnReceived(7)
         │                                                            │   productservice
         │                                                            │
         └────────────────────────────────────────→ Failure(0)
                      productservice UPDATE（審核不通過）
         │
         └────────────────────────────────────────→ Success(1)（特殊場景跳過物流）
                      productservice UPDATE
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| `0` (Failure) | 兌換失敗 | productservice | 審核不通過或退款 |
| `1` (Success) | 兌換成功 | productservice | 最終確認成功（通常用於不須物流的情況） |
| `2` (UnderReview) | 審核中 | 所有 writer | INSERT 時的預設值 |
| `3` (ReviewSuccesful) | 審核通過 | productservice | 管理員審核通過，準備出貨 |
| `4` (InTransit) | 運送中 | productservice | 出貨流程更新 |
| `5` (Delivered) | 已送達 | productservice | 物流回報送達 |
| `6` (Received) | 已收貨 | productservice | 使用者確認收貨（終態） |
| `7` (UnReceived) | 未收貨 | productservice | 配送異常（終態） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT status=`"2"` | 建立兌換記錄 | 預設審核中 |
| currencyservice | INSERT status=`"2"` | 建立兌換記錄 | 預設審核中 |
| inplayzsubscriptionsystem | INSERT status=`"2"` | 建立兌換記錄 | 預設審核中 |
| cryptoflowservice | INSERT status=`"2"` | 建立兌換記錄 | 預設審核中 |
| priceclientsystem | INSERT status=`"2"` | 建立兌換記錄 | 預設審核中 |
| productservice | UPDATE status | 審核、出貨、送達、收貨 | 僅能由 `UpdateStoreProductRedeemLogStatus` 觸發 |
| currencyservice | SELECT WHERE account= :account | 查詢使用者自己的兌換記錄 | 不可跨帳號查詢 |
| priceclientsystem | SELECT WHERE account= :account | 查詢使用者自己的兌換記錄 | 不可跨帳號查詢 |
| pricebackendservice | SELECT WHERE status IN(...) | 後台兌換記錄列表查詢 | 可依狀態過濾，需搭配 account 或 pclass 條件，不可全表掃描 |

**⚠️ 跨服務限制**：
- 一旦 status 設為 `"1"`(Success) 或 `"0"`(Failure) 或 `"6"`(Received) 或 `"7"`(UnReceived) 等終態後，不可再變更。
- 只有 productservice 能變更 status，其他服務僅能 INSERT 初始狀態。
- `account`、`pid`、`pclass` 寫入後不可變更，為叢集鍵的一部分。

---

### account / phonenumber / address / recipient 欄位

**型別**：text

| 服務 | 操作 | 說明 |
|------|------|------|
| productservice / currencyservice / inplayzsubscriptionsystem / cryptoflowservice | INSERT | 兌換時由使用者填入；寫入後不可修改 |
| pricebackendservice | SELECT WHERE account= :account | 後台查詢兌換記錄，需嚴格權限控管 | 僅讀取 |
| 所有服務 | — | ⚠️ 對外 API 預設不回傳這些欄位 | 僅內部訂單處理或管理後台脫敏顯示 |

**⚠️ 注意**：
- 這些欄位屬個人隱私，對外 GET API 不可回傳完整內容。
- `phonenumber` 可脫敏顯示（如 `0912***456`），`address` 僅訂單詳情 API 可回傳給該帳號本人。
- 管理後台查詢亦需記錄存取日誌（audit log）。

---

## Table：product_store_stock_logs

### quantity 欄位

**型別**：int（代表變動後的絕對數量）

| 服務 | 操作 | 說明 |
|------|------|------|
| productservice | INSERT | 庫存變更時寫入，記錄變動後的數量快照 |
| currencyservice | SELECT | 查詢庫存變動歷史 |
| pricebackendservice | SELECT | 後台庫存對帳與報表 | 僅讀取 |

**⚠️ 注意**：
- 此表為不可變日誌（immutable log），已存在的記錄不可 UPDATE 或 DELETE。
- 當前可用庫存應透過 `SUM(quantity)` 搭配 `pclass` + `pid` 聚合計算，不可直接回傳明細給前台。
- `id` 由系統內部產生，寫入後不可修改。

---

## Table：products_activity

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     pricecentersite          pricecentersite
      INSERT                  UPDATE（管理後台或夜間批次）
     status=1（販售中）───→ status=0（暫停）
         │
         └─→ status=2（售完）
              pricecentersite / productservice UPDATE（quantity ≤ 0 自動或手動觸發）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 暫停 | pricecentersite | 管理後台手動暫停；夜間批次可能根據外部條件暫停 |
| 1 | 販售中 | pricecentersite | 活動建立時預設；夜間批次同步時可能重設為啟用 |
| 2 | 售完 | pricecentersite / productservice | 庫存歸零時自動觸發；手動或批次亦可設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT status=1 | 建立活動商品 | 預設販售中 |
| pricecentersite | UPDATE status=0/1/2 | 管理後台手動操作；夜間批次同步 | 透過 `UpdateSiteActivityEventProductStatus` 寫入；批次更新應注意避免覆蓋即時售完狀態 |
| productservice | UPDATE status=2 | 庫存歸零 | 自動觸發 |
| currencyservice | SELECT WHERE status=1 AND quantity>0 | 前台活動列表 | 僅顯示有庫存且啟用的活動 |
| inplayzsubscriptionsystem | SELECT WHERE status=1 AND quantity>0 | 活動查詢 | 僅顯示有庫存且啟用的活動 |
| cryptoflowservice | SELECT WHERE status=1 | 活動查詢 | 僅顯示啟用活動 |
| pricebackendservice | SELECT WHERE status IN(0,1,2) | 後台活動列表查詢 | 後台可查看所有狀態，但前台相關場景須過濾 status=1 |
| paymentservice | SELECT WHERE status=1 AND quantity>0 | 支付流程讀取活動商品 | 確認可兌換 |

**⚠️ 跨服務限制**：
- 前端 API 不可直接寫入 status；僅 pricecentersite（`UpdateSiteActivityEventProductStatus`，包含夜間批次）或 productservice 可修改。
- 所有對一般用戶的查詢都必須加上 `status=1` 和 `quantity>0` 條件。
- 當 quantity 歸零時，應自動觸發 status 變更為 `2`（售完）；此後 pricecentersite 的夜間批次更新**不得將 status 覆蓋為 1**，除非有補貨並確認 quantity > 0。
- 夜間批次同步時，若需變更 status，應先檢查當前状态是否為終態（2）或已被其他服務變更，避免衝突。

---

### price 欄位

**型別**：int（分單位）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT / UPDATE | 建立或編輯活動；夜間批次同步 | 設定活動所需點數或價格 |
| productservice | UPDATE | 相容既有活動管理 | 可能因後台操作調整 |
| currencyservice | SELECT | 前台顯示活動價格 | 唯讀 |
| paymentservice | SELECT | 支付流程讀取活動金額 | 唯讀 |
| pricebackendservice | SELECT | 後台活動價格檢視 | 唯讀 |

**⚠️ 注意**：
- 價格修改後不自動改變 status，但需確認活動是否仍符合販售條件。
- 夜間批次更新價格時，不應影響正在進行中的兌換流程（歷史訂單不受影響，但可能需通知前台更新顯示）。

---

### quantity 欄位

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT / UPDATE | 建立活動、手動調整庫存、夜間批次補貨 | 庫存變動 |
| productservice | UPDATE | 庫存扣減（兌換成功後） | 需搭配 `products_activity_redeem_logs` 使用，確保一致性 |
| currencyservice | SELECT | 前台顯示剩餘數量 | 唯讀 |
| pricebackendservice | SELECT | 後台庫存檢視 | 唯讀 |

**⚠️ 注意**：
- 庫存異動不應直接 UPDATE，需透過 DAO 原子操作並搭配兌換記錄，防止超賣。
- 當 quantity 歸零時，應自動觸發 status 變更為 `2`（售完）。
- 夜間批次補貨（增加 quantity）時，若 status 為 2（售完），應檢查是否允許重新上架（建議僅在 `status=0` 或 `1` 時補貨，或補貨後手動變更 status）。
- 批次更新時不可覆蓋正在發生的即時扣減，應使用 `quantity = quantity + delta` 方式避免 race condition。

---

### names 欄位

**型別**：map<text, text>

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentersite | INSERT / UPDATE | 建立或編輯活動時設定多語言名稱 |
| currencyservice | SELECT | 對外輸出時依 Accept-Language 只回傳對應單一語系 value |
| pricebackendservice | SELECT | 後台可完整讀取所有語系供編輯 | 唯讀 |

**⚠️ 注意**：
- 寫入時每個 key 須為有效語言代碼（如 `zh-TW`, `en-US`），至少需包含 `zh-TW`。
- 對前台 API 不可回傳整個 map，避免不必要的資料暴露。

---

## Table：products_activity_redeem_logs

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     currencyservice/inplayzsubscriptionsystem/cryptoflowservice
      INSERT
     status=0（審核中） ──────────→ status=1（成功）
         │                        productservice UPDATE（活動結算確認）
         │
         └────────────────────────→ status=2（失敗）
                    productservice UPDATE（取消或拒絕）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 審核中 | currencyservice / inplayzsubscriptionsystem / cryptoflowservice | INSERT 時的預設值 |
| 1 | 成功 | productservice | 活動結算確認後，`UpdateActivityProductRedeemLogStatus` 設定 |
| 2 | 失敗 | productservice | 活動取消或拒絕後設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| currencyservice | INSERT status=0 | 建立活動兌換記錄 | 預設審核中 |
| inplayzsubscriptionsystem | INSERT status=0 | 建立活動兌換記錄 | 預設審核中 |
| cryptoflowservice | INSERT status=0 | 建立活動兌換記錄 | 預設審核中 |
| productservice | UPDATE status=1/2 | 活動結算或取消 | 成功後不可再變更 |
| pricebackendservice | SELECT WHERE account= :account AND activityevent= :event | 後台查詢活動兌換記錄 | 用於對帳或客服查詢，不可跨帳號 |
| pricecentersite | SELECT WHERE activityevent= :event | 兌換記錄查詢 | 管理後台查看活動兌換狀況 |

**⚠️ 跨服務限制**：
- `status` 僅能由 productservice 的 `UpdateActivityProductRedeemLogStatus` 更新為 1 或 2。
- `account`、`pid`、`id` 為叢集鍵，寫入後不可變更。
- 任何服務查詢此表時，非管理用途都必須以 `account` 過濾，防止洩漏其他用戶兌換資訊。

---

## Table：withdrawlogs_activity

### status 欄位

**型別**：int

> ⚠️ 衝突待人工：實際寫入服務（提現審核服務）尚未宣告於 product DB；目前僅有讀取操作宣告。

**值定義與狀態流轉**：（以下為推測，待確認）

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 審核中 | 未知 | INSERT 預設值 |
| 1 | 已完成 | 未知 | 撥款成功後 |
| 2 | 已拒絕 | 未知 | 審核不通過 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricebackendservice | SELECT WHERE account= :account AND activityevent= :event | 後台查詢活動提領記錄 | 用於報表或客服，僅讀取 |

**⚠️ 跨服務限制**：
- `account`、`site`、`activityevent`、`cid` 為分區鍵或叢集鍵，寫入後不可修改。
- `contactnumber` 欄位對外 API 必須脫敏，僅保留末四位或直接隱藏。
- 同一帳號在同一活動期別（`site`+`activityevent`+`account`+`cid`）僅能存在一筆記錄，不可重複寫入。

---

## Redis — ProductCache

### product:store:{pclass}:{pid}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | inplayzsubscriptionsystem | 商品查詢時 | TTL：30 秒，快取單一商品資訊 |
| GET | inplayzsubscriptionsystem | 前台查詢商品詳情 | 減少 DB 壓力 |
| DEL | inplayzsubscriptionsystem | 商品狀態變更、庫存變更時 | 必須主動清除，不可只靠 TTL |

**⚠️ 注意**：
- 當 `products_store.status` 切換或庫存發生變化（`product_store_stock_logs` 有新增記錄）時，必須主動 DEL 此 Key。
- 讀不到快取時應 fallback 查 DB，不可直接報錯。

### product:activity:{site}:{activityevent}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | inplayzsubscriptionsystem | 活動列表或單一活動查詢 | TTL：10 秒；活動開始前/結束後可加大 TTL |
| GET | inplayzsubscriptionsystem | 前台查詢活動資訊 | — |
| DEL | inplayzsubscriptionsystem | 活動狀態、價格、庫存變更時 | 必須在 DB 寫入後主動 DEL，確保前台一致性 |

**⚠️ 注意**：
- 當 `products_activity` 的任何會影響前台的欄位（status、quantity、price）變更時，必須主動 DEL 此 Key，不能只依賴 TTL。
- 夜間批次（pricecentersite）大量更新活動數據後，建議透過訊息佇列或事件通知 inplayzsubscriptionsystem 批次清除受影響的活動快取，避免大量快取過期瞬間擊穿 DB。
- 清除失敗時，應記錄錯誤並允許人工清除，不可阻塞主要業務流程。

---

## 常見錯誤（跨服務）

- ❌ **夜間批次覆蓋活動狀態** → pricecentersite 在 quantity 已歸零且 status=2 的情況下，因批次更新又將 status 設為 1，造成前台顯示售完又上架。應在更新前檢查當前 status，若為終態（2）則跳過或僅允許管理者手動介入。
- ❌ **庫存更新未考慮即時競爭** → productservice 在扣減 quantity 時未使用 CAS（Compare-and-Set）或原子操作，可能超賣。建議使用 Cassandra 的輕量級事務或透過兌換記錄與庫存日誌雙重驗證。
- ❌ **對外 API 洩漏全語系 map** → 直接回傳 `pnames` 或 `description` 的完整 map，應根據請求的 Accept-Language 僅回傳對應單一語言值。
- ❌ **兌換記錄查詢未以 account 過濾** → 查詢 `products_activity_redeem_logs` 時僅用 `activityevent`，未加 `account`，可能跨帳號暴露資料；且 Cassandra 不支援跨分區掃描，實際上會報錯。
- ❌ **快取與 DB 不一致** → 更新 `products_activity` 後未清除 `product:activity:*` 快取，導致前台長時間顯示錯誤的庫存或價格。應確保每次寫入後都觸發快取 DEL，或採用 Write-Through 模式。
- ❌ **隱私欄位外洩** → `product_store_redeem_logs` 的 `phonenumber`、`address` 等未脫敏即回傳給前端，違反個資保護。對外 API 必須遮蔽或僅回傳部分資訊。
- ❌ **批次更新價格未通知支付服務** → 若 paymentservice 在結帳過程中依賴快取或已讀取的價格，批次更新後未使其失效，可能導致支付金額與實際不符。建議批次更新後廣播價格變更事件。