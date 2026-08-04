# 單一帳號禁言

## 1. 場景目的
管理員透過後台對單一使用者帳號設定禁言，使其在社群（體育文章、新彩票論壇）中暫時或永久無法發文、留言。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/community/mute_single` | 對指定帳號進行禁言 |

來源：README.md 禁言管理章節。需驗證身份。

---

## 3. 流程總覽
1. 接收管理員禁言請求（包含 target account、禁言到期時間等參數）
2. 驗證呼叫者權限（需為網站管理員或具備禁言權限之角色）
3. 寫入禁言記錄至儲存層（Cassandra/Redis，**需人工確認**）
4. 更新社群內容索引（MeiliSearch）使該使用者的發文、留言不顯示或標記為隱藏（**需人工確認**）
5. 回傳操作成功

> ⚠️ 本服務未提供禁言專用資料表 schema，下列儲存層使用為推測，待確認實際實作。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | MuteController.mute_single (推測) | 解析請求參數，呼叫 Service |
| 2 | Service | MuteService.mute_user (推測) | 執行商業邏輯：權限檢查、寫入禁言資訊 |
| 3 | Provider | MuteProvider (推測) | 與 Casssandra / Redis / MeiliSearch 互動 |
| 4 | Validator | - | 驗證 target account 存在、禁言時間格式正確 |

確切類別需人工至 `communityservice` 程式碼確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | **未定義表**（推測為 `community.mute_list` 或類似） | Write | 記錄禁言帳號、到期時間 |
| DB | **未定義表**（推測） | Update/Delete | 解禁時移除或更新狀態 |
| MeiliSearch | 文章索引、留言索引 | Update | 將被禁言使用者的內容設為不可見（`hidden:true`）或過濾（**需人工確認**） |
| Redis | **未使用** | - | community 無 Redis 快取規範，禁言狀推測不經過 Redis |

> 若使用 Redis 實作禁言，需違反 README 與 db-usage，因此可能性低。

---

## 6. 重要規則
- **權限限制**：僅管理員或具禁言權限之後台角色可呼叫（由上游 auth service 控制，communityservice 僅接收已驗證 authkey）
- **禁言參數**：需提供 target account、到期時間（永久禁言可為 null）
- **不可暴露資料**：禁言名單中與 target account 相關的內部資訊不可洩漏給一般使用者
- **TTL 規則**：若使用 Redis，禁言資料 TTL 需搭配解禁邏輯，但目前未使用
- **不可修改欄位**：可能禁止直接修改禁言建立時間，只能標記解禁
- **冪等性**：若目標已遭禁言，重複請求應返回成功或更新禁言期限

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未帶有效 authkey | 401 Unauthorized |
| 呼叫者權限不足 | 403 Forbidden |
| target account 不存在 | 400 Bad Request，提示帳號無效 |
| 禁言時間格式錯誤 | 400 Bad Request |
| DB 寫入失敗（Cassandra 逾時） | 500 Internal Server Error，前端可重試 |
| MeiliSearch 更新失敗 | 500 或降級：禁言生效但內容可能短暫可見，需記錄 log 並觸發重試 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| MUTE-01 | Permission Test | 無管理權限呼叫 API | 403 |
| MUTE-02 | API Test | 提供正確參數禁言 | 200，使用者無法發文 |
| MUTE-03 | Flow Test | 禁言後查詢該使用者文章列表 | 文章或留言不顯示（或顯示為隱藏） |
| MUTE-04 | API Test | 重複對同一帳號禁言 | 應可更新禁言到期時間，不可重複建立兩筆啟用禁言 |
| MUTE-05 | Integration Test | MeiliSearch 索引更新延遲 | 在可接受延遲內生效，無錯誤 |

---

## 9. 高風險區域
- **禁言記錄表**：若儲存在 Cassandra，需注意 partition key 設計，避免熱點
- **MeiliSearch 大量更新**：若禁言大量使用者，可能導致索引寫入壓力
- **權限繞過**：API 未正確驗證權限，任何用戶可禁言他人
- **Cache Consistency**：若有地方快取了內容權限而未失效，可能仍顯示被禁言者內容
- **Idempotency**：重複請求可能建立多筆禁言記錄，需確保冪等或合併

---

## 10. 常見錯誤
- **新人容易犯錯**：未理解禁言只影響社群發言，誤以為與帳號凍結相同
- **AI 容易誤解**：可能誤以為 communityservice 直接操作 member.gameusers 狀態，實際上應僅管理社群行為限制
- **常見漏檢查**：禁言後未清除相關快取，導致前端仍可發言
- **常見錯誤流程**：直接修改前端顯示邏輯，而不是調整 MeiliSearch 過濾條件，導致後端仍接受請求

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/community/mute_single`（README.md） |
| 權限規則 | communityservice 不負責認證，僅接收已驗證 authkey（README.md） |
| 索引更新 | 推測更新 MeiliSearch 索引，因所有社群內容搜尋皆依賴該引擎（README 技術棧） |
| 儲存層限制 | community keyspace 僅含 newlottery_forums，禁言表未定義；Redis 未使用（communityservice-detail.md） |

> 需人工確認禁言記錄的實體儲存位置與表名稱。