# 版本檢查

## 1. 場景目的
提供服務版本資訊查詢，供內部系統或自動化腳本確認服務部署版本與健康狀態，常用於監控、部署驗證及依賴服務相容性檢查。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| GET | /api/version | 回傳當前服務的版本資訊 |

---

## 3. 流程總覽
1. 客戶端發送 GET 請求至 `/api/version`
2. Flask 路由接收請求，轉交對應 Controller/處理函式
3. 回傳包含版本號、環境、建置時間等靜態資訊的 JSON（通常由設定檔或環境變數注入）
4. 不進行資料庫讀寫、Redis 操作或 Kafka 日誌發送
5. 回傳 200 OK 並附帶版本資訊主體

---

## 4. 程式流程
> ⚠️ 本服務實際 Controller / Service 原始碼不在分析範圍內，以下流程依一般 Flask 實作推測，需人工確認。

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `VersionController.get_info`? (推測) | 接收 GET 請求 |
| 2 | Service | `VersionService.get_version()` (推測) | 從組態或環境變數讀取版本資訊並組合 |
| 3 | Response | `VersionController.get_info` 回傳 | 回傳 JSON `{"version": "x.y.z", ...}` |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| - | - | - | 本流程不涉及任何 DB、Redis、Kafka 或 Queue 操作 |

---

## 6. 重要規則
- **權限限制**：無需驗證，為公開端點（需人工確認是否限制內部網路）  
- **回傳內容**：不可回傳敏感資訊（如內部 IP、帳號密碼等）；僅回傳服務識別與版本  
- **效能**：應為極輕量，無需 IO，回應時間應小於 50ms  
- **變更原則**：版本號由 CI/CD 在部署時注入，不得在執行階段動態修改  

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 服務啟動中但尚未載入版本設定 | 回傳 503 或空版本（需人工確認具體行為） |
| 請求方法非 GET | 回傳 405 Method Not Allowed |
| 服務不可用 | 連線逾時或 502/503 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | API Test | 正常 GET /api/version | 200，JSON 包含版本欄位 |
| TC02 | Flow Test | 多次呼叫版本 API | 版本號不變，除非重新部署 |
| TC03 | Deployment Test | 部署後檢查 | 版本號與本次部署設定一致 |

---

## 9. 高風險區域
- **無**：此端點為唯讀、無狀態、無副作用，不存取任何持久化資源，不存在一致性或交易風險。

---

## 10. 常見錯誤
- ❌ 忘記在 CI/CD 中注入版本號，導致回傳預設值（例如 `"dev"` 或 `"0.0.0"`）  
- ❌ 誤將此端點對外網公開（若僅供內部使用應透過網路層限制）  
- ❌ 在版本資訊中夾帶不必要的環境變數（如密鑰）  
- ✅ 應確保版本號與 Git tag / commit hash 對應，便於除錯

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API 定義 | README.md（輔助工具 API 段落） |
| 路由 | 推測路由 `/api/version`，需人工確認 (webapi/sitegameoddservice/README.md) |
| 服務職責 | sitegameoddservice-detail.md（未使用 Redis / Kafka） |
| 無 DB 使用 | sitegameoddservice-detail.md 確認本服務未使用 Redis 快取帳戶或賽事資料 |

> 🔍 由於缺少實際 Controller/Service 原始碼，**需人工確認**回傳的具體 JSON 結構、版本號的產生方式（例如是否讀取環境變數 `APP_VERSION` 或檔案 `VERSION`），以及是否需要內部網路授權。

---

### 建議新增文件
- 無，現有 README 已涵蓋 API 清單

### 建議新增測試情境
- 整合測試：模擬服務部署後，確認 `/api/version` 回傳正確版本號與狀態碼

### 建議開發者注意事項
- 版本號管理建議遵循 Semantic Versioning，並與 GitLab Tag 對齊，可於 Docker build 時透過 `ARG` 傳入