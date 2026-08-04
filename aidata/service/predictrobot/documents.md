# predictrobot — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 10:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### TCZB-4061 [PredictRobot] - 機器人預測調整

> Confluence 頁面 ID：79466590
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466590)
> 摘要檔：[processed/79466590-summary.md](../../confluence/processed/79466590-summary.md)
> Confluence 最後更新：2025-12-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄 PredictRobot 服務針對機器人下注分佈不均問題的調整，採用限額過濾與單帳號下注上限機制分散下注，並減少策略種類、引入假下注記錄。

**關鍵業務規則**：
- PredictRobot 每完成一輪下注後容器會關閉重啟
- 從 gamerobots 表中選取 enabled=3 的帳號進行過濾，使每日可下注帳號總數降至約 320 個
- 每日更新不能下注的帳號清單
- 每次下注之間需間隔 2.5 小時
- 帳號選擇順序：策略優先帳號 → 高手榜帳號 → 通用帳號，並檢查下注歷史中是否已有該場比賽記錄，若已下過則跳過
- 單一帳號下注上限：棒球、籃球為該球種聯盟可下注比賽數的 70%；足球為 20%~30%；冰球為 50%~70%；網球、電競為 30%~40%
- 2025-11-27 起策略數從 17 種減少至 12 種（取消策略 38,39,40,41,42），並取消策略優先帳號
- 2025-11-27 起新增假下注機制：每個帳號每筆下注有 20% 機率觸發假下注，即不下注但記錄下注記錄
- 棄注機制已被棄用

**注意事項**：
- ⚠️ 電競和網球在規則中合併為 30% 上限，但先前描述中網球曾提到增加至 3~4 成，需人工確認最終值
- ⚠️ enabled=3 的篩選邏輯是否已正式採用，需人工確認
- ⚠️ 「每個帳號可下單一聯盟所有注數的一半」為未來規劃，尚未實作


### TCZB-3862 [AI預測爬蟲] - 足球預測賽事爬取

> Confluence 頁面 ID：76546166
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546166)
> 摘要檔：[processed/76546166-summary.md](../../confluence/processed/76546166-summary.md)
> Confluence 最後更新：2025-10-07
> 摘要最後同步：2026-05-27

**摘要**：
記錄 AI 預測爬蟲新增的足球預測數據來源網站，包含預測格式與支援聯盟清單，以及 ForebetProvider cookie 過期處理、Scores24 反爬機制繞過、picksandparlays 棄用等技術決策。

**關鍵業務規則**：
- oddstrader 網站的足球賽事頁面沒有 AI 預測，因此不爬取足球聯賽，僅爬取 NFL
- 各網站的預測數據寫入格式不同，必須依循文件指定的欄位進行記錄
- picksandparlays 因站台改版後 API 不再更新，不再列入爬取範圍

**注意事項**：
- ⚠️ picksandparlays 站台已棄用，相關配置與資料格式應從現行程式碼中移除
- ⚠️ oddstrader 雖被列入但足球預測無法取得，實際僅爬取非足球聯盟


### 預測下注流程

> Confluence 頁面 ID：47220184
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220184)
> 摘要檔：[processed/47220184-summary.md](../../confluence/processed/47220184-summary.md)
> Confluence 最後更新：2023-04-18
> 摘要最後同步：2026-05-27

**摘要**：
定義自動下注機器人的框架，核心設計為一個帳號綁定一個策略，策略需決定進場時機、適用的球種和聯盟、及下注類型。

**關鍵業務規則**：
- 下注時獨贏或讓分只能選擇其中一個玩法
- 一個機器人帳號只能使用一個策略
- 策略必須能決定是否進場、適用的球種（可設 ALL）、聯盟（可設 ALL）、下注類型（HA 或 OU 或都下）
- target 欄位以 map 格式儲存球種對應的聯盟清單
- cache 欄位用於儲存已處理過的賽事 ID，避免重複下注
- enable 欄位為 0 時機器人不執行，為 1 時啟用

**注意事項**：
- ⚠️ 文件最後更新於 2023-04-18，屬於舊的 Projects，可能已有變更
- ⚠️ 「獨贏或讓分只能選一個」未明確指定作用域，需人工確認


### TCZB-2387 [InplzyZ] - 機器人預測分組

> Confluence 頁面 ID：55577031
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577031)
> 摘要檔：[processed/55577031-summary.md](../../confluence/processed/55577031-summary.md)
> Confluence 最後更新：2024-01-30
> 摘要最後同步：2026-05-27

**摘要**：
記錄機器人預測分組的現有邏輯與已知問題。目前依帳號前兩碼分為五組（BK、BS、SC、FL、HL），各組對應固定球種，但會導致跨球種帳號被限制。

**關鍵業務規則**：
- 目前依帳號前兩碼分為五組，各組對應固定的球種預測

**注意事項**：
- ⚠️ 現有分組邏輯使跨球種的莊家殺手帳號被限制在單一組別
- ⚠️ 文件未標明最終採用何種改進方案，需人工確認後續實施結果

---

## 歷史決策類


### TCZB-4061 [PredictRobot] - 機器人預測調整

