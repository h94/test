# 刪除公告

## 1. 場景目的

後台管理人員指定 `aid`，將一筆公告從資料庫永久移除。此動作不可逆，且通常僅在公告已下架或無效時執行。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 刪除指定 `aid` 的公告 |

---

## 3. 流程總覽

1. 接收 delete request，其中包含 path 參數 `aid`
2. 驗證 authentication / authorization（僅後台管理人員可執行）
3. 依據 `aid` 查詢 `ads.bulletinboard_sport`
4. 驗證記錄是否存在及當前狀態
5. 執行刪除操作
6. 回傳成功或錯誤 response

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportBulletinBoardController.DeleteAnnouncement` (推測) | 接收 `aid`，呼叫 Service |
| 2 | Service / Provider | `BulletinBoardService.Delete` (推測) | 驗證權限、根據 `aid` 查詢 Cassandra |
| 3 | Provider | `CassandraProvider` | 執行 `DELETE FROM bulletinboard_sport WHERE aid = ?` |
| 4 | (無) | (無 Redis / Queue 操作) | 不須清除快取或發送事件 |

**需人工確認**：具體 Controller / Service class 名稱需核對實際 code 結構。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ads.bulletinboard_sport` | Read | 檢查公告是否存在及當前狀態 |
| DB | `ads.bulletinboard_sport` | Delete | 永久移除公告記錄 |
| - | Redis / Cache | - | 此操作未使用 Redis |
| - | Kafka / Queue | - | 此操作未使用 Queue |

---

## 6. 重要規則

- **狀態限制**：需人工確認是否可直接刪除。根據廣告服務 DB 邊界文件，公告狀態變更應遵循合法流程（0→1 可，1→0 可能限制），發布後不可直接刪除，應先下架（status=2）再刪除，或由管理端審核後直接刪除。
- **不可恢復**：Cassandra 中的刪除操作為永久移除，無軟刪除機制，刪除前應對操作者提供二次確認。
- **不可修改欄位**：`aid` 為分割區鍵，建立後不可修改。
- **權限限制**：僅後台管理人員可執行，需要通過 ECFramework 驗證。
- **寫入限制**：僅 advertisingservice 擁有寫入權限，其他服務均為唯讀。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未通過身份驗證或權限不足 | 回傳 401 Unauthorized 或 403 Forbidden |
| 提供的 `aid` 不存在 | 回傳 404 Not Found 或業務錯誤碼 |
| 公告已發布 (status=1) 且不允許直接刪除 | 回傳 422 Unprocessable Entity 並提示需先下架 |
| Cassandra 寫入 timeout 或失敗 | 回傳 500 Internal Server Error 並記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| DEL-AUTH-01 | Permission Test | 不帶 token 或使用無效 token 呼叫 | 401 或 403 |
| DEL-AUTH-02 | Permission Test | 使用非管理員 token 呼叫 | 403 或業務錯誤碼 |
| DEL-FLOW-01 | Flow Test | 刪除不存在的 `aid` | 404 或「公告不存在」訊息 |
| DEL-FLOW-02 | Flow Test | 成功刪除 status=0 的公告 | 200 OK，記錄從 DB 消失 |
| DEL-FLOW-03 | Flow Test | 刪除 status=1 (已發布) 的公告 | 422 Error |
| DEL-FLOW-04 | Flow Test | 刪除 status=2 (下架) 的公告 | 200 OK，記錄從 DB 消失 |
| DEL-DB-01 | Integration Test | 刪除後再次查詢該 `aid` | 查無資料 |
| DEL-DB-02 | Integration Test | 模擬 Cassandra 連線失敗 | 500 Error |

---

## 9. 高風險區域

- **高風險 Table**：`ads.bulletinboard_sport` — 刪除為物理刪除，無日誌表記錄（除非 Kafka 日誌記錄，此為推測）。
- **高風險 API**：`DELETE /api/v1/sport/bulletinboard/announcenments/{aid}` — 須嚴格控制權限。
- **跨服務資料同步**：無。
- **Cache consistency**：無 Redis 快取，不需處理。
- **Idempotency**：刪除操作天生具備冪等性（重複刪除不存在記錄應回傳成功或相同錯誤）。

---

## 10. 常見錯誤

- ❌ 未檢查公告是否存在，直接執行 DELETE 語句（Cassandra DELETE 即使記錄不存在也不會報錯），導致管理員誤認為已成功刪除。
  → ✅ 刪除前應先 SELECT 確認該 `aid` 是否存在。
- ❌ 允許直接刪除已發布 (status=1) 的公告，違反業務流程。
  → ✅ 嚴格檢查 `status`，僅允許刪除草稿 (0) 或下架 (2) 狀態的公告。
- ❌ 誤認 `DELETE` 為軟刪除或可恢復操作。
  → ✅ 文件與 UI 都必須標示此為永久刪除、不可恢復。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md — DELETE `/api/v1/sport/bulletinboard/announcenments/{aid}` |
| DB Table | `ads.bulletinboard_sport` |
| DB 狀態機 | `advertisingservice-detail.md` — `status` 欄位定義 (0=草稿, 1=發布, 2=下架) |
| DB 寫入規則 | `advertisingservice-detail.md` — 「`status`：狀態變更須遵循合法流程 (例如 0→1 可，1→0 可能限制)；禁止直接 UPDATE 跳過中間狀態。」 |
| 權限 | README.md — 此 API 「需要驗證」 |
| 不可恢復 | Cassandra 為 NoSQL 無內建 trash/recycle bin 機制 (系統推論) |