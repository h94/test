# 合併競猜下注

## 1. 場景目的
將多個已成立的競猜注單合併為一注，用於過關（串關）玩法。此流程允許用戶將同遊戲類型（`gameType`）中的多個預測，組合為一個合併注單，以提高潛在派彩倍率。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/merge/{gameType}/bets` | 合併多筆下注為一注 |

---

## 3. 流程總覽

1. 接收外部合併下注請求，包含 `gameType` 及欲合併的注單資訊。
2. 驗證請求來源的會員身份與帳號狀態（啟用、未凍結）。
3. 驗證所有欲合併的注單皆屬於同一 `gameType`，且注單存在且未被合併過。
4. 檢查會員錢包餘額是否足夠支付合併下注的總額。
5. 執行合併邏輯，產生新的合併注單，並將原始多筆注單狀態關聯至該合併注單。
6. 寫入新的合併注單至 `predict` keyspace
7. 需人工確認：是否寫入 `predict_bets` 表或其他專用合併注單表。
8. 回傳合併成功後的注單資訊。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MergeController.MergeBets` | 接收 `gameType` 與 `PredictMerge` body，轉發至 Service |
| 2 | Service | `BetMergeService.MergeAsync` | 協調驗證與合併邏輯 |
| 3 | Provider | `GameUserProvider.GetUserStatus` | 查詢 `member.gameusers` 驗證會員狀態 (status=1) |
| 4 | Provider | `AccountProvider.ValidateAccount` | 查詢 `pricecenter.accounts_{suffix}` 驗證站台帳號 (enabled=1) |
| 5 | Provider | `BetProvider.GetBetsByIds` | 查詢現有注單 (需人工確認 table) |
| 6 | Service | `BetMergeService.ValidateBets` | 驗證注單狀態、gameType、是否可合併 |
| 7 | Provider | `WalletProvider.CheckBalance` | 呼叫 `MemberService` 檢查餘額 |
| 8 | Service | `BetMergeService.ExecuteMerge` | 執行合併邏輯，產生新注單 ID |
| 9 | Provider | `BetProvider.CreateMergedBet` | 寫入合併注單至 Cassandra (predict keyspace) |
| 10 | Provider | `BetProvider.UpdateOriginalBets` | 更新原始注單的合併關聯狀態 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read | 驗證會員 authkey 與 status=1 |
| DB | `predict.predict_bets` | Read / Write | 查詢原始注單、寫入新合併注單 |
| DB | `pricecenter.accounts_{suffix}` | Read | 驗證帳號 enabled=1 且未關閉 (closetime 為空) |
| Redis | `GameUser:{authkey}` | Get | 優先讀取快取會員狀態，miss 時回源 DB |
| Kafka | `applogs` | Publish | 記錄合併下注操作日誌 |

---

## 6. 重要規則

- **權限限制**：僅有已驗證的會員（`member.gameusers.status = 1`）可操作。
- **遊戲類型限制**：合併的所有注單必須具有相同的 `gameType`。
- **注單狀態限制**：僅狀態為「已成立」且未被其他合併注單關聯的注單才可合併。需人工確認具體狀態值。
- **帳號限制**：操作者的 `pricecenter.accounts_{suffix}.enabled` 必須為 1，且 `closetime` 為空，否則拒絕。
- **不可變更欄位**：合併前的原始注單內容（如選項、金額）不可修改。合併後的新注單金額與選項由系統計算，不可由外部指定。
- **資料隔離**：不可跨站台 (`site`) 合併注單。必須根據站台選擇正確的 `accounts_{suffix}` 表。
- **Redis 快取**：若流程中更新了 `member` 相關資料，需確保對應的 `GameUser:{authkey}` 快取被清除。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 帳號不存在或未啟用 (status != 1) | 回傳 403 Forbidden，拒絕合併 |
| 站台帳號已停用或關閉 (enabled=0 / closetime 非空) | 回傳 403 Forbidden，拒絕操作 |
| 合併的注單包含不存在或非本人所有的注單 | 回傳 400 Bad Request，提示注單無效 |
| 合併的注單不屬於同一 gameType | 回傳 400 Bad Request，提示類型不符 |
| 錢包餘額不足 | 回傳 402 Payment Required，提示餘額不足 |
| 注單已被其他合併單關聯 | 回傳 409 Conflict，提示注單已被合併 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，記錄錯誤日誌，觸發告警 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| M1 | API Test | 用有效帳號合併多筆單一 gameType 的注單 | 返回 200，並回傳合併後的注單資訊 |
| M2 | Permission Test | 使用已停用 (status=2) 的會員帳號調用 API | 返回 403 |
| M3 | Permission Test | 使用帳號存在但 pricecenter 中 enabled=0 的站台帳號調用 | 返回 403 |
| M4 | Flow Test | 合併一筆已被其他合併單關聯的注單 | 返回 409 |
| M5 | Flow Test | 嘗試合併分屬不同 gameType 的注單 | 返回 400 |
| M6 | Flow Test | 在錢包餘額不足的情況下進行合併 | 返回 402 |
| M7 | Flow Test | 模擬 Cassandra 寫入失敗 | 返回 500，後端有錯誤日誌 |

---

## 9. 高風險區域

- **金流一致**：合併下注涉及扣點，需確保呼叫會員服務扣款與寫入注單的原子性，避免扣款但注單未成立的狀況。
- **高風險 Table**：`predict.predict_bets`。錯誤的合併邏輯可能導致注單狀態紊亂，影響後續結算。
- **跨服務資料同步**：與 `memberservice` 的餘額操作屬於跨服務呼叫，需有重試與補償機制。
- **冪等性**：前端重整或重複請求可能導致重複合併。需確保 API 具有冪等性設計（例如，根據請求 ID 防止重複處理）。

---

## 10. 常見錯誤

- ❌ 合併時未校驗所有注單的 `gameType` 一致性，導致後續資料錯誤。
- ❌ 忘記檢查 `pricecenter.accounts_{suffix}` 的 `closetime` 欄位，允許已被關閉的站台帳號操作。
- ❌ 直接根據 `account` 查詢 `member.gameusers`，應改為透過 token 取得的 `authkey` 查詢。
- ❌ 未處理合併過程中 `memberservice` 的呼叫逾時，導致金流與注單狀態不一致。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/merge/{gameType}/bets` (OpenAPI) |
| API | `PredictMerge` Model (OpenAPI) |
| DB | `member.gameusers` status, authkey (Schema & Detail) |
| DB | `pricecenter.accounts_{suffix}` enabled, closetime (Schema & Detail) |
| DB | `predict.predict_bets` (README) |
| Redis | `GameUser:{authkey}` (DB detail - Redis) |
| Code | `MergeController`, `BetMergeService` (Phase1 語意推斷) |