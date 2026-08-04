# PRDMonitor 內部服務目錄

## 概述
PRDMonitor 為內部基礎設施監控與自動化切換服務。透過定期檢測伺服器可用性，在發生異常時自動更新 Cloudflare DNS 記錄將流量導向備援 IP，並即時推送 Telegram 告警，確保關鍵服務持續可用。

## 主要功能
- **存活監控**：定期 ICMP Ping 檢查 `PingServers` 清單中的目標主機。
- **智能 DNS 切換**：監測到受保護域名 (`NeedChangeDNS`) 對應的主機異常時，透過 Cloudflare API 將 DNS 記錄指向預設的 `DNSBackupIP`。
- **即時告警**：透過 Telegram Bot 發送異常通知至指定群組。
- **集中日誌**：應用程式日誌輸出至 Kafka，便於後續分析。
- **遠端設定支援**：可選擇性啟用 Zookeeper 進行動態設定管理（目前關閉）。

## 技術棧
- **執行環境**：.NET 6
- **容器化**：Docker (基於 `mcr.microsoft.com/dotnet/sdk:6.0`)
- **設定管理**：Zookeeper (備用)、本機 JSON 設定檔
- **日誌收集**：Apache Kafka
- **DNS 控制**：Cloudflare API v4
- **通知管道**：Telegram Bot API
- **部署平台**：Portainer

## 組態與部署注意
- **時區**：容器內強制設定 `TZ=Asia/Taipei`，確保日誌時間與本地一致。
- **執行權限**：為簡化權限管理，容器以 `root` 身份執行。
- **環境差異**：
  - 正式環境使用 `appsettings.json`，開發環境使用 `appsettings.Development.json`。
  - 開發設定中的 Kafka broker 與 Ping 目標可能不同，部署前需確認正確環境。
- **敏感資訊保護**：Telegram Token 及 Cloudflare API Token 以明文存放於設定檔中，上線前建議遷移至秘密管理服務（如 Vault）或透過環境變數注入。
- **建置相依**：Docker 建置時使用內部 NuGet 來源 (`192.168.9.234:8079`)，若網路環境變更需調整 `Dockerfile` 中的來源位址。
- **服務名稱**：在 Portainer 中對應的容器名稱為 `prdmonitor`。

## 相關連結
- **程式碼倉庫**：[GitLab](https://git.zbdigital.net/Architecture/prdmonitor.git)