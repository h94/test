# 查詢所有商家

## 1. 場景目的

取得系統中所有商家的基本資訊，回傳時不包含 `authtoken` 欄位。供後台管理介面或其他內部服務查詢完整的商家清單。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/businesses` | 查詢所有商家 |

---

## 3. 流程總覽

1. 接收 GET `/api/v1/businesses` 請求
2. 通過 ECFramework 的授權驗證（需 `Enabled = 1` 的有效團隊）
3. 從 Cassandra `gamesettings.businesses` 讀取所有商家記錄
4. DTO 轉換時排除 `authtoken` 欄位
5. 回傳商家基本資訊列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BusinessController.GetAllBusinesses` | 接收 GET 請求，呼叫 Service |
| 2 | Service | `IBusinessService.GetBusinesses` | 讀取 Cassandra `businesses` 表所有記錄 |
| 3 | Service | `IBusinessService.GetBusinesses` | 將 `Business` 實體轉換為 DTO，排除 `authtoken` |
| 4 | Controller | `BusinessController.GetAllBusinesses` | 回傳 `List<Business>` JSON |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `gamesettings.businesses` | Read (全表掃描) | 取得所有商家資料 |

**注意**：本場景不使用 Redis 快取，直接查詢 Cassandra。根據 `gamesettingservice-detail.md`，本服務未直接使用 Redis。

---

## 6. 重要規則

- **授權**：需通過 ECFramework 驗證；`Enabled = 1` 的團隊才能呼叫
- **不可暴露 `authtoken`**：任何對外 API 回傳皆不可包含此欄位；僅後端服務溝通時使用
- **全表掃描**：`businesses` 表原則是單一主鍵查詢；此 API 為少數允許全表掃描的情境
- **無交易需求**：純讀取，不需 Transaction
- **TTL**：不適用（未使用快取）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未授權請求（缺少驗證 Header） | 回傳 `401 Unauthorized` |
| 團隊已停用（`Enabled = 0`） | 回傳 `403 Forbidden` |
| Cassandra 連線失敗或超時 | 回傳 `500 Internal Server Error` |
| `businesses` 表不存在 | 回傳 `500` 或底層拋出 Exception |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| BUS-QUERY-01 | API Test | 正常請求取得所有商家 | 回傳 `200`，不包含 `authtoken` |
| BUS-QUERY-02 | Permission Test | 未授權請求 | 回傳 `401` |
| BUS-QUERY-03 | API Test | 確認 `authtoken` 不在回應中 | 每個物件皆無 `authtoken` 欄位 |
| BUS-QUERY-04 | Flow Test | Cassandra 無資料 | 回傳空陣列 `[]` |

---

## 9. 高風險區域

- **全表掃描**：若商家數量龐大，可能影響 Cassandra 效能；需監控查詢延遲
- **`authtoken` 洩漏**：若 DTO 映射邏輯有誤，可能將敏感 Token 回傳至前端（高風險）
- **Cache consistency**：未使用快取，無一致性問題

---

## 10. 常見錯誤

- ❌ 回傳 `authtoken`：未在 DTO 轉換時排除，導致 Token 洩漏
- ❌ 新增不必要的快取：此場景為全表查詢，加上快取可能導致資料不一致
- ❌ 使用非同步方法但未處理取消：長時間查詢時未傳遞 `CancellationToken` 可能導致資源浪費
- ❌ 在 Controller 直接操作 Cassandra：應透過 Service 層封裝

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `BusinessController.GetAllBusinesses` (推斷) |
| DB | `gamesettings.businesses` |
| Code | `IBusinessService.GetBusinesses` (推斷) |
| 不可回傳欄位 | `gamesettingservice-detail.md` — authtoken 規則 |
| 驗證規則 | `gm.teams` (AuthToken + Enabled) |
| Schema | `gamesettings.businesses` (Cassandra) |

---

## 12. 建議事項

- **建議新增 Logging**：若尚無，建議記錄「查詢所有商家」的操作者與時間，寫入 `action_logs` (Cassandra)
- **建議新增分頁**：若商家數量成長，應改為分頁查詢，降低 Cassandra 負載
- **需人工確認**：實際 Controller 與 Service 的類別名稱、方法簽章是否與推斷一致