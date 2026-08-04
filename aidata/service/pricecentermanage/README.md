# PriceCenterManage

## 概述
PriceCenterManage 是價格中心管理後端服務，負責體育博彩站台（如 Bet365、Pinnacle）的爬蟲調度與狀態監控，同時提供運動站台的通知公告、裝置管理及日報表等 API 與簡易儀表板。

## 主要功能
- **系統監控**  
  服務心跳、版本查詢、站台即時狀態、各機器與爬蟲服務的心跳回報。
- **爬蟲管理**  
  Bet365 與 Pinnacle 頁面分配與參數調整、走地（RBG）控制、爬蟲停止／重啟通知及聯賽寫入。
- **通知與公告**  
  運動站台公告主題與訊息 CRUD、群發站內信、郵件查詢與讀取狀態更新。
- **App 裝置管理**  
  運動站台 App 裝置的新增與查詢。
- **日報表**  
  會員日報與預測日報的新增、查詢（依日期區間）。
- **後台顯示**  
  MVC 儀表板（`/Home/Index`）可視化各機器、頁面爬取狀態及延遲警示。

## 技術棧
- **框架**：.NET 6，ASP.NET Core MVC + Web API
- **資料庫**：關聯式資料庫（搭配 ECCore 等內部資料存取元件）
- **訊息佇列**：Kafka（用於日誌）
- **容器化**：Docker，部署於 Docker Swarm（生產環境標記 `PRD_Docker_Swarm`）

## 組態與部署注意
- **監聽埠**：`5000`（詳見 Dockerfile）
- **時區**：容器內設為 `Asia/Taipei`，需確保本地時間正確（已處理）
- **必要組態**：`appsettings.json` 須提供 `Version`、`Environment`、資料庫連線字串及 Kafka 相關設定
- **健康檢查**：可使用 `/api/heart` 端點（回傳當前伺服器時間）
- **相依服務**：爬蟲節點需定時呼叫心跳 API，否則分配功能可能異常

## 相關連結
- 原始碼倉庫：[GitLab](https://git.zbdigital.net/Biz/pricecentermanage.git)