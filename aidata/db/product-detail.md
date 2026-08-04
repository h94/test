# product DB — 完整使用脈絡

> 產出時間：2025-06-14 10:30
> 欄位結構定義：[product.json](./product.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| productservice | owner | 讀、寫、刪、管理商品、兌換記錄、庫存、活動 |
| pricecentersite | writer | 可寫入 `products_activity` 表；可讀取商品資訊 |
| currencyservice | writer | 可寫入兌換相關記錄（`products_activity_redeem_logs`、`product_store_redeem_logs`），讀取庫存與商品資訊 |
| inplayzsubscriptionsystem | writer | 可寫入兌換相關記錄（`products_activity_redeem_logs`、`product_store_redeem_logs`），管理 Redis 快取 |
| cryptoflowservice | writer | 可寫入 `product_store_redeem_logs` 的兌換記錄 |
| priceclientsystem | writer | 可讀取兌換記錄、庫存、商品資訊，並在特定流程中寫入狀態 |
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
      INSERT                  UPDATE（管理後台）
     status=1（販售中）───→ status=0（暫停）
         │
         └─→ status=2（售完）
              pricecentersite / productservice UPDATE（quantity ≤ 0 自動或手動觸發）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 暫停 | pricecentersite | 管理後台手動暫停活動 |
| 1 | 販售中 | pricecentersite | 活動建立時預設 |
| 2 | 售完 | pricecentersite / productservice | 庫存歸零時自動或手動觸發 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT status=1 | 建立活動商品 | 預設販售中 |
| pricecentersite | UPDATE status=0/1/2 | 管理後台 | 透過 `UpdateSiteActivityEventProductStatus` 寫入 |
| productservice | UPDATE status=2 | 庫存歸零 | 自動觸發 |
| currencyservice | SELECT WHERE status=1 AND quantity>0 | 前台活動列表 | 僅顯示有庫存且啟用的活動 |
| inplayzsubscriptionsystem | SELECT WHERE status=1 AND quantity>0 | 活動查詢 | 僅顯示有庫存且啟用的活動 |
| cryptoflowservice | SELECT WHERE status=1 | 活動查詢 | 僅顯示啟用活動 |
| pricebackendservice | SELECT WHERE status IN(0,1,2) | 後台活動列表查詢 | 後台可查看所有狀態，但前台相關場景須過濾 status=1 |
| paymentservice | SELECT WHERE status=1 AND quantity>0 | 支付流程讀取活動商品 | 確認可兌換 |

**⚠️ 跨服務限制**：
- 前端 API 不可直接寫入 status；僅 pricecentersite（`UpdateSiteActivityEventProductStatus`）或 productservice 可修改。
- 所有對一般用戶的查詢都必須加上 `status=1` 和 `quantity>0` 條件。
- 當 quantity 歸零時，應自動觸發 status 變更為 `2`（售完）。

---

### price 欄位

**型別**：int（分單位）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT / UPDATE | 建立或編輯活動 | 設定活動所需點數或價格 |
| productservice | UPDATE | 相容既有活動管理 | 可能因後台操作調整 |
| currencyservice | SELECT | 前台顯示活動價格 | 唯讀 |
| paymentservice | SELECT | 支付流程讀取活動金額 | 唯讀 |
| pricebackendservice | SELECT | 後台活動價格檢視 | 唯讀 |

**⚠️ 注意**：
- 價格修改後不自動改變 status，但需確認活動是否仍符合販售條件。

---

### quantity 欄位

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | INSERT / UPDATE | 建立活動或手動調整庫存 | 設定初始數量或補貨 |
| productservice | UPDATE | 庫存扣減（兌換成功後） | 需搭配 `products_activity_redeem_logs` 使用，確保一致性 |
| currencyservice | SELECT | 前台顯示剩餘數量 | 唯讀 |
| pricebackendservice | SELECT | 後台庫存檢視 | 唯讀 |

**⚠️ 注意**：
- 庫存異動不應直接 UPDATE，需透過 DAO 原子操作並搭配兌換記錄，防止超賣。
- 當 quantity 歸零時，應自動觸發 status 變更為 `2`（售完）。

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

> ℹ️ 目前無服務宣告對此表的寫入細節，推測為標準狀態枚舉。狀態流轉由提現審核流程控制。
> ⚠️ 衝突待人工：實際寫入服務（提現審核服務）尚未宣告於 product DB。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| (推測) 0 | 審核中 | 未知 | INSERT 預設值 |
| (推測) 1 | 已完成 | 未知 | 撥款成功後 |
| (推測) 2 | 已拒絕 | 未知 | 審核不通過 |

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
| DEL | inplayzsubscriptionsystem / pricecentersite | 活動狀態變更時 | 主動清除保持一致性 |
| DEL | pricecentersite | `products_activity` 寫入成功後 | 確保清單快取同步 |

**⚠️ 注意**：
- 活動狀態變更（上下架、售完）、名稱或價格修改時，都必須立刻 DEL，不可只靠 TTL。
- pricecentersite 更新活動後未主動 DEL 為常見錯誤，可能導致前台顯示過期資料。

---

## 常見錯誤（跨服務）

- ❌ 查詢兌換記錄（`product_store_redeem_logs`、`products_activity_redeem_logs`）時未依 `account` 過濾，導致回傳跨使用者敏感資料。
  ✅ 所有兌換記錄查詢 API 必須加入 `WHERE account = :account` 條件（後台如需跨帳號查詢需有獨立權限）。

- ❌ 直接 UPDATE `products_store.status` 欄位，而非透過 productservice 的 `UpdateStoreProductStatus` 方法。
  ✅ 僅 productservice 可寫入該欄位；其他服務不可直接 UPDATE。

- ❌ 直接 UPDATE `products_store.price` 或 `originalprice` 欄位，導致歷史訂單金額參考不一致。
  ✅ 價格修改需整筆重建商品記錄。

- ❌ 直接 UPDATE `products_activity.quantity` 而不生成兌換記錄，導致庫存與實際兌換不一致。
  ✅ 必須透過 `products_activity_redeem_logs` 的 INSERT 搭配庫存原子操作，防止超賣。

- ❌ 兌換記錄 status 設為終態（Success/Failure/Received/UnReceived）後又被嘗試改寫。
  ✅ 程式端須強制檢查當前狀態，終態不可再流轉。

- ❌ 前台活動查詢未過濾 `status=1`（啟用）和 `quantity>0`（有庫存），導致回傳暫停或缺貨活動。
  ✅ 所有對一般用戶的活動列表 API 必須加上這兩個條件。

- ❌ 對外 API 回傳 `product_store_redeem_logs` 包含 `account`、`phonenumber`、`address` 等完整敏感欄位。
  ✅ 這些欄位僅供內部管理，對外不可回傳；後台查詢也應脫敏（如電話 `0912***456`）。

- ❌ pricecentersite 更新 `products_activity` 後未主動 DEL Redis 快取。
  ✅ 活動資訊變更必須立即清除 `product:activity:{site}:{activityevent}` 快取，避免前台讀到過期資料。

- ❌ 兌換庫存判斷僅依賴 `products_store` 單一來源，而非透過 `product_store_stock_logs` 加總計算。
  ✅ 真實庫存應以 stock_logs 的聚合結果為準。

- ❌ 商品名稱更新（`products_store.pnames`）時直接覆蓋 map，導致其他語系遺失。
  ✅ 需先 GET 現有 map，再 MERGE 新的 key-value，確保多語言資料完整。