> Confluence 頁面 ID：79466590
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466590)
> 摘要檔：[processed/79466590-summary.md](../../confluence/processed/79466590-summary.md)
> Confluence 最後更新：2025-12-01
> 摘要最後同步：2026-05-27

**決策背景**：
機器人下注集中在策略優先帳號及高手榜前幾名帳號，導致下注分佈不均。

**決策結論**：
採用限額過濾 + 單帳號下注上限（依球種聯盟區分比例）來分散下注，並減少策略數至 12 種、移除策略優先帳號、引入 20% 假下注記錄。放棄棄注機制，因其無法解決集中問題。

**影響**：
下注行為已調整為分散模式，假下注機制使下注記錄看起來更分散。策略優先帳號機制已取消。


### TCZB-3862 [AI預測爬蟲] - 足球預測賽事爬取

> Confluence 頁面 ID：76546166
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546166)
> 摘要檔：[processed/76546166-summary.md](../../confluence/processed/76546166-summary.md)
> Confluence 最後更新：2025-10-07
> 摘要最後同步：2026-05-27

**決策背景**：
ForebetProvider cookie 過期導致 403 問題；Scores24 遭封鎖；picksandparlays 改版後無可用資料。

**決策結論**：
- ForebetProvider 改為先直接爬取，遭 403 才啟動 undetected_chromedriver 取得 cookie 重試
- Scores24 將 httpx 更換為 tls_client 繞過反爬
- 停止維護 picksandparlays

**影響**：
爬蟲依賴的 HTTP 套件已變更；picksandparlays 相關程式碼應移除。


### TCZB-2387 [InplzyZ] - 機器人預測分組

> Confluence 頁面 ID：55577031
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577031)
> 摘要檔：[processed/55577031-summary.md](../../confluence/processed/55577031-summary.md)
> Confluence 最後更新：2024-01-30
> 摘要最後同步：2026-05-27

**決策背景**：
現有依帳號前兩碼分組的邏輯，導致跨球種的莊家殺手帳號被限制在單一組別。

**決策結論**：
提出兩個方案：(1) 在 gamerobots 表新增球種欄位，依帳號身分或近期行為固定球種；(2) 依上次預測球種決定本次預測。最終採用方案未明確記錄。

**影響**：
現行分組邏輯可能仍依賴帳號前兩碼，新增球種時需注意遷移策略。

---

## 技術設計類


### 預測下注流程

> Confluence 頁面 ID：47220184
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220184)
> 摘要檔：[processed/47220184-summary.md](../../confluence/processed/47220184-summary.md)
> Confluence 最後更新：2023-04-18
> 摘要最後同步：2026-05-27

**摘要**：
定義自動下注機器人的基本框架，採用一個帳號綁定一個策略的設計，使用 predict_robot 資料表管理配置。

**關鍵設計決策**：
- 採用一個帳號對應一個策略的簡單綁定
- 使用 map 巢狀結構靈活配置不同球種下的聯盟
- 設計 cache 欄位儲存已下注的賽事 ID，實現冪等性
- 透過 enable 欄位提供啟用/停用機制

**影響範圍**：
- predict_robot 資料表結構（strategy_id、target、cache、enable 欄位）
- 策略介面需支援進場判斷、球種聯盟配置、下注類型選擇


### TCZB-3862 [AI預測爬蟲] - 足球預測賽事爬取

> Confluence 頁面 ID：76546166
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546166)
> 摘要檔：[processed/76546166-summary.md](../../confluence/processed/76546166-summary.md)
> Confluence 最後更新：2025-10-07
> 摘要最後同步：2026-05-27

**摘要**：
記錄 AI 預測爬蟲的數據來源變更與反爬蟲技術調整。

**關鍵設計決策**：
- ForebetProvider 採用「先直接爬取，403 才拿 cookie 重試」機制
- Scores24 將 HTTP 請求套件由 httpx 更換為 tls_client
- 停止維護 picksandparlays 站台

**影響範圍**：
- 爬蟲模組的 HTTP 客戶端依賴
- picksandparlays 相關配置與程式碼應移除

---

## 操作手冊類

_（本服務暫無明顯的操作手冊類文件。TCZB-4061 和 TCZB-3862 等文件雖包含部分操作細節，但本質上屬於決策記錄或業務規範，已歸類至對應章節。）_

---


## ⚠️ 跨文件衝突與待人工確認事項

| 事項 | 來源文件 | 說明 |
|------|---------|------|
| 電競與網球下注上限 | TCZB-4061 | 網球先前描述為 3~4 成，後續與電競合併為 30%，是否需分開設定需確認 |
| enabled=3 篩選邏輯 | TCZB-4061 | 僅為測試手法，是否正式採用需確認 |
| 「獨贏或讓分只能選一個」作用域 | 預測下注流程 | 未明確指定是單場賽事還是整個策略 |
| 機器人分組改進方案 | TCZB-2387 | 未標明最終採用何種方案，需確認現有邏輯 |
| predict_robot 表與 gamerobots 表的關聯 | 預測下注流程 / TCZB-4061 | 兩份文件描述的資料表不同，需確認當前使用哪張表或如何關聯 |
| 策略 ID 清單變更 | TCZB-4061 / 預測下注流程 | TCZB-4061 提到策略從 17 種減至 12 種，predict_robot 表中的 strategy_id 對應需確認 |