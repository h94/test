# MergeSite

## 概述
MergeSite 是體育賽事資料中台的核心服務，負責**主庫（Master）聯盟、賽事、隊伍**的查詢與維護，並提供**站台（Site）資料合併**機制。服務將來自不同數據源（如 OpenClaw）的站台資訊，透過自動比對或人工操作合併至主庫，確保前端呈現一致的賽事資料。

本服務部署於 Docker Swarm（Portainer 代碼：`PRD_Docker_Swarm|container|mergesite`），對外經由 Port 5000 提供 RESTful API。

## 主要功能

### 主庫管理（GameController）
- 查詢聯盟、賽事、隊伍（支援多重篩選條件）
- 更新聯盟／隊伍名稱、語系簡稱與全名對照
- 刪除聯盟、賽事、隊伍
- 設定聯盟鎖定狀態（禁止自動比對變更）
- 手動解除主庫隊伍與站台隊伍的合併關係

### 合併操作（MergeController）
- 查詢 OpenClaw merge 資料（依時間區間或主鍵）
- 強制合併兩筆主庫賽事／聯盟／隊伍
- 合併多筆站台賽事至指定主站賽事
- 站台聯盟合併（可合併至主庫聯盟或僅合併站台間）

### 站台管理（SiteGameController）
- 依時間、站台、主庫 LID 等維度查詢站台聯盟、隊伍、賽事
- 更新站台聯盟／隊伍顯示名稱與語系對照
- 解除站台聯盟／隊伍／賽事與主庫的合併關係

### AI 自動比對與調參（AiMergeController）
- 查詢待審核、衝突或被推斷的 AI 比對預測清單及單筆明細
- 人工確認或否定 AI 比對預測（單筆及批次，不觸發實際合併）
- 查詢每日 AI 比對報表，取得分類後的否定／錯誤樣本，並可將錯誤樣本人工標記為正確
- 執行 AI 比對回測，以及提交歷史資料學習任務（背景執行並可查詢狀態）
- 查詢最近一次 AI 回測結果
- 提交、查詢、重試 AI 調參資料包（tuning pack）匯出任務，並可下載已完成之調參包 JSON
- 手動觸發 Job1（每日自動比對）、Job2（對答案產報表）與 Job3（補寫訓練標籤）
- 手動觸發 Job4（高分 prediction 自動合併站台賽事，支援 dry run 模式）
- 查詢 AI 排程健康狀態、Job 進度（含 Job1 即時進度）
- 查詢與調整 AI 運行時配置（runtime config）
- 執行模擬回測，評估閾值調整效果
- 查詢 AI 運行時配置歷史及回滾

### 系統功能（SystemController）
- 服務版本與建置時間查詢
- 使用者操作紀錄的寫入與查詢
- 自動比對異常紀錄的查詢、確認／拒絕
- 隊伍手動確認合併
- 翻譯 API（關鍵字轉換至目標語系）
- 站台代碼與顯示名稱對照表

## 技術棧
- **框架**：.NET 8, ASP.NET Core Web API
- **資料庫**：Cassandra（存放 OpenClaw merge 與部分業務資料）
- **內部依賴**：`ECCore`（通用組態與基礎設施）、`GameDataModels`（賽事資料模型）
- **外部依賴**：`openclawservice`（AI Merge、調參包匯出與運行時配置相關功能透過 `IAiMergeService` / `IAiMergeTuningPackService` 代理）
- **容器化**：Docker，基於 `mcr.microsoft.com/dotnet/sdk:8.0` 映像
- **部署**：Docker Swarm，透過 Portainer 管理

## 組態與部署注意
- **時區**：容器內已強制設定為 `Asia/Taipei`，無需額外掛載。
- **端口**：預設監聽 Port `5000`，Dockerfile 中已宣告 `EXPOSE 5000`。
- **建置**：現有 Dockerfile 採用複製 `bin/Debug/net8.0/` 的方式，正式環境應改用 Release 構建產物，並考慮分階段建置（sdk 僅用於運行）。
- **組態**：
  - `appsettings.json` 必須提供 `Version` 與 `Environment` 區段（用於 Version API 回傳）。
  - 需正確設定 Cassandra 連線字串、站台對照等自訂組態（參考 `ECCore.IECConfig`）。
  - 若使用 AI 相關功能，須確保 `openclawservice` 端點可達，並正確配置背景服務與相關排程。
  - 若有使用翻譯功能，需確保外部翻譯 API 可達。
- **健康檢查**：可透過 `GET /api/version` 確認服務存活；AI 排程健康可透過 `GET /api/aimerge/health` 檢查。

## 相關連結
- GitLab 倉庫：[https://git.zbdigital.net/Biz/mergesite.git](https://git.zbdigital.net/Biz/mergesite.git)