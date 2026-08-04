# GameTools 服務

## 概述
GameTools 是一套內部後端服務，負責管理、合併與強制合併多個遊戲資料站台的聯賽（League）、隊伍（Team）及賽事（Game）數據。服務本身作為中間層，透過呼叫 PriceCenter API 取得原始資料，並提供統一的集合操作介面，支援站台名稱映射、翻譯建議、操作日誌查詢等功能。

此服務部署於 Docker Swarm（PRD 環境），以容器型式運行。

## 主要功能
- **聯賽與隊伍合併管理**  
  查詢聯賽/隊伍資料、編輯、刪除，以及進行名稱映射（Name Map）。
- **賽事數據合併與拆分**  
  合併多站台賽事（SiteGame）、拆分已合併賽事，支援客隊/主隊互換（Swap）。
- **強制合併**  
  強制合併聯賽、隊伍及賽事，用於處理特殊邏輯或修復資料。
- **站台原始數據查詢**  
  查詢原始站台聯賽（SiteLeague）、原始站台隊伍（SiteTeam），並支援取消合併（Unmerge）。
- **操作日誌**  
  查詢指定日期的操作紀錄（ActionLog）。
- **翻譯服務**  
  取得特定詞彙的翻譯建議。
- **遊戲數據維護**  
  查詢、編輯、刪除已合併的遊戲（Game）資料。

## 技術棧
- 語言與框架：.NET (C#)
- HTTP 請求：Flurl.Http
- 序列化：Newtonsoft.Json
- 執行環境：Docker / Docker Swarm (Linux containers)
- 依賴後端：PriceCenter API (內部服務)

## 組態與部署注意
- 服務會依據 `AppState.EnvType` 設定決定使用的 API 端點；`AppState.ApiUrl` 可選用內網閘道（`http://192.168.9.232/pricecenter/api`）、生產閘道（`http://192.168.55.60/pricecenter/api`）或公開域名（`https://ls.zbdigital.net/api`）。
- 部署於 Docker Swarm 叢集，需確保容器可連通內部 PriceCenter 服務與 Kafka 日誌端點（`http://192.168.55.60:22102`）。
- 翻譯功能依賴翻譯服務（`http://192.168.55.62/translate/api/suggest`），請確認網路設定。
- 多數端點使用 HTTP 溝通，若切換至 HTTPS 需調整防火牆與憑證。
- 主要設定集中於 `GameTools/Services/AppState.cs`，可考慮以環境變數或組態檔管理敏感資訊（如帳號密碼，目前已明文列入，建議正式環境抽離）。

## 相關連結
- GitLab 倉庫：[https://git.zbdigital.net/Biz/gametools.git](https://git.zbdigital.net/Biz/gametools.git)