# 內部服務目錄：ImageService

## 概述

**ImageService** 是一套基於 Flask 的圖片驗證碼處理微服務，專注於自動化解決各類驗證碼識別與定位需求。  
服務提供兩大類驗證碼處理：**數字驗證碼辨識**（支援 Google Cloud Vision 與 ddddocr 兩種引擎）與**滑塊驗證碼缺口定位**（透過影像処理演算法計算滑塊偏移量）。  
部署於 Docker Swarm 叢集，並與 Kafka 消息佇列整合，適用於爬蟲或自動化流程的驗證碼破解環節。

## 主要功能

- **數字驗證碼（Captcha）辨識**  
  - `POST /number/captcha`：使用 Google Cloud Vision API 進行文字偵測。  
  - `POST /number/captchaV2`：使用 ddddocr 本地端模型（無需外部 API）。  
  - `GET /number/version`：回傳服務版本號。  
- **滑塊驗證碼（Slide Captcha）缺口定位**  
  - `POST /slide/captcha`：接收 slider（滑塊圖）與 canvas（背景圖），回傳滑塊正確的偏移像素位置。  
  - `GET /slide/version`：回傳服務版本號。  
- **環境感知**：支援 `Local`、`PRD`、`PRD2`、`PRD3`、`PROD` 多組 Kafka 叢集與日誌設定。  
- **日誌與監控**：透過 `TCZB.Logger` 將日誌傳送至指定的 Kafka broker（Graylog / ELK 管道）。

## 技術棧

| 元件 | 技術 |
|------|------|
| 語言 | Python 3.9 |
| Web 框架 | Flask 3.0.3 |
| 容器化 | Docker, Docker Swarm |
| 影像處理 | OpenCV 4.10.0, numpy |
| 驗證碼引擎 | ddddocr 1.5.6, Google Cloud Vision |
| 消息佇列 | Kafka 2.0.2 (kafka-python), ZooKeeper (kazoo) |
| 私有套件 | `TCZB`（內部 logger、globals、versioning 套件，從內部 PyPI 安裝） |
| 部署環境 | Docker Swarm stack（Portainer 管理） |

## 組態與部署注意

1. **環境變數與參數**  
   - 啟動腳本範例（見 `README.md`）：  
     - `python .\project Local`（本地開發）  
     - `python .\project PRD`（正式環境）  
   - 正式環境需傳入對應的 Kafka broker 列表（定義於 `AppSettings.py`）。  
2. **內部相依套件**  
   - `TCZB` 套件需從內部 PyPI 鏡像安裝（`http://localhost:8070`），需確保 Docker 建置時能存取該鏡像。  
   - 在 Dockerfile 中已加入 `--trusted-host localhost:8070`。  
3. **Google Cloud Vision 憑證**  
   - 服務使用服務帳號憑證檔案 `aerial-prism-316101-677e13a100d5.json`（置於專案根目錄），認證金鑰已內含在映像檔中。**請注意金鑰安全性，勿洩漏至公開儲存庫**。  
4. **Kafka 拓樸**  
   - 不同環境使用不同 Kafka 叢集（.9、.10、.11 網段及 HK/BAK），請確認網路連通性。  
   - 服務會依環境設定 `receive_kafka`（接收任務）與 `send_game_data` / `send_html_data`（傳送結果）。  
5. **Docker 建置**  
   - 基礎映像 `python:3.9-slim-buster`，額外安裝 `ffmpeg libsm6 libxext6`（OpenCV 相依）。  
   - 暴露埠 `5000`，啟動進入點為 `python ./project/__main__.py`。  
   - 台灣時區（`TZ=Asia/Taipei`）。  
6. **Portainer 部署**  
   - 現有 stack 名稱為 `imageservice:latest`，容器 ID `9168ba70b065`，歸屬 `PRD_Docker_Swarm` 環境。  

## 相關連結

- **GitLab 原始碼**：<https://git.zbdigital.net/biz/imageservice.git>  
- **Portainer 管理介面**：請洽 DevOps 團隊取得首頁網址及 stack 管理權限  
- **內部套件 TCZB**：需從內網 PyPI 伺服器（`localhost:8070`）取得，維護團隊為平台組