# Price Front End Tools

## 概述
內部價格管理前端工具，提供價格相關資料的視覺化與操作介面，協助使用者快速檢視、編輯及管理產品定價、促銷方案等資訊。

## 主要功能
- 價格列表與搜尋
- 價格修改與批次更新
- 促銷活動設定
- 圖表與統計分析
- 使用者權限管理

## 技術棧
- **前端框架**: Vue 3 (Composition API)
- **語言**: TypeScript
- **狀態管理**: Vuex 4
- **路由**: Vue Router 4
- **HTTP 客戶端**: Axios
- **圖示**: Font Awesome (free-solid, free-regular)
- **樣式**: Sass (node-sass) + sass-loader
- **建置工具**: Vue CLI 4.5
- **靜態伺服器**: nginx (多階段 Docker 建置)
- **開發環境**: Node.js 14

## 組態與部署注意
- **部署平台**: Docker Swarm (生產環境，Portainer Key: `PRD_Docker_Swarm|swarm|pricefrontendtools|pricefrontendtools_PriceFrontEndTools`)
- **Dockerfile**: 使用 Node 14 進行建置，`npm run build` 後將 `dist` 目錄複製至 nginx 映像檔；注意 `RUN rm -rf .env` 刪除原始 .env 檔案，需在建置前或透過外部掛載提供組態。
- **Nginx 設定**: 位於 `docker-config/nginx.conf`，請確保正確設定反向代理或靜態檔案路由。
- **環境變數**: 請透過容器環境變數或掛載 .env 檔案傳遞 API 端點等設定（Dockerfile 在建置階段已移除 .env，故不可於映像檔內保留機敏資訊）。
- **開發模式**: 使用 `npm run serve` 啟動熱重載開發伺服器（預設埠 8080）。

## 相關連結
- **GitLab 儲存庫**: [https://git.zbdigital.net/biz/pricefrontendtools.git](https://git.zbdigital.net/biz/pricefrontendtools.git)
- **Portainer (生產環境)**: 請透過內部 Portainer 管理介面檢視服務 `pricefrontendtools`。