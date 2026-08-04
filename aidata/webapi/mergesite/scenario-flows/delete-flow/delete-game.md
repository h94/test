# 場景：刪除比賽

## 1. 場景目的

後台管理員刪除特定比賽記錄。此操作經由 PriceCenterService 執行，會連帶影響該比賽的合併狀態與前台顯示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| DELETE | `/api/game/{gameType}/{lid}/{gDate}/{gid}` | 刪除指定球種、聯盟、日期的特定比賽 |

---

## 3. 流程總覽

1. 接收後台管理員的刪除請求
2. 驗證使用者權限（需為已驗證的後台管理員）
3. 將請求轉發至 PriceCenterService 執行刪除
4. PriceCenterService 執行實際的比賽資料刪除（軟刪除或狀態變更）
5. 回傳操作結果給管理後台

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameController.DeleteGame` | 接收 DELETE 請求，解析路徑參數 `gameType`, `lid`, `gDate`, `gid` |
| 2 | Service | `PriceCenterService.DeleteGame` | 將刪除請求轉發至 PriceCenterService REST API |
| 3 | Provider | PriceCenterService REST API | 執行實際的刪除邏輯，更新比賽記錄狀態 |
| 4 | Controller | `GameController.DeleteGame` | 回傳 `ServiceMsgCode` 結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | sport 資料庫（比賽記錄表） | Update | PriceCenterService 執行比賽狀態變更或軟刪除 |
| Queue | Kafka | Publish | 記錄刪除操作日誌 |

**注意**：此服務無直接資料庫操作，所有 DB 操作均由 PriceCenterService 代理執行。

---

## 6. 重要規則

- **權限限制**：僅已驗證的後台管理員可執行此操作
- **路徑參數完整性**：`gameType`, `lid`, `gDate`, `gid` 必須全部提供，缺一不可
- **不可逆操作**：刪除比賽通常為軟刪除（標記狀態），而非物理刪除，以保留歷史記錄
- **連帶影響**：刪除比賽可能影響已合併的賽事顯示，需確認下游服務的同步機制
- **日誌記錄**：所有刪除操作均須記錄至 Kafka 供審計與監控使用
- **非 get 請求**：此為 DELETE 請求，不支援 GET 方式調用

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 使用者未通過驗證 | 回傳 `401 Unauthorized` |
| 使用者權限不足（非管理員） | 回傳 `403 Forbidden` |
| `gameType` 不存在或格式錯誤 | 回傳 `400 Bad Request` 或 `404 Not Found` |
| `lid` 對應的聯盟不存在 | 回傳 `404 Not Found`，訊息包含無效的聯盟 ID |
| `gDate` 格式不正確 | 回傳 `400 Bad Request`，提示日期格式錯誤 |
| `gid` 對應的比賽不存在 | 回傳 `404 Not Found`，訊息包含無效的比賽 ID |
| PriceCenterService 無回應或逾時 | 回傳 `502 Bad Gateway` 或 `504 Gateway Timeout` |
| PriceCenterService 回傳內部錯誤 | 回傳 `500 Internal Server Error`，記錄原始錯誤日誌 |
| 比賽已刪除（重複刪除） | 回傳 `404 Not Found` 或自定義業務錯誤，表示資源已不存在 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| DEL-01 | Permission Test | 未帶 token 呼叫刪除 API | 回傳 401 Unauthorized |
| DEL-02 | Permission Test | 非管理員 token 呼叫刪除 API | 回傳 403 Forbidden |
| DEL-03 | API Test | 提供有效的管理員 token 與正確的路徑參數 | 回傳 200 OK，比賽記錄狀態變更為已刪除 |
| DEL-04 | API Test | 提供正確參數但比賽不存在 | 回傳 404 Not Found |
| DEL-05 | API Test | 提供不存在的 `gameType` | 回傳 404 或 400 Bad Request |
| DEL-06 | API Test | 提供無效的 `gDate` 格式（如 `2023/01/01`） | 回傳 400 Bad Request |
| DEL-07 | Flow Test | 刪除後再次查詢該比賽 | 查詢結果不包含已刪除的比賽 |
| DEL-08 | Flow Test | 刪除比賽後檢查 Kafka 日誌 | 存在一條包含操作者、時間、比賽 ID 的刪除日誌 |

---

## 9. 高風險區域

- **高風險 API**：`DELETE /api/game/{gameType}/{lid}/{gDate}/{gid}` — 此為不可逆操作（或難以回復），需嚴格控制權限並記錄日誌
- **跨服務資料同步**：mergesite 無直接資料庫，完全依賴 PriceCenterService 執行刪除，網路或服務故障將導致操作失敗
- **軟刪除與硬刪除**：需確認刪除的實際行為是軟刪除（`status` 欄位變更）還是硬刪除（物理移除），避免誤解
- **合併一致性**：若比賽已被合併至其他記錄，刪除後可能導致合併資料不一致，需確認 PriceCenterService 的連帶處理邏輯
- **Queue 失敗處理**：Kafka 日誌發送失敗不應影響主要業務流程，但須記錄失敗事件以便監控

---

## 10. 常見錯誤

- ❌ **新人易錯**：誤以為 mergesite 直接操作資料庫，實際上所有操作由 PriceCenterService 代理
- ❌ **新人易錯**：未攜帶有效的管理員 token 進行測試，導致權限錯誤難以排查
- ❌ **AI 易誤解**：將此服務的刪除視為直接 DB 操作，忽略了 Gateway 代理架構
- ❌ **常見漏檢查**：未確認 `gDate` 格式（應為 `yyyy-MM-dd` 或類似格式），導致參數驗證失敗
- ❌ **常見錯誤流程**：刪除後未檢查 Kafka 日誌是否正確記錄，導致稽核遺漏

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `DELETE /api/game/{gameType}/{lid}/{gDate}/{gid}` |
| DB（實際操作由 PriceCenterService 執行） | 需人工確認 PriceCenterService 中的 Table 與欄位 |
| Code | 需人工確認 `GameController.DeleteGame` 方法簽名 |
| 權限 | README: 所有管理 API 均標記 `✅ 需要驗證` |
| Kafka | README: 服務相依包含 Kafka，用途為應用程式 Log 寫入 |
| 架構 | README: 服務無直接資料庫，透過 Gateway 呼叫 PriceCenterService REST API |