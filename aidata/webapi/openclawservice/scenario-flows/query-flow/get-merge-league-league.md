# 查詢聯盟合併清單

## 1. 場景目的

根據指定的球種與時間區間，從 Cassandra 查詢所有官方聯盟與各站台的聯盟映射，並產出兩份清單：
- **主聯盟**：在主系統 `leagues_{game_type}` 中存在，且在各站台有對應映射關聯的聯盟，代表可作為合併的目標基礎。
- **其他聯盟**：僅在站台映射 `siteleagues_{game_type}` 中出現，但未對應到任何主聯盟的項目，代表未被歸類的孤立聯盟，供龍蝦前端判斷是否需要合併。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/merge_league/league/{game_type}` | 根據時間區間產出主聯盟與其他聯盟清單 |

---

## 3. 流程總覽

1. 接收請求參數：球種 `game_type`、查詢的開始時間與結束時間。
2. 查詢主系統聯盟表 `leagues_{game_type}` 取得所有官方聯盟 ID，形成主聯盟集合。
3. 查詢站台聯盟映射表 `siteleagues_{game_type}`，取得所有站台的聯盟 ID 與其對應的官方聯盟 ID。
4. 邏輯分流：
   - 將 `siteleagues` 中 `lid` (主聯盟 ID) 有值的項目歸為**主聯盟**候選。
   - 將 `siteleagues` 中 `lid` 為空或不存在於 `leagues` 表的項目歸為**其他聯盟**候選。
5. 為每個「主聯盟」候選，查詢 `sitegames_{game_type}` 確認在指定時間區間內有無比賽存在，有比賽才列入最終主聯盟清單。
6. 將「其他聯盟」候選中不屬於任何主聯盟的項目加入最終其他聯盟清單。
7. 回傳兩個清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `MergeLeagueController.get_league()` | 接收 `game_type` 與請求參數 |
| 2 | Service | `MergeLeagueService.get_merge_league_list()` | 協調查詢與資料組合邏輯 |
| 3 | Provider | `SitegamesProvider.get_leagues()` | 查詢主系統 `leagues_{game_type}` |
| 4 | Provider | `SitegamesProvider.get_siteleagues()` | 查詢 `siteleagues_{game_type}` 取得站台映射 |
| 5 | Service | `MergeLeagueService._process_main_leagues()` | 過濾並組合主聯盟資料 |
| 6 | Provider | `SitegamesProvider.get_sitegames_by_league()` | 查詢 `sitegames_{game_type}` 確認比賽存在 |
| 7 | Service | `MergeLeagueService._process_other_leagues()` | 收集未映射的孤立聯盟 |
| 8 | Controller | `MergeLeagueController.get_league()` | 組裝最終 response 回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `leagues_{game_type}` | Read | 取得主聯盟基本資訊與 ID |
| DB | `siteleagues_{game_type}` | Read | 取得站台聯盟與主聯盟的對應關係 |
| DB | `sitegames_{game_type}` | Read | 驗證主聯盟在指定時間區間內有比賽 |
| Redis | 無使用 | - | - |
| Kafka | 無使用 | - | - |

---

## 6. 重要規則

- 聯盟 ID `lid` 為預設主鍵，不可為空 (主聯盟)。
- 所有對 `siteleagues` 的查詢必須包含站台 (`site`) 欄位，避免跨站台資料混淆。
- 比賽時間過濾依賴 `sitegames` 表的 `gdate` 欄位，格式為 `yyyy-MM-dd`。
- 此 API 為純查詢，不應涉及任何 DB 寫入或狀態變更。
- 無 Transaction 規則 (純讀取)。
- 無 TTL / Retry 邏輯。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不存在對應的 `leagues` 或 `siteleagues` 表 | 回傳空清單或明確錯誤訊息 (需人工確認實際實作) |
| Cassandra 查詢超時或連線失敗 | FastAPI 拋出 500 錯誤，依賴全域例外處理 |
| 時間參數無效 (格式錯誤或開始時間晚於結束時間) | 需人工確認是否有參數驗證；若無，可能查詢結果為空 |
| `sitegames` 查詢超時 | 可能導致主聯盟清單不完整或回應延遲 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ML-01 | API Test | 提供有效 `game_type` 與時間區間 | 回傳 200，內含非空的主聯盟與其他聯盟清單 |
| ML-02 | API Test | 提供不存在的 `game_type` | 回傳對應的錯誤碼或空清單 |
| ML-03 | Flow Test | 站台有聯盟但無對應的主聯盟 | 該聯盟應出現在「其他聯盟」清單中 |
| ML-04 | Flow Test | 主聯盟在指定時間區間內無比賽 | 該主聯盟不應出現在回傳的主聯盟清單中 |
| ML-05 | Integration Test | Cassandra 某一張表查詢失敗 | 應有明確的錯誤日誌，API 回傳 500 |

---

## 9. 高風險區域

- **Cassandra 查詢相依性**：流程依賴三次以上的 Cassandra 查詢 (`leagues`, `siteleagues`, `sitegames`)，任一次失敗都可能影響結果完整性。
- **比賽過濾邏輯**：主聯盟在有比賽才算有效，此邏輯若錯誤，將直接導致前端錯誤的合併建議。
- **大時間區間查詢**：若查詢時間範圍過大，`sitegames` 查詢可能成為效能瓶頸。

---

## 10. 常見錯誤

- ❌ 未過濾 `site`，導致跨站台聯盟映射錯誤。
- ❌ 直接將所有 `siteleagues` 有 `lid` 的項目當作主聯盟，未驗證該 `lid` 是否存在於 `leagues` 表。
- ❌ 未檢查 `sitegames` 就回傳主聯盟清單。
- ❌ 誤以為此流程需要做 Cache 或 Queue 操作。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/merge_league/league/{game_type}` |
| DB | `leagues_{game_type}`, `siteleagues_{game_type}`, `sitegames_{game_type}` |
| Code | `project/Provider/games.py`, `project/Provider/sitegames.py` |
| 服務說明 | `README.md` - 聯盟合併 (Merge League) 功能段落 |