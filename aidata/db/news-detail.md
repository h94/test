# news DB — 完整使用脈絡

> 產出時間：2026-05-30 08:23  
> 欄位結構定義：[news.json](./news.json)  
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| newsservice | owner | 讀、寫、刪 |
| gamesettingsite | reader | 唯讀（展示用途） |
| zaiservice | ⚠️ reader (摘要聲稱為 owner) | 唯讀（內部查詢） |
| pricebackendservice | reader | 唯讀（組合展示資料） |
| pricecentersite | reader | 唯讀（夜間排程讀取，用於組合價格相關資訊） |

⚠️ **衝突待人工**：  
1. `gamesettingsite` 的服務摘要中聲明對 `news` keyspace 擁有 **owner / writer / reader** 權限，但此處角色定為 `reader`；後續多個欄位操作明細中亦標記衝突，請確認實際寫入權限。  
2. `zaiservice` 在服務摘要中聲明對 `news` keyspace 擁有 **owner** 權限，但先前定義為 `reader` 且跨服務限制也僅允許 SELECT。請確認實際角色並一致化。

---

## Table：ainews（含 ainews_gs / ainews_lt）

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     newsservice           newsservice           newsservice
      INSERT                UPDATE                UPDATE
     value=0 ───────────→ value=1 ───────────→ value=2
                                  │
                                  └────────────────→ value=2 (直接修正)
                               newsservice UPDATE（特殊條件）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 待處理 | newsservice | INSERT 時預設值，AI 尚未回應 |
| 1 | 已回應 | newsservice | LLM 回調寫入 anwser 完成後 |
| 2 | 已修正 | newsservice | 管理後台觸發 reanwser 修正後 |

⚠️ **衝突待人工**：根據 `zaiservice` 服務摘要，`ainews` 表的 `status` 欄位另有定義：`2`=賽前, `0`=實況, `1`=賽後, `>2`=生成中。與上表定義（`0`=待處理, `1`=已回應, `2`=已修正，且 sample 中出現 `status=11`）衝突。可能為不同業務場景使用同一欄位，需確認實際狀態碼含義並統一修正。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT status=0 | 用戶提問寫入 | 預設待處理 |
| newsservice | UPDATE status=1 | LLM 回調完成 | 寫入 anwser 後 |
| newsservice | UPDATE status=2 | 管理後台修正 | 寫入 reanwser 後 |
| newsservice | SELECT WHERE status=1 | 前台查詢 | 只顯示已回應記錄 |
| newsservice | SELECT WHERE status IN(1,2) AND used=0 | AI 重新回答 | 篩選可重用的記錄 |
| gamesettingsite | SELECT WHERE status=1 | 前台展示新聞 | 只顯示已回應且無待修正 |
| gamesettingsite | SELECT WHERE status IN(0,1,2) AND used=0 | AI 重新回答 | 避免重複使用同一筆 |
| zaiservice | SELECT WHERE status=1 | 內部查詢 | 唯讀，僅查已回應記錄 |
| pricebackendservice | SELECT WHERE status IN (1,2) | 組合價格資訊 | 唯讀，取得已回應的新聞資料以呈現 |
| pricecentersite | SELECT WHERE status IN (1,2) | 夜間排程讀取 | 唯讀，取得已回應的新聞用於組合價格相關資訊 |

**⚠️ 跨服務限制**：
- status=1 → 2 只能由 newsservice（或 gamesettingsite 管理後台）設定，不可跳過 1 直接寫入 2
- status 僅可遞增，不得回退（0→1→2），任何服務都不可將 status 改回 0
- zaiservice 對 ainews 系列表僅有 SELECT 權限，不可執行任何寫入操作
- pricebackendservice 僅有 SELECT 權限，不可執行任何寫入操作
- pricecentersite 僅有 SELECT 權限，不可執行任何寫入操作

---

### used 欄位

**型別**：int

**值定義**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未使用 | newsservice | INSERT 時預設值 |
| 1 | 已使用 | newsservice / gamesettingsite | 擷取結果後標記，不可重設為 0 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT used=0 | 建立記錄 | 預設未使用 |
| newsservice | UPDATE used=1 | 擷取結果後 | 不可重設 |
| gamesettingsite | UPDATE used=1 | 展示服務使用後 | ⚠️ 衝突待人工：gamesettingsite 在服務角色總覽中為 reader，此處出現寫入操作，請確認權限。 |
| zaiservice | SELECT | 查詢記錄 | 唯讀，不寫入 |
| pricebackendservice | SELECT | 查詢記錄 | 唯讀，不寫入 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，不寫入 |

