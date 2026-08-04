# 查詢單一公告詳情

## 1. 場景目的
讓管理後台或前端頁面依 `aid` 查詢單筆公告的完整詳細內容，包含所有多語言欄位 (`maintopic`、`text1`～`text3`)。管理端可查詢任意狀態的公告，前台則只會看到狀態為「已公告」且在有效時間內的公告。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 查詢單一公告詳情 |

> **Evidence**: README.md - 公告佈告欄表格，`GET /api/v1/sport/bulletinboard/announcenments/{aid}`。

---

## 3. 流程總覽
1.  API 接收 `aid` 作為路徑參數，並透過驗證框架檢查請求權限。
2.  呼叫 Service 層執行查詢邏輯。
3.  依呼叫端身份（管理端 or 前台）決定是否過濾 `status`。
4.  從 Cassandra `ads.bulletinboard_sport` 依主鍵 (`aid`) 查詢公告資料。
5.  若為前台請求，在應用層驗證 `status=1` 且當前時間介於 `starttime` 與 `endtime` 之間。
6.  將查詢結果（所有多語言欄位及屬性）回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportBulletinBoardController.GetAnnouncement` | 接收 `aid`，呼叫 Service |
| 2 | Service | `BulletinBoardService.GetAnnouncementDetail` | 組合查詢條件，決定是否過濾狀態 |
| 3 | Provider | `BulletinBoardProvider.GetById` | 向 Cassandra 執行主鍵查詢 |
| 4 | Service | `BulletinBoardService` | 前台請求：驗證 `status==1` 與時間有效性 |
| 5 | Controller | `SportBulletinBoardController` | 回傳完整公告物件 |

> **需人工確認**: 實際 Controller / Service / Provider 類別與方法名稱，以上為依據 README 與 db-usage 慣例推斷。若原始碼不同，請以實際專案為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `ads.bulletinboard_sport` | Read | 依 `aid` 查詢單一公告的完整資料 |

> **重要**：本服務並未使用 Redis 快取公告資料，所有查詢均直接讀取 Cassandra。
> **Evidence**: `advertisingservice-detail.md` Redis 章節：`本服務未使用 Redis，所有資料均直接讀寫 Cassandra。`

---

## 6. 重要規則

- **權限限制**：所有 API 都需要驗證（✅）。
- **`aid` 不可修改**：`aid` 為 Partition Key，建立後不可更新。
- **狀態值限制**：
    - 前台查詢僅回傳 `status=1`（已公告）的記錄。
    - 管理端可查詢任意 `status`（0:草稿、1:已公告、2:已下架）。
- **`maintopic` / `text1~3`**：資料型態為 `map<text, text>`，前端須自行根據使用者語系選擇對應的顯示文字，服務端不回傳單一語言版本。
- **不可回傳欄位**：公告所有欄位皆屬公開資訊，無額外限制。
- **`starttime` / `endtime`**：前台查詢時必須驗證 `starttime <= 當前時間 <= endtime`。此查詢邏輯在應用層實作，非 DB 層。

> **Evidence**:
> - `advertisingservice-detail.md` -> `aid 欄位`、`status 欄位`、`maintopic / text1 / text2 / text3 欄位`。
> - `advertisingservice-detail.md` -> `bulletinboard_sport 查詢`規則。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `aid` 不存在 | API 回傳 404 Not Found 或錯誤碼，前端顯示「公告不存在」。 |
| 前台查詢 `status=0` (草稿) 或 `status=2` (已下架) 的公告 | 應用層過濾掉，回傳 404 或對應訊息。 |
| 前台查詢，當前時間小於 `starttime` | 應用層過濾掉，視為無效公告，回傳 404。 |
| 前台查詢，當前時間大於 `endtime` | 應用層過濾掉，視為過期公告，回傳 404。 |
| Cassandra 查詢超時或連線失敗 | 記錄錯誤日誌至 Kafka+Cassandra，API 回傳 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 以有效的 `aid` 查詢已公告且在時效內的公告 | 200 OK，回傳完整公告資料。 |
| T2 | Permission Test | 前台查詢草稿公告 (`status=0`) | 404，無法查詢。 |
| T3 | Flow Test | 前台查詢已過期公告 (`endtime` < now) | 404，無法查詢。 |
| T4 | API Test | 使用不存在的 `aid` 進行查詢 | 404 或對應錯誤碼。 |
| T5 | Flow Test | 管理端查詢任意 `status` 的公告 | 200 OK，成功回傳任意狀態的公告。 |
| T6 | Integration Test | Cassandra 離線時發起查詢 | 500 Internal Server Error，並記錄異常日誌。 |

---

## 9. 高風險區域

- **快取一致性**：雖然此場景無快取，但若未來導入 Redis 快取，需確保公告更新（`PUT`）或刪除（`DELETE`）時，相關快取有被確實清除或更新。
- **併發讀寫**：此為純讀取場景，風險低。風險主要發生在更新或刪除公告時，需確保查詢不會讀到不一致的資料（Cassandra `read_repair` 預設為 `BLOCKING`）。
- **時間驗證依賴**：前台查詢的有效時間驗證完全依賴於應用層邏輯，而非 DB 查詢。若程式碼未正確實作時間過濾，將導致未生效或已過期的公告洩漏至前台。

---

## 10. 常見錯誤

- **新人容易犯錯**：
    - 在前端進行 `status` 或時間過濾，誤以為服務端已處理。需明確：此過濾邏輯在服務端。
    - 對 `maintopic` 等 `map` 型態欄位進行服務端語言解析，試圖只回傳特定語系文字。正確做法為回傳完整 `map`，由前端選擇。
- **AI 容易誤解**：
    - 誤以為公告查詢有使用 Redis 快取。
    - 誤以為 `starttime` / `endtime` 的過濾是在 Cassandra 的 CQL 語句中完成。實際是服務端應用層過濾。
- **常見漏檢查項目**：前台請求時，漏掉對 `status=1` 的驗證。
- **常見錯誤流程**：管理後台查詢公告時，加入了多餘的 `status=1` 過濾，導致無法查詢到草稿或已下架公告。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md: `GET /api/v1/sport/bulletinboard/announcenments/{aid}` |
| DB | Cassandra `ads.bulletinboard_sport` |
| Code | Controller: `SportBulletinBoardController` (推斷) |
| 讀取規則 | advertisingservice-detail.md: `bulletinboard_sport 查詢`、`status 欄位`、`starttime / endtime 欄位` |
| 無 Redis 使用 | advertisingservice-detail.md: `Redis 章節` |