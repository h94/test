# 建立聯賽進行中設定

## 1. 場景目的

為特定商家 (`businessCode`) 建立或更新聯賽進行中的相關設定，控制聯賽在進行中賽事展示的玩法模式 (PlayMode) 與顯示邏輯。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/leagueinprogressconfigs` | 建立聯賽進行中設定 |
| PUT | `/api/v1/leagueinprogressconfigs` | 更新聯賽進行中設定 |

---

## 3. 流程總覽

1. 接收 API 請求 (包含 `businessCode`, `gameType`, `leagueInProgressPlayModes` 等資訊)
2. 驗證 Auth Token (驗證機制為 `ECFramework.ECService`)
3. 驗證請求參數 (businessCode 與 gameType 不可為空，且格式符合規範)
4. 查詢 `gamesettings.businesses` 確認商家存在
5. 驗證 `gameType` 是否在該商家的 `subgametypes` 清單中
6. 將 `leagueInProgressPlayModes` 序列化後寫入 `league_inprogress_configs` (需人工確認：實際 Cassandra Table 結構尚待確認)
7. 寫入操作日誌至 `gamesettings.league_logs` 或 `pricecenter.action_logs`
8. 回傳成功響應 (200 OK)

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ConfigController` | 接收並反序列化 Request Body |
| 2 | Validator | (ECFramework 整合) | 驗證 AuthToken 有效性 |
| 3 | Service | `IConfigService` (需人工確認) | 帶入 `businessCode` / `gameType` / playmodes 等參數 |
| 4 | Service | `ILeagueService` (需人工確認) | 寫入聯賽進行中設定 |
| 5 | Repository | 需人工確認 (Cassandra Mapper) | INSERT 或 UPDATE 至對應 Cassandra Table |
| 6 | Service | `ILogService` (需人工確認) | 寫入操作日誌 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB-Cassandra | `gamesettings.businesses` | Read | 驗證商家存在 (PK: `businesscode`) |
| DB-Cassandra | `gamesettings.businesses` | Read | 驗證 `gameType` 存在於 `subgametypes` list 中 |
| DB-Cassandra | 需人工確認 (推測為 `league_inprogress_configs` 或 `league_logs`) | Write / Update | 儲存序列化後的進行中玩法設定 |
| Kafka | 需人工確認 | Publish | 非同步通知前端站台設定變更 (根據 README，日誌寫入上報 Kafka + Cassandra) |

---

## 6. 重要規則

- **權限限制**：所有 `/api/v1/leagueinprogressconfigs` 端點均需驗證。
- **商家隔離**：查詢 `businesses` 時以 `businesscode` 為主鍵，不允許跨公司掃描。
- **GameType 限制**：`gameType` 必須包含在該商家 `businesses.subgametypes` list 中。
- **不可暴露資料**：
    - `business_accounts.password` 不可回傳。
    - `businesses.authtoken` 不可回傳。
- **不可修改欄位**：
    - `businesses.businesscode` (主鍵，建立後不可變更)
    - `updater`：此欄位應由後端自動填入當前操作者帳號 (通常從 `AuthToken` 解析)，不接受客戶端傳入。
- **操作日誌**：每次 POST/PUT 操作必須寫入操作日誌至 Cassandra (推測為 `pricecenter.action_logs` 或者 `gamesettings.league_logs`)。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|-------|----------|
| `businessCode` 不存在 | 回傳 404 / 400，訊息提示商家不存在 |
| `gameType` 未授權 | 回傳 403，因 `gameType` 不在商家訂閱清單 `subgametypes` 中 |
| `updater` 由客戶端傳入 | 後端邏輯應強制覆蓋為登入帳號或拒絕請求 (需人工確認) |
| Cassandra 寫入失敗 | Transaction 處理，回傳 500，記錄錯誤日誌 |
| Request body JSON 格式錯誤 | 回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| INP-FLOW-01 | Integration Test | 商家存在且 `gameType` 有效，POST 寫入設定成功 | 200 OK |
| INP-PERM-01 | Permission Test | 使用無效的 AuthToken | 401 Unauthorized |
| INP-FLOW-02 | Flow Test | 商家存在，但請求的 `gameType` 不在 `subgametypes` 中 | 403 Forbidden (或業務邏輯拒絕) |
| INP-FLOW-03 | API Test | `businessCode` 不存在 | 404 / 400 Not Found |
| INP-FLOW-04 | API Test | Push 更新遊戲設定，驗證日誌表寫入是否正確 | `league_logs` (需人工確認) 有對應記錄 |

---

## 9. 高風險區域

- **跨服務資料同步**：需確認 `gameType` 定義是否與外部服務 (如 `pricecenterservice`, `gamedataservice`) 一致。
- **Cache consistency**：若 Redis BusinessCache 有快取商家設定，此 API 寫入後若未主動刪除快取，會導致前台展示延遲 (需人工確認：`gamesettingservice` 宣稱未直接使用 Redis，但相依服務可能有快取)。
- **Table 結構**：Cassandra `league_settings` 與 `league_logs` 的詳細寫入邏輯和 `leagueInProgressPlayModes` 的對應關係需人工確認。

---

## 10. 常見錯誤

- ❌ **誤解 API 用途**：把聯賽進行中設定 (`leagueinprogressconfigs`) 寫入一般的 `league_settings` 表 (需人工確認兩者結構差異)。
- ❌ **漏檢查 GameType**：直接寫入設定卻未驗證商家是否有權限，造成未授權的 GameType 設定生效。
- ❌ **直接覆蓋全量設定**：部份業務邏輯可能需要 append 而非 full replace (需檢查 `IConfigService` 實作)。
- ❌ **回傳了 `updater` 以外的敏感欄位**：雖然查詢接口通常不直接暴露，但在日誌或 Debug 模式下需注意。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `ConfigController` (POST/PUT `leagueinprogressconfigs`) |
| DB | `gamesettings.businesses` (驗證商家與 subgametypes) |
| DB | `gamesettings.league_logs` (寫入推測) |
| DB | `pricecenter.action_logs` (操作日誌寫入規則) |
| Code | `IBusinessService` / `IConfigService` (推測的 Service 層) |
| Rule | `gamesettingservice` DB 操作邊界—寫入限制 (`subgametypes` 驗證) |
| Rule | `gamesettingservice` DB 操作邊界—不可暴露欄位 |