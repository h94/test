# 更新預設問題

## 1. 場景目的
管理員可針對任一業務站點（Sport、Stock）維護預設問答庫，修改問題內容、多語言翻譯、預設答案或啟用狀態。更新後的資料即時影響前端常見問題展示。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| PUT （推測） | `/api/admin/questions/{id}` | 更新指定站點下的預設問題（需人工確認具體路由） |

**需人工確認**：實際路由與 Controller 方法名尚未從原始碼中取得；後續應以實際 API 文件或 `AdminController` 為準。

---

## 3. 流程總覽
1. 管理後端發送 PUT 請求，攜帶站點參數（`site`）與欲修改的問題 ID。
2. Controller 驗證呼叫方是否具備管理員權限（需人工確認權限驗證機制）。
3. 解析請求體，取出 `question`、`answer`、`enabled`、`sort` 等欄位新值。
4. 根據站點 (`sport` 或 `stock`) 決定目標資料表：
   - 體育：`questions_sport`
   - 股票：`questions_stock`
5. 調用對應的 `QuestionDataProvider`（推測為 `SportQuestionDataProvider` / `StockQuestionDataProvider`）執行更新。
6. Provider 組裝 CQL `UPDATE` 語句，依據主鍵 `id` 更新指定欄位，並設定新的 `updatetime`（若表結構存在該欄位）。
7. 返回成功響應給呼叫方。
8. 若有前端快取，需人工確認是否需要同步刷新快取（目前無明確快取機制）。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | （推測）`AdminController.UpdateQuestion` | 接收請求、權限檢查、參數綁定 |
| 2 | Service | （推測）`QuestionService.UpdateQuestionAsync` | 組織業務邏輯、站點路由 |
| 3 | Provider | `SportQuestionDataProvider` 或 `StockQuestionDataProvider` | 對 `questions_sport` 或 `questions_stock` 執行 `UPDATE` |
| 4 | - | - | 無 Redis / Queue 操作 |

**需人工確認**：實際的 Layer 結構與類別名稱可能不同，以來源碼為主。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `questions_sport` | Update | 更新體育站預設問題資料 |
| DB | `questions_stock` | Update | 更新股票站預設問題資料 |
| — | Redis | 無 | 無快取機制（需人工確認是否後續會引入） |
| — | Kafka / Queue | 無 | 無非同步操作 |

---

## 6. 重要規則
- **權限限制**：僅管理後台可操作（管理員角色），一般用戶 API 不可呼叫。
- **站點識別**：必須傳入正確的 `site` 識別碼（`sport` 或 `stock`），否則拒絕請求。
- **欄位限制**：
  - 體育站問題和答案使用 `MAP<VARCHAR, VARCHAR>` 結構（支援多語言，如 `zh-TW`、`en`），寫入時需提供符合格式的 JSON 物件。
  - 股票站問題和答案為 `VARCHAR`，僅支援單一值。
  - `enabled` 為整數（0 或 1），預設 1。
- **不可修改欄位**：主鍵 `id` 一旦建立不可修改，`tid`（所屬主題）在更新時可否變更需視業務規則（建議預設不可變更）。
- **狀態值限制**：`enabled = 0` 表示停用，前端查詢預設問題時應過濾 `enabled = 1`。
- **無 Transaction 需求**（ScyllaDB 單行更新為原子操作，無跨行事務）。
- **無 Retry 機制**（直接回寫，失敗即返回錯誤）。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 站點參數非 `sport` 或 `stock` | 返回 400 Bad Request，提示無效站點 |
| 問題 ID 不存在 | 返回 404 Not Found |
| 請求體格式錯誤（如將 MAP 寫成非 JSON 格式） | 返回 400 並附帶錯誤訊息 |
| 無管理員權限 | 返回 403 Forbidden |
| 資料庫寫入超時 | 返回 500 Internal Server Error，前端可提示稍後重試 |
| `tid` 指向不存在的 Topic | 返回 400 Bad Request（需人工確認是否實作校驗） |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UP-01 | API Test | 正常更新體育站問題，含多語言 MAP | 200 OK，資料庫內容更新，時間戳變更 |
| UP-02 | API Test | 正常更新股票站問題，修改 answer 文字 | 200 OK，資料庫內容更新 |
| UP-03 | Permission Test | 一般用戶呼叫此 API | 403 Forbidden |
| UP-04 | Validation Test | 傳入無效的 `site`（如 `xxx`） | 400 Bad Request |
| UP-05 | Validation Test | 未傳入必填欄位（如 `question` 為空） | 400 Bad Request |
| UP-06 | Flow Test | 更新 `enabled=0` 後，查詢啟用問題 API 不回傳該筆 | 查詢結果不含該 ID |
| UP-07 | Flow Test | 更新體育站問題，寫入錯誤的 MAP JSON 格式 | 400 Bad Request |

---

## 9. 高風險區域
- **高風險 table**：`questions_sport`、`questions_stock` — 直接影響前端客服問答內容。
- **即時生效**：無快取層，更新後即刻影響前端查詢，若誤改可能導致用戶看到錯誤說明。
- **跨語言結構差異**：體育站使用 MAP 儲存多語言，寫入時若格式錯誤會導致前端無法正確展示，且無回退機制。
- **權限控管**：若 API 未正確守衛，一般用戶可能非法修改預設問題庫。
- **無歷史紀錄**：更新直接覆蓋原有資料，無版本控制或日誌（需人工確認是否需要加入 audit log）。

---

## 10. 常見錯誤
- **站點混淆**：對體育站送單一文字（非 MAP）或對股票站送 MAP 結構，導致 DbNull / 序列化錯誤。
- **忽略 `enabled` 狀態**：新人可能只修改內容卻未檢查啟用狀態，導致線上看不到更新。
- **直接呼叫 Provider 跳過 Service 驗證**：錯誤繞過站點檢查，寫入錯誤表格。
- **未處理多語言的 fallback**：後端未檢查 MAP 的必含鍵值，若缺少主要語系可能使前端空白。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | 無具體 Controller 證據，需人工確認路由（如 `AdminController.UpdateQuestion`） |
| DB | `sport_questions`、`stock_questions` 定義於 source code semantics (Phase0) |
| Code Provider | `QuestionDataProvider.cs`（推測透過 batch 分析，為操作 questions 表的資料存取層） |
| 資料結構 | `SportFeedbackDataProvider.cs` 定義 `questions_sport` 欄位包含 MAP 類型 |
| 權限 | 尚無明確證據，需人工確認 JWT／Middleware 驗管機制 |
| 狀態欄位 | `semantics` 中 `enabled` 為 `int`，來源 `SportQuestion.Enabled` / `StockQuestion.Enabled` |

---

## 額外建議
- **建議新增文件**：明確 API 規格與 Controllers 清單，避免依賴推測。
- **建議新增規則**：記錄 `updatetime` 的更新行為、`tid` 變更限制、多語言必填鍵定義。
- **建議新增測試**：跨語言邊界測試（如 MAP 中缺少 `zh-TW` 時的 fallback 行為）、大並發更新測試。