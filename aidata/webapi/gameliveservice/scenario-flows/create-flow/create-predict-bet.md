# 發布預測投注

## 1. 場景目的

讓已驗證的使用者在指定群組內發佈一筆賽事預測，內容包含玩法、盤口、賠率、投注點數與主推標記；系統記錄預測資料、寫入聊天室歷史並透過即時通道廣播，供群組成員查看與後續結算。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | /api/Community/Predict （需人工確認） | 發佈預測投注 |

實際路由與參數格式需查閱 OpenAPI 或 Controller 定義。目前無直接 evidence，以下流程基於表結構與 README 推導，細節需人工確認。

---

## 3. 流程總覽

1. Client 攜帶 AuthKey 請求發佈預測，內含群組 ID、比賽資訊（gameType、leagueId、gameId、gameDate）、預測內容（Mode、Spread、Odd、Points）及是否主推。
2. 系統自 `GameUserInfo` 依 AuthKey 取出 Account、Rank、UserName 等資訊；若無效或過期即拒絕。
3. 檢查 `Community_Groups` 中對應群組是否存在、`Enabled` 是否為 1，且發佈者有權限在該群組發言（群組類型與擁有者限制，需人工確認）。
4. 根據比賽類型及 ID 查詢對應動態表（如 `games_{gameType}`）或 `gamelive`，確認比賽有效且未截止（如 `status` 非結束、`GTime` 未超過預測截止時間，規則需人工確認）。
5. 驗證點數合理性（可能僅做數值範圍檢查，不扣餘額，因預測非實際下注；相關餘額/額度邏輯需人工確認）。
6. 為預測產生唯一 ID（可能使用 UUID 或自增序號）。
7. 寫入預測紀錄表（預估為 `CommunityPredictBet`，表結構未在本批揭露，可能命名為 `PredictBetResult`）。欄位推測包含：Account、GroupID、GameType、LID、GID、GDate、Mode、Spread、Odd、Points、IsMainBet、Status（預設待結算）、AddTime 等。
8. 構造預測訊息內容（JSON，含 Mode、Spread、Odd、Points …），以 `ChatType = "predict"` 寫入 `ChatRoomHistories`（GID、Account、Message …）。
9. 透過 SignalR Hub 將此訊息推播至群組中的所有連線。
10. 回傳成功，可能包含該筆預測的識別碼與基本資訊。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 | 備註 |
|------|-------|---------------|------|------|
| 1 | Controller | `CommunityController.PublishPredict`（名稱需人工確認） | 接收請求，呼叫 Service | 無直接 evidence |
| 2 | Service | `PredictService.Create` | 彙整驗證、調用 Provider 寫入 | 推測 |
| 3 | Provider | `CommunityDataProvider` | 讀取 `Community_Groups`、寫入 `ChatRoomHistories` | 僅基於表操作推斷 |
| 4 | Provider | `PredictDataProvider`（可能為 `GameLiveDateProvider` 的一部份） | 寫入 `CommunityPredictBet`（表名未定） | 需人工確認 |
| 5 | Hub | `ChatHub`（推測） | 透過 SignalR 發送訊息給群組連線 | 無直接 evidence |

詳細類名與方法名需對照程式碼，本表僅為示意。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `GameUserInfo` | Read | 驗證會員身份並取得帳號、等級、顯示名稱 |
| DB | `Community_Groups` | Read | 確認群組啟用、類型、擁有者 |
| DB | `games_{gameType}` 或 `gamelive` | Read | 檢查比賽是否存在、狀態 |
| DB | `CommunityPredictBet`（暫稱） | Write | 寫入預測投注明細 |
| DB | `ChatRoomHistories` | Write | 紀錄預測型聊天訊息 |
| SignalR | Hub（如 `/chat`） | Publish | 即時廣播預測訊息至群組 |
| Redis / Cache | 無明確使用 | — | 未發現結合快取的證據 |
| Queue / Kafka | 無明確使用 | — | 預測發布為同步操作，未涉非同步佇列 |

---

## 6. 重要規則

- **權限限制**：僅通過 AuthKey 驗證且非黑名單之會員可發佈；若群組為 `personal` 型，可能僅擁有者可發言（需人工確認）。
- **欄位限制**：
  - `Mode`（玩法）需符合可接受列舉值（ex. 讓分、大小…）。
  - `Points` 必須為正整數，可能設有上限（需求待確認）。
