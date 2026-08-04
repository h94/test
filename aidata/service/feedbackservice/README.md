# feedbackservice

## 概述
feedbackservice 為基於 .NET 6 的 Web API 服務，負責處理運動（sport）與股票（stock）相關的使用者反饋及商業合作訊息。服務涵蓋商業合作訊息、運動反饋、股票反饋三類業務，提供訊息 CRUD、客服回覆、圖片上傳及排程清理等功能，部署於 Docker Swarm 生產環境。

## 主要功能
- **商業合作訊息**
  - 建立、查詢（依業務類型 `sport`/`stock` 與時間區間、單筆）及更新回覆內容
- **運動反饋**
  - 反饋主題（Topic）與常見問題（Question）的管理（新增、查詢、更新）
  - 反饋訊息的提交、查詢、狀態更新及單則/全部客服回覆更新
  - 客服圖片上傳（支援多檔案，回傳存取 URL）
- **股票反饋**
  - 反饋主題與常見問題的 CRUD
  - 會員反饋訊息的建立、查詢（依帳號、分頁篩選）、更新與客服回覆
  - 支援分頁、排序及處理狀態篩選
- **系統服務**
  - 心跳檢測（Heartbeat）與版本查詢
  - 自動建表（AutoCreateTable）
  - 排程清理：移除已結束的運動反饋、已回覆的商業合作訊息（由外部排程觸發）
  - 圖片上傳

## 技術棧
- **後端框架**：.NET 6（ASP.NET Core Web API）
- **部署**：Docker（基礎映像 `mcr.microsoft.com/dotnet/sdk:6.0`），Portainer 管理 Docker Swarm 服務
- **內部相依**：ECCore（IECConfig）
- **資料儲存**：Cassandra（keyspace: `feedback`），詳見[資料模型](#資料模型)
- **時區**：Asia/Taipei（於 Dockerfile 設定）

## 資料模型

服務使用 **Cassandra** 作為主要資料儲存，keyspace 為 `feedback`，核心資料表如下：

| 表名 | 用途 | 主要索引 | 狀態流轉 |
|------|------|----------|----------|
| `businessmessages` | 商業合作訊息 | `(site, datetime, id)` | `status`: 0（未回覆）→ 1（已回覆） |
| `feedbacks_sport` | 運動反饋訊息 | `(tid, datetime, account, id)` | `status`: 0（未處理）→ 1（已處理）→ 2（已結案） |
| `feedbacks_stock` | 股票反饋訊息 | `(id)` | 同運動反饋 |
| `topics_sport` | 運動反饋主題分類 | `(id)` | `enabled`: 0（停用）/ 1（啟用） |
| `topics_stock` | 股票反饋主題分類 | `(id)` | `enabled`: 0 / 1 |
| `questions_sport` | 運動常見問題 | `(id)` | `enabled`: 0 / 1；支援多語系（`map<text,text>`） |
| `questions_stock` | 股票常見問題 | `(id)` | `enabled`: 0 / 1；單一語言文字 |

> **跨服務存取**：後台報表服務 (`pricebackendservice`) 對上述表具有 **唯讀** 權限，用於查詢反饋統計與客服處理；寫入操作僅由 `feedbackservice` 執行。  
> 詳細欄位定義、狀態轉換規則與限制請參閱內部文件 `db/feedback-detail.md`。

## 組態與部署注意
- 服務監聽 **5000** 連接埠
- 必須設定正確的 `IECConfig`（例如 Cassandra 連線、金鑰等），透過環境變數或設定檔注入
- CI/CD 流程中已將編譯產出複製至 `FeedbackService/bin/Debug/net6.0/`，Docker 建置時直接使用該目錄（注意 Release 模式應調整路徑）
- 排程清理端點需由外部排程系統（如 xxl-job）定期呼叫：
  - `DELETE /api/v1/system/sport/feedback/messages/end`
  - `DELETE /api/v1/system/business/messages/reply`
- 圖片上傳功能依賴檔案儲存實作，請確保容器能正確存取目標儲存空間（如掛載磁碟區或物件儲存憑證）
- 服務以 `dotnet FeedbackAppService.dll` 啟動，無須額外反向代理即可提供 HTTP API（必要時可前置 Nginx）

## 相關連結
- GitLab Repository：[https://git.zbdigital.net/Biz/feedbackservice.git](https://git.zbdigital.net/Biz/feedbackservice.git)