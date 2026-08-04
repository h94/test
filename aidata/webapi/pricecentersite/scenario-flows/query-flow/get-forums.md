# 查詢論壇列表

## 1. 場景目的
讓前端取得啟用中的論壇清單，可依國家代碼過濾，並根據使用者語系回傳對應的論壇名稱。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/forums?country_code={code}&lang={lang}`（需人工確認路徑） | 取得 `status=1` 的論壇，可選過濾 `country_code`，`lang` 用於選擇名稱語言 |

---

## 3. 流程總覽

1. Controller 接收查詢請求，擷取可選的 `country_code` 與 `lang` 參數
2. 調用 Service，傳入過濾條件
3. Service 呼叫 Provider 查詢 `community.newlottery_forums`
4. Provider 對 Cassandra 執行 `SELECT`，條件 `status=1`，若有 `country_code` 則增加 `country_code=?` 過濾
5. Service 收到結果後，對每一筆記錄，自 `names` map 中提取目標語言的名稱；若找不到則 fallback 至 `en` 或 `id`
6. 建構不含敏感欄位（如 `edit_timestamp`、完整 `names` map）的 DTO 列表
7. 回傳論壇列表給前端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ForumController.GetForums`（推測） | 接收 `country_code`（選填）、`lang`（選填），驗證參數 |
| 2 | Service | `CommunityService.GetActiveForums`（推測） | 組合查詢條件，調用 Provider |
| 3 | Provider | `CommunityProvider.QueryForums`（推測） | 執行 Cassandra 查詢 `SELECT * FROM community.newlottery_forums WHERE status=1 [AND country_code=?]` |
| 4 | Service | 同上 | 遍歷結果，依 `lang` 從 `names` map 提取對應名稱；若無則嘗試 `en` 或回傳 `id` |
| 5 | Service | 同上 | 映射為 DTO（僅回傳 `id`、`icon`、`country_code`、`name`） |
| 6 | Controller | 同上 | 回傳 `200 OK` 與論壇列表 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `community.newlottery_forums` | Read | 取得啟用中的論壇原始資料 |
| Cache | —（無） | — | 目前 community keyspace 未使用 Redis 快取 |

---

## 6. 重要規則

- **狀態過濾**：只回傳 `status=1`（啟用）的論壇；`status=0`（隱藏）不可暴露（參見 `community-detail.md`）
- **國家代碼過濾**：若請求帶入 `country_code`，應加入 `country_code=?` 條件（需注意：`country_code` 可為 null 的論壇是否也應包含？需人工確認）
- **名稱提取**：不可回傳完整 `names` map；須依語系提取對應名稱，缺失時 fallback 至 `en` 或 `id`（參見 `community-detail.md`）
- **不可回傳欄位**：`edit_timestamp` 為內部欄位，對外 API 不可回傳（參見 `pricecentersite-detail.md`）
- **權限**：前台查詢無需驗證；後台管理需具備管理權限才可取得停用論壇（但此場景僅前台）
- **查詢限制**：Cassandra 全表掃描風險低，因主鍵為 `id`，但需確保 `status` 欄位沒有索引，因此實際查詢可能為全表掃描後應用層過濾，或使用 allow filtering（需確認索引情況）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| Cassandra 連線失敗或查詢超時 | 回傳 `500 Internal Server Error`，可能記錄錯誤日誌 |
| 請求的 `lang` 參數無效（如非支援語言代碼） | 應正常處理，使用 fallback 機制，不回傳錯誤 |
| `country_code` 過長或包含非法字元 | 可能回傳 `400 Bad Request`（需驗證 Controller 層有無參數校驗） |
| 無任何啟用論壇 | 回傳空陣列 `[]` 與 `200 OK` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| FT-001 | API Test | 不帶任何參數請求論壇列表 | 回傳所有 `status=1` 的論壇，名稱基於預設語言（如 `en`） |
| FT-002 | API Test | 帶入 `country_code=jp` | 僅回傳 `status=1` 且 `country_code='jp'` 的論壇 |
| FT-003 | API Test | 帶入 `lang=zh-TW` | 每個論壇的 `name` 欄位為對應的繁體中文名稱 |
| FT-004 | Permission Test | 直接請求未經授權的 API | （若此端點無需驗證，則忽略） |
| FT-005 | Flow Test | 模擬 Cassandra 回傳多筆資料，部分 `names` 缺少目標語言 | 應使用 fallback 語言（如 `en`）或 `id` |
| FT-006 | Data Integrity | 確認回傳資料不包含 `edit_timestamp`、完整 `names` map | 只應有 `id`、`icon`、`country_code`、`name` |

---

## 9. 高風險區域

- **無**（此場景為單純讀取，無寫入、無快取同步、無事務風險）
- **潛在風險**：若論壇數量極大且無索引，全表掃描可能造成 Cassandra 壓力；需確認 `status` 欄位是否建立二級索引或使用物化視圖

---

## 10. 常見錯誤

- ❌ 未在查詢中過濾 `status=1`，導致前端顯示隱藏的論壇
- ❌ 直接將 `names` map 完整回傳，違反「不可暴露多語言完整映射」規則
- ❌ 未處理語言 fallback，導致回傳空名稱或 `null`
- ❌ 回傳了 `edit_timestamp`，可能暴露內部維護資訊（雖然影響不大）
- ❌ 將 `country_code` 為 null 的論壇排除在未過濾的請求之外（需確認業務邏輯）

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB | `community.newlottery_forums`（schema 定義 `id text PRIMARY KEY, country_code text, edit_timestamp bigint, icon text, status int, names map<text, text>`） |
| DB 使用規則 | `pricecentersite-detail.md` — community 段落：「論壇列表查詢：預設須 WHERE status=1（啟用）回傳」「名稱顯示：前端應根據使用者語系從 names map 中提取對應語言名稱」 |
| 不可回傳 | `pricecentersite-detail.md` — community 段落：「newlottery_forums.edit_timestamp：編輯時間戳為內部維護資訊，對外 API 無需回傳」 |
| 寫入限制 | `community-detail.md`：「pricecentersite 角色為 reader，僅 SELECT」;「pricecentersite SELECT status=1 前台網站列表，只回傳啟用中的論壇」 |
| 快取 | `pricecentersite-detail.md` — Redis 段落：community keyspace 無快取機制 |