**⚠️ 跨服務限制**：
- used=1 不可由任何服務重設為 0，標記即不可逆

---

### question / anwser / reanwser 欄位

**型別**：text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT question | 用戶提問 | 原始提問，不可手動篡改 |
| newsservice | UPDATE anwser | LLM 回調完成 | 僅由 LLM 服務回寫 |
| newsservice | UPDATE reanwser | 管理後台修正 | 僅在 status=1 後可寫入 |
| gamesettingsite | SELECT | 前台展示 | 不直接回傳原始內容 |
| zaiservice | SELECT | 內部查詢 | 唯讀，不對外暴露 |
| pricebackendservice | SELECT | 組合價格資訊 | 唯讀，不對外暴露 |
| pricecentersite | SELECT | 排程讀取新聞內容 | 唯讀，不對外暴露（用於內部組合價格資訊） |

**⚠️ 注意**：
- anwser / reanwser 對外 API 一律隱藏，僅返回 articleid、createtime 等元資訊

---

### llmhashkey 欄位

**型別**：text（Clustering Key）

**值定義**：由系統根據 `llmsettings` 內容自動計算之哈希值

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT（系統自動） | 建立記錄時 | 不可手動指定或修改 |
| gamesettingsite | — | — | ⚠️ 衝突待人工：若 gamesettingsite 有寫入權限，不可手動修改 llmhashkey |
| zaiservice | SELECT | 內部查詢 | 唯讀 |
| pricebackendservice | SELECT | 組合價格資訊 | 唯讀 |
| pricecentersite | SELECT | 排程讀取 | 唯讀 |

**⚠️ 注意**：
- llmhashkey 由系統自動生成，任何服務不得手動設定或修改，否則可能導致數據不一致。
- 該欄位作為 clustering key 之一，影響查詢排序，修改時需重寫整行。

**⚠️ 跨服務限制**：
- 嚴禁任何服務手動 INSERT/UPDATE llmhashkey，僅由系統內部流程處理。

---

### llmsettings 欄位

**型別**：map<text, text>

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | LLM 呼叫前設定 | 包含模型名稱、溫度等參數 |
| gamesettingsite | INSERT/UPDATE | 管理後台配置 | ⚠️ 衝突待人工：gamesettingsite 在服務角色總覽中為 reader，此處出現寫入操作，請確認權限。 |
| zaiservice | SELECT | 內部查詢 | 唯讀，不對外提供 GET 回傳 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀，不對外提供 GET 回傳 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，不對外暴露 |

**⚠️ 注意**：
- 可能包含敏感參數（如 API 金鑰雜湊），不得未經檢查直接寫入，且不對外暴露

---

### bets 欄位

**型別**：list<text>

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | 投注序列化寫入 | 內部分析數據 |
| gamesettingsite | SELECT | 管理後台查詢 | 不對外暴露 |
| zaiservice | SELECT | 內部查詢 | 唯讀，不對外暴露 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀，不對外暴露 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，不對外暴露（用於價格分析） |

**⚠️ 注意**：
- 屬內部分析數據，對外 API 一律隱藏

---

## Table：aireports

### results 欄位

**型別**：map<text, text>

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | AI 分析完成後 | 外部不可主動填充 |
| gamesettingsite | SELECT | 管理後台查詢 | 不對外暴露詳細內容 |
| zaiservice | SELECT | 內部查詢 | 唯讀 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，用於價格相關分析 |

**⚠️ 注意**：
- `results` 欄位僅由 AI 分析完成後寫入，外部（包括管理後台）不可主動填充
- bets / results / others 中的鍵值對結構由業務協定約束，不可隨意增減未知鍵

---

## Table：aifunshits

### funsname 欄位

**型別**：text（主鍵）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT | 管理後台建立 | 主鍵唯一，不重複 |
| gamesettingsite | INSERT | 管理 API 初始化 | ⚠️ 衝突待人工：gamesettingsite 在服務角色總覽中為 reader，此處出現寫入操作，請確認權限。 |
| zaiservice | SELECT | 內部查詢 | 唯讀 |
| pricebackendservice | SELECT | 取得功能提示設定 | 唯讀，組合顯示用 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，取得 AI 提示設定供內部使用 |

