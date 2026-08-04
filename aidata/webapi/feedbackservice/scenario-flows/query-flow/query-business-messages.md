# 查詢商務往來訊息

## 1. 場景目的

查詢 `business_messages` 表中儲存的商務反饋紀錄。該表記錄了平台與商務合作對象之間的通聯歷史，由管理員或具權限的後台人員檢視，用於追蹤溝通進度與審計。  
（⚠ 需人工確認：實際 API 路由與參數設計須由開發團隊提供）

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| 需人工確認 | 需人工確認 | 推測為後台管理 API，依站點 (`Site`) 過濾查詢，支援依時間、狀態、帳號等條件 |

---

## 3. 流程總覽

1. 接收查詢請求，可能包含站點 (`Site`)、時間範圍、狀態、帳號等過濾參數  
2. 驗證請求者權限（必須為管理員或擁有查詢商務訊息權限的角色）— 權限設計需人工確認  
3. 呼叫 Service 層組裝查詢條件  
4. Service 呼叫 Provider (`BusinessDataProvider`) 至 `business_messages` 表進行 SELECT  
5. 取得結果後，依需求過濾不應對外暴露的欄位（如 `SenderMail` 可能僅限高權限角色檢視）  
6. 回傳結果集，通常包含 `ID`、`DateTime`、`SendContent`、`RespContent`、`Status`、`UpdateTime` 等

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | 需人工確認（可能為 `BusinessController`） | 解析請求參數，檢查身分驗證與授權 |
| 2 | Service | 需人工確認（例如 `BusinessService`） | 組合查詢邏輯，呼叫 Provider |
| 3 | Provider | `BusinessDataProvider`（來源：Phase0 語意分析） | 對 `business_messages` 表執行 SELECT，依 `Site`、時間範圍等條件過濾 |

> 註：以上類別名稱基於語意分析推測，實際實作請參考原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `business_messages` | Read | 查詢符合條件的商務訊息紀錄 |
| Cache | 需人工確認 | - | 推測無快取（歷史資料即時性需求低），實際依實作 |
| Queue | 無 | - | 此場景僅為查詢，不涉及寫入或非同步任務 |

⚠ `business_messages` 表位於 feedbackservice 管轄的資料庫（可能為 ScyllaDB），確切結構見語意分析。主要欄位：`Site`、`DateTime`、`ID`、`SenderMail`、`SendContent`、`RespContent`、`Status`、`UpdateTime`。

---

## 6. 重要規則

- **權限限制**：僅管理員或特定角色可查詢，一般使用者不可存取商務訊息清單（需人工確認）
- **欄位限制**：
  - `SenderMail` 為敏感資訊，可能僅特定權限角色可讀取，對外回傳時需謹慎（需人工確認）
  - `Status` 值定義：`0` 未回覆、`1` 已回覆、`2` 結束（依業界慣例推論，需人工確認確切狀態碼）
- **查詢條件強制**：必須提供 `Site` 作為必要過濾條件，避免跨站點資料撈取或全表掃描
- **不可修改**：此場景為唯讀，不允許對表進行 INSERT/UPDATE/DELETE
- **分頁**：若結果集過大，應實施分頁機制（需人工確認是否有實作）
- **時間格式**：`DateTime` 為字串格式，查詢時需注意一致性（推測為 `yyyy-MM-dd HH:mm:ss`）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未提供 `Site` 參數 | 回傳 400 Bad Request，提示 `Site` 為必填 |
| 請求者無足夠權限 | 回傳 403 Forbidden |
| 提供的 `Site` 不存在或非「sport/stock」 | 回傳 400 或 404（視設計） |
| 資料庫連線失敗 | 回傳 500 Internal Server Error |
| 查詢條件過寬導致逾時 | 回傳 500 或 408，應限制時間範圍或強制分頁 |
| `SenderMail` 被未授權角色請求 | 應遮蔽或回傳空值，不可直接拋錯（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T-01 | Permission | 一般使用者呼叫查詢 API | 回傳 403 |
| T-02 | API | 管理員查詢不含 `Site` 參數 | 回傳 400，提示參數缺漏 |
| T-03 | API | 管理員查詢 `Site=sport`，時間範圍本月 | 成功回傳符合條件的訊息列表 |
| T-04 | Flow | 查詢結果中包含 `SenderMail`，確認權限較低的角色無法取得 | 回傳資料中不含 `SenderMail` 或顯示為遮蔽符號 |
| T-05 | DB | 表內有多筆不同 `Site` 的資料，僅查詢 `Site=stock` | 回傳結果僅限 `Site=stock` |
| T-06 | Error | 模擬資料庫逾時 | 回傳 500 並記錄錯誤日誌 |

---

## 9. 高風險區域

- **高風險 table**：`business_messages` — 儲存商務往來內容與聯絡資訊，若權限控管不當可能導致商業機密外洩
- **高風險 API**：查詢端點（推測）— 若未強制 `Site` 條件或未分頁，可能觸發全表掃描造成效能問題
- **跨服務資料同步**：無（此表僅由 feedbackservice 維護）
- **Cache consistency**：無（查詢即時資料，不涉及快取更新）
- **Idempotency**：無
- **敏感資料暴露**：`SenderMail` — 必須確保 API 層級依角色遮蔽，不可直接回傳給低權限用戶

---

## 10. 常見錯誤

- **新人易犯**：
  - 忘記加入 `Site` 條件，導致撈到跨站點資料，或呼叫端未傳遞此參數
  - 直接將 `SenderMail` 回傳給前端，違反資訊分級政策
- **AI 易誤解**：
  - 誤將 `business_messages` 視同一般用戶反饋表（如 `feedbacks_sport`），實際其欄位與用途不同
  - 可能誤判 `Status` 值僅有 0/1，忽略「結束」狀態（需人工確認）
- **常見漏檢查項目**：
  - 未驗證 `Site` 參數是否為合法站點識別碼（可能接受任意字串）
  - 查詢未有時間範圍上限，導致撈取過多歷史資料
  - 缺少對 `SenderMail` 的權限遮蔽邏輯
- **常見錯誤流程**：
  - 後台直接開放全量查詢，無任何過濾參數，引發 DB 負載

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB 結構 | Phase0/1 語意分析 `business_messages` 表（`Site`, `DateTime`, `ID`, `SenderMail`, `SendContent`, `RespContent`, `Status`, `UpdateTime`） |
| Provider | `BusinessDataProvider.cs`（Phase0/1 語意分析） |
| 服務角色 | `stock-detail.md` 指出 feedbackservice 對多數表為 reader，本場景為純查詢 |
| 權限假設 | 推測自 feedbackservice 作為後台服務的角色，具體需參照原始碼中的 `[Authorize]` 邏輯 |

> 本文件多處基於現有證據推論，內容需經由資深工程師審核並以原始碼驗證後方能定稿。