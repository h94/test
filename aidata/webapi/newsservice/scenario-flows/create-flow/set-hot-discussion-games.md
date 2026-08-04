# 設定 AI 熱門討論遊戲

## 1. 場景目的

管理人員在後台指定特定日期、特定球種下的某個聯賽為「AI 熱門討論遊戲」，該設定將影響 AI 內容生成的優先級、篩選列表或前端展示，確保重要的比賽能夠優先被 AI 處理並獲得更多關注。

---

## 2. 入口 API

> **注意**：根據現有文件，未找到直接對應的 `SetHotDiscussionGame` API 端點。此流程基於 `db/news-detail.md` 中 `gamesettingsite` 服務的寫入責任推導。API 定義需人工確認。

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sports/ai/hotdiscussion` (推估路徑) | 設定特定比賽為熱門討論 |

該 API 應由 `gamesettingsite` 管理後台調用，並通過 API gateway 預先進行用戶認證與授權。

---

## 3. 流程總覽

1. 管理員在後台選擇特定日期、球種、聯賽，並將其標記為「熱門討論」。
2. `gamesettingsite` 接收請求，驗證使用者權限（管理員角色）。
3. 調用 `newsservice` 的內部服務介面（如 `IAINewsService.SetAICommunityHotDiscussionGame`）。
4. `newsservice` 驗證 `gdate`、`gtype`、`lid` 必要參數和權限。
5. 將設定寫入 `aifunshits` 或 `ainews` 相關表（實際儲存方式需由 `gamesettingsite` 通過其寫入責任確認，可能寫入 `aireports` 的 `others` 欄位或 `ainews` 的 `others` 欄位標記熱門）。
6. 寫入成功後回傳確認訊息。

**流程備註**：根據 `db/news-detail.md`，`aifunshits` 表僅由管理後台寫入，極有可能用於此類偏好設定。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller (gamesettingsite) | `HotDiscussionController.Set` (推估) | 接收請求，解析 `gdate`、`gtype`、`lid` 參數 |
| 2 | Service (gamesettingsite) | `HotDiscussionService.SetAsync` (推估) | 執行業務邏輯，調用 newsservice |
| 3 | Service (newsservice) | `AINewsService.SetAICommunityHotDiscussionGame` | 驗證參數、確認比賽存在性，寫入設定 |
| 4 | Provider (newsservice) | `AINewsDataProvider` (推估) | 執行 Cassandra 寫入操作，可能涉及 `INSERT` 或 `UPDATE` `aifunshits` 或 `aireports`/`ainews` 的 `others` 欄位 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `aifunshits` 或 `ainews.others` / `aireports.others` | Write/Update | 標記特定聯賽為熱門討論，可能儲存為 `funsname="hotdiscussion"`, `workspace="..."`, `aihints` 包含聯賽資訊 |
| Redis | 未使用 | - | 無 |
| Kafka/Queue | 未明確提及 | - | 若後續需觸發 AI 生成或通知，可能透過事件匯流排，但目前無直接證據。 |

---

## 6. 重要規則

- **權限限制**：此操作僅限管理後台使用者執行，由 `gamesettingsite` 服務驗證。
- **欄位限制**：
  - `gdate`, `gtype`, `lid` 必須提供且不為空。
  - `lid` 必須對應到真實存在的聯賽（需人工確認是否有外部驗證）。
  - 若寫入 `aifunshits`，`funsname` 必須唯一，常使用 `INSERT ... IF NOT EXISTS`。
- **不可暴露資料**：若使用 `aifunshits`，其 `aihints` 欄位不可對外回傳。
- **狀態值限制**：此操作不涉及 `ainews` 的 `status` 或 `used` 欄位變更。
- **不可修改欄位**：無，此為新增或更新設定。
- **跨服務責任**：
  - `gamesettingsite` 負責管理邏輯與 API 暴露。
  - `newsservice` 負責資料持久化。
  - `sportsService` 提供聯賽與比賽基礎資料，設定時可能需調用驗證 `lid` 有效性（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供必要參數 (gdate, gtype, lid) | 回傳 400 錯誤，提示參數缺失 |
| 使用者無管理員權限 | 回傳 401 或 403 權限不足 |
| gtype 不在允許的球種列表中（如 SC, FB, BK） | 回傳 400 錯誤，提示球種代碼無效 |
| lid 對應的聯賽不存在 | 回傳 404 錯誤，提示聯賽不存在（若實作驗證） |
| newsservice 無法連接 Cassandra | 回傳 500 內部伺服器錯誤或 503 服務不可用 |
| 重複設定已存在之熱門討論（若為唯一約束） | `INSERT IF NOT EXISTS` 失敗，可回傳 409 Conflict 或視為成功（冪等） |
| 嘗試寫入 `aifunshits` 但 `funsname` 已存在 | 若使用 `INSERT` 無 `IF NOT EXISTS`，可能覆蓋，需人工確認策略 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-HOT-01 | Integration Test | 正常設定熱門討論遊戲，寫入成功 | 返回 200 OK，資料庫正確新增或更新記錄 |
| TC-HOT-02 | Permission Test | 非管理員角色嘗試設定 | 返回 403 Forbidden |
| TC-HOT-03 | API Test | 缺少 gdate 參數 | 返回 400 Bad Request，指出缺失欄位 |
| TC-HOT-04 | API Test | 提供無效的 gtype | 返回 400 Bad Request，指出 gtype 無效 |
| TC-HOT-05 | Flow Test | 設定後，查詢該聯賽的 AI 新聞狀態 | 確認該聯賽在 AI 生成列表或查詢中具有更高優先級（需定義優先級效果後再測） |
| TC-HOT-06 | API Test | 重複設定同一聯賽（驗證冪等性） | 返回 200 OK 或 409 Conflict，取決於實作。若 200，資料不得重複 |

---

## 9. 高風險區域

- **高風險 Table**：`aifunshits`（因其 `aihints` 可能影響 AI 行為，錯誤的設定可能導致 AI 生成內容偏差）。
- **高風險 API**：`gamesettingsite` 的設定 API，若暴露給錯誤的用戶群或缺乏嚴謹的參數驗證，可能導致大規模錯誤配置。
- **跨服務資料同步**：需確保 `gamesettingsite` 和 `newsservice` 之間的設定寫入是立即生效的，以影響後續 AI 生成排程。目前未使用訊息佇列，依賴同步 API 呼叫。
- **Cache consistency**：本服務未使用 Redis，暫無快取一致性問題。若未來前端快取管理後台設定，需考慮失效策略。
- **Idempotency**：重複設定應保持冪等，不應產生重複記錄或錯誤。若使用 `aifunshits` 且 `funsname` 為主鍵，重複 INSERT 可能失敗，需在 Service 層處理為 UPDATE。

---

## 10. 常見錯誤

- ❌ 開發人員誤認為這是前端直接調用的 API → 實際應由 `gamesettingsite` 的管理後臺觸發，間接調用 newsservice。
- ❌ 直接手動修改 `aifunshits` 或相關表中的資料，繞過服務層 → 可能導致資料格式錯誤或權限繞過，管理操作必須通過 API。
- ❌ 在設定時忽略了 `gtype` 的有效性驗證 → 可能寫入無效球種代碼，導致 AI 流程異常。
- ❌ 假設此操作會修改 `ainews` 表中的 `status` 或 `used` → 此設定不應影響既有新聞的處理狀態，僅作為配置標誌。
- ❌ 未正確處理 `gamesettingsite` 與 `newsservice` 之間的錯誤傳播 → 若 newsservice 內部錯誤，gamesettingsite 應對外返回適當的錯誤訊息，而非裸露內部異常。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 操作權責 | `db/news-detail.md`：「Table：aifunshits」章節，`gamesettingsite` 有寫入權限 |
| 操作權責 | `db/news-detail.md`：`gamesettingsite`「writer」角色 |
| 欄位權限 | `db/news-detail.md`：「aihints」僅由管理後台寫入 |
| 代碼語義 | `semantics`分析: `lid` 用於 `IAINewsService.GetAIHotDiscussionGames(lid)`，推斷內部有此概念 |