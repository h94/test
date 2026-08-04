# injuriesapi — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 09:58
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 技術設計類

### TCZB-2425[API] - NBA傷兵API

> Confluence 頁面 ID：44664866
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664866)
> 摘要檔：[processed/44664866-summary.md](../../confluence/processed/44664866-summary.md)
> Confluence 最後更新：2023-11-01 16:16
> 摘要最後同步：2026-05-27 08:47
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 NBA 傷兵資料的查詢與寫入 API。GET /v1/injurylist 支援依球種、聯盟、隊伍、日期過濾，回傳多層巢狀 JSON；POST /v1/update 接受含來源、球種、聯盟、隊伍、日期及球員傷勢資訊的陣列，全量更新至 Cassandra 資料表 injury_data。資料表以 (gtype, league, team, source) 為複合主鍵，傷兵明細以 JSON 字串儲存。開發此服務時，可依據此規格實作查詢與寫入邏輯，並注意輸入輸出格式轉換。

**關鍵設計決策**：
- 使用 Cassandra 作為儲存，主鍵設定為 (gtype, league, team, source)，以球種為分區鍵，其餘為集群鍵，支援快速篩選查詢。
- 傷兵明細（球員姓名、位置、傷勢、狀態）以 JSON 陣列字串存入 injury_info 欄位，保留結構彈性無需固定欄位。
- API 回傳格式採巢狀字典結構，外層為來源網站，中層為球種，內層為聯盟與隊伍，符合前端直接使用需求。

**注意事項**：
- ⚠️ 文件所屬路徑為「舊的Projects 1-200」，可能為已結案或不再維護的專案，需人工確認此 API 目前是否仍在使用。
- ⚠️ 文件中的 API URL 為內網 IP (192.168.55.60)，非公開地址，實作時需注意環境設定。

---

### TCZB-2504 [SportKing] - 傷兵

> Confluence 頁面 ID：47218907
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47218907)
> 摘要檔：[processed/47218907-summary.md](../../confluence/processed/47218907-summary.md)
> Confluence 最後更新：2023-02-16 15:50
> 摘要最後同步：2026-05-27 08:57
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義傷兵資料查詢 API（GET /injury/getinjurylist），支援三種查詢範圍：單一球隊、所有聯盟、單日所有名單。透過參數組合（球種、聯盟、隊伍、日期）區分查詢模式。回應結構包含球員姓名、日期、位置、傷勢名稱與狀態。此 API 規格可作為 injuriesapi 開發或對接的資料合約。

**關鍵設計決策**：
- —

**注意事項**：
- ⚠️ 文件最後更新為 2023-02-16，距今超過一年，需確認 API 是否仍維持相同規格
- ⚠️ 回應範例僅顯示部分欄位，實際可能包含更多屬性，需人工確認完整 schema

---

## 操作手冊類

### need db data

> Confluence 頁面 ID：55575041
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/need+db+data)
> 摘要檔：[processed/55575041-summary.md](../../confluence/processed/55575041-summary.md)
> Confluence 最後更新：2023-11-02 10:46
> 摘要最後同步：2026-05-27 09:58
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文說明如何定時獲取 CBS 傷兵資料並以 au8 的聯盟與隊名標準化後寫入 DB。流程為先從 DB 查詢 au8 聯盟與隊名，再透過 API 取得 CBS 傷兵資訊，最後以 au8 名稱寫入 DB，同步頻率為每小時一次。對 AI 開發而言，可了解傷兵資料的資料源、標準化規則及同步排程，避免重複實作相同邏輯。

**關鍵業務規則**：
- CBS 傷兵資訊必須使用 au8 的聯盟與隊名稱寫入 DB，不能直接使用原始資料源的名稱
- 資料同步頻率為每小時一次

**注意事項**：
- ⚠️ 文件更新時間為 2023-11-02，資料源或同步規則可能已變更，需確認是否仍有效