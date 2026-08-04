# 查詢會員每日報表

## 1. 場景目的

提供管理後台人員依日期區間查詢每日會員報表，取得指定區間內的會員註冊數、活躍數、聊天數與交易數等彙總數據，作為營運分析參考。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sport/report/member` | 查詢會員每日報表，須帶日期區間參數，需驗證 |

---

## 3. 流程總覽

1. 管理後台發起 GET request，附帶查詢參數 `sdate` 與 `edate`（來源：API query parameter）
2. ECFramework 驗證 Token 有效性（來源：README 驗證欄位 ✅）
3. Controller 接收請求，將參數傳遞至 Service 層
4. Service 層驗證日期格式與區間合理性（需人工確認是否有專用 Validator）
5. Service 層調用 Provider，組裝 CQL 查詢條件 `WHERE Reportdate >= sdate AND Reportdate <= edate`
6. Provider 執行對 Cassandra `pricecenter.member_daily_reports` 的查詢（來源：README Table 清單）
7. 將查詢結果映射為回傳物件（含 Reportdate、Registers、Actives、Chats、Trades 等欄位）
8. 回傳 JSON 陣列給前端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | ReportController.GetMemberReport | 接收 `sdate`、`edate` Query 參數 |
| 2 | Service | IReportService.GetMemberDailyReports | 驗證日期格式、區間，組裝查詢條件 |
| 3 | Provider | IMemberReportProvider.QueryByDateRange | 執行 Cassandra CQL 查詢 |
| 4 | Transfer | MemberDailyReportDto | 將查詢結果映射為 API 回傳格式 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `pricecenter.member_daily_reports` | Read | 依日期區間查詢會員每日彙總報表 |
| Redis | 無 | - | 此報表查詢未使用快取，直接查詢 DB |
| Queue/Kafka | 無 | - | 此查詢場景未涉及非同步佇列 |

---

## 6. 重要規則

- **日期區間限制**：必須同時傳入 `sdate` 與 `edate`，且 `edate >= sdate`。缺少任一參數或格式錯誤應回傳 400 Bad Request（來源：db-usage 讀取規則「不可無限制查詢」）
- **不可全表掃描**：CQL 必須以 `WHERE Reportdate >= ? AND Reportdate <= ?` 限制查詢範圍，服務層需確保此條件必定存在（來源：pricecenter-detail 讀取規則）
- **唯讀權限**：`pricecentermanage` 服務對 `member_daily_reports` 僅有唯讀權限，不可執行 INSERT / UPDATE / DELETE（來源：pricecenter DB 操作邊界）
- **不可回傳欄位**：報表僅回傳彙總欄位（Registers, Actives, Chats, Trades, Editorchats），無個人識別資訊，無額外遮蔽需求
- **日期格式**：`Reportdate` 格式為 `YYYY-MM-DD`（來源：DB schema sport）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未傳入 `sdate` 或 `edate` | 400 Bad Request，提示參數為必填 |
| 日期格式非 `YYYY-MM-DD` | 400 Bad Request，提示格式錯誤 |
| `sdate` > `edate` | 400 Bad Request，提示區間無效 |
| 查詢範圍過大（需人工確認是否設有上限，如大於 90 天） | 需人工確認：若有上限則回 400 提示縮小範圍 |
| Cassandra 查詢逾時 | 500 Internal Server Error，記錄錯誤日誌 |
| Cassandra 回傳空結果 | 200 OK 回傳空陣列 `[]` |
| 未帶有效 Token 或 Token 過期 | 401 Unauthorized |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | API Test | 傳入合法日期區間，區間內有資料 | 200，回傳正確筆數與欄位值 |
| TC02 | API Test | 傳入合法日期區間，區間內無資料 | 200，回傳空陣列 |
| TC03 | API Test | 未傳入 `sdate` | 400 Bad Request |
| TC04 | API Test | 未傳入 `edate` | 400 Bad Request |
| TC05 | API Test | `sdate` 晚於 `edate` | 400 Bad Request |
| TC06 | API Test | 日期格式錯誤（如 `2025/01/01`） | 400 Bad Request |
| TC07 | Permission Test | 不帶 Token 呼叫 | 401 Unauthorized |
| TC08 | Permission Test | 使用無效 Token 呼叫 | 401 Unauthorized |
| TC09 | Permission Test | 使用未授權角色呼叫（若有 RBAC） | 403 Forbidden（需人工確認角色設定） |
| TC10 | Flow Test | Cassandra 連線中斷時呼叫 | 500 Internal Server Error |
| TC11 | Flow Test | 查詢跨 90 天以上區間 | 需人工確認上限是否存在；若有則 400 |

---

## 9. 高風險區域

- **日期參數驗證不足**：若 Service 層未嚴格校驗日期格式與區間，可能導致 CQL injection 或全表掃描
- **全表掃描風險**：任何遺漏 `Reportdate` 範圍過濾的查詢，將對 Cassandra 造成嚴重效能影響
- **報表資料依賴**：`member_daily_reports` 由其他服務（排程）寫入，若寫入延遲或中斷，本查詢將回傳不完整資料（來源：pricecenter-detail 本服務不負責寫入）
- **無快取設計**：大量並發查詢直接命中 Cassandra，可能造成 DB 壓力；需人工確認是否需要導入 Redis 快取或 Query 限流

---

## 10. 常見錯誤

- ❌ 省略 `sdate` 或 `edate` 直接查詢 → 應在 Controller 或 Service 層強制校驗必填
- ❌ 日期傳入空字串或 `null` 卻未攔截 → Service 層需過濾空值並回傳 400
- ❌ 前端傳入時間戳格式而非 `YYYY-MM-DD` 字串 → 需在 API 文件明確規範格式
- ❌ 誤認為可寫入報表資料 → `pricecentermanage` 僅唯讀，寫入由其他服務負責
- ❌ 日期區間未加限制，允許查詢未來日期 → 需加入 `edate` 不得晚於今日的檢查

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/sport/report/member` (README API 路由) |
| DB Table | `pricecenter.member_daily_reports` (README Table 清單 / sport-detail.md) |
| 查詢條件 | `WHERE Reportdate >= ? AND Reportdate <= ?` (pricecenter-detail.md 讀取規則) |
| 服務角色 | `pricecentermanage` 對 pricecenter keyspace 為 reader (pricecenter-detail.md 服務角色總覽 / ServiceDetail pricecenter 本服務不負責) |
| 驗證 | API 需驗證 (README API 路由 ✅) |
| 不可回傳欄位 | 報表無 PII 欄位，無特殊遮蔽需求 (sport-detail.md memberdailyreport) |
| Code | Controller: ReportController.GetMemberReport, Provider: IMemberReportProvider.QueryByDateRange (Phase0/1 source code semantics 推斷) |