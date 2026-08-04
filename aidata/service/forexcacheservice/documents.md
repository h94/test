# forexcacheservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-26 13:09
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

<!--
文件類型說明：
  business_rule    業務規範（功能應該怎麼運作）← 最重要，AI 開發時必讀
  technical_design 技術設計（如何實作）
  decision_record  歷史決策（為什麼這樣做）
  operation_guide  操作手冊（怎麼操作）

優先順序：business_rule > decision_record > technical_design > 其他
當此文件和 service-detail.md 有衝突時，以此文件為準。
-->

## 業務規範類

<!--
這類文件最重要，AI 撰寫 Plan 時必須對照此區塊。
業務規則的優先順序高於 service-detail.md 的推論內容。
-->

_（無相關業務規範文件）_

---

## 技術設計類

<!--
說明技術實作的選擇和原因。
AI 開發時遇到設計疑問時查閱，不需要每次都讀。
-->

### Cnyes API 規格

> Confluence 頁面 ID：24087914
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087914)
> 摘要檔：[processed/24087914-summary.md](../../confluence/processed/24087914-summary.md)
> Confluence 最後更新：2021-11-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 Cnyes 通用報價 API 的請求方式與參數格式，主要用於取得外匯（預設 type=ALLFX）相關報價。對 AI 開發的幫助是：了解此 API 端點是 GET 請求，接受 type、page、limit、column、param 五個參數；回應欄位包含多個貨幣代碼（如 200033 等），但文件未定義各欄位的具體型別與意義，需人工確認或從其他文件補充。若需串接此 API 取得外匯報價給 currencymanageservice 或 forexcacheservice 使用，可先參考此規格建立基本請求結構。

**關鍵設計決策**：
- 採用 RESTful GET 方法取得報價資料，查詢參數直接附加於 URL
- 預設 type=ALLFX，表示此 API 預設回傳所有外匯相關報價
- 預設 limit=300，單次請求最多回傳 300 筆資料
- 預設 column=D_FORMAT，可能控制回傳欄位的格式（需人工確認具體作用）
- 預設 param=currency=USD，可能以美元作為基準貨幣進行查詢
- API 版本為 v2（路徑含 /ws/api/v2/），但文件未說明版本變更歷史

**注意事項**：
- ⚠️ 文件內容極不完整：API Response 表格僅列出 key 值（如 200033），未提供 type 與 define 說明，無法得知各欄位的資料型態與定義
- ⚠️ 參數表中的 value type 與 define 皆為「?」，僅少數有猜測性描述（如 0 的 define 為 currency），所有參數定義均需人工確認
- ⚠️ 文件缺少 API 錯誤碼、認證方式、Rate Limit 等重要技術細節，無法直接用於開發
- ⚠️ 最後更新日期為 2021-11-03，距今已超過兩年，API 可能有變更，需確認是否仍為現行規格

---

## 歷史決策類

<!--
說明為什麼當時這樣做，避免未來重複踩坑或誤改。
-->

_（無相關歷史決策文件）_

---

## 操作手冊類

<!--
說明如何操作某個功能或系統。
通常是給維運人員看的，AI 開發時不需要讀，
但若涉及程式需要支援的操作流程則需要參考。
-->

_（無相關操作手冊文件）_