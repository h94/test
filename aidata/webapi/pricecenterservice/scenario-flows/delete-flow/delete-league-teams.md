# 刪除聯賽球隊

## 1. 場景目的

此場景用於後台管理工具，根據指定的遊戲類型 (`gameType`) 與聯賽 ID (`lid`)，刪除該聯賽下所有或特定的球隊資料。此為維護性 API，用於清理不再使用或錯誤配置的聯賽與球隊關聯。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| DELETE | `/api/v1/leagues/{gameType}/{lid}/teams` | 刪除指定聯賽下的球隊。OpenAPI 標記為「手動執行 API 工具」。 |

---

## 3. 流程總覽

1. 接收 Delete 請求，路徑包含 `gameType` 和 `lid`。
2. 驗證請求是否通過 ECFramework.ECService 的內部驗證。
3. 根據 `gameType` 和 `lid`，在 **MySQL Sport DB** 中查詢對應的球隊記錄。
4. 執行刪除操作，移除聯賽與球隊的關聯。
5. 回傳 HTTP 200 成功響應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `LeagueController` | 接收 `gameType` 與 `lid` 參數。 |
| 2 | Validator | ECFramework 驗證層 | 驗證請求權限。 |
| 3 | Service | `LeagueService` | 根據 `gameType` 與 `lid` 調用 Provider 層進行刪除。 |
| 4 | Provider | (TeamRepository) | 執行對 MySQL Sport DB 中 `Team` 相關表的 DELETE 操作。 |
| 5 | Controller | `LeagueController` | 回傳 200 OK。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL Sport DB - `Team` 表 | Delete | 刪除聯賽下的球隊記錄。 |
| DB | MySQL Sport DB - `Team` 相關對照表（如 `TeamAlias`） | Delete | 移除球隊名稱縮寫等對照資訊。 |
| Redis | Redis DB7 (`leagueMap:{gameType}`) | （需人工確認） | 刪除後，相關的聯賽對照快取可能需被動或被動失效。 |

---

## 6. 重要規則

- **權限限制**：需要通過內部驗證，為管理後台工具 API，不應對一般使用者開放。
- **不可逆操作**：刪除動作執行後，球隊與聯賽的關聯將被永久移除。需人工確認是否有提供回復機制。
- **資料一致性**：刪除球隊時，必須同時清理與其相關聯的對照表資料（如名稱縮寫），避免殘留無效數據。
- **Redis 快取**：刪除操作可能影響聯賽快取的一致性。若存在相關快取，應主動使其失效，而非等待 TTL 過期。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 權限不足或未通過驗證 | 回傳 401 Unauthorized 或相應的驗證失敗錯誤。 |
| `gameType` 或 `lid` 格式無效 | 回傳 400 Bad Request。 |
| 指定的 `gameType` 或 `lid` 不存在 | 可能是業務上成功的操作（刪除不存在的關聯），回傳 200 OK。 |
| 數據庫寫入（刪除）失敗 | 回傳 500 Internal Server Error，並記錄詳細錯誤日誌。 |
| 刪除操作時發生並發衝突 | 依賴 DB 的事務隔離級別處理，可能導致部分成功或操作失敗。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| DEL-01 | Flow Test | 提供有效的 `gameType` 和 `lid`，確認該聯賽下有測試球隊。 | 成功刪除，DB 中不再有此聯賽下的球隊記錄，API 回傳 200。 |
| DEL-02 | API Test | 對一個已刪除或不存在球隊的聯賽，再次發送刪除請求。 | API 回傳 200 OK（冪等性）。 |
| DEL-03 | Permission Test | 使用不具管理權限的 Token 發送請求。 | API 回傳 401 Unauthorized。 |
| DEL-04 | Flow Test | 刪除成功後，檢查相關聯的 Redis 快取或對照表是否同步更新。 | 相關快取資料已被清除或更新，不會出現幽靈球隊。 |

---

## 9. 高風險區域

- **高風險 Table**：MySQL Sport DB 中的 `Team` 相關表。此操作為物理刪除，可能導致歷史資料或報表關聯中斷。
- **高風險 API**：`DELETE /api/v1/leagues/{gameType}/{lid}/teams`。此 API 為批量操作，若傳入錯誤的 `lid`，可能意外刪除大量球隊資料。
- **Cache Consistency**：刪除後若未清除 Redis 快取（如 `leagueMap`），可能導致前端顯示已刪除的球隊資料，造成資料不一致。
- **缺少回復機制**：需人工確認此 API 是否為硬刪除，以及是否有任何日誌或備份機制可供資料回復。

---

## 10. 常見錯誤

- ❌ **對外開放此 API**：此 API 被標記為「手動執行 API 工具」，應僅限內部管理網路或具備最高管理權限的帳號呼叫，不應註冊在對外 API 閘道上。
- ❌ **忽略資料庫事務**：若刪除涉及多張表，必須包裹在數據庫交易中以確保原子性，避免部分表刪除成功而另一部分失敗，導致資料不一致。
- ❌ **AI 誤解為一般使用者功能**：AI 在產生程式碼時，可能會將此刪除功能與前台使用者的「取消關注」或「隱藏」功能混淆，誤提供給一般使用者。
- ❌ **未處理外鍵約束**：若 `Team` 表與其他表（如賽事記錄）存在外鍵約束，直接刪除可能會引發資料庫錯誤。必須先解除或級聯刪除相關記錄。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `LeagueController.DeleteTeams` (推測路由: `[HttpDelete("{gameType}/{lid}/teams")]`) |
| API 說明 | OpenAPI: `/api/v1/leagues/{gameType}/{lid}/teams` 的 `delete` 方法，Summary 為「刪除沒有主站台的聯盟隊伍(手動執行API工具)」。 |
| DB 操作 | MySQL Sport DB 中的 `Team` 相關表。 |
| 程式語意 | Phase0/1 分析顯示 `LeagueService.cs` 和 `pricecenterservice` 的模型定義中使用了 `Team`, `TeamAlias`, `LeagueAlias` 等。 |
| 權限 | README 中 API 列表的「聯賽與球隊管理」一節，所有 API 均標註為「需要驗證」。 |