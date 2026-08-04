# 建立活動提現記錄

## 1. 場景目的

會員於活動期間申請提現獎金或收益，透過此 API 建立一筆「活動提現記錄」。該記錄寫入 `payment.withdrawlogs_activity` 表，初始狀態為待審核，供後續財務人員進行人工審核與實際放款。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/withdrawlogs` | 建立活動提現記錄 |

**Evidence**：`README.md` > 活動商品與兌換 > `POST /api/v1/activity/withdrawlogs`。

---

## 3. 流程總覽

1. 接收會員的提現請求（含 `ActivityWithdraw` schema）。
2. 驗證請求參數完整性（需人工確認 Validation 規則細節）。
3. 寫入一筆新記錄至 `payment.withdrawlogs_activity`。
4. 初始 `status` 應設為「待審核」狀態（推測為 `0`，需人工確認狀態枚舉）。
5. 回傳成功回應。

---

## 4. 程式流程

由於缺少 Controller / Service / Provider 的具體 Code 路徑證據，以下為基於現有結構的推測流程，**需人工確認**。

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.CreateWithdrawLog` | 接收 request，呼叫 Service |
| 2 | Service | `IActivityService.CreateWithdrawLog` | 處理業務邏輯、驗證 |
| 3 | Provider | `IActivityDataProvider.InsertWithdrawLog` | 寫入 `payment.withdrawlogs_activity` |

**Evidence**：基於 README 中其他 `POST` API（如 `POST /api/v1/activity/productredeemlogs`）的命名慣例推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.withdrawlogs_activity` | Write (INSERT) | 建立提現記錄 |

**Evidence**：
- `phase1` batch 語意 指出 `withdrawlogs_activity` 表存在，欄位包含 `site`, `activityevent`, `account`, `cid`, `status` 等。
- **衝突待人工**：`product-detail.md` 指出此表尚無服務聲明操作，但 `phase1` 明確標記其屬於 `payment` keyspace。本文件認定 `paymentservice` 為寫入方。

---

## 6. 重要規則

- **初始狀態**：寫入記錄的 `status` 必須為「待審核」（推測為 `0`）。
- **不可修改主鍵**：`site`, `activityevent`, `account`, `cid` 寫入後不可變更。
- **稽核欄位**：`updatetime` 應由系統自動設定為寫入當下的時間戳。
- **狀態限制**：`status` 欄位僅由後續審核流程更新，前端不可直接設定為成功或失敗。
- **權限驗證**：API 需要驗證，確保只有合法會員可提交自身提現申請。

**Evidence**：
- 初始狀態規則來自 `paymentservice-detail.md`：提現應「初始化為待審核，後續由審核或排程更新」。
- 主鍵不可變更為 Cassandra 的一般性限制。
- `phase1` 語意 顯示該表有 `status` 與 `updatetime` 欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求參數缺失（如 `account`, `amount` 等） | 回傳 400 Bad Request |
| 使用者未通過驗證 | 回傳 401 或 403 |
| DB 寫入失敗（如連線逾時） | 回傳 500 Internal Server Error |
| 重複建立相同的提現記錄 | 需人工確認是否為冪等操作或回傳衝突錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| ACT-WD-01 | API Test | 提交完整的提現請求 | 回傳 200 OK，DB 中出現一筆新記錄 |
| ACT-WD-02 | Flow Test | 建立記錄後檢查 `status` | `status` 必須為待審核 (0) |
| ACT-WD-03 | API Test | 缺少必填欄位 | 回傳 400 Bad Request |
| ACT-WD-04 | Permission Test | 未帶 token 或 token 無效 | 回傳 401 Unauthorized |
| ACT-WD-05 | Integration Test | 重複提交相同的 site+activityevent+account+cid | 需人工確認行為（報錯或冪等） |

---

## 9. 高風險區域

- **DB Schema 歸屬矛盾**：`product-detail.md` 指出此表無服務操作，但 `phase1` 顯示其在 `payment` keyspace。若歸屬不明，可能導致未來 Schema 變更不一致。
- **狀態值定義不明**：`status` 的枚舉值未在現有任何文件、Schema 或 Code 中明確定義，團隊可能採用不同版本的值，導致狀態判斷錯誤。
- **敏感個資**：`accountname` 和 `contactnumber` 欄位為個人資料，API 回應時應避免暴露（對非本人或非管理員）。**需人工確認回應欄位遮蔽規則**。

---

## 10. 常見錯誤

- ❌ 前端直接將 `status` 設為 `1`（成功）或 `2`（失敗）。
  ✅ 必須由後台審核 API 更新。
- ❌ 忘記記錄 `updatetime`，導致後續無法追蹤狀態變更時間。
- ❌ 未驗證請求者是否為 `account` 本人或管理員，導致越權操作。
- ❌ 誤認為提現記錄需要搭配 Redis 快取。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md > Activity WithdrawLogs |
| DB | `phase1` batch 語意 > `withdrawlogs_activity` |
| Key Schema | phase1: `site`, `activityevent`, `account`, `cid` |
| Status Rule | `paymentservice-detail.md`：提現初始狀態為待審核 |
| Conflicts | `product-detail.md`：尚無服務聲明；`phase1`：歸屬 `payment` keyspace |

---

## 12. 建議新增

- **建議新增規則**：明確定義 `withdrawlogs_activity.status` 的枚舉值（如 0:待審核, 1:已放款, 2:已拒絕）。
- **建議新增文件**：`db/payment-detail.md` 應補充 `withdrawlogs_activity` 的完整欄位說明與狀態流轉圖。
- **建議新增測試情境**：測試提現記錄中 PII（`accountname`, `contactnumber`）在回應中是否被正確遮蔽。