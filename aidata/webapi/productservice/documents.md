# productservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 03:20
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### TCZB-3655 [ProductService] - 球王商城商品系統 & Sprint 203 CodeReview

> Confluence 頁面 ID：55584452, 55584775
> 原始文件：[查看 TCZB-3655](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584452) | [查看 Sprint 203 CodeReview](https://confluence.zbdigital.net/display/TCZB/Sprint+203+CodeReview)
> 摘要檔：[processed/55584452-summary.md](../../confluence/processed/55584452-summary.md), [processed/55584775-summary.md](../../confluence/processed/55584775-summary.md)
> Confluence 最後更新：2025-04-17, 2025-03-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義球王商城商品系統核心業務規則與資料操作限制。商品剩餘數量須透過「進貨數量 - 成功兌換數量」動態計算，不可直接寫入欄位；庫存數量不存入 Cassandra，改由庫存紀錄總和計算。非站內商品建立時只能為已下架狀態，須先生成庫存才能上架。兌換紀錄狀態流轉嚴格限制：僅審核中(status=2)可改為成功(1)或失敗(0)，失敗狀態不可再變更。商品刪除時須同時移除所有進貨與兌換紀錄。

**關鍵業務規則**：
- 商品剩餘數量 = 進貨數量 - 成功兌換數量，更新商品時不得直接修改數量欄位
- 更新商品快取資料時，不得更動商品剩餘數量
- 新增商品兌換紀錄前，必須先確認商品剩餘數量足夠
- addtime（新增時間）為 clustering 依據，任何更新操作不應更動此欄位
- 若只需更新商品狀態，必須使用專用函數，不得使用會影響數量的更新方法
- 刪除商品時，須先檢查是否存在未結案的兌換紀錄，若存在則不可刪除；刪除通過時，須同時移除進貨紀錄與兌換紀錄
- 計算商品剩餘數量的邏輯應提取為共用函數，供多處使用
- 只有兌換狀態為失敗(0)的兌換紀錄才可以被刪除
- 更新兌換紀錄狀態時：status=2 才能改為 1 或 0；status=0 不能改為其他非 0 狀態
- 非站內商品(inplayz)建立時，商品狀態只能為已下架(0)
- 兌換紀錄建立後，會員暱稱(cname)與會員大頭貼(cheadshot)固定，不可修改

**注意事項**：
- ⚠️ TCZB-3621 定義商品狀態為「上架中」或「已停售」，TCZB-3655 定義狀態包含 0-7 多種代碼（含審核中 2），兩份文件的狀態定義不完全一致，需人工確認適用的系統版本
- ⚠️ TCZB-3621 對應的刪除規則為「無條件級聯刪除」，Sprint 203 CodeReview 要求「先檢查未結案兌換」，規則有衝突，需人工確認現行規則

---


### plan-zcoin-report-store-redeem-tabs & task-understanding-zcoin-report-store-redeem-tabs

> Confluence 頁面 ID：79471882, 79471868
> 原始文件：[查看 plan](https://confluence.zbdigital.net/display/TCZB/plan-zcoin-report-store-redeem-tabs) | [查看 task-understanding](https://confluence.zbdigital.net/display/TCZB/task-understanding-zcoin-report-store-redeem-tabs)
> 摘要檔：[processed/79471882-summary.md](../../confluence/processed/79471882-summary.md), [processed/79471868-summary.md](../../confluence/processed/79471868-summary.md)
> Confluence 最後更新：2026-05-24
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為 PriceBackendService 的 Z 幣報表新增商城兌換 Tab。定義 ProductService 新 API（一次回傳 redeem logs 與對應商品清單），BFF 向 MemberService 取得錢包扣款加總 Z 幣。明確規則：只計算成功交易、排除退款與機器人、Z 幣以錢包 Amount 為準。查詢端點固定篩選 status="1"，不提供可變 status 參數。

**關鍵業務規則**：
- Z 幣統計僅包含 product.product_store_redeem_logs 中 status = '1'（Success）的記錄
- Z 幣金額來源為 gameusers_wallet_transactions 表中 Type = 3 的交易，且必須排除 PType = 'refund'
- 對帳以錢包交易 Amount 為準，不得使用 products_store.Price 推算
- 兌換記錄與錢包交易的對應鍵為 Account、PClass、PID、AddTime、ID（五鍵完全匹配）
- 排除 Robot 玩家，透過 MemberService.GetRobots 取得 HashAuthString 名單過濾
- 所有 PClass（含 inplayz）皆列入計算
- ProductService 查詢端點 (PS-1) 固定篩選 status="1"，僅接受 startTime、endTime，endTime < startTime 時回傳 400

**注意事項**：
- ⚠️ 採用全量讀取 + 記憶體過濾，上線後需加 log 監控耗時，若變慢再優化
- ⚠️ 若成功兌換記錄找不到對應扣款，應記錄警告 log 並略過，不可任意填 0 或商品價格

---

### Sprint199 - CodeReview

> Confluence 頁面 ID：55583117
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Sprint199+-+CodeReview)
> 摘要檔：[processed/55583117-summary.md](../../confluence/processed/55583117-summary.md)
> Confluence 最後更新：2025-02-17
> 摘要最後同步：2026-05-27

**摘要**：
Code review 記錄指出 productservice 相關程式碼的多項實作規範與修正方向，包括 API 行為規範、Cassandra 語句格式、型態宣告、路由設計等。

**關鍵業務規則**：
- 新增、更新、刪除類型的 API 操作不回傳訊息（如不回傳實體內容或成功訊息）
- 若資料表欄位為 Cassandra 的 clustering key，該欄位不可更新，前端或服務層不應對其進行任何驗證
- domain service 中若無特殊需求，內部使用的清單變數必須宣告為 private
- 未在路由邏輯中使用的路由參數必須移除以保持路由簡潔

**注意事項**：
- ⚠️ 此 Code Review 結論是否仍適用於現行系統流程，需對照目前 productservice 實作確認

---

## 技術設計類


### TCZB-3621 [ProductService] - 球王商品服務

> Confluence 頁面 ID：55582655
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55582655)
> 摘要檔：[processed/55582655-summary.md](../../confluence/processed/55582655-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27

**摘要**：
定義 ProductService 中商城商品的 CRUD 功能設計，包含 Cassandra 與 Redis 的資料結構、API 路由與參數、管理員操作商品的完整流程。Cassandra 為持久層，Redis 為快取層並儲存剩餘數量。查詢商品時快取參數 cache 預設為 true（從 Redis 讀取），設為 false 時從 Cassandra 讀取。

**關鍵設計決策**：
- 選擇 Cassandra 作為主要資料庫，Redis 作為快取層：Cassandra 儲存完整商品資料（含初始數量），Redis 儲存快取資料並以「剩餘數量」取代「初始數量」
- Redis Key 設計為 Store_{class}_Products，以商品種類作為快取分群
- 更新商品時會先檢查商品是否存在及狀態是否為已停售，再決定是否更新及操作快取
- API 設計採用 RESTful 風格，以 pclass 和 pid 作為路徑參數進行資源定位

**影響範圍**：
- 更新商品時若狀態為「已停售」，需刪除 Redis 中的對應快取
- 刪除商品時，需同步刪除 Redis 中的對應快取

---


### TCZB-3655 [ProductService] - 球王商城商品系統

> Confluence 頁面 ID：55584452
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584452)
> 摘要檔：[processed/55584452-summary.md](../../confluence/processed/55584452-summary.md)
> Confluence 最後更新：2025-04-17
> 摘要最後同步：2026-05-27

