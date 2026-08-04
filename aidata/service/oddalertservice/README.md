# oddalertservice

## 概述
`oddalertservice` 為內部體育數據即時警示服務，負責消費 Kafka 中已處理的賠率賽事事件，依據多條規則（賠率劇變、抖動、跨站機率分歧、比分來源偏離、比分修正、來源斷線、賽事關盤過久）進行偵測，產出結構化警示並推送至 Kafka 與 PostgreSQL，供運維與業務團隊即時監控數據異常。

## 主要功能
- **賽事事件過濾**  
  依球種白名單、主／輔助資料來源角色、監控玩法清單篩選需處理的賽事與賠率線。
- **賠率異常偵測（7 條規則）**  
  - `odds_spike`：單站賠率單次變動幅度超過閾值。  
  - `odds_flutter`：短時間內賠率高頻變動。  
  - `odds_implied_probability_divergence`：跨站隱含機率差異過大。  
  - `score_source_divergence`：不同來源比分不一致。  
  - `score_correction`：比分回退（修正）。  
  - `source_stale_source`：資料來源斷線逾時（來源層級警示）。  
  - `odds_stale_game`：整場賽事所有盤口關閉過久（賽事層級警示）。  
  各規則閾值可從 AppSettings 全域設定、PostgreSQL 資料表（`effective_thresholds`、`scorethreshold_setting`）依賽事或球種覆寫；玩法白名單可來自 PostgreSQL `monitored_play_modes` 表（按球種設定）或 AppSettings 全域設定。
- **去抖動（Debounce）**  
  固定窗口緩衝，同線短期內多次變動僅取最後一筆再進入偵測，減少重複運算與雜訊。
- **警示輸出**  
  產生標準化 `alert_events` 訊息（含賽事快照、賠率 snapshot、觸發條件等），先以 Kafka 推送（必做），再以最佳努力寫入 PostgreSQL `alerts` 表。
- **定時掃描**  
  每分鐘背景任務掃描所有來源最後資料時間，檢查 `source_stale_source`；亦掃描處於「盤口關閉」狀態的賽事，檢查 `odds_stale_game`，確保斷線與長期無盤口的賽事能被即時發現。

## 技術棧
- **運行環境**：Python 3.11-slim（Docker）
- **訊息佇列**：Apache Kafka（消費者與生產者，搭配 `aiokafka`）
- **資料儲存**：PostgreSQL（`asyncpg`）
- **內部相依**：`TCZB`（私有套件，提供內部共通功能）
- **HTTP 客戶端**：`aiohttp`
- **排程與輔助**：`watchdog`（檔案監控）、`shortuuid`、`kazoo`（ZooKeeper 操作）
- **部署**：Docker Swarm（Portainer 管理），容器名 `oddalertservice`

## 組態與部署注意
- 服務依賴內部 PyPI（`http://localhost:8070`）安裝 `TCZB`，建置映像時需確認該來源可達；若無內部 PyPI，請改用本機 wheel 或調整 `Dockerfile` 中的 pip 指令。
- 時區固定為 `Asia/Taipei`，所有時間比對以 UTC 進行內部處理，但容器時區已設置便於日誌檢視。
- 主要設定透過 `AppSettings` 注入（來源推測為組態檔或環境變數），包含：
  - Kafka 連線資訊與 topic 名稱
  - PostgreSQL 連線字串
  - 監控球種、玩法白名單、來源角色、閾值等業務參數
- 閾值支援多層覆寫：預設值來自 AppSettings，可被 PostgreSQL `effective_thresholds` 表（依賽事）覆寫；`source_stale_source` 規則另有依來源的 `effective_thresholds` 覆寫（`source_stale_minutes`）；`score_source_divergence` / `score_correction` 則另有 `scorethreshold_setting` 機制。
- 服務啟動後會持續消費 Kafka，並啟動背景排程執行定時掃描，請確保 Kafka 群組設定與 partition 分配正確，避免重複消費或漏訊息。

## 資料庫操作邊界
`oddalertservice` 負責維護 `Alert` 資料庫，主要寫入 `alerts` 表，但有以下嚴格限制：

- **`alerts` 表寫入限制**：
  - `id` 由服務內部以 `shortuuid` 生成，不允許任何外部指定。
  - `created_at`、`updated_at` 由資料庫預設值自動維護，禁止手動修改。
  - `status` 只能透過服務 API 變更，且必須遵循 `pending → ignored` 或 `pending → resolved`，每次變更都必須在**同一交易內**自動寫入 `alert_change_log` 記錄操作者與新舊值。
  - `operator_account` 由 API 後端從認證資訊（JWT）強制注入，不允許請求參數自訂。
  - `detail`、`threshold_snapshot`、`game_info` 皆為觸發告警時的**不可變證據快照**，不對外提供修改介面。
  - `rule_code`、`level`、`source`、`game_id`、`game_type`、`play_mode`、`spread`、`selection`、`league_id` 在插入後**不可變更**。
- **配置表唯讀**：`monitored_play_modes`、`scorethreshold_setting`、`source_type`、`sport_alert_sources` 等表僅供偵測模組讀取，所有配置變更必須由獨立的後台管理服務進行。
- **歸檔表保護**：`alerts_archive` 僅允許內部排程或存檔程序寫入，對外不開放任何 INSERT / UPDATE / DELETE。
- **變更日誌表**：`alert_change_log` 無任何外部寫入介面，僅在 `alerts.status` 變更時由系統自動產生。

這些約束是為了確保審計完整性與資料一致性，部署時請確保資料庫帳號權限符合上述讀寫規則。

## 相關連結
- GitLab 倉庫：`https://git.zbdigital.net/Biz/oddalertservice.git`
- 容器管理：Portainer 堆疊 `PRD_Docker_Swarm`，服務 `oddalertservice`