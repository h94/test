# 查詢檢舉記錄

## 1. 場景目的
讓一般使用者能查詢自己發起的檢舉記錄；讓後台管理員能查詢系統中所有的檢舉記錄，以進行審核與管理。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/backend/report/{report_id}` | 查詢指定 ID 的檢舉記錄 |

---

## 3. 流程總覽

1. 客戶端（前台或後台）攜帶 auth token 呼叫查詢 API
2. 系統驗證使用者身份與權限（由 auth / member service 完成）
3. 解析請求參數：`report_id`（路徑參數）
4. 根據使用者角色決定查詢範圍：
   - 一般使用者：只能查詢自己發起的檢舉
   - 後台人員：可查詢任意檢舉
5. 查詢 Cassandra `community.report` 表
6. 進行資料遮蔽處理
7. 回傳結果（若無權限則回傳 403；找不到則回傳 404）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | AuthMiddleware | 驗證 auth token，將使用者資訊附加至 request |
| 2 | Controller | `ReportController.get_report(report_id)` | 接收請求，呼叫 Service |
| 3 | Service | `ReportService.get_report(report_id, user)` | 組裝查詢條件，根據使用者角色決定過濾規則 |
| 4 | Provider | `ReportProvider.get_by_id(report_id)` | 查詢 Cassandra `community.report` 表 |
| 5 | Service | `ReportService.get_report(...)` | 進行權限二次確認與資料遮蔽 |
| 6 | Controller | `ReportController.get_report(...)` | 格式化並回傳 JSON response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `community.report` | Read | 查詢檢舉記錄的主資料來源 |
| Redis | 無 | - | 依據規則，community 無使用 Redis 快取 |
| Queue | 無 | - | 本查詢流程不涉及 Kafka |

---

## 6. 重要規則

- **權限限制**
  - 一般使用者僅能查詢 `user` 欄位等於自己 authkey 的記錄。
  - 後台管理員可查詢所有記錄。
  - 身分驗證與 authkey 解析由 auth / member service 負責，communityservice 僅接收已驗證的請求。

- **不可暴露資料**
  - `account`：對外 API 須一律遮蔽或轉為暱稱，不可回傳完整帳號。
  - `reported_user`、`reported_username`：僅檢舉人自身及後台可見。
  - `user`（authkey）：不可直接回傳，須轉譯為顯示資訊。

- **欄位限制**
  - `reason` 長度：1 ~ 100 字元。
  - `article_id` 格式：22 位字母數字。
  - `status` 變更僅限後台處理程序，一般使用者查詢時不應修改此欄位。

- **讀取規則**
  - 一般使用者查詢時，須在應用層過濾 `user` 等於自身。
  - 查詢不到記錄時應回傳 404，不可因權限不足而暴露記錄存在與否的事實。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 一般使用者查詢非本人的檢舉 | 回傳 404 或權限不足提示（不暴露記錄存在資訊） |
| 提供的 `report_id` 不存在 | 回傳 404 及對應訊息 |
| 未提供有效 auth token | 回傳 401 Unauthorized |
| attempt to query without auth | 回傳 403 Forbidden |
| Cassandra 連線逾時或失敗 | 回傳 500 Internal Server Error |
| `user` 參數遭竄改，試圖查詢他人記錄 | 服務端忽略前端傳入的 `user`，強制以 session 內的 authkey 為準，並回傳 403/404 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| RT-001 | Permission Test | 一般使用者查詢自己建立的檢舉 | 成功回傳該筆記錄（含遮蔽後帳號） |
| RT-002 | Permission Test | 一般使用者查詢他人的檢舉 | 回傳 404 或無權限錯誤 |
| RT-003 | Permission Test | 後台管理員查詢任意檢舉 | 成功回傳完整記錄 |
| RT-004 | Flow Test | 查詢不存在的 `report_id` | 回傳 404 |
| RT-005 | Data Privacy Test | 一般使用者取得記錄後，確認回傳內容 | `account` 為遮蔽格式；`reported_user` 等欄位存在但正確遮蔽 |
| RT-006 | API Test | 未帶 auth token 請求 | 回傳 401 |

---

## 9. 高風險區域

- **高風險 table**：`community.report`（包含檢舉人與被檢舉人的帳號資訊）。
- **高風險 API**：`GET /api/community/backend/report/{report_id}`（權限控制不當將導致個資外洩）。
- **權限驗證依賴**：服務本身不實作使用者驗證，完全依賴 auth / member service。若上游傳遞的 authkey 被偽造或錯誤解析，將導致資料越權存取。
- **資料遮蔽**：程式碼中若直接回傳原始 DB 欄位而未經遮蔽處理，將造成嚴重個資外洩。

---

## 10. 常見錯誤

- **新人容易犯錯**
  - 未區分前台與後台權限，直接將所有記錄回傳給請求者。
  - 直接回傳 `reported_user` 或 `account` 完整欄位，未進行遮蔽。
  - 在 Controller 層直接操作 DB Provider，繞過 Service 層的權限與遮蔽邏輯。

- **AI 容易誤解**
  - 誤以為此 API 支援「查詢檢舉列表」（實際上僅支援單筆查詢，需人工確認是否有列表查詢 API）。
  - 誤將 `report_table` 的寫入規則套用到讀取流程上。

- **常見漏檢查項目**
  - 查詢前未驗證使用者是否已登入或 token 是否有效。
  - 未對回傳內容進行個資遮罩處理。

- **常見錯誤流程**
  - 先撈出資料再判斷權限，應在查詢條件中就帶入 `user` 限制，避免將資料載入記憶體。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/community/backend/report/{report_id}` (from README) |
| DB | `Cassandra: community.report` (from README & community-detail.md) |
| 權限規則 | community-detail.md: "一般使用者只能查詢自己發起的檢舉（過濾 user 等於自己）；後台可查全部。" |
| 不可回傳欄位 | community-detail.md: "account...對外 API 一律遮蔽...reported_user...僅檢舉人自身及後台可見。" |
| 服務相依 | communityservice README: "使用者帳號認證與權限驗證 - auth / member service" |