**摘要**：
新增商品兌換紀錄與庫存紀錄的 CRUD 功能，包含 15 個 REST API 的完整契約定義。

**關鍵設計決策**：
- 庫存數量不存入 Cassandra 的獨立欄位，而是通過庫存紀錄總和動態計算，避免數據不一致
- 商品刪除採用級聯刪除（cascade），不保留兌換與庫存紀錄
- 兌換紀錄中的會員暱稱與頭貼在建檔時固化，後續不跟隨會員資料變動
- Redis 快取 Store_{class}_Products 作為商品查詢的快取層，支援 cache 參數切換資料來源
- API 路徑設計採用分層 RESTful 風格，區分商品、兌換紀錄、庫存紀錄的資源層級

**影響範圍**：
- ⚠️ API 路徑不一致：更新兌換紀錄(狀態)使用 /productservice/store/productredeemlogs 而非 /productservice/api/store/...

---


### plan-zcoin-report-store-redeem-tabs & task-understanding

> Confluence 頁面 ID：79471882, 79471868
> 原始文件：[查看 plan](https://confluence.zbdigital.net/display/TCZB/plan-zcoin-report-store-redeem-tabs) | [查看 task-understanding](https://confluence.zbdigital.net/display/TCZB/task-understanding-zcoin-report-store-redeem-tabs)
> 摘要檔：[processed/79471882-summary.md](../../confluence/processed/79471882-summary.md), [processed/79471868-summary.md](../../confluence/processed/79471868-summary.md)
> Confluence 最後更新：2026-05-24
> 摘要最後同步：2026-05-27

**摘要**：
為 Z 幣報表新增商城兌換 Tab 的詳細技術設計，涵蓋 ProductService、PriceBackendService 與前端 Nuxt3 的 API 合約。

**關鍵設計決策**：
- 採用 BFF (PriceBackendService) 聚合 ProductService 與 MemberService，ProductService 一次回傳 redeemLogs 和 products 兩個 list
- ProductService 第一版實作採全量讀取+內存篩選，後續再優化
- 不修改既有 GET /api/v1/store/productredeemlogs 的行為，改用新路徑 /report，保持 backward compatibility
- ProductService 新 API 路徑建議為 /api/v1/store/productredeemlogs/report

**影響範圍**：
- PS-1 端點回傳的 products 是完整 ProductStore 物件，需注意資料量與敏感欄位

---

## 歷史決策類


### Sprint205 CodeReview

> Confluence 頁面 ID：55585158
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Sprint205+CodeReview)
> 摘要檔：[processed/55585158-summary.md](../../confluence/processed/55585158-summary.md)
> Confluence 最後更新：2025-04-01
> 摘要最後同步：2026-05-27