- **不可暴露資料**：不得在回傳中洩漏其他使用者的投注記錄或結算狀態。
- **TTL 規則**：無顯式 TTL；訊息歷史永久存放於 `ChatRoomHistories`。
- **Transaction 規則**：寫入 `CommunityPredictBet` 與 `ChatRoomHistories` 應在同一交易範圍內，以確保一致性（需人工確認有無使用 TransactionScope 或 DB transaction）。
- **Retry 規則**：若 SignalR 推送失敗，目前機制不保證重送，訊息可能僅存於歷史而不觸發即時更新（需人工確認）。
- **狀態值限制**：新建預測狀態應為未結算（例如 `Status = 0`）；後續由結算流程更新。
- **不可修改欄位**：預測一經發佈，投注內容（Mode、Spread、Odd、Points）不應允許用戶自行修改（業務規則需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| AuthKey 無效或已過期 | 回傳 401 Unauthorized |
| 群組 ID 不存在或 `Enabled = 0` | 回傳 400 Bad Request，提示群組無效 |
| 比賽不存在（GID 或 GameType 不符） | 回傳 400 Bad Request，提示比賽資訊錯誤 |
| 比賽已結束或超過投注截止時間 | 回傳 400 Bad Request，提示無法投注 |
| Points 為零或負數 | 回傳 400 Bad Request，提示點數不合規 |
| 系統寫入 DB 失敗（如主鍵衝突、連線逾時） | 回傳 500 Internal Server Error，不寫入任何資料 |
| SignalR 推送失敗（連線數過多或 Hub 異常） | 仍回傳成功，但部分客戶端可能未即時收到訊息；此為已知風險 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 提供有效 AuthKey、群組、比賽與合法預測參數 | 回傳 200，`CommunityPredictBet`、`ChatRoomHistories` 出現新紀錄 |
| T02 | Permission Test | 使用無效 AuthKey | 回傳 401 |
| T03 | API Test | 群組停用（`Enabled=0`） | 回傳 400 |
| T04 | API Test | 比賽不存在或已結束 | 回傳 400 |
| T05 | Flow Test | 發佈後觀察 SignalR 訊息 | 同群組客戶端收到 predict 類型訊息 |
| T06 | Integration Test | 模擬 DB 寫入異常 | 回傳 500，兩張表皆無新資料 |
| T07 | API Test | Points = 0 | 回傳 400 |

---

## 9. 高風險區域

- **高風險 table**：`CommunityPredictBet`（寫入）— 若無適當唯一索引可能導致重複投注，應確保（Account, GID, Mode, Spread）的業務唯一性規則明確。
- **高風險 API**：發佈預測為面向所有用戶的高頻寫入介面，需考慮流量限制與防重複提交。
- **跨服務資料同步**：預測紀錄需供後續結算服務讀取，若與結算服務資料隔離，可能產生同步延遲或遺漏。
- **Transaction**：寫入兩張表務必保持原子性，避免預測存在但聊天室無記錄。
- **Cache consistency**：並未使用外部快取，風險較低。
- **Queue retry**：未使用佇列，若即時推送失敗無重試會影響使用者體驗。
- **Idempotency**：客戶端重送相同 request 可能產生多筆相同預測；應考慮實作 request id 或冪等鍵（需人工確認）。

---

## 10. 常見錯誤

- **新人容易犯錯**：  
  - 直接寫入 `ChatRoomHistories` 而未先驗證群組啟用狀態，導致垃圾訊息。  
  - 忘記將預測內容序列化為 JSON 存入 `Message`，使後續解析異常。  
  - 未在 response 中返回預測 ID，使前端無法關聯後續操作。
- **AI 容易誤解**：  
  - 誤認預測過程會扣減會員點數，但當前功能僅記錄投注，實際扣點可能發生於結算階段（需確認）。  
  - 錯誤產生無意義的 Cache 設計，但此場景未使用 Redis。
- **常見漏檢查項目**：  
  - 未限制同一使用者對同一場比賽發佈多筆預測（需規則明確）。  
  - 未檢查比賽日期是否已過期（截止時間）。  
  - 未處理 `GameType` 不存在於分表的情況。
- **常見錯誤流程**：  
  - 僅寫入 `CommunityPredictBet` 而未寫入 `ChatRoomHistories`，導致聊天室看不見預測。

---

## 11. Evidence

| 類型 | 來源 | 說明 |
|------|------|------|
| 功能介紹 | README.md（「預測投注」段落） | 說明玩法、盤口、賠率、點數與主推方案 |
| DB：聊天室訊息 | `ChatRoomHistories` 表（`ChatType` 可能值含 "predict"） | 預測訊息存在聊天歷史中 |
| DB：使用者驗證 | `GameUserInfo` 表 | 用 AuthKey 查 Account、Rank 等 |
| DB：群組驗證 | `Community_Groups` 表 | 檢查群組存在與啟用 |
| DB：比賽資訊 | `games_{gameType}` 或 `gamelive` 表 | 確認比賽有效 |
| DB：預測紀錄 | `PredictBetResult`（暫定） | 存放預測結果，推測發佈時寫入 |
| 即時通訊 | SignalR Hub（README 提及） | 廣播訊息 |
| 無直接 code evidence | Controller、Service 方法名未提供 | 所有詳細流程均為推斷，需人工確認 |