# games DB — 完整使用脈絡

> 產出時間：2025-07-24 12:00
> 欄位結構定義：[games.json](./games.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| gameliveservice | owner | 讀、寫、刪 |
| predictservice | writer | 僅可更新 games_{sport_code} 表的 status, match_h, match_a, match_detail, resultinfo 欄位 |
| mergesite | reader | 唯讀，用於合併站台賽事資料時查詢比對 |
| backendservice | reader | 唯讀，組合資料後回傳前台 |
| pricecenterservice | writer / reader | 對 games_{sport_code} 表唯讀；對 aimerge_* 表可寫入 `aimerge_label_overrides`, `aimerge_source_mapping`, `aimerge_runtime_config`（詳見各表章節），其餘 aimerge_* 表唯讀。⚠️ 衝突待人工：原定義僅 reader，現依服務摘要擴展為部分表寫入角色，需確認授權邊界與安全規範。 |
| tradegameservice | reader | 唯讀，提供前端可下注比賽列表與賠率相關查詢 |
| syncservice | reader | 唯讀，增量或批次同步賽事資料 |
| predictrobot | reader | 唯讀，機器人預測策略查詢比賽狀態與比分 |

---

## Table：games_{sport_code}（所有 games_* 系列賽事資料表）

> 本 DB 含多張相同結構的賽事資料表（如 `games_bk`, `games_bm`, `games_bs`, `games_ck`, `games_es`, `games_fl`, `games_hb` 等，共 112 張），每張表代表不同的運動類別或聯盟，欄位定義完全一致，本節以通用結構進行說明。

### status 欄位

**型別**：text

**值定義與狀態流轉**：

```
     gameliveservice       gameliveservice       predictservice
      INSERT                UPDATE                UPDATE
     PreGame ─────────→ Live ─────────→ Final
         │
         └─────────────────────────────→ Cancelled
                       gameliveservice（管理員）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| PreGame | 未開始 | gameliveservice | INSERT 時預設值 |
| Live | 進行中 | gameliveservice | 比賽開始時根據即時資料觸發更新 |
| Final | 已結束 | predictservice | 賽果確認且結算完成後寫入 |
| Cancelled | 取消 | gameliveservice | 管理員在後台手動操作 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT status='PreGame' | 建立比賽 | 預設未開始 |
| gameliveservice | UPDATE status='Live' | 比賽開始 | 即時資料開始推送，自動觸發 |
| gameliveservice | UPDATE status='Cancelled' | 管理員操作 | 手動取消 |
| predictservice | UPDATE status='Final' | 賽果回傳且結算完成 | 只有 predictservice 有權設定 |
| predictservice | SELECT WHERE status='Live' | 查詢進行中比賽 | 判斷是否開放預測 |
| mergesite | SELECT WHERE status IN ('Live','Final') | 合併站台比對 | 僅查詢有效賽事進行比對 |
| backendservice | SELECT WHERE status IN ('Live','Final') | 前台查詢 | 不顯示未開始與取消的比賽 |
| pricecenterservice | SELECT WHERE status IN ('Live','Final') | 前台查詢 | 不顯示未開始與取消的比賽 |
| pricecenterservice | SELECT WHERE gdate BETWEEN ... AND lid = ... | 定期快取／報表查詢 | 必須指定日期範圍與聯盟，防止全表掃描 |
| tradegameservice | SELECT WHERE status IN ('PreGame','Live') | 提供可下注比賽列表 | 過濾已結束與取消的比賽 |
| tradegameservice | SELECT WHERE id = ? AND status IN ('PreGame','Live') | 單筆比賽查詢 | 確認比賽仍可交易 |
| syncservice | SELECT WHERE status IN ('PreGame','Live') | 增量同步進行中賽事 | 跳過 Final 賽事避免重複處理 |
| syncservice | SELECT WHERE status = 'Final' | 同步最終賽果 | 僅取已結束比賽 |
| predictrobot | SELECT WHERE status = 'Live' | 機器人預測策略 | 僅對進行中比賽進行預測 |

**⚠️ 跨服務限制**：

- status='Final' 只能由 predictservice 設定，gameliveservice 不可直接寫入
- status='Cancelled' 之後不可再變更為其他值，任何服務都不可修改
- mergesite 對所有欄位只有 SELECT 權限，不可執行任何寫入
- backendservice 對所有欄位只有 SELECT 權限，不可執行任何寫入
- pricecenterservice 對 games_{sport_code} 表只有 SELECT 權限，不可執行任何寫入（對 aimerge 表的寫入權限見後續章節）
- tradegameservice 對所有欄位只有 SELECT 權限，不可執行任何寫入
- syncservice 對所有欄位只有 SELECT 權限，不可執行任何寫入
- predictrobot 對所有欄位只有 SELECT 權限，不可執行任何寫入
- pricecenterservice 進行賽事查詢必須帶 gdate 範圍與 lid 等條件，避免全表掃描

---

### match_h / match_a 欄位

**型別**：bigint

**值定義與狀態流轉**：

無狀態流轉，僅為比分數值。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT match_h=0, match_a=0 | 建立比賽 | 預設 0 |
| gameliveservice | UPDATE match_h, match_a | 比賽進行中 | 即時更新主客隊得分 |
| predictservice | UPDATE match_h, match_a | 賽果結算時 | 覆蓋為最終比分（如有差異） |
| mergesite | SELECT | 合併比對 | 讀取比分 |
| backendservice | SELECT | 前台展示 | 讀取比分 |
| pricecenterservice | SELECT | 前台展示（不可單獨作為完賽判斷） | 讀取比分，必須搭配 status='Final' 確認賽事已結束 |
| tradegameservice | SELECT | 前台展示 | 讀取比分 |
| syncservice | SELECT | 增量同步 | 讀取比分 |
| predictrobot | SELECT | 機器人預測 | 讀取比分作為預測依據 |

**⚠️ 跨服務限制**：

- 當 status='Final' 後，gameliveservice 不可再更新 match_h 或 match_a
- predictservice 應僅在寫入 Final 狀態時一併設定最終比分，且之後不可再修改
- pricecenterservice 若需判斷賽事是否結束，應以 `status = 'Final'` 為準，不可僅靠 match_h / match_a 非空或非零
- predictrobot 預測時需以 status='Final' 的 match_h/match_a 為最終結果，進行中比賽的比分僅供參考

---

### match_detail 欄位

**型別**：jsonb

**值定義與狀態流轉**：

無狀態流轉，儲存各局／盤的詳細比分陣列（如 `[[1, 5, 4], [2, 3, 4]]`）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT match_detail='[]' | 建立比賽 | 預設空陣列 |
| gameliveservice | UPDATE match_detail | 比賽進行中 | 逐局更新詳細比分 |
| predictservice | UPDATE match_detail | 賽果結算時 | 寫入最終的完整詳細比分 |
| mergesite | SELECT | 合併比對 | 讀取詳細比分 |
| backendservice | SELECT | 前台展示 | 讀取詳細比分 |
| pricecenterservice | SELECT | 前台展示 | 讀取詳細比分（注意：僅在 status='Final' 後視為可信） |
| tradegameservice | SELECT | 前台展示 | 讀取詳細比分 |
| syncservice | SELECT | 增量同步 | 讀取詳細比分 |

**⚠️ 跨服務限制**：

- 與 match_h / match_a 相同，status='Final' 後只允許 predictservice 寫入一次，gameliveservice 不得再修改
- pricecenterservice 讀取時，仍應以 status='Final' 作為確認完賽的主要依據

---

### resultinfo 欄位

**型別**：jsonb

**值定義與狀態流轉**：

無狀態流轉，儲存賽果完整資訊（勝負、盤分、特殊事件等），由賽果預測或結算服務產生。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| predictservice | UPDATE resultinfo | 賽果結算完成後 | 寫入完整賽果 JSON |
| mergesite | SELECT | 合併比對 | 讀取賽果 |
| backendservice | SELECT | 前台查詢 | 讀取賽果 |
| gameliveservice | SELECT | 內部比對 | 唯讀，不可寫入 |
| pricecenterservice | SELECT | 前台查詢 | 讀取賽果（不作為完賽判定，仍以 status 為準） |
| tradegameservice | SELECT | 前台查詢 | 讀取賽果 |

**⚠️ 跨服務限制**：

- gameliveservice 無權寫入 resultinfo
- resultinfo 一旦寫入即不可修改（如需修正需透過專門的管理 API，非本節所涉服務）
- mergesite 無權寫入 resultinfo
- tradegameservice 無權寫入 resultinfo
- pricecenterservice 對外 API 不可回傳未清洗的 resultinfo，避免洩漏內部處理邏輯或敏感設定

---

### source 欄位

**型別**：text

**值定義與狀態流轉**：

無狀態流轉，標示賽事資料來源站台（如 `panda`, `1xbet.com` 等）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT source | 建立比賽 | 來自哪個資料源 |
| mergesite | SELECT | 合併比對 | 識別賽事來源，進行跨站台對應 |
| mergesite | SELECT WHERE source IN (...) | 合併站台 | 依特定站台篩選賽事 |
| backendservice | SELECT | 前台展示 | 可能用於顯示資料來源 |
| pricecenterservice | SELECT | 前台展示 | 可能用於顯示資料來源 |
| tradegameservice | SELECT WHERE source = ? | 提供可下注比賽 | 過濾特定站台的賽事 |
| syncservice | SELECT WHERE source = ? | 增量同步 | 僅獲取指定站台的賽事 |
| predictrobot | SELECT WHERE source = ? | 機器人預測 | 依來源站台篩選賽事 |

**⚠️ 跨服務限制**：

- source 在 INSERT 時設定，之後不應變更
- mergesite 僅讀取 source 進行比對，無權新增或修改
- tradegameservice 查詢時必須指定 source 條件，避免跨資料來源的比賽 ID 衝突或混淆

---

### gdate / gtime 欄位

**型別**：gdate 為 date（無時區），gtime 為 time without time zone

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT gdate, gtime | 建立比賽時設定開賽日期與時間 |
| gameliveservice | UPDATE gdate, gtime | 賽程異動時更新 |
| mergesite | SELECT | 比對賽事時間以確認是否為同一場比賽 |
| backendservice | SELECT | 前台展示開賽時間，需轉換為台灣時間 |
| pricecenterservice | SELECT（必須帶 gdate 範圍與 lid） | 前台展示開賽時間，需轉換為台灣時間；查詢時務必使用 `gdate BETWEEN` 條件並搭配 `lid` 過濾，禁止全表掃描 |
| tradegameservice | SELECT WHERE gdate BETWEEN ... AND lid = ... | 提供可下注比賽列表 | 必須指定日期範圍與聯盟，避免全表掃描 |
| syncservice | SELECT WHERE gdate = CURRENT_DATE | 日級同步 | 依日期批次處理 |
| syncservice | SELECT WHERE create_at > ? ORDER BY create_at | 增量同步 | 依建立時間戳增量獲取 |

**⚠️ 注意**：
- gdate 與 gtime 為無時區欄位，各服務需自行約定時區解釋。依現有實務，gameliveservice 儲存時應以 UTC 為準
- mergesite 進行跨站台比對時，需考慮時差容忍範圍（通常 ± 數分鐘內視為同一場）
- backendservice 與 pricecenterservice 回傳前台時須轉為台灣時間（+8 小時）
- ⚠️ 衝突待人工：mergesite 摘要中提及「查詢比對」，但未明確說明時區處理策略；建議與 gameliveservice 一致，以 UTC 為內部比對基準

---

### siteidmaps 欄位

**型別**：jsonb

**值定義與狀態流轉**：

無狀態流轉，儲存各來源站台的對應識別資訊（如 `{"1xbet.com": "[{\"Site\": \"1xbet.com\", \"SiteGID\": \"...\", \"SiteLID\": \"...\"}]"}`）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT siteidmaps | 建立比賽 | 記錄各站台的對應識別碼 |
| gameliveservice | UPDATE siteidmaps | 賽事資料更新 | 新增或修改站台對應 |
| mergesite | SELECT | 合併比對 | 用於跨站台賽事去重與合併 |
| backendservice | SELECT | 前台查詢 | 可能用於站台對應顯示 |
| pricecenterservice | SELECT | ⚠️ 衝突待人工：前台查詢（摘要規範為不可回傳） | 現有設計可能用於站台對應顯示，但摘要要求 pricecenterservice 對外 API 禁止回傳 siteidmaps；待確認實際前端需求 |
| pricecenterservice | SELECT | 後台管理查詢 | 內部管理用途可讀取，前台 API 必須屏蔽 |
| tradegameservice | SELECT | 前台查詢 | 可能用於站台對應顯示 |
| syncservice | SELECT | 內部比對 | 增量同步時讀取，不對外暴露 |

**⚠️ 跨服務限制**：

- mergesite 僅讀取 siteidmaps 進行合併比對，不可直接修改
- siteidmaps 由 gameliveservice 維護，其他服務無權寫入
- pricecenterservice 對外查詢 API 嚴禁回傳 siteidmaps（含原始 JSON 與任何衍伸資訊），僅後台管理端點可有限度讀取
- syncservice 在增量同步時可讀取 siteidmaps，但不可對外暴露

---

### teams 欄位

**型別**：jsonb

**值定義與狀態流轉**：

無狀態流轉，儲存隊伍內部附加資訊（預設為 `{}`）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT teams='{}' | 建立比賽 | 預設空物件 |
| gameliveservice | UPDATE teams | 賽事資料更新 | 更新隊伍資訊 |
| pricecenterservice | SELECT | 後台管理查詢 | 內部管理用途可讀取，前台 API 必須屏蔽 |

**⚠️ 跨服務限制**：

- teams 含站台特有的隊伍內部附加資訊，若未經業務處理，不應直接暴露於一般查詢
- pricecenterservice 對外查詢 API 嚴禁回傳 teams，僅後台管理端點可有限度讀取

---

### create_at 欄位

**型別**：bigint

**值定義與狀態流轉**：

無狀態流轉，儲存記錄建立時間的 Unix 毫秒時間戳。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT create_at | 建立比賽 | 寫入當前時間戳 |
| syncservice | SELECT WHERE create_at > ? ORDER BY create_at | 增量同步 | 依時間戳增量獲取新進或更新賽事 |
| predictrobot | SELECT | 內部查詢 | 查詢時若用時間範圍篩選，需轉換為毫秒時間戳 |

**⚠️ 跨服務限制**：

- create_at 對一般使用者無業務意義，pricecenterservice 對外 API 不建議回傳
- syncservice 增量同步時以 create_at 為基準，必須確保該欄位在 UPDATE 時也一併更新

---

### otherinfo 欄位

**型別**：jsonb

**值定義與狀態流轉**：

無狀態流轉，儲存非結構化擴展資訊。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT otherinfo='{}' | 建立比賽 | 預設空物件 |
| gameliveservice | UPDATE otherinfo | 賽事資料更新 | 更新擴展資訊 |
| predictservice | SELECT | 內部查詢 | 唯讀 |
| pricecenterservice | SELECT | 後台管理查詢 | 內部管理用途可讀取，前台 API 應過濾 |

**⚠️ 跨服務限制**：

- otherinfo 可能包含未清洗的內部數據，建議僅後台管理 API 回傳
- pricecenterservice 對外查詢 API 應避免回傳 otherinfo，除非經明確授權

---

### lid 欄位

**型別**：bigint

**值定義與狀態流轉**：

無狀態流轉，標示賽事所屬聯盟 ID。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT lid | 建立比賽 | 設定所屬聯盟 |
| pricecenterservice | SELECT WHERE gdate BETWEEN ... AND lid = ... | 定期快取／報表查詢 | 必須搭配 lid 過濾 |
| tradegameservice | SELECT WHERE lid = ? | 提供可下注比賽 | 依聯盟篩選賽事 |
| syncservice | SELECT WHERE lid = ? AND gdate = ? | 清理過期資料 | 依業務主鍵刪除無效賽事 |
| predictrobot | SELECT WHERE lid = ? | 機器人預測 | 依聯盟篩選賽事 |

**⚠️ 跨服務限制**：

- lid 在 INSERT 時設定，之後不應變更
- 所有查詢服務應善用 lid 條件以避免全表掃描

---

## Table：aimerge_match_predictions

> AI 合併預測結果表，記錄跨站台賽事配對的相似度評分與狀態。

### status 欄位

**型別**：text

**值定義**：
由 AI 合併排程系統維護，pricecenterservice 唯讀。已知常見狀態值（以下清單可能不完整，以實際排程寫入為準）：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| pending | 待人工審核 | 合併排程 | 預測分數落在需複審區間時 |
| auto_confirmed | 自動確認 | 合併排程 | 預測分數極高，無需人工介入 |
| auto_error | 自動判定為不同比賽 | 合併排程 | 預測分數極低，視為錯誤配對 |
| conflict | 發生衝突 | 合併排程 | 多個來源結果矛盾 |
| inferred_confirmed | 推斷確認 | 合併排程 | 透過間接規則確認 |
| inferred_rejected | 推斷排除 | 合併排程 | 透過間接規則排除 |

**pricecenterservice 操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | SELECT WHERE status IN ('pending', 'auto_confirmed') AND game_type = ? AND gdate = ? | 查詢待審核配對 | 後台人工審核列表，避免全表掃描 |

**⚠️ 跨服務限制**：

- pricecenterservice 對本表 **僅有 SELECT 權限**，不可執行 INSERT / UPDATE / DELETE。
- 查詢時必須帶 `game_type` 與 `gdate` 條件，不可全表掃描。

---

### 其他查詢相關欄位

| 欄位 | 型別 | 說明 |
|------|------|------|
| game_type | text | 運動類型（如 bk, ft） |
| gdate | text | 比賽日期（字串格式） |
| source_b | text | 來源 B 站台識別 |
| game_a_sitegid | text | 站台 A 的賽事 GID |
| source_b_sitegid | text | 站台 B 的賽事 GID |
| prediction_id | text | 預測唯一識別碼 |
| score | double precision | 配對相似度分數 |
| score_detail | jsonb | 配對詳細資訊 |
| inferred_via | text | 推斷路徑（若非直接預測） |

pricecenterservice 僅能查詢這些欄位，用於呈現審核資訊，不可修改。

---

## Table：aimerge_label_overrides

> 人工審核覆蓋表，允許管理員對預測結果進行標注或排除。

### 可寫入欄位（pricecenterservice）

| 欄位 | 型別 | 寫入限制 | 說明 |
|------|------|---------|------|
| override_label | boolean | 人工審核時可設定 | 最終判定是否為同一場比賽（`true`：是；`false`：否） |
| excluded_from_training | boolean | 預設 `false`，可手動設為 `true` | 是否排除於訓練資料集 |
| reason | text | 可選擇性填寫 | 變更原因說明 |
| reviewed_by | text | 必須填寫 | 審核人員識別 |
| reviewed_at | timestamp with time zone | 自動設定為當前時間 | 審核時間戳 |

**⚠️ 嚴禁修改的欄位**：`game_type`, `gdate`, `prediction_id`, `source_b`, `game_a_sitegid`, `source_b_sitegid`。
- 這些欄位為關聯鍵值，僅能透過對應的預測記錄或自動化流程建立，人工審核時不可直接修改。

**pricecenterservice 操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT / UPDATE | 人工審核操作 | 寫入上述允許的欄位，需驗證審核者權限 |
| pricecenterservice | SELECT WHERE game_type = ? AND gdate = ? | 查詢歷史覆蓋記錄 | 可依 `reviewed_by`, `reviewed_at` 排序 |

**⚠️ 注意**：
- 執行 UPDATE 前必須確保 `prediction_id` 對應的記錄已存在（由合併排程建立）。
- 不可透過本表直接建立新的預測關聯，僅能修改現有記錄。

---

## Table：aimerge_source_mapping

> 站台賽事對應關係確認表，記錄人工或自動確認的跨站台配對。

### 可寫入欄位（pricecenterservice）

| 欄位 | 型別 | 寫入限制 | 說明 |
|------|------|---------|------|
| confirmed_at | timestamp with time zone | 自動設定為當前時間 | 確認時間 |
| confirmed_by | text | 必須填寫 | 確認人員 |

**禁止直接修改的欄位**：`game_type`, `gdate`, `game_a_sitegid`, `source_b`, `source_b_sitegid`, `prediction_id`。
- 這些映射關係由預測流程自動建立，pricecenterservice 僅能透過確認 API 寫入 `confirmed_at` 與 `confirmed_by`，不可人工直接建立新對應。

**pricecenterservice 操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | UPDATE | 人工確認配對正確時 | 設定 `confirmed_at`, `confirmed_by`，並與對應的 `prediction_id` 關聯 |
| pricecenterservice | SELECT WHERE game_type = ? AND gdate = ? [AND source_b = ?] | 查詢已確認的對應 | 避免全表掃描 |

---

## Table：aimerge_runtime_config

> 執行期配置表，控制 AI 合併流程的參數。

### 寫入規範（pricecenterservice）

- 限授權管理員透過專用 API 進行新增或更新。
- 修改記錄時必須撰寫 `updated_by`, `updated_at`, `change_reason`。
- **不可直接刪除**記錄，若需停用應將 `is_active` 更新為 `false`。
- `params`（JSONB）格式需符合預定義結構；變更時需管理版本（`version_id`, `parent_version_id`）。

**重要欄位**：

| 欄位 | 型別 | 說明 |
|------|------|------|
| scope | text | 配置作用域（如 game_type） |
| version_id | uuid | 唯一版本識別碼，由 DB 自動產生 |
| params | jsonb | 參數內容 |
| effective_from | timestamp with time zone | 生效時間 |
| is_active | boolean | 是否啟用（`true`／`false`） |
| updated_by | text | 更新人員 |
| updated_at | timestamp with time zone | 更新時間（預設 now()） |
| change_reason | text | 變更原因 |

**pricecenterservice 操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT / UPDATE | 管理員變更參數 | 需驗證授權，記錄變更原因 |
| pricecenterservice | SELECT WHERE is_active = true AND effective_from <= NOW() ORDER BY version_id DESC LIMIT 1 | 讀取當前生效配置 | 確保取得最新啟用版本 |

---

## Table：aimerge_daily_reports

> 每日合併報告，彙總預測審核統計資訊。

pricecenterservice **唯讀**。查詢時必須帶入 `game_type` 與 `report_date` 範圍，禁止全表掃描。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | SELECT WHERE game_type = ? AND report_date BETWEEN ? AND ? | 產生日報表或後台查詢 | 僅供內部管理 |

---

## Table：aimerge_backtest_runs

> 回測執行記錄，用於評估 AI 模型改善效果。

pricecenterservice **唯讀**。查詢需指定 `game_type` 與 `backtest_date` 範圍。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | SELECT WHERE game_type = ? AND backtest_date BETWEEN ? AND ? | 後台檢視回測結果 | 注意：`improved_samples`, `regression_samples` 等欄位不對外提供原始內容 |

---

## Table：aimerge_historical_runs

> 歷史批次執行記錄，用於追蹤合併任務狀態。

pricecenterservice **唯讀**。查詢需指定 `game_type` 與 `target_date` 範圍。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | SELECT WHERE game_type = ? AND target_date BETWEEN ? AND ? | 後台查詢執行紀錄 | 可依 `status` 過濾 |

---

## Table：aimerge_team_aliases

> 隊伍別名對照表，供內部匹配演算法使用。

pricecenterservice **唯讀**，且不對外暴露此表內容。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | SELECT | 內部匹配演算法調用（後台） | 嚴禁透過前台 API 回傳任何別名資料 |

---

## Redis — GameLiveCache

### game:live:{gameId}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SETEX | gameliveservice | 當 status 變更為 Live 時 | TTL：10 分鐘，快取進行中比賽基本資訊 |
| GET | mergesite | 合併比對進行中賽事 | 減輕 DB 負擔 |
| GET | backendservice | 前台讀取進行中比賽列表 | 減輕 DB 負擔 |
| GET | pricecenterservice | 前台讀取進行中比賽列表 | 減輕 DB 負擔 |
| GET | tradegameservice | 前台讀取進行中比賽列表 | 減輕 DB 負擔 |
| DEL | gameliveservice | 當 status 變更為 Final 或 Cancelled 時 | 立即清除快取 |

**⚠️ 注意**：

- status 變更為 Final 或 Cancelled 時必須主動 DEL，不可只靠 TTL 自然過期
- mergesite 讀不到此 Key 時必須 fallback 查 DB，不可直接報錯
- backendservice 讀不到此 Key 時必須 fallback 查 DB，不可直接報錯
- pricecenterservice 讀不到此 Key 時必須 fallback 查 DB，不可直接報錯
- tradegameservice 讀不到此 Key 時必須 fallback 查 DB，不可直接報錯
- ⚠️ 衝突待人工：mergesite 摘要中未明確提及 Redis 快取操作；此處假設其與 backendservice 同為 reader，行為一致，且在 nightly_batch 觸發的合併流程中可透過快取加速進行中賽事比對

---

## 常見錯誤（跨服務）

### games_{sport_code} 表相關
- ❌ gameliveservice 直接把 status 改為 Final → 只有 predictservice 可以設定結束狀態
- ❌ backendservice、pricecenterservice、mergesite 或 tradegameservice 查詢忘記排除 status 為 PreGame 或 Cancelled → 讀取到不該處理的比賽資料
- ❌ status 變更後沒有主動 DEL Redis 快取 → 各服務讀到過期快取，資料不一致
- ❌ gameliveservice 在 status='Final' 後仍更新比分 → 破壞最終結果一致性
- ❌ predictservice 寫入 resultinfo 後又被 gameliveservice 覆蓋 → 權限控制不當
- ❌ mergesite 試圖寫入 status, match_h, match_a, resultinfo, source 等欄位 → mergesite 為 reader，不可執行任何寫入操作
- ❌ pricecenterservice 試圖寫入 games_{sport_code} 表的任何欄位 → pricecenterservice 對這些表只有 SELECT 權限
- ❌ tradegameservice 試圖寫入任何欄位 → tradegameservice 為 reader，不可執行任何寫入操作
- ❌ syncservice 試圖寫入任何欄位 → syncservice 為 reader，不可執行任何寫入操作
- ❌ predictrobot 試圖寫入任何欄位 → predictrobot 為 reader，不可執行任何寫入操作
- ❌ mergesite 合併比對時未考慮 gdate/gtime 時區 → 可能將不同比賽誤判為同一場，或同一場比賽視為不同
- ❌ mergesite 比對 siteidmaps 時未處理 JSON 結構差異 → 站台對應失敗，造成重複賽事
- ❌ pricecenterservice 回傳 siteidmaps 至前台 API → 洩漏內部站台對應資訊（違反摘要規範）；後台管理端點方可讀取
- ❌ pricecenterservice 回傳 teams 或 create_at 至前台 API → 無業務意義且可能洩漏內部資料

### aimerge_* 表相關
- ❌ pricecenterservice 直接修改 `aimerge_match_predictions` 的 status 或 score → 本表僅供 AI 排程系統維護，pricecenterservice 為唯讀
- ❌ pricecenterservice 試圖修改 `aimerge_label_overrides` 中的 `game_type` 或 `prediction_id` → 這些欄位禁止人工異動，只能審核標籤
- ❌ pricecenterservice 在沒有對應 prediction_id 的情況下 INSERT `aimerge_source_mapping` → 映射關係必須由預測記錄驅動，不可憑空建立
- ❌ pricecenterservice 刪除 `aimerge_runtime_config` 記錄 → 應改為將 `is_active` 設為 `false` 進行軟停用，以保留歷史
- ❌ 查詢 `aimerge_daily_reports`、`aimerge_backtest_runs`、`aimerge_historical_runs` 時未帶 `game_type` 與日期範圍 → 造成全表掃描，影響效能
- ❌ 將 `aimerge_team_aliases` 的資料回傳至前台 API → 內部匹配數據不應對外暴露