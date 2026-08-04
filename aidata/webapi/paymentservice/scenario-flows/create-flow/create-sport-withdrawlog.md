# 建立體育提現記錄

## 1. 場景目的

會員在前台提交體育錢包餘額的提現申請，系統建立一筆新的提現記錄（`status=0` 待審核），供後台財務人員後續人工審核與撥款。

---

## 2. 入口 API

| Method | Path                       | 說明                 |
|--------|----------------------------|----------------------|
| POST   | /api/v1/sport/withdrawlogs | 建立一筆體育提現記錄 |

---

## 3. 流程總覽

1. 接收前端 POST 請求（包含會員帳號、提現金額等必要欄位）
2. 驗證請求格式與必要欄位
3. 呼叫 `memberservice` 驗證會員身份（`gameusers.status=1` 且非機器人，並檢查錢包）
4. 將提現記錄寫入 `payment.sport_withdraw_logs`，狀態設為 `0`（待審核）
5. 回傳建立成功的記錄資訊（不含過多敏感欄位）

---

## 4. 程式流程

| 順序 | Layer      | Class / Method                       | 動作                                                     |
|------|------------|--------------------------------------|----------------------------------------------------------|
| 1    | Controller | `SportWithdrawController.Post`       | 接收請求，呼叫 `SportWithdrawService.CreateAsync`        |
| 2    | Service    | `SportWithdrawService.CreateAsync`   | 1) 參數驗證 2) 呼叫 memberservice 確認會員狀態 3) 生成 `date_time` 與 id 4) 寫入 DB |
| 3    | Provider   | `SportWithdrawDataProvider.Insert`   | 執行 Cassandra INSERT，`status=0`，寫入 `account`, `date_time`, `amount` 等 |
| 4    | External   | `MemberserviceClient.VerifyAccount`  | 查詢 `member.gameusers` 確認 `status=1`，並排除 `gamerobots`；確認錢包餘額（sport.gameusers_wallet）足夠 |

---

## 5. DB / Cache / Queue 使用

| 類型   | 資源                            | 操作   | 用途                                   |
|--------|---------------------------------|--------|----------------------------------------|
| DB     | payment.sport_withdraw_logs     | Write  | 寫入提現記錄（`status=0`）             |
| DB     | member.gameusers                | Read   | 驗證會員狀態（status=1）               |
| DB     | member.gamerobots               | Read   | 排除機器人帳號                         |
| DB     | sport.gameusers_wallet          | Read   | 檢查錢包餘額是否足夠此次提現金額       |
| External (RPC) | memberservice           | 驗證   | 透過內部 RPC 確認會員身份與錢包資訊    |

> Redis / Kafka / Queue 未參與此場景。

---

## 6. 重要規則

- **權限限制**：需通過 `ECFramework.ECService` 驗證，僅合法會員可申請提現。
- **欄位限制**：`account` 對應 `gameusers.authkey`（內部鍵），不可直接暴露明文 authkey 給前端；request body 可能使用 `account` 展示名稱，後端需轉換。
- **不可暴露資料**：`password`, `email` 等敏感欄位絕不回傳；提現記錄回傳僅含必要資訊（如 `amount`, `date_time`, `status`）。
- **狀態值限制**：插入時強制 `status=0`（待審核），絕不可由前端或服務直接設為 1（已完成）或 2（失敗）。
- **Transaction 規則**：Cassandra 輕量級事務（LWT）或應用層檢查，避免重複插入相同 `account` + `date_time` 的記錄（若主鍵衝突則報錯）。
- **不可修改欄位**：提現記錄建立後，除 `status` 可經由審核 API 更新外，其他欄位不可變更。

---

## 7. 錯誤情境

| 情境                       | 預期結果                                                     |
|----------------------------|--------------------------------------------------------------|
| 會員帳號不存在或已停用     | 回傳 403/422，拒絕申請，不建立記錄                           |
| 帳號為機器人               | 回傳 403，拒絕，並記錄告警                                   |
| 錢包餘額不足提現金額       | 回傳 400，提示餘額不足，不建立記錄                           |
| 請求缺少必填欄位（如 amount） | 回傳 400 Bad Request，標示錯誤欄位                         |
| Cassandra 寫入失敗         | 回傳 500，並記錄錯誤日誌至 Kafka，前台顯示系統繁忙           |
| 重複申請（相同 account + date_time） | 回傳 409 Conflict，告知已有待審核記錄              |

---

## 8. 測試重點

| Test ID | 類型             | 情境                                     | 預期結果                               |
|---------|------------------|------------------------------------------|----------------------------------------|
| T01     | API Test         | 正常提現，帶有效 token 與合法金額        | 200，回傳建立記錄，status=0            |
| T02     | Permission Test  | 未帶 token 或過期 token                  | 401 Unauthorized                       |
| T03     | Flow Test        | 停用會員 (gameusers.status=2)             | 403 Forbidden，不建立記錄                |
| T04     | Flow Test        | 機器人帳號 (gamerobots.enabled=1)        | 403 Forbidden，拒絕申請                |
| T05     | Integration Test | 錢包餘額小於提現金額                     | 400 Bad Request，訊息提示餘額不足       |
| T06     | API Test         | 重複請求（相同 account, date_time 模擬）| 409 Conflict 或 idempotent 保證不重複  |
| T07     | DB Check         | 建立後檢查 `payment.sport_withdraw_logs`| 記錄存在，status=0，金額正確           |

---

## 9. 高風險區域

- **高風險 table**：`payment.sport_withdraw_logs` — 直接影響財務，寫入錯誤金額或狀態將導致金流錯亂。
- **跨服務資料同步**：依賴 `memberservice` 與 `sport` DB 的錢包餘額，需確保呼叫成功或快速失敗。
- **Cache consistency**：本場景未使用快取，但若 `sport.gameusers_wallet` 有快取，提現前需確保餘額即時性（建議直接查 DB）。
- **Idempotency**：需避免同一筆申請因網路重試造成重複記錄，可藉由唯一約束（`account` + `date_time` 或分散式鎖）保證。
- **Race condition**：同一會員同時發起多筆提現，可能超過餘額，需在服務層加上悲觀或樂觀鎖控制。

---

## 10. 常見錯誤

- ❌ **人為直接將提現狀態設為成功（status=1）** → 必須經過財務審核流程，透過獨立 API 更新。
- ❌ **未驗證會員錢包餘額** → 提現金額可能超出錢包現有餘額，導致後續財務對帳錯誤。
- ❌ **直接使用前端傳入的 `account` 當作 `authkey`** → 需由 token 解析出內部 `authkey`，確保安全性。
- ❌ **忘記排除機器人帳號 (`gamerobots`)** → 可能讓測試帳號進行真實提現，影響數據。
- ❌ **建立記錄後未妥善處理失敗** → 若 DB 寫入失敗，需確保回應正確，並記錄完整日誌以便追查。
- ❌ **回傳記錄時帶有 `authkey` 或內部 ID** → 對外應使用展示帳號，敏感主鍵絕不暴露。

---

## 11. Evidence

| 類型     | 來源                                               |
|----------|----------------------------------------------------|
| API      | `SportWithdrawController.Post`（依慣例推斷）       |
| DB 結構  | `payment.sport_withdraw_logs`（README 重要 Table） |
| 狀態值   | `db/payment-detail.md` 常見錯誤中提及 `status=0` 初始值 |
| 服務相依 | README 服務相依表：`memberservice` 驗證會員身份    |
| 錢包檢查 | `sport.gameusers_wallet` (DB schema sport)         |
| 驗證方式 | README 技術棧：`ECFramework.ECService`             |