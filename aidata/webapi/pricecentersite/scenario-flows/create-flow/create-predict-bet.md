# 建立預測投注

## 1. 場景目的

選取 `betpool_games` 中狀態為進行中、未派彩且標記為熱門的有效比賽，檢查使用者是否具備 VIP 權限後，寫入 `betpool_bets` 投注記錄（僅包含投注選項與投注 Z 幣金額）。投注建立時不預設贏利（profitzcoin）與輸贏結果（winlose），後續由結算服務負責回填。

---

## 2. 入口 API

需人工確認：OpenAPI 檔案未明確包含投注建立 endpoint，但依據 predict keyspace 業務邏輯推測存在類似 `/api/predict/bets/{gid}` 的端點。

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/predict/bets/{gid}`（推測） | 建立預測投注，傳入 betoption, betzcoin |

---

## 3. 流程總覽

1. 接收投注請求（authKey、gid、betoption、betzcoin）
2. 驗證 authKey 有效，取得 account 與 memberships
3. 查詢 `betpool_games` 驗證比賽：`hot=true AND payout=false AND status=1` 且 `endtime > 當前時間戳`
4. 若比賽 `viponly=true`，檢查使用者 `memberships` 非空且對應訂閱未過期
5. 驗證投注選項存在於 `betpool_games.betoptions`，且 `betzcoin` 有效
6. 產生唯一投注 id，寫入 `betpool_bets`：`gid, account, id, addtime, betoption, betzcoin`
7. 不回填 `profitzcoin` 或 `winlose`
8. 回傳投注 id 與 gid 供前端識別

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | PredictController.CreateBet | 接收 request，驗證 authKey，調用 Service |
| 2 | Service | PredictService.CreateHotBetPoolInplayGamePredictBet | 組合查詢條件，驗證比賽與權限 |
| 3 | Provider | GameDataProvider.GetActiveGame | 查詢 `betpool_games`（hot=true, payout=false, status=1, endtime > now） |
| 4 | Provider | MemberService.VIPGuard | 若 viponly=true，檢查 memberships 與 subendtime 有效 |
| 5 | Provider | PredictDataProvider.InsertBet | INSERT `betpool_bets`（僅 betoption, betzcoin） |
| 6 | Transfer | PredictTransfer.ToBetResultDTO | 轉換投注結果為 DTO（不含 profitzcoin, winlose）|

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_games` | Read | 驗證比賽資格、VIP 限制、投注選項 |
| DB | `predict.betpool_bets` | Write | 寫入投注記錄 |
| DB | `member.gameusers` | Read | 取得 memberships 以驗證 VIP 身份 |
| DB | `member.gamesublogs` | Read | 檢查訂閱到期日，確認 VIP 有效 |
| Redis | `predict:bets:{gid}` | 應於投注寫入時一併維護（需人工確認） | 快取該場比賽投注清單，加速查詢 |
| Queue | - | - | 本場景無 Queue 操作 |

---

## 6. 重要規則

