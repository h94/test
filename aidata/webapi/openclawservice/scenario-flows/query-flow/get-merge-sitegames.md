# 查詢站台比賽

## 1. 場景目的

查詢各站台的原始比賽資料，並補上站台層級的聯盟名稱與隊伍名稱映射，協助龍蝦前端進行跨站台賽事合併比對。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/merge/sitegames` | 查詢指定球種、日期、時間區間的站台比賽，回傳含聯盟與隊伍名稱的完整資料。 |

---

## 3. 流程總覽

1. 接收 request，解析查詢參數（球種、日期、時間區間）。
2. 呼叫 Provider 查詢 Cassandra `sitegames_{game_type}` 表，取得站台原始比賽清單。
3. 對每一筆比賽，查詢 `siteleagues_{game_type}` 補上聯盟名稱對照。
4. 對每一筆比賽，查詢 `siteteams_{game_type}` 補上主隊與客隊名稱對照。
5. 組合資料並回傳 JSON。
6. 若查詢無結果，回傳空陣列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `MergeController` | 接收 GET 請求，解析 query params |
| 2 | Service | `MergeService.get_sitegames()` | 依參數呼叫對應 Provider，組合回傳格式 |
| 3 | Provider | `Sitegames.get_sitegames()` | 查詢 `sitegames_{game_type}` 表（Cassandra） |
| 4 | Provider | `Sitegames.get_siteleagues()` | 查詢 `siteleagues_{game_type}` 表（Cassandra），取得聯盟名稱對照 |
| 5 | Provider | `Sitegames.get_siteteams()` | 查詢 `siteteams_{game_type}` 表（Cassandra），取得隊伍名稱對照 |
| 6 | Service | `MergeService.get_sitegames()` | 將聯盟/隊伍名稱映射補入比賽資料後回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sitegames_{game_type}` (Cassandra) | Read | 取得站台原始比賽清單（含 `gid`, `sitegid`, `sitelid`, `teamid_h`, `teamid_a`, `gdate`, `gtime`, `site`） |
| DB | `siteleagues_{game_type}` (Cassandra) | Read | 取得站台聯盟名稱對照（`sitelid` → `name_map`, `en_name`, `source_name`） |
| DB | `siteteams_{game_type}` (Cassandra) | Read | 取得站台隊伍名稱對照（`sitetid` → `name_map`, `en_name`, `source_name`） |
| DB | `games_{game_type}` (Cassandra) | Read（間接） | 透過 `gid` 取得主客隊 `teamid_h` / `teamid_a` 的基礎對照（若 sitegames 表已含 teamid 則可能省略） |
| Redis | 本場景未使用 | — | 無操作 |
| Kafka | 本場景未使用 | — | 無操作（或僅用於非同步日誌） |

---

## 6. 重要規則

- **球種參數**：`game_type` 必須為有效球種（SC / BK / BS / FL / HL / ES / TN 等），否則需人工確認是否回傳空或拋錯。
- **日期時間必要參數**：至少需提供 `gdate` 與時間區間（`start_time`, `end_time`），避免掃描全表。
- **跨站台隔離**：`sitegames` 表包含 `site` 欄位區分站台，查詢時可能需要過濾特定站台（需人工確認是否有 `site` 參數）。
- **唯讀操作**：本場景為純查詢，不允許任何寫入。
- **不回傳敏感欄位**：sitegames 原始資料不得暴露帳號或密碼等資訊（本場景不涉及 accounts 表）。
- **空值處理**：若某比賽對應的聯盟或隊伍名稱不存在，該欄位應回傳空值或預設值（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 無效或不支援 | 需人工確認：回傳 HTTP 400 或空陣列 |
| 未提供 `gdate` 或時間區間 | 需人工確認：回傳 HTTP 400 參數錯誤 |
| Cassandra `sitegames` 表撈取失敗 | 回傳 HTTP 500，並記錄 Kafka 錯誤日誌 |
| `siteleagues` 或 `siteteams` 查無對應資料 | 補 name 時回傳空值或 `null`，不中斷流程 |
| 查詢時間範圍過大導致逾時 | 需人工確認：是否有查詢限制或分頁機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 查詢有效球種（如 SC），指定日期與時間區間 | 回傳 200，包含比賽清單與聯盟/隊伍名稱 |
| T2 | API Test | 查詢不存在的球種 | 需人工確認：400 或 200 空陣列 |
| T3 | Flow Test | 查詢期間無任何比賽 | 回傳 200，空陣列 |
| T4 | Flow Test | 部分比賽的聯盟或隊伍對照不存在 | name 欄位為 `null`，比賽仍回傳 |
| T5 | Integration Test | Cassandra 連線中斷 | 回傳 500，Kafka 記錄錯誤 |
| T6 | API Test | 缺少必要參數 | 回傳 422 或 400 |

---

## 9. 高風險區域

- **大範圍查詢**：若未限制日期或時間區間，可能掃描全表導致 Cassandra 效能瓶頸。
- **電文對照缺失**：`siteleagues` / `siteteams` 資料不完整時，前端可能顯示空白名稱，須確保爬蟲資料同步完整。
- **多表查詢一致性**：查詢 `sitegames` 後再查 `siteleagues` 與 `siteteams` 屬多次查詢，若其間資料更新可能導致不一致（但本場景為靜態對照，風險低）。
- **無 Transaction**：Cassandra 不支援跨表 ACID，但本場景僅讀取，無一致性问题。

---

## 10. 常見錯誤

- ❌ **忘記過濾時間範圍**：直接 `SELECT *` 全表，造成 Cassandra 壓力過大。
- ❌ **回傳不必要欄位**：將 `sitegames` 內部欄位（如部分內部 ID）暴露給前端。
- ❌ **誤將 `sitegames` 當作正式比賽**：`sitegames` 為站台原始資料，尚未合併，不可直接用於賠率展示。
- ❌ **未正確補名稱對照**：直接回傳 `teamid_h` 數字，前端無法識別。
- ❌ **跨球種共用表名**：每個球種的表名皆不同（`sitegames_SC` / `sitegames_BK`...），不可以硬寫。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | `README.md` 中合併賽事功能定義 `/api/merge/sitegames` |
| Cassandra 表 | `sitegames_SC`, `sitegames_BK` 等（`project/Provider/sitegames.py` 語義彙總） |
| 聯盟對照表 | `siteleagues_SC`, `siteleagues_BK` （同 Provider 語義） |
| 隊伍對照表 | `siteteams_SC`, `siteteams_BK` （同 Provider 語義） |
| 球種列表 | `project/Provider/games.py` 中 `games_SC` / `games_BK` 等表定義 |
| 技術棧 | `README.md` 技術棧段落：Cassandra keyspace `pricecenter` |
| 錯誤日誌 | `README.md` Kafka 日誌傳輸機制 |

---

## 建議新增項目

- **建議新增文件**：API 參數規格（`game_type`, `gdate`, `start_time`, `end_time`, `site` 是否必要）
- **建議新增規則**：查詢時間範圍上限（如最多 24 小時）
- **建議新增測試**：multisite 過濾測試、時間邊界測試（start_time == end_time）