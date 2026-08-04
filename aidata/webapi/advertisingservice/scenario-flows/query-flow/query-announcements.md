# 前台查詢公告列表

## 1. 場景目的
供前端（使用者端）取得已發佈且於時效內的公告清單，以顯示於首頁或公告欄。僅回傳 `status=1`（已公告）且當前時間介於 `starttime` 與 `endtime` 之間的記錄，並依指定排序呈現。公告內容以多語言 Map 格式儲存，前端依使用者語系擷取對應文字。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/bulletinboard/announcenments` | 前台查詢公告列表，需驗證 |
| Query | `cache` (bool, default true) | 是否優先讀取快取（README 描述存在 Redis 快取，但 detail 文檔宣稱無 Redis） |

---

## 3. 流程總覽

1. 客戶端請求經 API Gateway 或直接抵達 Controller，先經過 `ECFramework.ECService` 驗證（服務需傳遞有效認證）。
2. Controller 接收請求，若參數 `cache=true` 且 Redis 快取存在（**需人工確認**，README 與 detail 描述不一致），則直接回傳快取結果，流程結束。
3. 若無快取或 `cache=false`，則呼叫 Service 層進行 Cassandra 查詢。
4. Service 層（推測為 `BulletinBoardService`）組裝查詢條件：
   - `status = 1`
   - 當前時間（伺服器時間）在 `starttime` 與 `endtime` 之間（`starttime`、`endtime` 為字串格式 `yyyy-MM-dd HH:mm:ss`，需正確轉換比對）
5. 呼叫 Data Provider 執行 Cassandra 查詢（SELECT FROM `ads.bulletinboard_sport`）。
6. 取得結果後按規則排序（預設依 `addtime` 降冪，或依 `sequence` 升冪）。
7. 若使用 Redis，將結果寫入快取（可能設有 TTL）。
8. 回傳公告列表（Announcement 物件不含內部操作欄位，所有欄位皆可公開）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportBulletinBoardController.Get()` | 接收請求，檢查 `cache` 參數，若快取有效則直接回傳，否則呼叫 Service |
| 2 | Service | `BulletinBoardService.GetAnnouncements(cache)` | 若需查詢 DB，組合條件（status=1, 時間範圍）並呼叫 Provider |
| 3 | Provider | `CassandraProvider` (或 `AdsRepository`) | 執行 CQL SELECT，過濾 `status`、`starttime`、`endtime` |
| 4 | Service | (排序邏輯) | 將結果依 `addtime` 降冪或 `sequence` 升冪排序 |
| 5 | (可選) | `RedisProvider` | 若使用 Redis，將結果快取，否則直接回傳 |

> **需人工確認**：實際實作是否有 Redis 快取、Provider 名稱是否正確。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `ads.bulletinboard_sport` | Read | 查詢符合條件之公告資料 |
| Cache | Redis `SportAdCache` (待確認) | Read / Write | 快取公告列表，加速前台查詢（README 宣稱使用，detail 為「本服務未使用 Redis」） |
| Queue | - | - | 本場景無佇列操作 |

---

## 6. 重要規則

- **權限限制**：必須通過 ECService 驗證，僅允許合法登入使用者請求（所有公告 API 皆需驗證）。
- **欄位限制**：
  - 僅回傳 `status=1`（已公告）資料。
  - 時間過濾：`starttime`（字串 `yyyy-MM-dd HH:mm:ss`） ≤ 當前時間 ≤ `endtime`，不可漏濾。
  - `aid` 為分割區鍵，不可修改。
  - `addtime` 自動產生，API 不得傳入。
  - `announcementmethod` 僅能為 0（彈窗）或 1（橫幅），回傳時可提供，但前端不須限制。
