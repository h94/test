# GameLiveService

## 概述
GameLiveService 為內部遊戲直播與社群互動後端服務，負責管理遊戲頻道、社群群組聊天室、即時訊息推播及預測注單。服務以 RESTful API 對外暴露，並透過 SignalR 提供即時通訊功能。

## 主要功能
- **社群群組管理**  
  - 新增、查詢、更新社群群組（名稱、描述、封面圖片）  
  - 設定與修改置頂訊息  
- **社群聊天室**  
  - 即時訊息收發（文字、圖片）  
  - 查詢歷史訊息與最後一則訊息  
  - 上傳聊天室圖片  
- **預測注單**  
  - 建立、查詢、編輯預測注單  
  - 設定主推注單與推薦說明  
  - 查詢會員每日推薦次數  
- **遊戲頻道控制**  
  - 新增、修改、查詢頻道（依遊戲類型、日期、開關狀態篩選）  
  - 批次更新頻道資訊  
  - 開啟／關閉指定頻道  
- **即時推播與連線管理**  
  - 通知社群群組預測結果  
  - 查看 SignalR 連線資訊  
  - 自動控制頻道開關  
  - 清理過時心跳連線  
- **系統輔助功能**  
  - 版本查詢、心跳檢測  
  - 查詢全站對話紀錄及小編工作報告  

## 技術棧
- **語言與框架**：.NET 6 (ASP.NET Core)
- **即時通訊**：SignalR
- **容器化**：Docker（基於 `mcr.microsoft.com/dotnet/sdk:6.0`）
- **依賴**：相依注入 (DI)、ECCore 設定模組、快取（推測使用 Redis 或記憶體快取）

## 組態與部署注意
- **環境變數／設定檔**：需於 `appsettings.json` 或環境變數中提供 `Version`、`Environment` 等自訂組態。
- **時區**：容器預設設定為 `Asia/Taipei`，確保台灣時間正確。
- **端口**：應用程式監聽 `5000` 連接埠（詳見 Dockerfile）。
- **執行方式**  
  ```bash
  docker build -t gameliveservice .
  docker run -d -p 5000:5000 gameliveservice
  ```
  或直接以 `dotnet GameLiveService.dll` 執行（需確保 `/app` 目錄下有發行後的檔案）。
- **相依服務**：需確保資料庫、快取服務（若有）已正確連線，相關連線字串應放置於設定檔中。

## 相關連結
- 原始碼倉庫：https://git.zbdigital.net/Biz/gameliveservice.git