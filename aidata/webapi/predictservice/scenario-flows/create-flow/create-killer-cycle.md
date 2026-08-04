# 建立Killer周期設定

## 1. 場景目的
管理員或後台為指定遊戲類型（gameType）建立 Killer 機制的初始週期設定，定義該週期適用的聯賽、週期編號及核心派彩參數，作為後續 Killer 帳號管理與結算的基礎。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/settings/killer/cycles/{gameType}` | 建立 Killer 週期設定，需驗證 |

---

## 3. 流程總覽

1. 接收包含週期參數（`lid`, `cid`, `pay_out` 等）的 POST 請求。
2. 驗證呼叫者權限（需後台管理角色，具體角色待確認）。
3. 校驗 `gameType` 必須為已定義的遊戲類型。
4. 檢查同一 `gameType + lid + cid` 組合是否已存在，避免重複建立。
5. 寫入 `predict.killer_cycle_settings` 表。
6. 回傳成功回應，無需觸發快取或佇列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `KillerSettingsController.CreateCycle` (推測) | 接收請求參數，呼叫 Service |
| 2 | Validator | `KillerCycleRequestValidator` (推測) | 驗證必填欄位、型別、數值範圍及遊戲類型有效性 |
| 3 | Service | `KillerSettingsService.CreateCycle` | 檢查唯一性後，透過 Provider 寫入資料庫 |
| 4 | Provider | `PredictDBProvider.InsertKillerCycle` | 執行 Cassandra INSERT 操作 |

> **需人工確認**：實際 Controller、Service、Provider 的類別與方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.killer_cycle_settings` | INSERT | 儲存新週期設定，主要欄位：`game_type`, `lid`, `cid`, `pay_out` |
| Redis | 無 | - | 此場景未啟用快取，後續讀取時可能有快取策略 |
| Queue | 無 | - | 未涉及訊息佇列 |

---

## 6. 重要規則

- **權限限制**：僅限具有 `killer_admin` 或同等後臺管理角色的使用者操作（需人工確認角色名稱）。
- **gameType 限制**：必須為系統中已定義的遊戲類型（如 `football`, `basketball`），否則拒絕建立。
- **唯一性約束**：`gameType + lid + cid` 組合不可重複，重複請求應回傳 `409 Conflict`。
- **不可修改欄位**：`gameType`, `lid`, `cid` 建立後不可修改，後續如有變更需要刪除再重建。
- **pay_out 數值規則**：必須為正整數，可能代表該週期擊殺可獲得的基礎點數，不可為負數或零（若允許零一併定義）。
- **時間範圍**：週期設定可能包含 `start_time`/`end_time`（若存在），但現有文件未提及，需以實際 schema 為準。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 無效的 `gameType` | 400 Bad Request，提示未知遊戲類型 |
| 缺少必填欄位 (`lid` 或 `cid`) | 400 Bad Request，提示缺少欄位 |
| 同一 `gameType+lid+cid` 已存在 | 409 Conflict，提示週期已存在 |
| `pay_out` 小於零或超出範圍 | 400 Bad Request，提示數值無效 |
| 權限不足 | 403 Forbidden |
| Cassandra 寫入失敗或超時 | 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| KC-C01 | API Test | 提供合法參數成功建立週期 | 200 OK，資料庫出現該筆記錄 |
| KC-C02 | Permission Test | 使用無權限帳號呼叫 | 403 Forbidden |
| KC-C03 | Validation Test | 只有 `lid` 而沒有 `cid` | 400 Bad Request |
| KC-C04 | Duplicate Test | 重複發送相同 `gameType+lid+cid` | 409 Conflict |
| KC-C05 | Boundary Test | `pay_out` 設為 0 | 400 或 200（依實際規則） |
| KC-C06 | DB Error Test | 模擬 Cassandra 不可用 | 500 Internal Server Error |

---

## 9. 高風險區域

- **`killer_cycle_settings` 表**：重複寫入會導致後續結算與排行榜出現多份同週期設定，必須在前端或資料庫層級確保唯一性。
- **權限控制**：若權限誤開放，一般使用者可能惡意建立大量週期或設定異常派彩，影響平臺經濟。
- **參數驗證不足**：未校驗 `lid` 有效性的話，可能建立指向不存在聯賽的週期，引發後續 Killer 計算報錯。
- **無快取失效**：目前無快取，但未來若加入週期列表快取，寫入後必須主動失效，避免不一致。

---

## 10. 常見錯誤

- ❌ 未對 `gameType` 做列舉檢查，使用了不存在的遊戲類型。
- ❌ 漏掉 `gameType+lid+cid` 唯一性檢查，導致重複資料。
- ❌ 未處理 Cassandra 寫入失敗的例外，導致 API 回應 200 但實際未建立。
- ❌ 直接允許前端傳入任意 `pay_out` 而無上限，可能產生巨大數值。
- ❌ 假設後續流程會自動檢查 `lid`，忽略前端驗證。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路徑 | README.md：POST `/api/v1/settings/killer/cycles/{gameType}` |
| DB 表 | README.md：`predict.killer_cycle_settings` |
| DB 欄位（推測） | README.md 列出 `game_type`, `lid`, `cid`, `pay_out` |
| 服務角色 | predictservice 是 predict keyspace 的 owner，有寫入權限 |
| 權限需求 | README 標記此 API 需要驗證，但未指定角色，需人工確認 |
| 唯一性限制 | 依據 Cassandra 主鍵設計慣例，主鍵很可能為 (`game_type`, `lid`, `cid`)，自然保證唯一 |

> ⚠️ **需人工確認**：`killer_cycle_settings` 的完整 Schema（含 TTL、狀態欄位）、Controller 類別名稱、權限角色定義、API 請求體詳細規格。目前資訊不足以完全確認所有細節，本文基於現有 `README` 與 `db-usage` 文件推導。