- **不可暴露資料**：無（公告皆為公開資訊）。
- **多語言處理**：`maintopic`、`text1`～`text3` 為 `map<text,text>`，key 為語言代碼（如 `zh`），前端自行依語系選取。
- **排序規則**：預設依 `addtime` 降冪，或依 `sequence` 升冪；不可同時使用兩種，需擇一明確。
- **狀態流轉**：公告狀態僅允許 0→1→2，禁止由 1 回退 0。
- **時間格式**：`starttime` / `endtime` 為字串，比較時需轉為時間物件，不可單純比對字串（可能跨年/月導致錯誤）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證 | 回傳 401 Unauthorized |
| `cache` 參數非法 | 忽略或回傳 400（視實作而定） |
| Cassandra 查詢逾時 | 回傳 5xx 服務錯誤，前端應顯示 fallback |
| Redis 快取失效/不可用（若有使用） | 降級直接查詢 DB，不影響可用性 |
| `starttime` / `endtime` 格式錯誤 | 若為查詢過濾條件，無法正確比對，可能回傳空列表；若寫入時違規則應於建立 API 阻擋，本查詢場景不處理 |
| 公告超過一頁 | 目前 API 無分頁參數，若資料量過大可能導致回應延遲 → **需人工確認**是否有分頁機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 帶有效認證，不帶 cache 參數（預設 true） | 回傳公告列表，僅 status=1 且時間有效之記錄 |
| T2 | Flow Test | 查詢後驗證排序 | 依 `addtime` 降冪或 `sequence` 升冪 |
| T3 | Permission Test | 未帶 token 請求 | 401 |
| T4 | Data Filter Test | 存在 status=0 或時間失效的公告 | 不應出現在回傳列表 |
| T5 | Cache Test | 首次請求後 Redis 有值，第二次請求應從快取回覆（若有使用） | 第二次請求更快，且內容一致 |
| T6 | Multi-Lang | 公告內容包含多語言，前端依 zh-TW 顯示 | 後端回傳完整 Map，不做篩選 |

---

## 9. 高風險區域

- **Redis 緩存與 DB 一致性**：若啟用 Redis，寫入公告（POST/PUT/DELETE）後需同步清除或更新對應快取，否則前台顯示舊資料。
- **公告時間過濾**：`starttime`/`endtime` 為字串，轉換不當可能導致時區錯誤或漏掉邊界值；尤其是跨日或跨年。
- **排序欄位變更**：若業務方要求 `sequence`，但程式預設 `addtime` 降冪，可能造成前台顯示混亂。
- **無分頁機制**：公告資料量大時可能造成回應延遲或記憶體壓力，長期累積需考慮分頁或限制回傳筆數。
- **跨服務讀取**：依據 `ads-detail.md`，其他服務（如 `productservice`、`communityservice`）也可能直讀此表，需確保他們也遵守相同 `status=1` 與時間過濾規則，否則可能從自有後台看到草稿公告（但本服務為 owner，不影響本查詢）。

---

## 10. 常見錯誤

- ❌ **未過濾 `status`**：前台端點直接 SELECT * 無 WHERE status=1，導致尚未發佈的公告（status=0）被使用者看見。
- ❌ **未比較時間**：僅檢查 `starttime` 但忘記 `endtime`，或字串直接比對而非轉時間物件，造成已過期公告仍在列表上。
- ❌ **Redis 與 DB 資料不同步**：若後台更新公告後未清除快取，前台仍顯示舊版。
- ❌ **多語言 key 不匹配**：前端預期 key 為 `zh-TW`，但 DB 儲存為 `zh`，導致無法顯示；後端應確保 Map key 使用系統定義的標準語言代碼。
- ❌ **對外洩露內部欄位**：雖然公告無敏感欄位，但仍需注意不要回傳 `advertising` 表的 `createdby` 等管理資訊（本場景無此問題）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `SportBulletinBoardController.Get` (OpenAPI: `/api/v1/sport/bulletinboard/announcenments`) |
| DB | Cassandra `ads.bulletinboard_sport` (Schema: `ads.md`, Detail: `advertisingservice-detail.md`) |
| 規則 | `advertisingservice-detail.md` 讀取規則段落 |
| Redis | README 提到 `Redis SportAdCache` 快取公告；detail 文件：「本服務未使用 Redis」→ **衝突需人工確認** |
| 驗證 | README API 路由標示「需要驗證」、ECFramework.ECService 統一驗證 |
| 狀態流轉 | `ads-detail.md` 中 `status` 欄位說明：0→1→2，禁止回退 |
| 欄位語意 | `bulletinboard_sport` 各欄位說明於 `advertisingservice-detail.md` 與 `ads-detail.md` |

---

## 建議新增文件 / 規則

- **Redis 快取策略文件**：若實際使用 Redis，應補充快取 Key 設計（如 `bulletin:{site}`）、TTL、清除機制、降級策略。
- **公告分頁規則**：若 API 無分頁，建議定義最大回傳筆數或實作分頁，避免效能問題。
- **時間過濾實作規範**：明確定義時間字串格式、轉換方式與邊界處理（包含 `endtime` 當下是否有效）。