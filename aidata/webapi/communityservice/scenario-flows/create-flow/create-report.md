# 建立檢舉記錄

## 1. 場景目的

使用者提交對社群內容的檢舉，寫入 Cassandra `community` keyspace 的 `report` table，記錄檢舉內容供後台審核處理。此流程不涉及審核、通知或自動隱藏等後續處理。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/community/backend/report` | 建立檢舉記錄 |

---

## 3. 流程總覽

1. 接收檢舉 request（含 `reason`、`article_id` 等欄位）
2. 驗證 authKey（由 auth / member service 完成，communityservice 接收已驗證 authkey）
3. 驗證 `reason` 長度（1～100 字元）與 `article_id` 格式（22 位字母數字）
4. 檢查使用者是否存在於 `member.gameusers`（status=1）
5. 產生 report ID
6. 寫入 Cassandra `community.report_table`（status 預設 `open`）
7. 回傳檢舉記錄資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ReportController.CreateReport` | 接收 HTTP POST，解析 request body |
| 2 | Validator | `ReportSchema` | 驗證 `reason` 長度 1~100、`article_id` 格式 22 位字母數字 |
| 3 | Service | `ReportService.CreateReport` | 查詢 `member.gameusers` 驗證會員狀態 |
| 4 | Service | `ReportService.CreateReport` | 生成 report ID（UUID） |
| 5 | Provider | `ReportProvider.Insert` | 寫入 Cassandra `report_table`（status=`open`, user=authkey, timestamp=now） |
| 6 | Controller | `ReportController.CreateReport` | 回傳 `ReportDocumentResponse` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read（SELECT WHERE authkey=?） | 驗證會員存在且 status=1 |
| DB | `community.report_table` | Write（INSERT） | 建立檢舉記錄 |
| Redis | 無 | - | community 無使用 Redis 快取 |
| Queue | 無 | - | 檢舉建立無使用 Queue |

---

## 6. 重要規則

- **權限限制**：需已驗證 authkey；communityservice 接收已驗證的 authkey，不處理登入 token 驗證
- **欄位限制**：
  - `reason`：長度 1～100 字元
  - `article_id`：需符合 22 位字母數字格式
  - `status`：僅允許值 `open`（建立時寫入），一般使用者不可變更
- **不可暴露資料**：
  - `report_table.account`：對外 API 一律遮蔽或轉為暱稱
  - `report_table.reported_user`、`reported_username`：僅檢舉人自身及後台可見
  - `report_table.user`（authkey）：不可直接回傳
- **Transaction 規則**：無跨表 transaction，單一 Cassandra INSERT
- **Retry 規則**：若有 Cassandra 寫入失敗，可重試（冪等性需人工確認 report ID 是否由 client 提供或服務端生成）
- **狀態值限制**：`status` 僅可為 `open`（建立時），後續由後台變更為 `done`
- **不可修改欄位**：建立後的 `report_id`、`user`（authkey）、`article_id`、`reason` 寫入後不可由使用者修改

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| authKey 未提供或無效 | 回傳 401 Unauthorized（由 auth service 攔截） |
| reason 空白或超過 100 字元 | 回傳 422 Validation Error |
| article_id 格式不符（非 22 位字母數字） | 回傳 422 Validation Error |
| 會員不存在或 status != 1 | 回傳 404 或 403 Forbidden |
| Cassandra 寫入失敗（timeout） | 回傳 500 Internal Server Error，可重試 |
| authKey 被停用/凍結 | 回傳 403 Forbidden |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T-REP-01 | Flow Test | 正常建立檢舉（帶完整 reason + article_id） | 回傳 200，report status=`open` |
| T-REP-02 | Validation Test | reason 為空字串 | 回傳 422 |
| T-REP-03 | Validation Test | reason 超過 100 字元 | 回傳 422 |
| T-REP-04 | Validation Test | article_id 格式不符（非 22 位字母數字） | 回傳 422 |
| T-REP-05 | Permission Test | 無 authKey | 回傳 401 |
| T-REP-06 | Permission Test | 會員 status=2（凍結） | 回傳 403 |
| T-REP-07 | Flow Test | Cassandra timeout 模擬 | 回傳 500 |
| T-REP-08 | Privacy Test | 查詢檢舉記錄時 account 欄位是否遮蔽 | 回傳遮蔽後帳號 |

---

## 9. 高風險區域

- **高風險 table**：
  - `community.report_table`：儲存檢舉人與被檢舉人身份資訊，不可洩漏
- **高風險 API**：
  - `POST /api/community/backend/report`：寫入檢舉記錄，需確保 authkey 正確對應
- **跨服務資料同步**：無（僅寫入 Cassandra）
- **Transaction**：單一 Cassandra INSERT，無分散式事務
- **Cache consistency**：無使用快取
- **Queue retry**：無使用 Queue
- **Idempotency**：需人工確認：report ID 若由 client 提供，可支援 idempotent；若服務端生成，重試可能建立多筆重複記錄

---

## 10. 常見錯誤

- ❌ 回傳 `report_table.account` 完整帳號 → 對外 API 一律遮蔽
- ❌ 回傳 `report_table.reported_user` / `reported_username` 給非檢舉人或非後台 → 僅檢舉人自身及後台可見
- ❌ 未驗證 `article_id` 格式 → 寫入任意字串可能導致後續查詢失敗
- ❌ 未驗證會員 status（如 status=2 凍結仍可建立檢舉） → 需檢查 `member.gameusers.status=1`
- ❌ 以為 communityservice 有 Redis 快取 → community 無使用 Redis 快取
- ❌ 以為檢舉建立後會自動處理審核或通知 → communityservice 僅儲存檢舉記錄，不負責審核、通知、自動隱藏等後續流程

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/community/backend/report` (README: 檢舉管理) |
| DB | `community.report_table` (README: 檢舉記錄) |
| DB | `member.gameusers` (member-detail.md: authkey/stauts=1 驗證) |
| Code | `ReportController.CreateReport` (OpenAPI: /api/community/backend/report POST) |
| Code | `ReportService.CreateReport` (phase1 batch-1 程式語意) |
| Code | `ReportProvider.Insert` (phase1 batch-1 程式語意) |
| Rule | reason 長度 1~100、article_id 22 位字母數字 (communityservice-detail.md: 寫入限制) |
| Rule | status 僅後台可變更 (communityservice-detail.md: 寫入限制) |
| Rule | account 不可回傳、reported_user 不可暴露 (communityservice-detail.md: 不可回傳欄位) |
| Rule | community 無 Redis 快取 (communityservice-detail.md: Redis) |