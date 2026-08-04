# 更新反饋狀態

## 1. 場景目的

管理員變更反饋的處理狀態（未回覆 → 已回覆 / 結束），以便追蹤客服進度。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | /api/{site}/feedback/{id}/status | 更新指定反饋狀態（site 為 sport 或 stock） |

> **需人工確認**：實際 API 路由與參數格式依 Controller 定義為準。

---

## 3. 流程總覽

1. 管理員請求更新反饋狀態，傳入反饋 ID 與目標狀態值。
2. 驗證管理員權限（後台角色或特定 Token）。
3. 根據 `site` 參數選擇對應的資料表（`feedbacks_sport`、`feedbacks_stock`、`business_messages`）。
4. 查詢該反饋是否存在，並檢查當前狀態是否允許變更。
5. 更新 `Status` 欄位，同時刷新 `UpdateTime` 為目前時間戳。
6. 回傳成功（或失敗）訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | FeedbackController.UpdateStatus | 接收 HTTP 請求，參數驗證，呼叫 Service |
| 2 | Service | FeedbackService.ChangeStatus | 組合站點識別、調用對應 Provider |
| 3 | Provider | SportFeedbackDataProvider / MessageDataProvider / BusinessDataProvider | 執行 ScyllaDB CQL UPDATE 語句 |
| 4 | Validator | StatusValidator | 驗證狀態值有效（0/1/2）與狀態轉移規則 |

> **需人工確認**：具體 Class 名稱與方法簽名需從原始碼確認，目前僅依據命名慣例推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `feedbacks_sport` | Update | 更新體育站點反饋的 Status、UpdateTime |
| DB | `feedbacks_stock` | Update | 更新股票站點反饋的 Status、UpdateTime |
| DB | `business_messages` | Update | 更新商務反饋的 Status、UpdateTime |

> 無使用 Redis、Kafka 或 Queue 的證據。

---

## 6. 重要規則

- **權限限制**：僅管理員（後台角色）可呼叫此 API；普通使用者不可存取。
- **狀態值限制**：`Status` 為 `int` 型別，有效值需對應「未回覆（0）」「已回覆（1）」「結束（2）」。
  > **需人工確認**：狀態值對應關係應參照原始碼中定義的 enum 或常數。
- **不可修改欄位**：除 `Status` 與 `UpdateTime` 外，其他欄位（如 `Problem`、`RespContent`）不可在此流程變更。
- **狀態轉移規則**：
  - 僅允許「未回覆 → 已回覆」或「未回覆 → 結束」。
  - 「已回覆 → 結束」可能允許（依業務邏輯）。
  - 已結束狀態不可再更改。
  > **需人工確認**：需查閱原始碼或業務規則文件確認轉移條件。
- **UpdateTime 規則**：每次狀態變更時必須更新為 `DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()` 或其他當前時間戳。
- **站點隔離**：不同站點（sport/stock）操作獨立表，不可跨站點存取。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 反饋 ID 不存在 | 回傳 404，訊息「反饋不存在」 |
| 狀態值無效（非 0/1/2） | 回傳 400，訊息「無效的狀態值」 |
| 狀態轉移不合法（如對已結束反饋再次變更） | 回傳 422，訊息「不允許的狀態轉移」 |
| 權限不足（非管理員 Token） | 回傳 403 |
| 資料庫寫入失敗 | 回傳 500，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-01 | API Test | 提供有效 ID 與合法狀態值（0→1） | 200 OK，Status 變更為 1，UpdateTime 更新 |
| UT-02 | API Test | 提供不存在的 ID | 404 Not Found |
| UT-03 | Permission Test | 使用一般使用者 Token 呼叫 | 403 Forbidden |
| UT-04 | Flow Test | 對已結束的反饋嘗試更新 | 422 Unprocessable Entity |
| UT-05 | Integration Test | 資料庫查詢確認記錄已更新 | 撈取該 ID 記錄，Status 與 UpdateTime 符合預期 |

---

## 9. 高風險區域

- **高風險 Table**：`feedbacks_sport`、`feedbacks_stock`、`business_messages`（直接寫入狀態欄位，錯誤更新可能導致客服進度混亂）。
- **高風險 API**：狀態更新 API，需嚴防越權操作（如一般使用者修改狀態）或不合法狀態跳轉。
- **Cache Inconsistency**：若有快取層（目前無證據），狀態變更後需清除快取。
- **Idempotency**：重複請求相同狀態變更應判定為成功（不變），避免重複觸發通知或日誌。

---

## 10. 常見錯誤

- 忘記驗證狀態轉移規則，允許任意修改。
- 未更新 `UpdateTime`，導致前端無法判斷最新變更。
- 混淆 `site` 參數，對錯誤的資料表執行更新。
- 未處理資料庫寫入異常，導致部分成功無回滾（ScyllaDB 無事務，需注意冪等設計）。
- 回傳過多敏感欄位（如 Account、Email）違反最小權限原則。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB Table（體育） | `feedbacks_sport`（SportFeedbackDataProvider.cs） |
| DB Table（股票） | `feedbacks_stock`（MessageDataProvider.cs） |
| DB Table（商務） | `business_messages`（BusinessDataProvider.cs） |
| 狀態欄位語意 | `SportMessage.Status`、`StockFeedback.Status`、`BusinessMessage.Status` |
| 更新時間語意 | `SportMessage.UpdateTime`、`StockFeedback.UpdateTime`、`BusinessMessage.UpdateTime` |
| 狀態值定義 | README 描述「未回覆」「已回覆」「結束」，但對應數值需程式碼確認 |
| 權限需求 | 由業務邏輯推斷（管理員後台），具體驗證機制（JWT/角色）需檢視 Auth Middleware |

---

**⚠️ 資訊不足標記**  
- 確切 API 路由與 Method 需從 Controller 確認。  
- 狀態值（int）對應的 enum 定義需從原始碼確認。  
- 狀態轉移規則需查閱 Service 層邏輯或業務規則文件。  
- Redis/Kafka 等中間件在此場景中無使用證據，若有應補充。