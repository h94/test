# 健康檢查

## 1. 場景目的

提供服務存活性訊號 (Liveness)，供負載平衡器、容器調度平台、監控系統判定服務實例是否正常運行，無需任何認證即可存取。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/heart` | Health Check 端點，回應 200 OK 表示服務正常 |

---

## 3. 流程總覽

1. 負載平衡器或監控系統發起 `GET /api/heart` 請求。
2. 請求命中 `HeartController`，不觸發認證中間件（全域白名單）。
3. Controller 直接回傳 `200 OK`，可附帶系統版本等純資訊性內容。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `HeartController.Heart` | 回傳 `200 OK` 與純文字或簡單物件（如 `Heartbeat` 模型） |

---

## 5. DB / Cache / Queue 使用

**本場景不使用任何 DB、Redis、Kafka 或 Message Queue。**

---

## 6. 重要規則

- 權限限制：**無需認證**，此端點為全網域白名單。
- 不可暴露資料：回傳內容不可包含連線字串、主機 IP、內部機器名稱等敏感資訊。
- TTL 規則：N/A。
- Transaction 規則：N/A。
- Retry 規則：監控系統調用失敗時使用指數退避重試。
- 狀態值限制：HTTP Status 一律為 `200 OK`，若服務無法正常回應即表示故障。
- 不可修改欄位：N/A。
- **需人工確認**：外部負載平衡器（如 Nginx, HAProxy）是否已正確設定 `GET /api/heart` 為健康檢查路徑。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 服務執行中，正常接收請求 | `200 OK`，可附帶 `Heartbeat` 結構 |
| 服務不可用（待機、崩潰、未啟動） | 連線逾時或 `503 Service Unavailable`，由負載平衡器標記為不健康節點 |
| 對 `/api/heart` 發送非 GET 請求（如 POST） | ASP.NET Core 路由層自動回傳 `405 Method Not Allowed` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| HT-01 | API Test | 對 `/api/heart` 發送 GET 請求，無 Token | 回傳 `200 OK` |
| HT-02 | Integration Test | 部署後透過負載平衡器健康檢查路徑存取 | 回傳 `200 OK`，節點標記為健康 |
| HT-03 | Flow Test | 確認健康檢查端點不應經過 ECFramework 認證中間件 | 無 `401 Unauthorized` |

---

## 9. 高風險區域

無。本場景不操作任何持久化資源。主要風險為**設定錯誤**：若誤將 `/api/heart` 加入需驗證的路由清單，將導致監控與服務發現功能失效。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤認為 Health Check 需要傳入 Token 或特定 Header。
- **AI 容易誤解**：將所有無需驗證的端點（例如 `/api/version`）都歸類為 Health Check，功能目的不同（版本查詢 vs 存活性偵測）。
- **常見漏檢查項目**：回傳內容可能不慎透漏內部 IP 或資料庫連線狀態，應避免。
- **常見錯誤流程**：添加 DB 連線或 Redis 嘗試，導致「看似活著但實際半死不活」的假 OK 回應。本場景應保持最輕量。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `HeartController` (from source semantics, `pricecentermanage`) |
| API | `README.md`：`GET /api/heart` 標記為 `Health Check` 且 `❌` 不需驗證 |
| Route | ASP.NET Core 預設無需 `[Authorize]` 屬性，`ECFramework` 全域過濾器應跳過此路由（由架構規則決定） |
| Code | `HeartController` → 回傳 `Ok()` 或 `Ok(Heartbeat)` |