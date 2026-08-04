# LeisuParserV2

## 概述

LeisuParserV2 為內部爬蟲解析服務，負責訂閱 Kafka 中 **leisu** 來源的原始 HTML 資料，解析即時賠率、比分與賽事狀態，並將結構化後的 game_data 回傳至指定的 Kafka 叢集，供下游服務使用。支援 **provider**（接收原始 HTML）與 **parser**（解析並發出 game_data）兩種運作角色，可部署於多套環境（Local、PRD、PRD2、PRD3、PRD60）。

## 主要功能

- **Kafka 即時消費**：從 topic `leisuhtml` 接收 HTML 資料，支援多台 Kafka broker 叢集。
- **資料解析**：解析足球、籃球等賽事的賠率、比分、比賽狀態、走地統計與逐球紀錄（play-by-play）。
- **賠率比對與合併**：比對多頁面取得的賠率變化（Compair），合併至同一場賽事（Merge），並自動關閉已失效的賠率。
- **賽事狀態管理**：依比賽狀態（賽前、進行中、已結束、延賽、取消）自動過濾與更新，避免因多 provider 時間差導致的資料錯亂。
- **流量控制與心跳**：定期檢查快取有效時間，刪除長期無更新的賽事；每分鐘發送心跳記錄已送出的賽事數量。
- **統計資料寫檔與上傳**：比賽進行中依設定時間點（如足球 15’、30’、45’ …）寫入走地統計，可寫入本地或上傳至 NAS（透過 pysftp）。
- **名稱映射服務**：將賽事聯盟、隊伍名稱定期上傳至 name map API，維持名稱一致性。
- **單元測試**：提供 `Unittest.py` 測試賠率比對、合併與賠率關閉等核心邏輯。

## 技術棧

| 元件 | 技術 |
|------|------|
| 語言 | Python 3.9 |
| 容器化 | Docker（基於 `python:3.9-slim-buster`） |
| Kafka 客戶端 | kafka-python |
| ZooKeeper 客戶端 | kazoo |
| SFTP 上傳 | pysftp / paramiko |
| HTTP 請求 | requests |
| 快取 | expiringdict |
| 並行處理 | threading, queue |
| 內部函式庫 | TCZB（Logger、Globals、Redis、Kafka、Datetime、Versioning 等） |

## 組態與部署注意

1. **環境參數**：啟動容器時需帶入環境名稱（如 `Local`、`PRD`、`PRD60`），對應 `AppSettings.py` 中 `environment_path` 定義的 Kafka broker 清單及日誌設定。
2. **Kafka 依賴**：確保對應環境的 Kafka 叢集可連線，並已建立 topic `leisuhtml`。
3. **內部套件**：需在私有 PyPI 源（`http://localhost:8070`）安裝 `TCZB` 套件，Dockerfile 中已設定安裝指令。
4. **NAS 連線**：若啟用統計寫檔上傳功能（`PRD60` 環境），需確保 NAS IP `192.168.55.20` 可連線，並正確設定帳號密碼。
5. **容器時區**：容器預設使用 `Asia/Taipei` 時區。
6. **監控與日誌**：日誌經由 `Logger` 模組發送至指定的 Kafka Gateway 主題，便於集中監控。
7. **注意事項**：
   - 多頁面賠率合併時，若某個頁面超過 3 分鐘（賽中）或 10 分鐘（賽前）無更新，該頁面賠率會自動關閉。
   - 比賽日期與當前時間差距超過 1 天時，資料將被跳過，避免錯誤寫檔。
   - 賠率中若所有值皆為 `-1` 表示該玩法已關閉，經過 4 次心跳後會從快取移除。

## 相關連結

- **原始碼**：[GitLab](https://git.zbdigital.net/CrawlerAgent/leisuparserv2.git)
- **Portainer 服務標籤**：`SRV60|container|leisuparserv2`
- **依賴內部套件**：`TCZB`（需由內部 PyPI 或編譯方式取得）