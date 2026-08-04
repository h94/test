# 批次禁言設定

## 1. 場景目的
管理員透過後台系統對多個帳號進行一次性禁言設定。此流程用於處理大量違規用戶，提高管理效率。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/community/mute` | 批次設定多個帳號的禁言狀態 |

---

## 3. 流程總覽

1. 後台管理員提交禁言名單與設定
2. API Gateway 驗證管理員權限（auth service 負責）
3. communityservice 接收 request
4. 驗證輸入參數（帳號清單、禁言類型、時效）
5. 「需人工確認」寫入禁言記錄至對應儲存層（目前無明確 evidence）
6. 「需人工確認」更新 MeiliSearch 索引或 Cassandra 狀態
7. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `CommunityMuteController.put_mute` (推測) | 接收 request，呼叫 Service |
| 2 | Validator | `MuteSchema` (推測) | 驗證帳號清單格式、禁言類型、時效 |
| 3 | Service | `MuteService.batch_mute` (推測) | 執行批次禁言邏輯 |
| 4 | Provider | 「需人工確認」 | 寫入禁言狀態與時效 |
| 5 | Provider | 「需人工確認」 | 更新相關索引或快取 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community` | 「需人工確認」 | 儲存禁言記錄或更新用戶狀態 |
| DB | Cassandra `member.gameusers_banned` | 「需人工確認」 | 可能寫入封禁記錄 |
| Search | MeiliSearch | 「需人工確認」 | 更新文章/留言的可見性或過濾 |
| Cache | Redis | 「需人工確認」 | 清除相關快取 |

---

## 6. 重要規則

### 權限限制

- ✅ 僅後台管理員可呼叫此 API
- ✅ API request 須包含有效 authkey，由 auth service 驗證為管理員
- ✅ communityservice 不自行驗證 token，僅接收已驗證請求

### 欄位限制

- 「需人工確認」禁言類型枚舉值（如：全站禁言、單版禁言、限時禁言）
- 「需人工確認」禁言時效格式與範圍
- 「需人工確認」帳號清單長度上限

### 不可暴露資料

- ✅ 任何 API response 不可回傳完整 `authkey`
- ✅ 禁言操作記錄中的管理員帳號不應對外暴露

### 高風險規則

- 「需人工確認」批次操作是否需支援 idempotency（防重複執行）
- 「需人工確認」禁言時的連帶效果（如：隱藏既有文章/留言）
- 「需人工確認」解除禁言機制與排程

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 非管理員呼叫 API | 403 Forbidden |
| 帳號清單為空 | 400 Bad Request |
| 禁言類型不在允許範圍 | 400 Bad Request |
| 時效格式錯誤 | 400 Bad Request |
| 目標帳號不存在 | 「需人工確認」 |
| 帳號已被禁言（重複設定） | 「需人工確認」 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| MUTE-01 | Permission Test | 一般使用者呼叫 API | 403 |
| MUTE-02 | API Test | 有效管理員批次禁言 | 200，名單生效 |
| MUTE-03 | Flow Test | 禁言後查詢被禁言用戶文章 | 文章被隱藏或過濾 |
| MUTE-04 | API Test | 空帳號清單 | 400 |
| MUTE-05 | API Test | 無效禁言類型 | 400 |

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/community/mute` — 批次修改用戶權限，若誤用影響大
- **跨服務同步**：禁言後需確保所有前台頁面（文章列表/留言/搜尋）立即生效
- **Cache consistency**：「需人工確認」禁言後須清除相關快取
- **Idempotency**：若前端 retry，需確保不重複建立禁言記錄
- **權限 bypass**：「需人工確認」確認禁言用戶無法透過其他 API（如編輯文章）繞過限制

---

## 10. 常見錯誤

- ❌ 新人容易直接操作 DB 修改禁言狀態，繞過 API 邏輯
- ❌ 忘記同步清除 MeiliSearch 索引，導致禁言用戶文章仍出現在搜尋結果
- ❌ 未處理批次操作部分失敗的情況
- ❌ 禁言時效到期後未自動解除
- ❌ 對外回傳 authkey 或管理員帳號

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `README.md` — PUT `/api/community/mute` |
| Service | `communityservice-detail.md` — communityservice 為 community keyspace owner |
| DB | `member.gameusers_banned` — 封禁記錄表 |
| Code | 「需人工確認」— 無 controller/service 原始碼 |

---

## 12. 需人工確認

以下項目因無明確 code evidence 或文件說明，需人工確認：

1. **API Request/Response Schema** — OpenAPI 未包含此路由的 spec
2. **禁言資料儲存位置** — 無明確 table 對應（member.gameusers_banned 可能使用，但不確定）
3. **禁言類型枚舉值** — 無 documents 定義可用禁言類型
4. **禁言與既有文章/留言的互動** — 禁言後是否自動隱藏內容
5. **解除禁言機制** — 時效到期如何解除（排程？被動檢查？）
6. **Redis 快取策略** — community 無用 Redis，但禁言是否影響其他快取
7. **批次上限** — 單次 API 最多可禁言幾個帳號