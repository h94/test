# 查詢單一主題

## 1. 場景目的

讓已登入使用者根據主題 ID 查詢新彩票論壇中指定主題的詳細內容（包含作者資訊、標題、內容、時間等），並對敏感欄位進行遮蔽處理。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}` | 查詢單一主題 |

---

## 3. 流程總覽

1. 接收 request，取得路徑參數 `forum_id` 與 `subject_id`
2. 驗證 authkey（須為已登入使用者）
3. 驗證 `forum_id` 與 `subject_id` 格式
4. 查詢 MeiliSearch 索引 `newlottery_subjects`，依 `subject_id` 取得主題文件
5. 驗證主題存在
6. 驗證主題狀態為公開（`status=1`）
7. 遮蔽 `account` 欄位
8. 回傳主題詳細內容

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | NewLotterySubjectController.GetSubject | 接收 request，取得 authkey |
| 2 | Validator | SubjectIdValidator | 驗證 `forum_id` 與 `subject_id` 格式 |
| 3 | Service | NewLotterySubjectService.GetSubjectById | 組合查詢條件，呼叫 Provider |
| 4 | Provider | MeiliSearchProvider.GetDocument | 查詢 MeiliSearch `newlottery_subjects` 索引 |
| 5 | Service | NewLotterySubjectService.GetSubjectById | 驗證回傳結果（存在、狀態） |
| 6 | Transfer | SubjectTransfer.ToResponse | 遮蔽 `account`，轉換為 Response DTO |
| 7 | Controller | NewLotterySubjectController.GetSubject | 回傳 200 OK |

> **需人工確認**：實際 Controller / Service / Provider 類別名稱與方法名稱，請依據原始碼確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| MeiliSearch | `newlottery_subjects` 索引 | Read | 依 `subject_id` 查詢主題文件 |
| Cassandra | `community.newlottery_forums` | 未使用 | 此 API 不直接查詢論壇主表 |

**注意**：
- community 無使用 Redis 快取（證據：`communityservice-detail.md` 明確說明「community 無使用 Redis 快取」）
- 無 Kafka / Queue 操作

---

## 6. 重要規則

### 權限限制
- 需要驗證（authkey 必須有效），由 auth / member service 負責（communityservice 僅接收已驗證的 authkey）
- 所有已登入使用者皆可查詢公開主題

### 讀取規則
- 必須過濾 `status=1`（公開），隱藏（`status=0`）的主題不可回傳（證據：`communityservice-detail.md`「討論串列表查詢」）
- 若 `subject_id` 不存在，回傳 404（證據：OpenAPI 未明確定義 404，但 README 路由表無特別說明，**需人工確認**實際錯誤處理）

### 不可暴露資料
- `account` 欄位必須遮蔽（如 `name***`），不可回傳完整帳號（證據：`communityservice-detail.md`「不可回傳欄位」）
- `user`（authkey）不可回傳（證據：同上）

### 狀態值限制
- `status` 僅允許 0（隱藏）或 1（公開）（證據：`communityservice-detail.md`「寫入限制」）
- 此 API 僅回傳 `status=1` 的主題

### 不可修改欄位
- 此 API 為唯讀查詢，無寫入操作

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 authkey 或 authkey 無效 | 401 Unauthorized（由 auth service 攔截） |
| `subject_id` 不存在 | 404 Not Found 或回傳空物件（**需人工確認**） |
| 主題 `status=0`（隱藏） | 404 Not Found 或 403 Forbidden（**需人工確認**） |
| MeiliSearch 查詢失敗（連線逾時） | 500 Internal Server Error |
| MeiliSearch 回傳格式異常 | 500 Internal Server Error |
| `forum_id` 格式不符 | 422 Unprocessable Entity |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| S01 | API Test | 查詢存在的公開主題 | 200 OK，回傳主題詳細內容，`account` 已遮蔽 |
| S02 | API Test | 查詢不存在的 `subject_id` | 404 Not Found |
| S03 | Permission Test | 查詢 `status=0` 的主題 | 404 或 403（**需人工確認**） |
| S04 | Permission Test | 未帶 authkey | 401 Unauthorized |
| S05 | API Test | 驗證回傳欄位無 `user`（authkey） | 回傳 JSON 不包含 `user` 欄位 |
| S06 | API Test | 驗證 `account` 已遮蔽 | `account` 值符合遮蔽格式（如 `name***`） |
| S07 | Flow Test | MeiliSearch 無法連線 | 500 Internal Server Error，不揭露內部錯誤細節 |

---

## 9. 高風險區域

- **帳號洩漏**：若未正確遮蔽 `account`，可能導致個資外洩
- **隱藏主題外洩**：若未正確過濾 `status=1`，可能回傳不應公開的內容
- **MeiliSearch 相依性**：MeiliSearch 為唯一查詢來源，若服務中斷將無法查詢
- **無快取**：每次查詢都直接訪問 MeiliSearch，高流量時可能造成效能瓶頸（**建議新增**：後續可考慮加入 Redis 快取，TTL 60 秒）

---

## 10. 常見錯誤

- ❌ 忘記遮蔽 `account` 欄位，直接回傳完整帳號 → 必須遮蔽處理
- ❌ 未過濾 `status=1`，回傳隱藏主題 → 查詢時必須加上 `status=1` 條件
- ❌ 回傳 `user`（authkey）欄位 → 對外 API 不可回傳 authkey
- ❌ 主題不存在時回傳 200 空物件 → 應回傳 404（**需人工確認**）
- ❌ AI 誤解此 API 需查詢 Cassandra `newlottery_forums` 表 → 此 API 僅查詢 MeiliSearch 索引
- ❌ 新人誤以為 community 有 Redis 快取 → community 無使用 Redis 快取

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | `README.md`：「GET /api/newlottery/forums/{forum_id}/subjects/{subject_id}」 |
| 需要驗證 | `README.md`：路由表標示 ✅ |
| DB 讀取規則 | `communityservice-detail.md`：「討論串列表查詢」須過濾 `status=1` |
| 不可回傳欄位 | `communityservice-detail.md`：「不可回傳欄位」— `account` 須遮蔽 |
| 無 Redis | `communityservice-detail.md`：「community 無使用 Redis 快取」 |
| MeiliSearch 索引 | `README.md`：「MeiliSearch newlottery_subjects」 |
| 服務相依 | `README.md`：「MeiliSearch 作為主要查詢引擎」 |