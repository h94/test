# payment DB — 完整使用脈絡

> 產出時間：2026-06-10 16:00
> 欄位結構定義：[payment.json](./payment.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| paymentservice | owner | 讀、寫、刪所有表格 |
| productservice | owner | 讀、寫：products_activity、products_activity_redeem_logs、paymethods_sport(enabled)、rechargeplans_newlottery、commissions_betpool_newlottery、withdrawlogs_activity 等 |
| newlotterybackendservice | owner | 讀、寫：commissions_betpool_newlottery、rechargeplans_newlottery 等 |
| newlotterysite | reader | 唯讀，用於前台展示充值方案、支付方式、活動商品與兌換紀錄 |
| pricecentersite | reader / writer | 讀寫：rechargeplans_newlottery、subplans_sport（後台管理）；唯讀：其他 payment 表 |
| pricebackendservice | writer / reader | 讀寫：products_activity、products_activity_redeem_logs、commissions_betpool_newlottery、rechargeplans_newlottery 等 |
| backendservice | reader | 唯讀，用於前台展示與查詢 |
| reportservice | reader | 唯讀，用於財務與分潤報表統計 |

---

## Table：paymethods_sport

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     paymentservice / productservice    paymentservice / productservice
      INSERT                            UPDATE
     enabled=1 ───────────────────────→ enabled=0
         │                                  │
         └──────────────────────────────────→ enabled=1
              paymentservice / productservice UPDATE（啟用）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 停用 | paymentservice / productservice | 後台關閉 |
| 1 | 啟用 | paymentservice / productservice | INSERT 預設或後台啟用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT enabled=1 | 新增付款方式 | 預設啟用 |
| paymentservice | UPDATE enabled=0/1 | 後台設定 | 啟用/停用 |
| productservice | UPDATE enabled | 後台支付設定 API | 前端不可操作 |
| backendservice | SELECT WHERE enabled=1 | 前台顯示可用付款方式 | 只顯示啟用 |
| newlotterysite | SELECT WHERE enabled=1 | 前台查詢 | 唯讀 |
| reportservice | SELECT | 統計已啟用付款方式 | 唯讀 |
| pricecentersite | SELECT WHERE enabled=1 | 查詢可用支付方式 | 唯讀；不可回傳停用方式 |

**⚠️ 跨服務限制**：
- 只有 paymentservice 和 productservice 可以修改 enabled；其他服務唯讀。
- `paytype` 與 `mode` 為 Partition Key / Clustering Key，不可更新。

### names 欄位

**型別**：map<text, text>

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| paymentservice | INSERT/UPDATE | 後台設定多語系名稱映射 |
| productservice | UPDATE | 後台支付設定，更新特定語言鍵值 |
| backendservice | SELECT | 根據前端語言回傳單一語系名稱，不可暴露完整 map |
| newlotterysite | SELECT | 回傳前台所需語言名稱 |

**⚠️ 跨服務限制**：
- 對外 API 不可暴露完整 `names` map，應轉為當前語言字串。
- `names` 僅可透過管理 API 更新，不可由使用者端修改。

---

## Table：products_activity

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     productservice / paymentservice     productservice / paymentservice
      INSERT                              UPDATE
     status=0 ─────────────────────────→ status=1
         │
         └────────────────────────────────→ status=2
                    productservice / paymentservice UPDATE（售完或下架）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 暫停 | productservice / paymentservice | INSERT 預設或後台下架 |
| 1 | 販售中 | productservice / paymentservice | 管理員手動上架或排程 |
| 2 | 售完 | productservice / paymentservice | 庫存為 0 或後台下架 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT status=0 | CreateActivityProduct | 預設暫停 |
| productservice | UPDATE status=0/1/2 | `UpdateSiteActivityEventProductStatus` | 前端不可寫入 |
| paymentservice | UPDATE status=0/1/2 | 後台操作或排程 | 上架/下架 |
| backendservice | SELECT WHERE status=1 | 前台顯示 | 唯讀 |
| newlotterysite | SELECT WHERE status=1 AND quantity > 0 | 前台查詢可用商品 | 唯讀 |
| reportservice | SELECT | 統計活動狀態 | 唯讀 |
| pricecentersite | SELECT WHERE status=1 AND quantity > 0 | 查詢活動商品 | 唯讀 |
| pricebackendservice | SELECT / UPDATE status | 後台管理 | 查詢或變更狀態（僅後台） |

**⚠️ 跨服務限制**：
- 只有 `UpdateSiteActivityEventProductStatus`（productservice）或 paymentservice 後台可變更 status；前端任何 API 不可直接 UPDATE。
- 一旦設為 2（售完）不應再改回 1，除非手動補貨（需走後台審核流程）。
- `price`、`quantity` 僅在 `CreateActivityProduct` 時一次性寫入，後續不允許單一欄位更新。

### price / quantity / names 欄位

**型別**：int / int / map<text, text>

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT price/quantity/names | `CreateActivityProduct` | 一次寫入，後續不可部分更新 |
| newlotterysite | SELECT quantity > 0 | 前台查詢可用商品 | 過濾有庫存商品 |
| pricecentersite | SELECT price, quantity, names | 查詢商品資訊 | 唯讀 |

**⚠️ 注意**：
- `updatetime` 應由系統在每次變更時自動更新，不允許 API 直接設定。
- `id`、`site`、`activityevent` 不可修改。

---

## Table：products_activity_redeem_logs

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     productservice / paymentservice      productservice / paymentservice
      INSERT                               UPDATE
     status=0 ──────────────────────────→ status=1
         │
         └────────────────────────────────→ status=2
                    productservice / paymentservice UPDATE（審核拒絕）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 審核中 | productservice / paymentservice | 用戶提交兌換時 INSERT 預設 |
| 1 | 成功 | productservice / paymentservice | 審核通過 |
| 2 | 失敗 | productservice / paymentservice | 審核拒絕 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT status=0 | 用戶提交兌換 | 預設審核中 |
| productservice | UPDATE status=1/2 | `UpdateActivityProductRedeemLogStatus` | 成功後不可再變更 |
| paymentservice | UPDATE status=1/2 | 後台審核 | 通過或拒絕 |
| backendservice | SELECT | 查詢用戶兌換記錄 | 唯讀 |
| newlotterysite | SELECT WHERE site=? AND activityevent=? AND account=? | 查詢使用者兌換紀錄 | 不可跨帳號查詢 |
| pricecentersite | SELECT WHERE site=? AND activityevent=? AND account=? | 查詢特定用戶兌換記錄 | 必須指定完整分區鍵，唯讀 |
| pricebackendservice | SELECT / UPDATE status | 後台管理 | 審核或查詢 |

**⚠️ 跨服務限制**：
- 僅 `UpdateActivityProductRedeemLogStatus` 或 paymentservice 後台可更新 status；設為成功或失敗後不可再變更。
- `id` 由系統自動產生，不可手動指定。
- `addtime` 由系統自動生成，不可手動寫入。
- 前端查詢只能看自己的記錄，後台可查全部但需指定 site 及 activityevent。

---

## Table：rechargeplans_newlottery

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     paymentservice / productservice / pricecentersite / pricebackendservice
      INSERT
     enabled=1 ─────────────────────────────→ enabled=0
         │                                         │
         └──────────────────────────────────────────→ enabled=1
              paymentservice / productservice / pricecentersite / pricebackendservice UPDATE
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 停用 | 上述服務 | 後台關閉方案 |
| 1 | 啟用 | 上述服務 | INSERT 預設或後台啟用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT enabled=1 | 新增充值方案 | 預設啟用 |
| paymentservice | UPDATE enabled=0/1 | 後台設定 | 啟用/停用 |
| productservice | UPDATE enabled | 後台編輯方案 | 不可與 starttime/endtime 衝突 |
| pricecentersite | INSERT enabled=1, amount, coin, currency, starttime, endtime | 新增方案（後台） | 僅後台操作 |
| pricecentersite | UPDATE enabled, starttime, endtime, amount, coin, currency | 修改方案（後台） | 啟用時必須確保當前時間在有效期間內 |
| pricebackendservice | UPDATE enabled | 後台管理 | 修改方案狀態 |
| backendservice | SELECT WHERE enabled=1 | 前台顯示可用方案 | 唯讀 |
| newlotterysite | SELECT WHERE enabled=1 AND starttime <= NOW AND NOW < endtime | 前台查詢 | 過期或未啟用方案不可暴露 |
| reportservice | SELECT | 統計方案使用狀況 | 唯讀 |

**⚠️ 跨服務限制**：
- 以上四個服務可寫，其餘服務唯讀。
- `id` 由系統生成，不可修改。
- `starttime`、`endtime` 與 `enabled` 須同時檢查邏輯一致性；不可單獨設 `enabled=1` 卻忽略時間範圍。
- `lastupdatetime` 由系統自動維護，API 不可手動設定，對外不可回傳原始值。

---

## Table：subplans_sport

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     paymentservice / pricecentersite        paymentservice / pricecentersite
      INSERT                                  UPDATE
     enabled=1 ───────────────────────────→ enabled=0
         │                                      │
         └──────────────────────────────────────→ enabled=1
              paymentservice / pricecentersite UPDATE
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 停用 | paymentservice / pricecentersite | 後台關閉方案 |
| 1 | 啟用 | paymentservice / pricecentersite | INSERT 預設或後台啟用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT enabled=1 | 新增訂閱方案 | 預設啟用 |
| paymentservice | UPDATE enabled=0/1 | 後台設定 | 啟用/停用 |
| pricecentersite | INSERT enabled=1, amount, currency, effectivelength, startdate, enddate, names | 新增方案（後台） | 僅後台操作 |
| pricecentersite | UPDATE enabled, startdate, enddate, amount, currency, effectivelength, names | 修改方案（後台） | 啟用時必須確保當前日期在有效期間內 |
| backendservice | SELECT WHERE enabled=1 | 前台顯示可用方案 | 唯讀 |
| newlotterysite | SELECT WHERE enabled=1 AND startdate <= 當前日期 AND 當前日期 < enddate | 前台查詢 | 過期或未啟用方案不可暴露 |

**⚠️ 跨服務限制**：
- 只有 paymentservice 和 pricecentersite 可修改；其餘唯讀。
- `id` 由系統生成，不可修改。
- `startdate`、`enddate` 與 `enabled` 須同時生效檢查。
- `lastupdatetime` 由系統自動更新，不可手動設定，對外 API 不可回傳。

### names 欄位

**型別**：map<text, text>

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| paymentservice | INSERT/UPDATE | 後台設定多語系名稱 |
| pricecentersite | INSERT/UPDATE | 後台設定 |
| backendservice | SELECT | 根據請求語言回傳單一語系名稱 |
| newlotterysite | SELECT | 回傳前台所需語言名稱 |

**⚠️ 跨服務限制**：
- 對外 API 不可暴露完整 `names` map，應轉為當前語言字串。

---

## Table：reports_sport

### finishing 欄位

**型別**：boolean

**值定義與狀態流轉**：

```
     reportservice            reportservice
      INSERT                   UPDATE
     finishing=false ────────→ finishing=true
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| false | 未完成 | reportservice | 報表開始計算時預設 |
| true  | 已完成 | reportservice | 報表計算完成後 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| reportservice | INSERT finishing=false | 月初建立報表 | 預設未完成 |
| reportservice | UPDATE finishing=true | 報表結算完成 | 標記完成 |
| backendservice | SELECT finishing | 查詢報表狀態 | 唯讀 |
| pricecentersite | SELECT WHERE year=? AND month=? AND finishing=true | 查詢報表摘要 | 僅回傳已完成月份；leaguesunlock 須轉為結構化摘要，不得直接暴露原始 JSON |

**⚠️ 跨服務限制**：
- 只有 reportservice 可修改 finishing；其它服務唯讀。
- paymentservice 雖為 owner，但不可直接寫入此表，報表結算由專屬服務處理。

---

## Table：reports_sport_recommend

### finishing 欄位

同 **reports_sport**，狀態定義與流轉一致。

**各服務操作明細**（僅補充與 reports_sport 不同處）：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentersite | SELECT WHERE year=? AND month=? AND finishing=true | 查詢推薦報表 | 必須指定年月；僅回傳已完成報表 |

**⚠️ 跨服務限制**：同 reports_sport。

---

## Table：sharereports_sport

### payout 欄位

**型別**：boolean

**值定義與狀態流轉**：

```
     paymentservice           paymentservice
      INSERT                   UPDATE
     payout=false ───────────→ payout=true
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| false | 未發放 | paymentservice | 分潤報表建立時 |
| true  | 已發放 | paymentservice | 實際支付分潤後 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT payout=false | 建立分潤報表 | 預設未發放 |
| paymentservice | UPDATE payout=true | 完成分潤發送 | 標記已發放 |
| backendservice | SELECT payout | 查詢分潤狀態 | 唯讀 |
| reportservice | SELECT payout | 統計待發放分潤 | 唯讀 |
| pricecentersite | SELECT payout, shareamount | 查詢分潤明細 | 唯讀 |

**⚠️ 跨服務限制**：
- 只有 paymentservice 可以變更 payout；設定為 true 後不可回退。

---

## Table：sharereports_sport_recommend

此表主要用於記錄推薦分潤明細，無特殊業務狀態欄位，所有欄位供查閱與統計。寫入由 paymentservice 負責，讀取由 backendservice、reportservice、pricecentersite 等服務進行。

---

## Table：shakehandlogs_service_sport

### actiontype 欄位

**型別**：text

**值定義與狀態流轉**：無狀態流轉，為操作類型標記。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| add | 新增 | paymentservice | 執行新增操作時記錄 |
| update | 更新 | paymentservice | 執行更新操作時記錄 |
| delete | 刪除 | paymentservice | 執行刪除操作時記錄 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT actiontype={value} | 每次服務 shakehand 操作 | 記錄操作日誌 |
| backendservice | SELECT actiontype | 查詢操作日誌 | 唯讀 |

**⚠️ 跨服務限制**：
- 僅 paymentservice 可寫入；其他服務（包括 backendservice）唯讀。

---

## Table：shakehandlogs_site_sport

### actiontype 欄位

同 **shakehandlogs_service_sport** 的 actiontype，值意義相同。寫入與讀取規則也相同，由 paymentservice 寫入，其他服務唯讀。

---

## Table：commissions_betpool_newlottery

### ctype 欄位

**型別**：text

**值定義與狀態流轉**：此欄位為固定分類標籤，無狀態流轉。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| ticket | 票券佣金 | NewLotteryCommissionService（由 paymentservice 或 newlotterybackendservice 觸發） | INSERT 時依來源判斷 |
| sell | 銷售佣金 | NewLotteryCommissionService | INSERT 時依來源判斷 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| paymentservice | INSERT ctype={value} | 佣金建立時 | 由佣金計算邏輯寫入 |
| newlotterybackendservice | INSERT ctype={value} | 佣金建立時 | 由內部佣金服務寫入 |
| backendservice | SELECT ctype | 查詢佣金明細 | 唯讀 |
| reportservice | SELECT ctype | 報表統計分類 | 唯讀 |
| pricecentersite | SELECT ctype | 查詢佣金明細（依 betpool 分頁，LIMIT 100） | 唯讀；不可回傳 source_cid |
| pricebackendservice | SELECT ctype | 查詢佣金 | 唯讀 |

**⚠️ 跨服務限制**：
- 所有欄位僅由佣金計算服務（NewLotteryCommissionService）經由 paymentservice 或 newlotterybackendservice 寫入，禁止人工 INSERT 或 UPDATE。
- `id`、`betpool`、`source_uid` 一旦寫入不可變更；佣金記錄不可 DELETE。
- pricecentersite 查詢時不可回傳敏感欄位如 `source_cid`。

---

## Table：withdrawlogs_activity

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     paymentservice / productservice      paymentservice / productservice
      INSERT                               UPDATE
     status=0 ──────────────────────────→ status=1
         │
         └────────────────────────────────→ status=2
                    paymentservice / productservice UPDATE（拒絕）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 待審核 | paymentservice / productservice | 用戶發起提領時 INSERT 預設 |
| 1 | 成功 | paymentservice / productservice | 審核通過，完成發放 |
| 2 | 失敗 | paymentservice / productservice | 審核拒絕 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| productservice | INSERT status=0 | 用戶提交提領申請 | 預設待審核 |
| productservice | UPDATE status=1/2 | 內部狀態更新 API | 設為成功/失敗後不可回退 |
| paymentservice | INSERT status=0 | 用戶提領 | 記錄申請 |
| paymentservice | UPDATE status=1/2 | 後台審核 | 通過或拒絕 |
| backendservice | SELECT | 查詢用戶提領記錄 | 唯讀 |
| newlotterysite | SELECT WHERE account=? | 查詢自己的提領記錄 | 不可查詢他人 |
| pricecentersite | SELECT | 查詢提領明細（後台） | 唯讀 |
| pricebackendservice | SELECT / UPDATE status | 後台審核 | 變更狀態（需內部 API） |

**⚠️ 跨服務限制**：
- 僅 paymentservice 或 productservice 可變更 status；設定為成功(1)或失敗(2)後不可再更改。
- 個人資料欄位（accountname、contactnumber）僅在建立時由使用者提供，後續不可修改。
- 提領記錄不可刪除，只能變更狀態。

---

## Redis — RechargePlansCache

### rechargeplans:all:{site}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | newlotterysite | 後台更新充值方案後 | 快取該站點所有啟用方案清單；TTL 建議 5 分鐘或根據 `lastupdatetime` 動態計算 |
| DEL | newlotterysite / pricecentersite | 充值方案新增/修改/刪除時 | 主動失效，確保下次查詢重新讀取 DB |
| GET | newlotterysite | 每次展示充值方案列表時 | 快取啟用方案 |

**⚠️ 注意**：
- 方案變更時必須主動 DEL，不可只靠 TTL 自然過期。
- pricecentersite 修改方案後應觸發快取清除或通知 newlotterysite，避免前台顯示舊資料。

---

## Redis — PayMethodsCache

### paymethods:enabled:{site}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | newlotterysite | 後台更新支付方式後 | 快取啟用的支付方式（`enabled=1`），TTL 建議 10 分鐘 |
| GET | newlotterysite | 每次展示支付方式列表時 | 讀取快取 |

**⚠️ 注意**：
- `enabled` 變更時必須主動 DEL 相關快取，前台才能立即反應。
- 若快取未命中，須 fallback 查詢 DB 並重新設定快取，不可直接報錯。

---

## 常見錯誤（跨服務）

- ❌ 前端直接呼叫 API 更新 `rechargeplans_newlottery.enabled` → 只有 paymentservice、productservice、pricecentersite、pricebackendservice 的後台 API 才能修改。
- ❌ 查詢方案時未過濾 `enabled=1` 或忽略 `starttime` / `endtime` → 前台可能顯示過期或未啟用方案，造成使用者操作錯誤。
- ❌ 修改 `products_activity.status` 為 1 後未確認 `quantity > 0` → 可能顯示已售完商品，造成兌換失敗。
- ❌ 在 `products_activity_redeem_logs` 審核完成後仍嘗試 UPDATE status → 設定為 1 或 2 後禁止再變更，防止資料不一致。
- ❌ 查詢 `products_activity_redeem_logs` 時未指定 `site` 分區鍵 → Cassandra 全表掃描效能極差，且可能暴露他人資料。
- ❌ `pricecentersite` 查詢 `reports_sport.leaguesunlock` 時未轉換 JSON 直接回傳前端 → 洩漏內部結構，應格式化為摘要。
- ❌ 忘記清除 `RechargePlansCache` 就更新方案 → 前台持續顯示舊資料，影響使用者。
- ❌ `withdrawlogs_activity.status` 設置為成功後再次變更 → 違反不可回退原則，可能導致財務錯誤。
- ❌ paymentservice 或 productservice 嘗試直接修改 `commissions_betpool_newlottery` 的 `coin` 值 → 只能由佣金計算服務寫入，否則數據失真。