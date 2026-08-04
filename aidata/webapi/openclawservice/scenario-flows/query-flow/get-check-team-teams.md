# 取得球種所有聯盟的隊伍

## 1. 場景目的

提供指定球種（game_type）所有聯盟的隊伍清單。結果僅顯示主站台（'ou'）的隊伍映射，不包含各站台層級的原始隊伍映射。每個隊伍會補上對應的聯盟名稱（lname）與隊伍名稱（tname），供「龍蝦」前端進行隊伍檢查與比對。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/check-team/teams/{game_type}` | 取得指定球種所有聯盟的隊伍清單（僅主站台映射） |

---

## 3. 流程總覽

1. 接收 GET 請求，路徑參數 `game_type` 為球種代碼（如 SC、BK）。
2. 驗證 `game_type` 是否為支援的球種。
3. 查詢站台隊伍表（`siteteams_{game_type}`），條件為 `site = 'ou'`（主站台）。
4. 若查無資料，回傳空陣列。
5. 使用查詢結果中的 `lid`（聯盟ID）與 `tid`（隊伍ID），分別查詢 `leagues_{game_type}` 與 `teams_{game_type}`。
6. 將聯盟名稱（lname）與隊伍名稱（tname）補入對應的隊伍資料中。
7. 回傳整理後的隊伍清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `CheckTeamController.teams(game_type)` | 接收請求，調用 Service |
| 2 | Service | `CheckTeamService.get_teams(game_type)` | 協調資料查詢與組裝 |
| 3 | Provider | `SiteGamesProvider.get_siteteams(site='ou', game_type)` | 查詢 `siteteams_{game_type}` 表中 `site='ou'` 的所有資料 |
| 4 | Provider | `GamesProvider.get_leagues(lids, game_type)` | 根據 `lid` 查詢 `leagues_{game_type}` 表 |
| 5 | Provider | `GamesProvider.get_teams(tids, game_type)` | 根據 `tid` 查詢 `teams_{game_type}` 表 |
| 6 | Service | `CheckTeamService.get_teams(...)` | 將聯盟名稱、隊伍名稱合併到結果集 |
| 7 | Controller | `CheckTeamController.teams(...)` | 回傳 JSON 陣列 |

**需人工確認**：實際的 Class 名稱與方法名稱可能依賴具體的專案結構，上述名稱基於典型 FastAPI 架構推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `siteteams_{game_type}` (Cassandra) | Read | 查詢主站台（'ou'）的所有站台隊伍對應 |
| DB | `leagues_{game_type}` (Cassandra) | Read | 根據聯盟ID查詢聯盟名稱（lname） |
| DB | `teams_{game_type}` (Cassandra) | Read | 根據隊伍ID查詢隊伍名稱（tname） |

- **Redis**：此查詢流程本身**不使用** Redis 快取。所有隊伍資料均直接從 Cassandra 讀取。
- **Kafka**：此流程為同步查詢，不涉及訊息佇列。

---

## 6. 重要規則

- **權限限制**：此 API 為內部服務間呼叫，需人工確認是否有 API Key 或 IP 白名單驗證。
- **球種限制**：`game_type` 必須是系統支援的球種（如 SC、BK、BS、FL、HL、ES、TN 等），否則可能拋出 400 錯誤或回傳空值。
- **主站台限制**：查詢 `siteteams` 時，強制過濾 `site = 'ou'`。此為本場景的核心邏輯，確保只回傳「主站台」映射，排除各站台（如 AU8、HGA 等）的原始隊伍對應。
- **不可暴露資料**：回應中不應包含來自 `siteteams` 的 `source_name` 或其他站台專屬欄位（除非做為輔助資訊）。回應主體應聚焦於 `tid`、`lid`、`lname`、`tname` 等主站台資訊。
- **名稱對照**：`teams_{game_type}` 表中的 `tname` 預設應為主站台使用的標準名稱，若有 `name_map`（多語言對照），則需確認回應中是否應包含或僅回傳預設名稱。**需人工確認**：當前實作回傳的是 `tname` 還是從 `name_map` 中提取特定語言名稱。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不存在或未支援 | 回傳 HTTP 400 或 404，錯誤訊息提示球種無效 |
| 指定的 `game_type` 無任何隊伍資料 (`site='ou'` 無資料) | 回傳 HTTP 200，body 為空陣列 `[]` |
| Cassandra 連線中斷（`siteteams` 查詢失敗） | 回傳 HTTP 500，並記錄錯誤日誌 |
| `leagues` 或 `teams` 表中缺少對應的 `lid` 或 `tid`（資料不一致） | 隊伍仍可回傳，但對應的 `lname` 或 `tname` 可能為空值或 `null`。需確認服務是否有預設值（如 'Unknown'）|
| 傳入的 `game_type` 包含特殊字元，如水號（water id）| 球種驗證應拒絕，回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CT-01 | API Test | 傳入有效的 `game_type=SC` | 回傳 200，body 為非空陣列，每個物件含 `tid`、`lid`、`lname`、`tname` |
| CT-02 | API Test | 傳入無資料的 `game_type`（如空 Table） | 回傳 200，body 為空陣列 `[]` |
| CT-03 | API Test | 傳入無效的 `game_type=XXX` | 回傳 400 或 404 |
| CT-04 | Data Integrity | 驗證回傳的 `lid` 與 `tid` 確實只來自 `site='ou'` | 對照 DB 中 `siteteams` 的 `site` 欄位確認 |
| CT-05 | Data Integrity | 驗證 `lname` 與 `tname` 正確對應 `leagues` 與 `teams` 表 | 隨機抽樣 `lid` 與 `tid` 驗證 |

---

## 9. 高風險區域

- **Cassandra 全表掃描**：若 `siteteams_{game_type}` 表資料量極大，且 `site` 欄位未被設定為 Partition Key 或未建立 Secondary Index，`WHERE site='ou'` 可能會觸發全表掃描，導致查詢效能低落或超時。
- **N+1 查詢問題**：若實作對查詢結果逐一調用 `get_leagues` 或 `get_teams`，在高隊伍數量時會造成大量查詢，嚴重影響效能。正確做法應批量查詢。
- **跨表資料不一致**：若 `siteteams` 中存在 `lid` 或 `tid`，但對應的 `leagues` 或 `teams` 表已被刪除或尚未同步，會導致名稱缺失。服務需有防禦性處理（如 try-catch 或預設空字串）。

## 10. 常見錯誤

- ❌ **忘記過濾 `site='ou'`**：直接回傳所有 `siteteams` 資料，導致前端取得大量非主站台的原始隊伍映射，混淆比對邏輯。
- ❌ **誤用其他欄位做為名稱來源**：如回傳 `siteteams` 中的 `source_name` 而非 `teams` 表的 `tname`，導致隊伍名稱非標準化。
- ❌ **球種參數未經白名單驗證**：直接將 `game_type` 拼接進 CQL 查詢語句，可能導致 Cassandra 注入攻擊（Cassandra Injection）。
- ❌ **未處理 `lname` 或 `tname` 為 NULL 的情況**：前端收到 `null` 值可能導致顯示錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 定義 | README.md: `GET /api/check-team/teams/{game_type}` |
| DB Table (siteteams) | Code semantics: `siteteams_SC`、`siteteams_BK` 的 `site`, `tid`, `lid` 欄位 |
| DB Table (teams) | Code semantics: `teams_SC`、`teams_BK` 的 `id`, `tname`, `lid` 欄位 |
| DB Table (leagues) | Code semantics: `leagues_SC`、`leagues_BK` 的 `id`, `lname` 欄位 |
| 僅顯示主站台規則 | README.md: "僅顯示主站台映射" |
| DB 操作 | 基於 `project/Provider/games.py` 與 `sitegames.py` 推斷的 Cassandra 查詢操作 |