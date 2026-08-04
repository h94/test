# CurrencyService 內部服務目錄

## 概述
CurrencyService 為一個提供加密貨幣、穩定幣及外匯匯率查詢與轉換的 Web API 服務。作為內部匯率中樞，它整合多個交易所（如 MaicoinMax、Binance、Huobi、Pionex）的加密貨幣報價、穩定幣兌美元匯率（Yahoo、Coinbase Pro），以及外匯（台灣銀行、Yahoo Finance、Investing.com、SMBC）的即時匯率，並支援多種法幣之間的交叉轉換。

## 主要功能
- **加密貨幣報價查詢**：支援從多個交易所取得加密貨幣（BTC、ETH、USDC 等）兌穩定幣（USDT、BUSD 等）的價格。
- **穩定幣兌美元匯率**：取得 USDT 等穩定幣對 USD 的即時匯率。
- **外匯匯率查詢與轉換**：從多個外匯來源（台灣銀行、Yahoo、Investing、SMBC）取得 USD 兌各法幣（TWD、JPY、VND、CNY 等）匯率，並支援交叉匯率計算。
- **自動匯率報價**：提供單一報價（`GetCryptoQuotation`）與多法幣報價清單（`GetCryptoQuotations`），回傳買入/賣出價。
- **資料表自動建立**：`AutoCreateTable` 方法依據設定自動在 Cassandra 中建立各年度的歷史匯率表。
- **Redis 快取**：匯率資料暫存於 Redis，降低對外部 API 的依賴並提升查詢效能。
- **Kafka 日誌**：透過 Kafka 輸出應用日誌，便於監控與除錯。

## 技術棧
| 技術 | 用途 |
|------|------|
| .NET 6 / ASP.NET Core | 開發框架，Web API |
| Docker / Docker Swarm | 容器化部署（生產環境為 Swarm） |
| Redis | 即時匯率快取 |
| Cassandra | 歷史匯率資料持久化 |
| Apache Kafka | 應用日誌輸出 |
| ZooKeeper | 分散式設定管理（可選） |
| ECCore / ECFramework | 內部基礎架構套件（DI、設定、日誌等） |
| CryptoModel / ForexModel | 內部資料模型套件 |

## 組態與部署注意
- **環境設定**：透過 `appsettings.{Environment}.json` 區分開發（Local）、測試（BAK）、正式（PRD）環境，使用 `Environment` 欄位切換。
- **RemoteConfig**：若設為 `true`，設定將從 ZooKeeper 動態讀取；預設為 `false` 使用本機 JSON。
- **Port**：Dockerfile 暴露 `5000` 埠，容器內服務綁定此埠。
- **時區**：強制設定 `TZ=Asia/Taipei`，確保時間戳正確。
- **資料庫與快取**：
  - Cassandra：需指定 `Server` 與 `Keyspace`，依環境區分（如 PRD 使用 192.168.55.80）。
  - Redis：需指定 `ConnectId`、`Servers`、`DB` 編號。
- **Kafka**：需設定 `BootstrapServers` 與 `Topic` 以輸出日誌。
- **部署架構**：正式環境以 Docker Swarm 運行，PortainerKey 標示為 `PRD_Docker_Swarm|swarm|currencyservice`。
- **相依套件**：內部套件（CryptoModel、ForexModel、ECCore、ECFramework）需透過內部 NuGet 源取得。

## 相關連結
- GitLab 原始碼：[https://git.zbdigital.net/Currency/currencyservice.git](https://git.zbdigital.net/Currency/currencyservice.git)
- Docker Swarm Production 部署標籤：`PRD_Docker_Swarm`