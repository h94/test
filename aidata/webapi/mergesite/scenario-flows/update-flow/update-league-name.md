# 更新聯盟名稱

## 1. 場景目的

允許管理後台運維人員變更指定聯盟的主顯示名稱。MergeSite 作為閘道，將更新請求轉發至 PriceCenterService 執行實際寫入。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/leagues/{gameType}/{id}/name` | 更新指定聯盟名稱 |

---

## 3. 流程總覽

1. 接收包含 `gameType` 與 `id` 路徑參數以及新名稱的 PUT 請求
2. 驗證請求者權限（ECCore 驗證機制）
3. 封裝請求，透過 PriceCenterService Gateway（`192.168.55.60`）呼叫對應 API 更新名稱
4. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LeagueController.UpdateName` | 接收 HTTP 請求，呼叫 Service 層 |
| 2 | Service | `LeagueService.UpdateName` | 組合請求 payload，呼叫 PriceCenter gateway |
| 3 | Gateway | `PriceCenterGateway` | 向 PriceCenterService 發送更新請求 |
| 4 | Response | - | 回傳 `ServiceMsgCode` 操作結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| REST API | PriceCenterService | Write (PUT) | 透過 Gateway 轉發更新請求 |

---

## 6. 重要規則

- **權限限制**：需為已驗證使用者（`README.md` 標記為 ✅ 需要驗證）。
- **欄位限制**：名稱字串長度或格式限制需人工確認（現有文件中未明確定義上限）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或 Token 無效 | 回傳 401 Unauthorized |
| 權限不足（非管理員角色） | 回傳 403 Forbidden |
| `gameType` 或 `id` 無效（路徑參數格式錯誤） | 回傳 400 Bad Request |
| PriceCenterService 無法連線 | 回傳 502 Bad Gateway 或 500 Internal Server Error |
| 指定聯盟不存在 | 回傳 404 Not Found（由 PriceCenterService 回傳） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-01 | API Test | 發送有效 PUT 請求，包含合法 payload | 返回 200 及成功訊息 |
| UT-02 | Permission Test | 使用未驗證或權限不足的 Token 發送請求 | 返回 401 或 403 |
| UT-03 | Flow Test | 模擬 PriceCenterService 回傳錯誤 | MergeSite 正確映射錯誤碼並回傳 |

---

## 9. 高風險區域

- **跨服務資料同步**：MergeSite 本身無資料庫，資料一致性完全依賴 PriceCenterService。若 PriceCenterService 內部寫入失敗或延遲，前端可能看到不一致狀態。
- **Idempotency**：重複發送相同名稱更新請求應具備冪等性，但需人工確認 PriceCenterService 是否支援。

---

## 10. 常見錯誤

- 新手可能未指定 Content-Type 為 `application/json` 而導致 415 Unsupported Media Type。
- AI 可能誤解 `{id}` 路徑參數為數字，實際上應為字串（`OpenAPI` 定義為 `string`）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `OpenAPI`: `PUT /api/leagues/{gameType}/{id}/name` |
| 驗證需求 | `README.md` 聯盟管理表格 |
| 流程 | `scenario-description`: "透過 PriceCenterService 寫回更新" |
| 服務相依 | `README.md`: 資料讀寫均透過 PriceCenterService 進行 |
| Code | `LeagueController.UpdateName` (from source semantics) |