---

### aihints / workspace 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | 管理後台寫入 | 僅由管理介面操作 |
| gamesettingsite | INSERT/UPDATE | 管理 API 寫入 | ⚠️ 衝突待人工：gamesettingsite 在服務角色總覽中為 reader，此處出現寫入操作，請確認權限。 |
| pricebackendservice | SELECT | 取得提示內容 | 唯讀，取得 AI 提示 |
| pricecentersite | SELECT | 排程讀取提示內容 | 唯讀，用於夜間批次處理 |

---

## Table：botarticles

### predict 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | 機器人產生文章時寫入 | 預測內容 |
| zaiservice | SELECT | 內部查詢 | 唯讀 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，用於價格相關資訊組合 |

---

## Table：commonarticles

### predict 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | 管理後台寫入 | 一般文章預測 |
| zaiservice | SELECT | 內部查詢 | 唯讀 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀 |
| pricecentersite | SELECT | 排程讀取 | 唯讀，用於價格組合 |

---

### scores 欄位

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newsservice | INSERT/UPDATE | 管理後台寫入 | 分數/評分 |
| pricebackendservice | SELECT | 內部查詢 | 唯讀 |
| pricecentersite | SELECT | 排程讀取 | 唯讀 |

---

## Redis

本資料庫目前**未使用 Redis**。若未來引入快取，應遵從以下規範：

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| — | — | — | 待擴充 |

---

## 常見錯誤（跨服務）

- ❌ newsservice 直接把 status 改為 2（跳過 1） → 只能依序流轉：0 → 1 → 2
- ❌ 查詢 ainews 系列表時未帶入 gdate → 必須至少指定 gdate（分區鍵），否則觸發全表掃描
- ❌ 前台查詢未排除 status=0（待處理）或使用錯誤條件 → 前台只應顯示 status=1 的記錄
- ❌ used 已為 1 卻嘗試重設為 0 → used 不可逆，標記後無法重設
- ❌ anwser / reanwser / llmsettings / bets 等敏感欄位未遮蔽即回傳 → 這些欄位對外 API 一律隱藏
- ❌ 外部服務直接寫入 llmsettings → 僅 newsservice 或 gamesettingsite 管理後台可寫入（⚠️ 衝突待人工：gamesettingsite 寫入權限待確認）
- ❌ zaiservice 執行寫入操作 → zaiservice 對 news keyspace 僅有 SELECT 權限
- ❌ pricebackendservice 執行寫入操作 → pricebackendservice 對 news keyspace 僅有 SELECT 權限
- ❌ pricecentersite 執行寫入操作 → pricecentersite 僅為 reader，對所有表只有 SELECT 權限，不可 INSERT / UPDATE / DELETE
- ❌ pricecentersite 排程讀取時未指定分區鍵 → 若未帶 gdate 等必要分區條件可能造成全表掃描，影響效能
- ❌ aireports 查詢時未指定完整主鍵（gdate, gtype, lid） → 不支援全範圍掃描，須精確查詢
- ❌ sports_{gameType} 動態表名模糊匹配 → 必須明確指定 gameType，不可模糊查詢
- ❌ gamesettingsite 寫入 used / llmsettings 等欄位（若權限僅為 reader） → 應確認是否剝奪寫入權限，若非必要寫入應移除
- ❌ 手動設定或修改 llmhashkey → 該欄位由系統自動計算，任何服務不得手動寫入

---

⚠️ **待人工審核事項**：
1. `gamesettingsite` 服務角色總覽定為 `reader`，但服務摘要聲明有 `owner/writer/reader` 權限；部分欄位（used, llmsettings, aifunshits 相關）已有寫入操作衝突標記，請確認最終角色並修改文件。
2. `gamesettingsite` 對 `ainews` 系列表的寫入權限（尤其是 `used`, `llmsettings`）需重新評估。
3. `zaiservice` 角色衝突：服務摘要聲稱為 `owner`，但目前定義為 `reader` 且跨服務限制僅允許 SELECT，請確認實際權限並統一。
4. `status` 欄位語意衝突：依現有文件定義為 0=待處理、1=已回應、2=已修正；服務摘要中另有 2=賽前、0=實況、1=賽後、>2=生成中的描述，且資料 sample 出現 status=11。兩套語意可能並存於不同業務場景，需釐清並修正文件。
5. 所有標記「⚠️ 衝突待人工」的項目請資深工程師決議後修正。