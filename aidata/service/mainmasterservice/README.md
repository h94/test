# MainMasterService 內部服務目錄

## 概述
MainMasterService 是一個專注於計算主推（main bet）玩家連勝紀錄的內部資料分析服務。它從 Apache Cassandra 資料庫中讀取各球種的預測投注記錄，透過複雜的玩家勝率與獲利計算模型，篩選出高品質的主推玩家榜單，並將結果寫入 Google Sheets 或推送至下游預測服務 API。

## 主要功能
- 定期從 inplayz.com API 取得最新賽事清單與聯盟代號（lid）。
- 查詢 Cassandra 資料表 `predictbets_{game_type}`，彙總玩家在特定日期範圍內的投注資料。
- 依據是否為主推（mainbet）、投注模式（1X2、HA、OU、GameHA、GameOU）計算每日勝負、連勝天數、平均勝率、獲利點數與分數。
- 支援多球種：BK（籃球）、BS（棒球）、SC（足球）、HL（冰球）、TN（網球）、ES（電競）、FL（美式足球）。
- 過濾機器人帳號（透過 `member.gamerobots` 表）與黑名單帳號。
- 自動將篩選後的主推榜單以 POST 方式送到 `http://192.168.55.60/predictservice/api/reports/predictfilterreports/mainbets`。
- 每日清理過期資料（刪除 90 天前的記錄）。
- 錯誤訊息與心跳日誌透過 Kafka 回報。

## 技術棧
| 類別 | 名稱 |
|------|------|
| 語言 | Python 3.8.5 |
| 容器化 | Docker（基礎映像 `python:3.8.5-slim-buster`） |
| 資料庫 | Apache Cassandra（Cluster: 192.168.55.80） |
| 訊息佇列 | Apache Kafka（多集群，見 AppSettings） |
| 外部 API | Google Sheets API（OAuth2 憑證）、inplayz.com 賽事 API |
| 內部套件 | TCZB（Logger、Globals、Versioning） |
| 依賴 | cachetools, cassandra-driver, google-api-python-client, kafka-python, requests 等（詳見 requirements.txt） |

## 組態與部署注意
- **環境變數**：啟動時須帶入命令列參數，例如 `python project/__main__.py PRD`，對應 `AppSettings.environment_path` 中的設定。
- **Kafka 配置**：依環境（Local、PRD、PROD）使用不同的 broker 位址，請在 `AppSettings.py` 中確認。
- **Cassandra 連線**：硬編碼於 `project/DataProvider.py`，需確保網路可達 `192.168.55.80`。
- **Google Sheets 憑證**：檔案 `cred.json` 需掛載至容器工作目錄（路徑 `./cred.json`）。
- **Docker 部署**：建議使用 Docker Swarm / Portainer；鏡像標籤 `mainmasterservice:latest`。
- **排程與重試**：服務會進入無限循環（每 30 分鐘執行一次主流程），異常時等待 10 分鐘後重試。
- **自訂篩選**：可在 `AppSettings.settings.transformer.blacklist` 中設定帳號黑名單日期；調整 `Seq_Score` 權重可影響排名。

## 相關連結
- **GitLab 儲存庫**：https://git.zbdigital.net/biz/mainmasterservice.git
- **Portainer 部署**：`PRD_Docker_Swarm|container|77b51f4c750d|mainmasterservice:latest`
- **內部依賴套件**：TCZB（可從內部 PyPI 伺服器取得）