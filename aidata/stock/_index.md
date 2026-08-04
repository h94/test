# 股票（Stock）Confluence 文件目錄

此目錄收錄**股票線爬蟲與資料來源**相關的 Confluence 摘要（`stock/crawler` 路徑）。
一般股票業務規則（訂閱、選股、權限等）請優先讀 [others/stock_bussiness-documents.md](../others/stock_bussiness-documents.md)。

> 全域目錄（僅在無對應摘要或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### stock/` 或 `others/stock_bussiness` 關鍵字。

---

## Confluence 業務文件

| 主題 | Confluence 路徑 | 摘要檔 | 說明 |
|------|----------------|--------|------|
| 爬蟲／資料來源 | `stock/crawler` | [crawler-documents.md](./crawler-documents.md) | A 股等資料抓取 API、爬蟲規格 |

---

## 相關索引

| 位置 | 用途 |
|------|------|
| [others/_index.md](../others/_index.md) | 股票業務規則（`stock_bussiness`）、架構 |
| [frontend/_index.md](../frontend/_index.md) | stockfrontendsite 等前台 |
| [webapi/_index.md](../webapi/_index.md) | 股票相關 WebAPI（若有） |
| [db/_index.md](../db/_index.md) | 股票業務線 `_stock` 表（Cassandra keyspace） |

---

## 查閱原則

```
股票爬蟲／外部資料 API  → stock/crawler-documents.md
訂閱策略、選股、權限    → others/stock_bussiness-documents.md
前台展示／會員操作      → frontend/stockfrontendsite/documents.md（若有）
```
