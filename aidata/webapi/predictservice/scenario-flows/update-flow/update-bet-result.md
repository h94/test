# 更新競猜結果

## 1. 場景目的
當賽事結束並提供最終賽果後，由後台或 pricebackendservice 觸發此流程，根據賽果結算所有相關下注，更新注單的輸贏狀態與盈利金額，並通知彩金派發服務進行獎金發放。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/bets/results/{gameType}` | 更新指定遊戲類型（如 soccer, basketball）的競猜結果 |

- 需要驗證：✅（內部服務認證，非前台用戶）
- 請求體：包含賽事識別資訊及賽果（具體欄位需人工確認，推測包含 `lid`, `g_date`, `gid`, `winresult`）

---

## 3. 流程總覽

1. 接收賽事結果結算請求，驗證請求來源（pricebackendservice 或排程）及權限。
2. 根據 `{gameType}` 及請求參數定位特定賽事。
3. 從 Cassandra `predict.predict_bets`（或 `predictbets_{gameType}` 系列表）查詢該賽事所有尚未結算的下注。
4. 根據賽果計算每筆下注的輸贏（`winloss`）及盈利（`profitpoint`）。
5. 批次更新所有注單的 `winloss`、`profitpoint` 及結算狀態。
6. 通知彩金派發服務（MemberService 或 WalletService，需人工確認）執行實際獎金發放。
7. 記錄結算日誌（Kafka `applogs` 或 `predict.calculate_logs`）。
8. 回傳操作結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `BetController.UpdateBetResults(gameType)` | 接收請求，驗證 gameType 參數 |
| 2 | Validator | （推測）`ValidateSettlementRequest` | 檢查必要欄位（lid, g_date, gid, winresult） |
| 3 | Service | `BetService.SettleGame(gameType, dto)` | 查詢未結算注單、計算結果、批次更新、通知派彩 |
| 4 | Provider | `BetDataProvider` | 讀取 `predict_bets` / `predictbets_{gtype}` 表；執行批次 UPDATE |
| 5 | Service | `PrizeDistributionService` | 呼叫外部服務（MemberService / WalletService）派彩 |
| 6 | Logger | `KafkaLogProvider` | 發送結算日誌至 Kafka `applogs` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `predict.predict_bets` 或 `predictbets_{gameType}` | Read | 查詢指定賽事未結算的下注 |
| DB (Cassandra) | `predict.predict_bets` 或 `predictbets_{gameType}` | Update | 更新 `winloss`, `profitpoint`, `status`（標記已結算） |
| DB (Cassandra) | `predict.calculate_logs` | Write | 寫入結算日誌記錄 |
| Cache (Redis) | 無明確使用 | ─ | 若有相關快取（賽事狀態），結算後應清除，但目前文件未提及，需人工確認 |
| Queue (Kafka) | `applogs` | Publish | 記錄結算操作，供監控與稽核 |

---

## 6. 重要規則

- **權限限制**：僅允許內部服務（如 pricebackendservice）或排程調用，前台用戶禁止存取。
- **冪等性**：同一賽事重複結算請求不得重複計算與派彩，需根據注單已有狀態判斷（如 status 為已結算則直接返回成功）。
- **狀態限制**：結算後只能將 `status` 從未結算（例如 0）改為已結算（例如 1 或 2），不可逆。
- **不可修改欄位**：`betzcoin`（原始投注額）、`addtime` 等不可變更。
- **金額計算**：`profitpoint` 應由服務端根據設定賠率計算，不允許請求端直接傳入。
- **批次處理事務**：因 Cassandra 非強一致事務，應使用 Batch 語句更新多條下注，若部分失敗需回報錯誤，避免部分結算。
- **外部呼叫重試**：派彩服務呼叫失敗應有重試機制，並記錄至日誌；若最終失敗需人工介入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求的 gameType 無效 | 回傳 400 Bad Request |
| 賽事不存在或無對應下注 | 回傳 404，或視為成功（無需結算） |
| 賽事已結算（重複請求） | 回傳 200（冪等），不重複更新與派彩 |
| Cassandra 寫入失敗／逾時 | 回傳 500，停止流程，記錄錯誤，不進行派彩通知 |
| 外部派彩服務呼叫失敗 | 注單狀態已更新，但記錄派彩失敗；可設計獨立重試或人工補發機制（需人工確認） |
| 部分下注更新成功但 Batch 失敗 | 回報錯誤，由後續補償邏輯處理或人工介入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | 整合測試 | 正常賽事結算，包含贏家與輸家 | 所有下注正確更新 winloss/profitpoint，派彩 API 被呼叫一次 |
| TC02 | API 測試 | 重複傳送相同結算請求 | 第二次請求無任何 DB 變更，回傳成功，派彩服務不被重複呼叫 |
| TC03 | 權限測試 | 使用前台用戶 token 呼叫 | 回傳 403 Forbidden |
| TC04 | 錯誤測試 | 提供不存在的 gid | 回傳 404 或明確錯誤訊息 |
| TC05 | 容錯測試 | Cassandra 暫時不可用 | 回傳 500，下注狀態未變更，無派彩通知 |
| TC06 | 外部相依測試 | 派彩服務逾時 | 結算記錄已更新，派彩失敗記錄於日誌，可觸發告警 |

---

## 9. 高風險區域

- **高風險 Table**：`predict.predict_bets` / `predictbets_{gameType}` — 直接修改金額與狀態，錯誤將導致財務損失。
- **高風險 API**：派彩服務呼叫（MemberService/WalletService）— 調用失敗可能造成「已結算但未發獎」。
- **跨服務資料同步**：predictservice 的結算狀態與錢包系統的獎金發放需保持一致；若無補償機制，可能產生資料不一致。
- **Cassandra Batch 事務**：雖然 Batch 可實現原子性，但仍需注意跨分區 Batch 的性能與一致性限制。
- **快取一致性**：若存在賽事狀態快取，結算後需主動失效，但目前文件未提及，需人工確認。
- **冪等設計**：必須確保重試安全，通常可透過 `gid` 維度的結算旗標實現，避免重複派彩。

---

## 10. 常見錯誤

- ❌ 新人容易誤解：以為 predictservice 直接扣加錢包金額；實際上它只負責計算結果，真正金流由其他服務處理。
- ❌ AI 可能遺漏：結算後清理相關快取（若存在），導致前台仍顯示未結算狀態。
- ❌ 漏檢查：未驗證 `winresult` 是否屬於該賽事的有效選項，造成錯誤計算。
- ❌ 流程漏洞：更新注單成功但調用派彩前當機，導致獎金未發放；應考慮非同步派彩或補償機制。
- ❌ 數據處理疏忽：`profitpoint` 未正確考慮賠率或特殊玩法（如串關），使計算結果錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/v1/bets/results/{gameType}`（README, OpenAPI） |
| DB | `predict.predict_bets` 表（README）；`predictbets_{gameType}` 系列表（predict-detail.md） |
| 服務邊界 | predictservice 不負責實際金流操作（predictservice-detail.md「本服務不負責」段落） |
| 依賴服務 | `memberservice` 提供錢包查詢與獎金發放（README 服務相依） |
| 日誌 | Kafka topic `applogs`（README） |
| 狀態機 | 下注狀態通常 0=未結算, 1=已結算...（參考 predict-detail.md betpool 類似定義） |

**⚠️ 需人工確認事項**：  
- 請求體的精確結構（賽果欄位、格式）  
- 派彩通知的方式（直接 API 呼叫或訊息佇列）  
- 結算狀態的具體數值定義  
- 是否使用 Redis 快取賽事狀態，若有則結算後需清除  
- Cassandra Batch 的實際使用策略與邊界處理