- **權限限制**：僅已登入使用者（authKey 有效）可投注；`viponly=true` 比賽僅 VIP 使用者可投注
- **VIP 驗證規則**：memberships 非空，且 `gamesublogs.subendtime` 大於當前時間
- **投注時間限制**：`betpool_games.endtime` 必須大於當前 UTC 時間戳，始得投注
- **不可寫入欄位**：`winlose`、`profitzcoin` 於投注建立時不可寫入，僅由結算服務回填
- **狀態檢查**：比賽須滿足 `hot=true, payout=false, status=1`
- **投注選項驗證**：`betoption` 必須存在於 `betpool_games.betoptions` 中
- **Transaction 規則**：投注寫入為單一 partition INSERT，不須跨表 transaction
- **不可回傳欄位**：投注建立後回傳 DTO 不應包含 `profitzcoin` 或 `winlose`

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 比賽不存在或已結束（endtime ≤ now） | 拒絕投注，回傳「比賽已結束」 |
| 比賽 payout 已為 true（已派彩） | 拒絕投注，回傳「比賽已結算」 |
| 比賽 hot=false（非熱門） | 拒絕投注，回傳「比賽不可用」 |
| 使用者非 VIP 但比賽 viponly=true | 拒絕投注，回傳「VIP 限定」 |
| VIP 身份存在但訂閱已過期 | 拒絕投注，回傳「VIP 已過期」 |
| betoption 不存在於 betoptions map 中 | 拒絕投注，回傳「無效投注選項」 |
| betzcoin 為負數或零 | 拒絕投注，回傳「無效投注金額」 |
| DB timeout（betpool_games 讀取） | 回傳系統錯誤，建議重試 |
| INSERT betpool_bets 失敗 | 回傳投注失敗，不可 silent fail |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-BET-01 | Integration Test | 一般使用者對普通比賽投注 | 成功建立投注記錄，profitzcoin 為空 |
| IT-BET-02 | Permission Test | 非 VIP 使用者對 viponly=true 比賽投注 | 拒絕投注，回傳 VIP 限定 |
| IT-BET-03 | Permission Test | VIP 使用者對 viponly=true 比賽投注（訂閱有效） | 成功建立投注 |
| IT-BET-04 | Permission Test | VIP 使用者對 viponly=true 比賽投注（訂閱過期） | 拒絕投注 |
| IT-BET-05 | Flow Test | 對已結束比賽投注（endtime < now） | 拒絕投注 |
| IT-BET-06 | Flow Test | 對 payout=true 比賽投注 | 拒絕投注 |
| IT-BET-07 | Flow Test | 對 hot=false 比賽投注 | 拒絕投注 |
| IT-BET-08 | API Test | 傳入無效 betoption | 拒絕投注，回傳錯誤訊息 |
| IT-BET-09 | DB Test | 檢查投注記錄 profitzcoin / winlose | 寫入時為 null 或不存在 |

---

## 9. 高風險區域

- **高風險 table**：`predict.betpool_bets`（金流相關投注記錄，一旦寫入不可修改金額）
- **高風險 API**：投注建立端點（需嚴格驗證權限與比賽狀態，防止超時投注）
- **VIP 驗證邏輯**：需同時檢查 `memberships` 清單與 `gamesublogs.subendtime`，缺少任一檢查可能導致授權錯誤
- **狀態併發**：同一比賽接近 endtime 時投注請求湧入，需確保 Cassandra partition 寫入效能
- **Cache consistency**：若使用 Redis 快取比賽資訊，`hot`、`viponly` 或 `payout` 變更時必須主動失效快取，不可僅靠 TTL
- **Idempotency**：本場景無明確冪等設計（無投注去重機制），需人工確認是否需防止重複投注

---

## 10. 常見錯誤

- ❌ 未過濾 `hot=true` 與 `payout=false` → 允許對非熱門或已派彩比賽投注
- ❌ 僅檢查 `memberships` 非空，未比對 `subendtime` → 過期 VIP 仍可投注
- ❌ 投注時預先寫入 `profitzcoin` 或 `winlose` → 應由結算服務負責，違反規則
- ❌ 逾時比賽未檢查 `endtime` → 允許對已結束比賽投注
- ❌ 回傳 `betpool_bets.id` 以外的內部主鍵給前端 → 應盡量使用 `gid` + `account` 識別
- ❌ 未驗證 `betoption` 是否存在於 `betoptions` → 可能寫入無效投注選項

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | PredictController.CreateBet（推測） |
| DB 讀取規則 | `predict.betpool_games` 須 WHERE `hot=true AND payout=false AND status=1 AND endtime > now` |
| DB 寫入限制 | `predict.betpool_bets` 僅可 INSERT `betoption`, `betzcoin`；不可寫入 `profitzcoin` 或 `winlose` |
| VIP 驗證 | `member.gameusers.memberships` 非空 + `member.gamesublogs.subendtime` > 當前時間 |
| 服務職責 | pricecentersite 為 reader/writer；結算由 GameResultService 負責 |
| 不可回傳欄位 | `betpool_bets.profitzcoin`, `winlose` 未結算前禁止回傳 |

---

## 建議新增文件與規則

- **需人工確認**：投注建立端點的實際 Controller / Service 名稱與 API 路徑
- **建議新增規則**：投注冪等性設計（如同一 gid+account 是否允許重複投注）
- **建議新增測試**：併發投注情境、VIP 權限邊界測試（訂閱剛到期瞬間）