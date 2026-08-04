# 查詢預設問題列表

## 1. 場景目的
根據使用者指定之站點（運動／股票）與主題，回傳該主題下所有啟用中的預設問答（FAQ）清單。此流程為前端客服頁面提供即時常用的問答對，無需登入或權限驗證。

---

## 2. 入口 API
需人工確認：因原始碼中未提供 Controller 路由，僅由 Provider 命名推斷對外 API 格式。以下為推測常見路徑。

| Method | Path | 說明 |
|--------|------|------|
| GET | /api/{site}/topics/{tid}/questions | 取得指定站點、主題下的預設問題列表，依排序號遞增回傳 |

{sit} 接受 `sport` 或 `stock`。

---

## 3. 流程總覽
1. 接收帶有站點識別與主題 ID 的 request
2. 依據站別選擇對應資料表（`questions_sport` 或 `questions_stock`）
3. 查詢 `topics_*` 表驗證主題存在且為啟用（`Enabled=1`）
4. 對 `questions_*` 表執行 `WHERE TID=:tid AND Enabled=1`，依 `Sort` 欄位升冪排序
5. 將查詢結果組合成 DTO，包含問題與答案內容
6. 回傳問題列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | 需人工確認 | 接收 request，呼叫對應 Service |
| 2 | Service | 需人工確認 | 取得站別參數，決定查詢對象，呼叫 Provider |
| 3 | Provider | `QuestionDataProvider.GetQuestions(string site, string tid)` | 針對 `sport` 或 `stock` 執行 CQL 查詢 `questions_*` 並過濾 `Enabled=1`、依 `Sort` 排序 |
| 4 | Provider | `TopicDataProvider.GetTopic(string site, string id)` | 先查 `topics_*` 確認主題存在且啟用（可選，依業務邏輯決定是否強制） |
| 5 | Assembler | 需人工確認 | 將資料列轉換為 UI 所需模型（多語言內容解析等） |

來源證據：`QuestionDataProvider.cs`、`TopicDataProvider.cs`（Phase1 語意解析）。

---

## 5. DB 使用

本流程僅讀取資料庫，不寫入、不觸發任何 Trigger 或異步作業。

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (ScyllaDB) | `questions_sport` | Read (`SELECT`) | 取得運動站點預設問答 |
| DB (ScyllaDB) | `questions_stock` | Read (`SELECT`) | 取得股票站點預設問答 |
| DB (ScyllaDB) | `topics_sport` | Read (`SELECT`) | 驗證主題啟用狀態（可選） |
| DB (ScyllaDB) | `topics_stock` | Read (`SELECT`) | 驗證主題啟用狀態（可選） |

- CQL 需注意分區鍵，依資料模型設計可能使用 `TID` 作為分區鍵或叢集鍵。
- `questions_sport` 的 `question` 與 `answer` 欄位為 `MAP<VARCHAR,VARCHAR>`，支援多語言查詢，通常直接回傳整份 MAP，由前端根據語系解析。

---

## 6. 重要規則
- **站點隔離**：`sport` 與 `stock` 的 FAQ 資料完全隔離，不可跨站查詢。
- **只顯示啟用項目**：查詢條件務必包含 `Enabled=1`，已停用的問答不應回傳。
- **排序強制**：結果必須依 `Sort` 欄位遞增排序，確保前端展示一致性。
- **主題驗證**：若查詢前需驗證主題 `Enabled`，則必須查 `topics_*` 表；此處可依業務決定是否要求主題必須啟用，否則回傳空列表。
- **無權限驗證**：此查詢為公開資源，無需驗證使用者身份。
- **多語言處理**：對於 `sport`，`question` 與 `answer` 為多語 MAP，需以原始格式回傳；`stock` 則為單一 `varchar` 純文字。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 主題 ID 不存在（`topics_*` 無資料） | 回傳 HTTP 200 但空列表，或 HTTP 404（由產品規則決定） |
| 主題已被停用（`Enabled=0`） | 若強制檢查則回傳空列表或 HTTP 400；若不檢查，可能仍回傳該主題下問題（風險低） |
| 主題下沒有任何啟用問題 | 回傳空列表 HTTP 200 |
| 資料庫連線失敗或查詢逾時 | HTTP 500，記錄錯誤日誌 |
| `site` 參數非 `sport` 或 `stock` | 回傳 HTTP 400 Bad Request |
| CQL 查詢因無分區鍵導致全表掃描 | 可能造成效能瓶頸，應在 `TID` 上建立適當索引或調整模型 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| QA-01 | API Test | 查詢運動站點已啟用主題（提供有效 TID） | 回傳至少一筆問題，字段包含 ID、問題內容、答案內容、排序 |
| QA-02 | API Test | 查詢股票站點已啟用主題 | 回傳問題列表，格式不同於運動（無多語 MAP） |
| QA-03 | API Test | 查詢不存在的 TID | 回傳空列表或 404 |
| QA-04 | Flow Test | 主題停用後再查詢 | 不應回傳該主題下的問題（若強制檢查） |
| QA-05 | API Test | 使用無效的 site 參數 | HTTP 400 |
| QA-06 | Integration Test | 大量問題（100 筆以上）測試排序 | 確認結果依 Sort 遞增，無缺失或重複 |

---

## 9. 高風險區域
- **資料表查詢性能**：若 `TID` 非分區鍵且資料量大，`WHERE TID=? AND Enabled=1` 可能觸發跨節點掃描，需確認 ScyllaDB 表設計。
- **空指標風險**：`questions_sport` 的 `question` 或 `answer` MAP 可能為 NULL，反序列化時需防禦。
- **多語言內容暴露**：無需過濾，但應確保 MAP 中不包含未清理的 HTML/JS 腳本（若來自後台輸入）。
- **無快取機制**：重複查詢可能造成資料庫壓力，建議加入短時快取（如 1 分鐘），但此為可選項。

---

## 10. 常見錯誤
- 新人容易忽略 `Enabled` 過濾，導致停用問答顯示在前端。
- 忘記依 `Sort` 排序，使前端顯示順序錯亂。
- 對 `stock` 站點誤用多語言 MAP 解析，導致反序列化錯誤。
- 在查詢 `questions_*` 前未檢查 `topics_*` 啟用狀態，若產品需求強制，將出現幽靈問題。
- AI 生成代碼時可能直接使用全表查詢而不帶 `TID` 條件，造成性能問題。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 表結構 | `questions_sport`, `questions_stock` 定義於 ScyllaDB（詳見 Phase1 語意批次） |
| Provider 類 | `QuestionDataProvider.cs`, `TopicDataProvider.cs`（Phase1 batch-1/3） |
| 多語言欄位定義 | `questions_sport.question (MAP<VARCHAR,VARCHAR>)`、`answer`，源於 `SportFeedbackDataProvider.cs` |
| Enabled 語意 | 欄位意義確認為啟用狀態，Phase1 語意批次及 DB detail 皆有描述 |
| Sort 欄位 | 用於排序，來自 `SportFeedbackDataProvider` / `QuestionDataProvider` |

所有結論均基於已知 `db-usage` 與程式語意，未包含部分依標記「需人工確認」處理。