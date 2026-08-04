# 跨服務 Confluence 文件目錄

此目錄彙整**不屬單一微服務**的 Confluence 摘要，依主題分檔（`{topic}-documents.md`）。
引導師在任務涉及架構、博彩業務規則、股票業務、機器學習等跨服務議題時，**優先讀此處**，再視需要查各 `{kind}/{service}/documents.md`。

> 全域目錄（僅在下方無對應主題檔或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### others/{topic}` 或關鍵字後讀 `confluence/processed/{pageId}-summary.md`。

---

## Confluence 業務文件（依主題）

| 主題 | Confluence 路徑 | 摘要檔 | 適用情境 |
|------|----------------|--------|----------|
| 系統／前端架構 | `others/architecture` | [architecture-documents.md](./architecture-documents.md) | Vue3 / Nuxt3、PriceCenter 整體架構、爬蟲網路、Redis/Kafka 定義、`@arch-teacher` |
| 博彩業務 | `others/game_bussiness` | [game_bussiness-documents.md](./game_bussiness-documents.md) | 賽事合併、玩法、球種站台、即時賠率、後台操作 SOP |
| 股票業務 | `others/stock_bussiness` | [stock_bussiness-documents.md](./stock_bussiness-documents.md) | 股票 API、訂閱策略、選股、權限、券商相關規則 |
| 機器學習／預測 | `others/machine_learning` | [machine_learning-documents.md](./machine_learning-documents.md) | 預測 API、酒田戰法、OtherInfo、走地賽事定義、ChatGPT 整合 |

---

## 與其他 kind 的關係

| kind | 說明 |
|------|------|
| [webapi/_index.md](../webapi/_index.md) | 各 WebAPI 服務的 `documents.md` |
| [service/_index.md](../service/_index.md) | 各 BackgroundService 的 `documents.md` |
| [frontend/_index.md](../frontend/_index.md) | 各前端站台的 `documents.md` |
| [game/_index.md](../game/_index.md) | 博彩**爬蟲**專題（`game/crawler-documents.md`） |
| [stock/_index.md](../stock/_index.md) | 股票**爬蟲**專題（`stock/crawler-documents.md`） |

---

## 查閱原則

```
需要了解跨服務業務規則     → 本頁對應主題的 *-documents.md「業務規範類」
需要了解架構或歷史決策     → architecture-documents.md 對應區塊
需要看完整原始文件       → 摘要內 Confluence 連結
不確定主題              → grep confluence/_index.md 的「依服務分類」中 others/*
```
