# Architecture — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2023-10-11 18:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### BitCoin Currency

> Confluence 頁面 ID：24087271
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Cryptocurrency)
> 摘要檔：[processed/24087271-summary.md](../../confluence/processed/24087271-summary.md)
> Confluence 最後更新：2021-11-08
> 摘要最後同步：2023-10-11

**摘要**：
虛擬幣與外匯系統的整體組件架構，包含爬取代理、後端流程與服務整合。這份文件幫助 AI 開發者掌握各模組的職責與技術棧，對於理解與開發虛擬幣/外匯數據服務至關重要。

**關鍵業務規則**：
- —
  
**注意事項**：
- ⚠️ 文件可能已過期，建議檢查目前系統架構。

### Nuxt3 Architecture

> Confluence 頁面 ID：47218871
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Nuxt3+Architecture)
> 摘要檔：[processed/47218871-summary.md](../../confluence/processed/47218871-summary.md)
> Confluence 最後更新：2023-02-10
> 摘要最後同步：2023-10-11

**摘要**：
Nuxt3 框架下的前端專案架構指南，包含目錄結構與設計慣例。對於設計基於 Nuxt3 的前端頁面和自動化機制作為參考。

**關鍵業務規則**：
- —

**注意事項**：
- ⚠️ 已有新版本 Nuxt3，設計慣例可能需要更新。

### PriceCenter Service

> Confluence 頁面 ID：2884076
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceCenter+Service)
> 摘要檔：[processed/2884076-summary.md](../../confluence/processed/2884076-summary.md)
> Confluence 最後更新：2024-06-21
> 摘要最後同步：2023-10-11

**摘要**：
描述 PriceCenter 系統包含博彩爬蟲、Kafka 傳輸及資料處理的完整架構。對於開發者了解服務間的責任邊界及瓶頸處理至關重要。

**關鍵業務規則**：
- Kafka topic 每秒消息量控制在 40 以下
- PriceCenterSubscribeService 的 CPU 使用率不可超過 100%

**注意事項**：
- ⚠️ PRDMonitor 自動切換功能未曾測試，應確認其可靠性。

---

## 技術設計類

### Cryptocurrency

> Confluence 頁面 ID：24087271
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Cryptocurrency)
> 摘要檔：[processed/24087271-summary.md](../../confluence/processed/24087271-summary.md)
> Confluence 最後更新：2021-11-08
> 摘要最後同步：2023-10-11

**摘要**：
文件描述虛擬幣與外匯系統技術設計，涉及 Go 爬蟲與 .Net 後端的結合。

**關鍵設計決策**：
- Crawler 與後端服務分離，各自負責不同層面
- Redis 作為緩存，減少 DB 壓力

**影響範圍**：
- 涉及所有基於 Crypto 與 Forex 的數據操作服務

### Nuxt3 Architecture

> Confluence 頁面 ID：47218871
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Nuxt3+Architecture)
> 摘要檔：[processed/47218871-summary.md](../../confluence/processed/47218871-summary.md)
> Confluence 最後更新：2023-02-10
> 摘要最後同步：2023-10-11

**摘要**：
Nuxt3 前端專案的技術設計，提供如何設計目錄、命名與自動化的規範。

**關鍵設計決策**：
- 使用 Nuxt 內建 useFetch 進行 API 呼叫
- 自動化命名與路由配置

**影響範圍**：
- 前端專案結構設計與實作方式

---

## 歷史決策類

### FingerPrinter研究

> Confluence 頁面 ID：8716730
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=8716730)
> 摘要檔：[processed/8716730-summary.md](../../confluence/processed/8716730-summary.md)
> Confluence 最後更新：2020-10-12
> 摘要最後同步：2023-10-11

**決策背景**：
指紋辨識技術選用與部署考量，為後續的使用者行為追蹤系統打下基礎。

**決策結論**：
- 前端取得 appname 與 pagename 的方式分析
- 指紋 API 應獨立部署以增強安全性

**影響**：
- 為使用者追蹤系統提供技術基礎，但部署細節可能已變

---

## 操作手冊類

### PRD Rebuild On 234

> Confluence 頁面 ID：22970382
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PRD+Rebuild+On+234)
> 摘要檔：[processed/22970382-summary.md](../../confluence/processed/22970382-summary.md)
> Confluence 最後更新：2021-07-03
> 摘要最後同步：2023-10-11

**摘要**：
重建 PRD 環境的操作指南，包含部署多項基礎服務，是了解舊有基礎設施運作的參考。

**AI 開發需要注意的部分**：
- 服務的部署限制，如單節點 Kafka 和 Cassandra
- 確保配置正確，避免因環境錯誤導致的服務異常