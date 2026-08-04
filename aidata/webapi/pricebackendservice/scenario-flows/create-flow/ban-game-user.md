# 封禁遊戲會員

## 1. 場景目的

後台管理員通過 pricebackendservice 封禁特定遊戲會員，寫入停權記錄，使該會員無法繼續使用平台服務。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/member/game/users/banned` | 封禁遊戲會員 |

---

## 3. 流程總覽

1. 後台管理員發起封禁請求，攜帶目標會員識別資訊（如 authKey、account 等）及停權原因。
2. pricebackendservice 驗證管理員身份與權限（透過 ECFramework.ECService）。
3. Controller 將請求傳遞給對應的 Service。
4. Service 調用下游 `memberservice` 的 `CreateBannedGameUser` 方法（REST API）。
5. `memberservice` 寫入 `member.gameusers_banned` 記錄。
6. `memberservice` 更新 `member.gameusers.status` 為 2（凍結），必要時更新 `closetime` 或相關標記。
7. pricebackendservice 回傳封禁結果給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MemberGameController.BannedUsers` | 接收 POST 請求，解析封禁參數 |
| 2 | Validator | (推測有權限檢查) | 驗證管理員身份 |
| 3 | Service | `MemberService.BannedGameUsers` | 轉換 DTO，調用下游 memberservice |
| 4 | Provider | `MemberProvider.BannedGameUsersAsync` | 發送 REST 請求至 memberservice |
| 5 | (下游) | `MemberService.CreateBannedGameUser` | 寫入 gameusers_banned，更新 gameusers.status |

> 備註：pricebackendservice 不直接操作 DB，需透過 `memberservice`；具體類名需依實際 source code 確認（在此根據命名慣例推測）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers_banned` | Write (INSERT) | 新增停權記錄 |
| DB | `member.gameusers` | Write (UPDATE) | 將 status 設為 2（凍結） |
| Redis | `GameUser:{authkey}` | Delete | 失效 user 快取，確保後續讀取最新狀態 |
| Kafka | Topic: `applogs` (可選) | Publish | 記錄封禁操作日誌 |

> 根據 `member-detail.md`：封禁時須清除 Redis 快取 `GameUser:{authkey}` 以確保一致性。

---

## 6. 重要規則

- **權限限制**：僅後台管理員（具備適當角色）可執行封禁操作；需通過 ECFramework 驗證。
- **不可直接 DB 操作**：pricebackendservice 不允許直接寫入 `gameusers_banned`，必須透過 `memberservice.CreateBannedGameUser` 方法。（Evidence: `member-detail.md` 寫入限制）
- **狀態同步**：停權後 `gameusers.status` 必須設為 2，且不可再由 2 直升 1；需解封流程。
- **不可回傳敏感欄位**：對外 API 不能回傳 `gameusers.password`、`authkey` 等。
- **快取一致性**：封禁後必須立即清除 `GameUser:{authkey}` Redis 快取，以免用戶仍能操作。
- **記錄完整性**：停權記錄包含 `authkey`、`addtime`、`description`、`endtime`（可為永久）等。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 目標會員不存在（無效 authKey） | 返回錯誤，停止流程 |
| 管理員權限不足 | 返回 403 Forbidden |
| memberservice 不可用 / 回應逾時 | 返回 5xx，操作失敗 |
| 會員已被封禁（雙重封禁） | 依業務規則：拒絕重複封禁或覆蓋；此處建議返回「已封禁」提示 |
| Redis 快取刪除失敗 | 記錄 log，不影響主流程，但需注意可能導致短暫不一致（需人工監控） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-BAN-01 | API Test | 正常封禁一個有效會員，提供完整原因 | HTTP 200，gameusers_banned 新增記錄，status 改為 2 |
| TC-BAN-02 | Permission Test | 一般使用者呼叫此 API | 401/403 拒絕 |
| TC-BAN-03 | Flow Test | 封禁後，馬上以該會員 token 查詢 API | 權限拒絕，無法登入 |
| TC-BAN-04 | Integration Test | 停權記錄寫入時，快取是否同步失效 | 查詢快取為空，重新讀取 DB 得到 status=2 |
| TC-BAN-05 | Error Test | 向 memberservice 送出不存在的 authKey | 收到 memberservice 錯誤回應，pricebackendservice 妥善轉換為 4xx |

---

## 9. 高風險區域

- **高風險 table**：`member.gameusers` 和 `member.gameusers_banned`。錯誤更新可能導致正常用戶無法使用。
- **跨服務資料同步**：pricebackendservice → memberservice，需確保 idempotency（避免重複請求造成多筆封禁）。
- **Transaction**：雖為分散式操作，但封禁應追求強一致性；若 memberservice 寫入成功但快取刪除失敗，會有一致性問題，建議採用最終一致 + 補償機制。
- **Cache consistency**：status 變更時若未刪除 Redis，可能允許被封禁用戶繼續操作，風險極高。
- **Idempotency**：前端重複提交相同封禁請求，需由 memberservice 端檢查是否已存在有效封禁記錄（根據 authKey + 未過期），防止重複建立。

---

## 10. 常見錯誤

- 新人誤以為 pricebackendservice 可直接寫入 Cassandra，而繞過 memberservice。
- 未檢查會員是否已封禁就重複呼叫 `CreateBannedGameUser`，導致重複記錄。
- 忘記在封禁後刪除 Redis 快取，使得被封禁會員仍可短暫使用。
- 回傳資訊中包含 `authkey`、`password` 等敏感欄位。
- 錯誤設定 `status`，例如直接設為 0 而非 2，或從 2 跳至 1。
- 封禁請求中未包含正確的 `endtime`（永久封禁可能設為 null 或特定值），導致狀態判斷錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README: `POST /api/v1/member/game/users/banned` |
| DB | member-detail: gameusers_banned 寫入限制 |
| DB | member-detail: gameusers.status 狀態流轉 (0→1→2) |
| Cache | member-detail: Redis `GameUser:{authkey}` 管理 |
| Code (推測) | Controller: `MemberGameController`, Service: `MemberService` |
| SQL | （透過 downstream REST，非直接 SQL） |

> 實際 Controller / Service 名稱以原始碼為準，本文件基於命名慣例給出推測。若需準確方法簽名，請參考 `pricebackendservice` 原始碼。