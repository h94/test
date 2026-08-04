# 列出比分閥值設定

## 1. 場景目的
查詢所有球種（game_type）的比分閥值設定，取得完整的設定清單，供管理員檢視或後續維護使用。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | `/api/scorethreshold` | 列出全部比分閥值設定 |

---

## 3. 流程總覽
1. 接收 GET 請求。
2. 呼叫 Service 層查詢所有 `scorethreshold_setting` 資料。
3. 將查詢結果（包含球種、設定內容、操作者、時間戳記）序列化後回傳。
4. 若查詢過程發生例外，回傳 HTTP 500。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ScorethresholdResource.Get` | 接收請求，呼叫 `ScorethresholdService.list_all()`。 |
| 2 | Service | `ScorethresholdService.list_all` | 呼叫 `ScorethresholdProvider.list_all()` 取得資料，並格式化回傳。 |
| 3 | Provider | `ScorethresholdProvider.list_all` | 對 `scorethreshold_setting` 表執行 `SELECT *` 查詢，回傳所有記錄。 |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `scorethreshold_setting` | Read | 查詢所有球種的比分閥值設定。 |

---

## 6. 重要規則
- **權限限制**：此端點目前無強制認證或授權機制（需人工確認：管理後台可能需要加入 API Key 或 JWT 驗證）。
- **欄位限制**：`setting` 欄位為 JSONB，內部結構由業務端定義，後端不做格式校驗。
- **不可暴露資料**：`operator_account` 僅記錄最後異動者，無敏感個資。
- **TTL 規則**：無。
- **Transaction 規則**：單一 SELECT 查詢，無交易需求。
- **Retry 規則**：無。
- **狀態值限制**：無。
- **不可修改欄位**：此端點僅供查詢，無修改行為。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 資料表不存在或無權限 | HTTP 500 Internal Server Error，並記錄錯誤日誌。|
| 資料庫連線失敗 | HTTP 500 Internal Server Error，並記錄錯誤日誌。|
| `scorethreshold_setting` 表為空 | 回傳空陣列 `[]`，HTTP 200。 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ST-01 | API Test | 查詢所有比分閥值設定 | HTTP 200，回傳正確筆數的 JSON 陣列，且每筆包含 `game_type`, `setting`, `operator_account`, `created_at`, `updated_at` 欄位。 |
| ST-02 | API Test | 資料表為空時查詢 | HTTP 200，回傳空陣列 `[]`。 |
| ST-03 | API Test | 資料庫異常時查詢 | HTTP 500，回應包含錯誤訊息。 |

---

## 9. 高風險區域
- **高風險 table**：無。`scorethreshold_setting` 為設定檔，查詢不涉及交易或鎖定。
- **高風險 API**：無。單純查詢，不修改資料。
- **跨服務資料同步**：無。
- **Transaction**：無。
- **Cache consistency**：無快取層，每次查詢直接存取資料庫。
- **Queue retry**：無。
- **Idempotency**：GET 請求本身具備冪等性。

---

## 10. 常見錯誤
- **新人容易犯錯**：
  - 誤以為 `setting` 欄位有固定 schema，實則為任意 JSON，需參考業務文件或既有資料。
  - 在 Provider 層直接操作 dict/row，忘記轉換為 response model。
- **AI 容易誤解**：
  - 把 `scorethreshold_setting` 與 `oddthreshold_sport_setting` 或其他閥值設定表混淆。
  - 誤以為此端點支援以 `game_type` 查詢參數篩選單一球種。目前 OpenAPI 無此參數，為全量查詢（需人工確認：正確實作可能支援 `?game_type=` 篩選，但 OpenAPI Schema 未定義）。
- **常見漏檢查項目**：
  - 未檢查資料庫連線是否成功。
  - 未記錄查詢錯誤日誌。
- **常見錯誤流程**：無。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | OpenAPI `paths./api/scorethreshold.get` |
| Controller | `Resources/ScorethresholdResource.py` `Get` 方法 |
| Service | `Service/ScorethresholdService.py` `list_all` 方法 |
| Provider | `Provider/ScorethresholdProvider.py` `list_all` 方法 |
| DB | `migrations/001_create_core_tables.sql` `scorethreshold_setting` 表定義 |