**決策背景**：
「取得所有商城商品」的效能優化需求。

**決策結論**：
組件商品數量不透過多次 API 請求取得，而是直接取 pclass 的進貨紀錄和兌換紀錄，針對 pclass 下的商品數量進行計算，以減少 API 請求次數。

**影響**：
此決策定義了商品數量查詢的實作模式，影響後續報表與商品查詢功能的設計。

---


### Sprint199 - CodeReview

> Confluence 頁面 ID：55583117
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Sprint199+-+CodeReview)
> 摘要檔：[processed/55583117-summary.md](../../confluence/processed/55583117-summary.md)
> Confluence 最後更新：2025-02-17
> 摘要最後同步：2026-05-27

**決策背景**：
Productservice 相關程式碼的 Code Review 改善。

**決策結論**：
- Cassandra 的 UPDATE 陳述式必須包含所有 partition key 與 clustering key 條件
- 資料型態統一使用 VARCHAR 取代 TEXT
- 對於 clustering key 欄位，因其禁止更新，直接省略相關驗證邏輯
- API 路由參數若未被使用即應移除

**影響**：
這些決策定義了 ProductService 的實作規範，特別是在 Cassandra 操作與 API 設計方面。

---

## 操作手冊類


### TCZB-3620 [訓練] - 新人訓練

> Confluence 頁面 ID：55582622
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55582622)
> 摘要檔：[processed/55582622-summary.md](../../confluence/processed/55582622-summary.md)
> Confluence 最後更新：2025-02-21
> 摘要最後同步：2026-05-27

**摘要**：
新人訓練計畫與執行記錄，涵蓋環境設置（JIRA、Confluence、GitLab）、專案開發實作（球王商品服務的時序圖、資料表設計、API CRUD、Redis 操作、中介服務）、以及 CI/CD 流程練習。

**AI 開發需要注意的部分**：
- 因 SSH 設定曾出現 BUG，改採 HTTP 配合 Token 方式進行 GitLab clone，若遇到相似問題可參考此備案
- 中介服務與後台服務皆須對輸入資料進行驗證，並檢查資料是否存在
- 環境配置可能存在不一致問題，新人導入時需注意環境準備