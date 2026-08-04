# 博彩（Game）Confluence 文件目錄

此目錄收錄**博彩線爬蟲與資料管線**相關的 Confluence 摘要（`game/crawler` 路徑）。
一般博彩業務規則（玩法、合併、站台配置等）請優先讀 [others/game_bussiness-documents.md](../others/game_bussiness-documents.md)。

> 全域目錄（僅在無對應摘要或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### game/` 或 `others/game_bussiness` 關鍵字。

---

## Confluence 業務文件

| 主題 | Confluence 路徑 | 摘要檔 | 說明 |
|------|----------------|--------|------|
| 爬蟲／資料管線 | `game/crawler` | [crawler-documents.md](./crawler-documents.md) | Bet365、各站台爬蟲流程、Parser、與 PriceCenter 互動 |

---

## 相關索引

| 位置 | 用途 |
|------|------|
| [others/_index.md](../others/_index.md) | 博彩業務規則（`game_bussiness`）、系統架構 |
| [service/_index.md](../service/_index.md) | CrawlerService、ZBAParser、FlowControlService 等背景服務 |
| [webapi/_index.md](../webapi/_index.md) | PriceCenter、MergeSite、GameSetting 等 API |

---

## 查閱原則

```
爬蟲流程／Parser／站台資料來源  → game/crawler-documents.md
玩法、合併、球種、後台操作 SOP  → others/game_bussiness-documents.md
單一微服務 API／結算邏輯        → 對應 webapi 或 service 的 documents.md
```
