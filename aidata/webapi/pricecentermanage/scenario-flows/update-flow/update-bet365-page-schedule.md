# 更新指定 Bet365 頁面排程

## 1. 場景目的

後台管理員調整單一 Bet365 爬蟲頁面的排程參數（如 Cron 表達式、間隔時間等），以控制爬蟲的執行頻率與啟動狀態。此操作直接影響底層爬蟲程式的任務調度。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/bet365/page/{pagename}` | 根據頁面名稱更新其排程設定 |

---

## 3. 流程總覽

1.  後台管理員通過前端頁面提交某個 `pagename` 的新排程設定。
2.  `pricecentermanage` 接收 POST 請求，通過 ECFramework 驗證管理員身份與權限。
3.  系統根據 `pagename` 在資料庫中查詢對應的頁面配置記錄。
4.  若頁面存在，則以請求中的新設定更新該記錄的排程欄位（如 `cronsetting`）。
5.  更新成功後，該爬蟲頁面的排程立即生效，下一個排程週期將採用新的設定。

---

## 4. 程式流程

| 順序 | Layer | Class / Method (推測) | 動作 |
|---|---|---|---|
| 1 | Controller | `Bet365Controller` | 接收 `pagename` 路徑參數與 Request Body。 |
| 2 | Service | `IBet365Service` / `Bet365Service` | 調用 Provider 進行資料更新。 |
| 3 | Provider | `IBet365Provider` | 根據 `pagename` 組裝更新語句，操作 DB 寫入新的排程參數。 |

> **需人工確認**：確切的 Class 與 Method 名稱，以及是否涉及 Provider 層的具體實作。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `pricecenter.crawlerpage` | Read / Write | 查詢特定 `pagename` 的頁面設定，並更新其 `cronsetting` 等參數。 |

> **需人工確認**：根據語意，更新操作應發生在 `pricecenter` keyspace 的 `crawlerpage` 或類似表中。具體表名需核實。

---

## 6. 重要規則

- **權限限制**：此為管理後台功能，需通過 `ECFramework` 驗證，僅允許具備管理員權限的角色操作。
- **不可修改欄位**：`pagename` 作為主鍵，僅用於定位記錄，不可變更。
- **即時生效**：此操作直接更新資料庫中的排程配置，爬蟲系統應能即時或準實時地讀取新配置並應用，不應有長時間的快取延遲。
- **參數驗證**：必須驗證提交的 Cron 表達式格式是否合法，以及間隔時間等數值是否符合系統可接受的範圍，防止設定錯誤導致爬蟲異常。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 無效的 `pagename`（頁面不存在） | 返回 404 Not Found。 |
| 權限不足（非管理員請求） | 返回 401 Unauthorized 或 403 Forbidden。 |
| 提交的 `cronsetting` 格式非法 | 返回 400 Bad Request，並提示格式錯誤。 |
| 資料庫寫入失敗 | 返回 500 Internal Server Error，操作被回滾。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `B365-UPDATE-01` | API Test | 以有效管理員權限，為一個已存在的 `pagename` 提交正確格式的排程設定。 | 200 OK。`cronsetting` 在 DB 中被更新。 |
| `B365-UPDATE-02` | Permission Test | 以無效 token 或非管理員帳號進行請求。 | 401 或 403。DB 未被修改。 |
| `B365-UPDATE-03` | API Test | 提交一個不存在的 `pagename`。 | 404 Not Found。 |
| `B365-UPDATE-04` | Flow Test | 提交一個格式錯誤的 Cron 表達式。 | 400 Bad Request。 |

---

## 9. 高風險區域

- **直接影響爬蟲集群**：不當的排程設定（如過於頻繁的 Cron）可能瞬間對目標網站或後端服務造成巨大壓力。
- **無審批流程**：若更新即時生效且無審批，可能因人為失誤導致線上事故。

---

## 10. 常見錯誤

- ❌ **直接修改資料庫而不通過 API**：這會繞過權限驗證和參數合法性檢查，是極度危險的操作。
- ❌ **在更新 Request Body 中嘗試修改 `pagename`**：`pagename` 是路徑參數，用於定位資源，不應在 Body 中被修改。
- ❌ **忽略對 `cronsetting` 合法性的完整校驗**：僅簡單的字串檢查不足以防範所有錯誤，應有專門的 Cron 表達式解析與驗證邏輯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/bet365/page/{pagename}` |
| 驗證框架 | 技術棧中的 `ECFramework.ECService 2.0.0` |
| DB 操作 | 語意推測為對 `pricecenter.crawlerpage` 表的寫入 |