# 服務版本查詢

## 1. 場景目的

提供一個無需驗證（No Auth）的端點，讓維運監控系統、部署工具或開發人員查詢目前運行中服務的版本號，以確認部署版本正確或服務仍在運行。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/version` | 回傳目前服務的版本號，無需認證 |

---

## 3. 流程總覽

1. 接收 GET `/api/version` request。
2. 從服務的 Assembly 或配置中讀取目前版本號（例如 `1.0.0` 或從 `appsettings.json` / 環境變數取得）。
3. 將版本號以純文字（`text/plain`）或 JSON 格式回傳。
4. 完成，不回寫任何 DB、Cache 或 Queue。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SystemController.Version` (推測) | 接收 GET request。因 README 顯示路由為 `/api/version`，且同控制器下有 `/api/heart` (Health Check) |
| 2 | Provider/Service | `ISysManagerProvider` 或 `VersionService` | 若版本號由 Assembly 讀取，則由 Provider / Helper 呼叫 `Assembly.GetExecutingAssembly().GetName().Version.ToString()` |
| 3 | Controller | 同上 | 將版本號字串以 `200 OK` 回傳，Content-Type 可能是 `text/plain` 或 `application/json` |

*需人工確認*：版本號確切來源（如 Assembly Version、File Version、appsettings 中的自訂字串）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 無 | 無 | 無 | 此場景為純靜態資訊回傳，不讀寫任何 DB、Redis、Kafka 或 Queue |

此 API 極度輕量，僅回傳記憶體中的常數或 Assembly 資訊，無任何 I/O 操作。

---

## 6. 重要規則

- **權限限制**：無，API 未標示「✅ 需要驗證」，且 README 中 `/api/version` 與 `/api/heart` 並列，兩者皆為 Public Endpoint。
- **欄位限制**：無輸入參數。回傳值僅為一個簡短的字串，不可包含任何敏感資料或錯誤詳細資訊。
- **不可暴露資料**：版本號字串不可包含連線字串、內部 IP、主機名稱或金鑰。
- **TTL 規則**：不適用。
- **Transaction 規則**：不適用。
- **Retry 規則**：不適用（存取成本極低）。
- **狀態值限制**：不適用。
- **不可修改欄位**：版本號在服務啟動後為唯讀，不可透過 API 動態變更。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| URL 路徑拼寫錯誤（例如 `/api/versoin`） | 預設路由回傳 404 Not Found（若未另外設定 MVC 例外處理）。 |
| 請求方法不是 GET（例如 POST） | ASP.NET Core 會回傳 405 Method Not Allowed，因該路由未設定 `[HttpPost]`。 |
| 服務尚未完全啟動 | 負載均衡器或反向代理會收到連線錯誤，通常會自動重試，此處不應回傳特殊內容。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| VT-01 | API Test | GET `/api/version` | 狀態碼 200，Response Body 為非空版本字串。 |
| VT-02 | API Test | GET `/api/version` 在部署新版本後 | 回傳的版本號應等於本次部署的預期版本號。 |
| VT-03 | Permission Test | GET `/api/version`（無 token） | 200 OK，與攜帶 token 無異，無權限阻擋。 |
| VT-04 | Flow Test | 連續快速請求 `/api/version` 10 次 | 全部回傳 200 且版本號一致，無 throttle 或降級。 |
| VT-05 | API Test | POST `/api/version` | 405 Method Not Allowed。 |

---

## 9. 高風險區域

- **高風險 table**：無。
- **高風險 API**：無。此 API 不存取任何內部資源，無法造成資料洩漏或修改。
- **跨服務資料同步**：無。
- **Transaction**：無。
- **Cache consistency**：無快取層，理論上無一致性風險。唯一的風險是：若服務 Process 未重啟但部署工具誤認為已更新，需仰賴回傳正確版本號來驗證，此責任在部署流程而非服務本身。
- **Queue retry**：無。
- **Idempotency**：GET 方法本身為冪等，且回應永遠一致（除非服務重啟並載入新版本 Assembly）。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 為 `/api/version` 加上不必要的 `[Authorize]` 驗證，導致監控系統因 401 而無法取得版本。
  - 在回傳字串中加入換行或空白，造成監控系統解析異常。
- **AI 容易誤解**：
  - 以為版本號儲存在 DB（如 `extension_version` 表）而進行查詢。`extension_version` 是對外部爬蟲平台發布的版本，與本服務自身版本無關。
- **常見漏檢查項目**：
  - 忘記在部署後測試此端點確認新版本生效，特別是在容器（Docker / K8s）環境，若 image tag 錯誤，將回傳舊版本號。
  - 忘記確認 `Content-Type` 標頭，雖然監控系統通常只處理 Body，但若需解析 JSON，則需確認格式。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` -> 對外 API 重點 -> 系統監控與 Bet365 爬蟲管理 -> `GET /api/version` 查詢版本號 ❌ (不需驗證) |
| Code | `SystemController.Version()` (推測) — 程式碼未提供細節 |
| DB | 不涉及任何 DB 讀寫 |
| Redis | 不使用 |
| Queue | 不使用 |