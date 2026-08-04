# 健康檢查與版本

## 1. 場景目的

提供無需驗證的輕量級端點，用於外部監控系統（如負載平衡器、Kubernetes probes）進行服務存活檢測（Liveness）及確認當前部署版本。此流程為運維基礎設施，不涉及任何業務邏輯、資料庫存取或狀態變更。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/heart` | Health Check，回應 HTTP 200 即表示服務進程存活 |
| GET | `/api/version` | 版本查詢，回應目前部署的服務版本號 |

---

## 3. 流程總覽

1. 負載平衡器或監控系統發送 HTTP GET 請求至 `/api/heart`
2. 服務進程直接回應 `200 OK`（可能包含簡單狀態字串如 "OK"）
3. 若需確認版本，請求發送至 `/api/version`
4. 服務讀取嵌入的版本資訊（通常來自程式集或構建時注入的檔案）
5. 直接回應版本號字串

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `HealthController` / `VersionController` | 接收 GET 請求 |
| 2 | Controller | 同上 | **Health**: 直接返回 HttpStatusCode 200 **Version**: 呼叫 Service 層取得版本資訊 |
| 3 | Service | `VersionService` (推測) | 從 `IWebHostEnvironment` 或靜態檔案讀取版本號 |
| 4 | Controller | 同上 | 將版本號以 `text/plain` 或 `application/json` 格式回傳 |

**需人工確認**：Code evidence 中未直接提供 Controller 路徑對應的原始碼檔案，以上流程基於 ASP.NET Core 健康檢查與版本查詢的通用實現模式推估。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| **無** | **無** | **無** | 此流程不涉及任何 DB、Redis、Queue 操作。 |

---

## 6. 重要規則

- **權限限制**：
  - 完全公開，**無需任何驗證**（`[AllowAnonymous]`）。
- **不可暴露資料**：
  - **禁止**在健康檢查或版本端點的回應中，包含任何內部配置、主機名稱、資料庫連接字串或任何敏感資訊。
- **版本號格式**：
  - 版本號應遵循語意化版本控制（Semantic Versioning）或構建編號。需人工確認具體格式。
- **回應延遲**：
  - 為確保監控準確性，此端點的回應必須快速（毫秒級），**嚴禁**在處理過程中執行依賴外部資源的健康檢查（如 DB 查詢、Redis 連線）。
- **日誌記錄**：
  - 為避免日誌系統被監控請求淹沒，通常預設不記錄此類請求的存取日誌，或由基礎設施層（如反向代理）過濾。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 服務進程崩潰或未啟動 | 請求無法到達，HTTP 連線逾時或被拒絕 |
| 部署了錯誤的版本號檔案 | `/api/version` 會回傳錯誤的版本字串，此為部署流程問題，非服務運行時錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| **HCV-01** | API Test | 對 `/api/heart` 發送 GET 請求 | 回應 HTTP Status `200 OK` |
| **HCV-02** | API Test | 對 `/api/version` 發送 GET 請求 | 回應 HTTP Status `200 OK`，且回應 body 為非空字串（如 `1.0.0`） |
| **HCV-03** | Permission Test | 在未攜帶任何 Token 或 Auth Header 的情況下呼叫兩個端點 | 皆成功得到 `200 OK` 回應 |
| **HCV-04** | Flow Test | 在 Docker / K8s 環境中配置 Liveness Probe 指向 `/api/heart` | Pod / Container 狀態保持為 `Running`，不會因健康檢查失敗而被重啟 |
| **HCV-05** | Flow Test | 部署新版本後，呼叫 `/api/version` | 回應的版本號與預期部署的版本號完全一致 |

---

## 9. 高風險區域

- **無**。此場景本身不涉及任何高風險操作。潛在風險來自於錯誤的實現，對此端點進行了不當的擴充，例如在健康檢查中添加對 DB 或外部服務的依賴，導致健康檢查失敗並觸發容器重啟。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - ❌ 為了“完整”，在健康檢查流程中增加對 `Cassandra` 或 `Zookeeper` 的連線檢查。這會使簡單的監控行為變成依賴鏈檢測，可能導致級聯故障或不必要的容器重啟。服務存活探針（Liveness Probe）應僅檢查進程本身。
- **AI 容易誤解**：
  - ❌ 自動為健康檢查端點添加權限驗證。此端點在文檔中已明確標記為 ❌ 無需驗證。
  - ❌ 在生成測試時，為 `/api/heart` 建立複雜的測試場景，例如檢查回傳的 JSON 結構。健康檢查的核心是 HTTP 狀態碼，而非回應內容。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 端點與權限設定 | `README.md` - **系統工具**章節，明確標記 `GET /api/heart` 與 `GET /api/version` **需要驗證**為 ❌。 |
| 服務職責邊界 | `predictservice-detail.md` - **本服務不負責**章節，未將健康檢查歸責於任何其他服務，屬於基礎設施功能。 |
| DB 存取限制 | `predictservice-detail.md` - **member / predict / pricecenter** 角色描述，確認此服務對相關資料庫為唯讀或擁有者，但健康檢查場景不需要使用。 |
| 服務相依性 | `README.md` - **服務相依**章節，列出 memberservice 與 pricecenter，驗證健康檢查不應依賴外部服務。 |