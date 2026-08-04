# AlertBackEndService

## 概述
AlertBackEndService 為賠率異常監控系統的後台原子 REST 服務，使用 Python FastAPI 框架實作。提供警示資料查詢、狀態管理、Webhook 派送、匯出作業以及各類閥值設定的管理功能，並整合定時排程與內部訊息同步，確保監控數據的即時性與一致性。

## 專案結構
```
project/
├── __main__.py              # 入口
├── AppSettings.py           # 環境設定
├── Tasks.py                 # 背景 worker
├── Tests.py                 # API 測試
├── Resources/               # FastAPI 路由
├── Service/                 # 業務邏輯
└── Provider/                # 資料存取
migrations/                  # PostgreSQL migration
```

## 主要功能
- **警示查詢與狀態更新**：支援依球種、時間區間、來源等條件篩選警示清單；可查詢單筆警示完整內容，並將狀態更新為 pending／ignored，同時透過 Webhook 廣播變更。
- **匯出服務**：接受匯出請求建立任務，背景 Worker 處理大量警示資料匯出為 CSV，並自動上傳至 NAS 儲存。
- **閥值設定管理**：
  - 賠率閥值（oddthreshold）：支援遊戲層級監控玩法的新增、修改、刪除與同步。
  - 比分閥值（scorethreshold）：依球種設定比分相關閥值參數。
  - 監控玩法（monitored_play_modes）：定義各球種啟用的賠率監控玩法。
  - 資料來源類型（source_type）：管理資料源支援的遊戲類型映射。
  - 警示來源設定（sport_alert_sources）：指定各球種的主要與次要警示來源。
- **Webhook 通知**：管理 Webhook 組態，提供測試、重試及歷史記錄查詢；背景 Worker 負責發送與重試，並具備速率控制。
- **定時排程**：
  - 每月 1 日執行警示資料自動封存。
  - 每日清理過期的遊戲閥值設定與同步暫存記錄。
- **資料完整性與稽核**：閥值異動皆寫入 changelog，並將變更排入同步佇列供下游消費。

## 技術棧
- **後端框架**：Python 3.9 + FastAPI + uvicorn
- **資料庫**：PostgreSQL（透過 asyncpg 與 psycopg2-binary 存取）
- **快取／佇列**：Redis、Apache Kafka（kafka‑python）
- **協調服務**：Apache ZooKeeper（kazoo）
- **HTTP 客戶端**：httpx
- **檔案處理**：openpyxl（用於 XLSX 匯出）
- **遠端傳輸**：paramiko／pysftp（用於 NAS 上傳）
- **內部共用庫**：TCZB（需從私有索引安裝）

## 組態與部署注意
- **容器映像**：基於 Python 3.9-slim-buster，暴露埠口 `5000`。
- **API 前綴**：對外路由皆以 `/alertbackendservice/api/` 開頭；服務存活檢查：`GET /alertbackendservice/api/version`，健康檢查（含資料庫連線）：`GET /alertbackendservice/api/health`。
- **資料庫初始化**：部署前須先執行 `migrations/` 目錄下的 SQL 腳本，包含 `001_create_core_tables.sql` 與 `002_create_supplement_tables.sql`，建立核心及擴充資料表。
- **環境變數**：服務透過 `AppSettings.py` 讀取設定，需提供資料庫連線資訊、Redis、Kafka、ZooKeeper 位址等必要的環境變數。
- **依賴安裝**：執行 `pip install -r requirements.txt`；`TCZB` 套件須以 `pip install TCZB -i http://localhost:8070 --trusted-host localhost:8070` 從內部索引安裝。
- **時區**：容器預設時區設為 `Asia/Taipei`，所有時間處理皆以台灣時間為準。
- **啟動方式**：`ENTRYPOINT ["python", "./project/__main__.py"]`，主程式會依序啟動 Web 伺服器與所有背景 Worker（匯出、Webhook、排程等）。
- **相依服務**：需要可存取的 PostgreSQL、Redis、Kafka、ZooKeeper 以及可寫入的 NAS 共享目錄。

## 相關連結
- **原始碼倉庫**：https://git.zbdigital.net/biz/alertbackendservice
- **Confluence 文件**：https://confluence.zbdigital.net/pages/viewpage.action?pageId=79472869
- **Phase 1 計劃**：`_plans/AlertBackendService-phase1-plan.md`