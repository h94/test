# 建立系統佈局

## 1. 場景目的
為特定 GameType（如足球、籃球）建立系統層級的佈局設定，此設定將影響所有使用該 GameType 的商家前端顯示。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/system/layout/{gameType}` | 建立系統佈局 |

---

## 3. 流程總覽

1. 接收建立系統佈局請求，路徑中包含 `{gameType}`。
2. 驗證請求者的操作權限（需人工確認：權限驗證具體實作）。
3. 驗證輸入的佈局設定內容是否為合法 JSON 格式。
4. 將佈局設定寫入 Cassandra `gamesettings.gametype_settings` 表。
5. **需人工確認**：是否需要與 `pricecenterservice` 互動以獲取賽事資訊。
6. **需人工確認**：寫入成功後，是否需更新 Redis `BusinessCache` 或觸發其他快取失效。
7. 回傳操作成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameSettingServiceController` | 接收 HTTP POST 請求及 `{gameType}` 參數 |
| 2 | Controller | `GameSettingServiceController` | 調用對應的 Service 方法（需人工確認：具體方法名稱） |
| 3 | Service | (需人工確認) | 執行業務邏輯，包含驗證與資料組裝 |
| 4 | Provider | (需人工確認) | 負責與 Cassandra 進行資料互動 |
| 5 | Provider | (需人工確認) | 組裝 Cassandra CQL `INSERT` 語句並執行 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `gamesettings.gametype_settings` | Write | 寫入新的系統佈局設定 |
| DB | Cassandra `gamesettings.gametype_settings` | Read | 驗證是否已存在相同 `company` + `gametype` 的設定（若為唯一性檢查） |
| Cache | Redis `BusinessCache` | (待確認) | **需人工確認**：寫入後是否需要更新或清除相關快取 |

---

## 6. 重要規則

- **權限限制**：所有對 `/api/v1/system/layout/{gameType}` 的請求都需要驗證。
- **欄位限制**：
  - `settings` 欄位寫入時必須為合法 JSON 字串。
  - `updater` 欄位必須由系統自動填入當前操作者帳號，不可由客戶端傳入。
- **不可暴露資料**：API 回傳中不可包含任何密碼、AuthToken 等敏感資訊。
- **不可修改欄位**：此為新增操作，主鍵 `company` 和 `gametype` 一旦建立則不可更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求者未通過身份驗證或權限不足 | 回傳 401 Unauthorized 或 403 Forbidden |
| 輸入的 `settings` 內容不是合法 JSON 字串 | 回傳 400 Bad Request，並提示格式錯誤 |
| 相同 `company` + `gametype` 的設定已存在 | 回傳 409 Conflict 或 400 Bad Request，提示重複建立 |
| Cassandra 寫入失敗或 Timeout | 回傳 500 Internal Server Error，並記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Unit Test | 模擬 Provider 寫入 Cassandra 成功 | 收到成功結果 |
| UT-02 | Unit Test | 模擬 Provider 寫入 Cassandra 失敗 | 觸發異常處理流程 |
| IT-01 | Integration Test | 對 API 發送有效請求，檢查 DB 寫入內容 | DB 中存在正確的設定資料，`updater` 正確 |
| IT-02 | Integration Test | 對 API 發送格式錯誤的 JSON | 收到 400 錯誤 |
| PT-01 | Permission Test | 使用無效 Token 發送請求 | 收到 401 錯誤 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.gametype_settings`
- **高風險操作**：寫入非法 JSON 格式的 `settings` 會導致前端無法解析，可能引發前台的顯示異常或崩潰。
- **寫入責任**：必須確保 `updater` 自動填入，以利後續稽核。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 忘記對輸入的 `settings` 進行 JSON 格式校驗。
  - 將明文密碼或其他敏感資訊寫入 `settings` JSON 內。
- **常見漏檢查項目**：
  - 未檢查使用者權限。
  - 未處理 DB Write 可能拋出的例外狀況。
- **AI 容易誤解**：
  - 可能誤以為可以直接要求客戶端傳入 `updater` 或 `updatetime`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | GameSettingServiceController `POST /api/v1/system/layout/{gameType}` |
| DB | Cassandra `gamesettings.gametype_settings` |
| Code | (需人工確認) Service / Provider 類別 |
| Rule | `gamesettings-detail.md`：`settings` 須為合法 JSON、`updater` 自動填入 |
| Rule | `gamesettings-detail.md`：`password`、`authtoken` 不可回傳 |

## 12. 建議新增文件與規則

- **建議新增規則**：明確定義 `POST /api/v1/system/layout/{gameType}` 的請求與回應 JSON Schema。
- **建議新增測試情境**：寫入超大 JSON 字串或包含特殊字元的情況測試。