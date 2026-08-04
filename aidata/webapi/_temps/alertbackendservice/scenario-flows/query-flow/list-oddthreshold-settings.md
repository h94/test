# 列出賠率閥值設定（遊戲/聯盟/運動層級）

## 1. 場景目的
提供查詢所有已設定的賠率閥值，涵蓋運動（sport）、聯盟（league）與遊戲（game）三個層級。
可用於後台管理介面呈現設定現狀，或供 AI 排程/監控邏輯讀取基準值。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | `/alertbackendservice/api/oddthreshold/settings` | 查詢所有層級的賠率閥值設定，支援以 `game_type`, `source`, `level` 參數過濾（*需人工確認確切 query 參數：OpenAPI 截斷未能完整顯示此路由定義，但從 Provider code 可推斷此 API 存在*） |

---

## 3. 流程總覽
1. API Gateway 接收 GET 請求，附帶選擇性過濾參數 `game_type`, `source`, `level`。
2. FastAPI Router 路由至 `Resources/OddThreshold.py` 對應端點。
3. 調用 `Service/OddThresholdService.py` 的 `list_all` 或 `get_by_filter` 方法。
4. Service 層組裝查詢邏輯，根據 `level` 參數決定查詢對象：
   - `sport` → `oddthreshold_sport_setting`
   - `league` → `oddthreshold_league_setting`
   - `game` → `oddthreshold_game_setting`
   - 未指定則同時查詢三表並合併結果。
5. 呼叫 `Provider/OddThresholdProvider.py` 執行 SQL 查詢。
6. Provider 連線 PostgreSQL，執行對應的 SELECT 語句，回傳資料列。
7. Service 層將結果整理為統一的 DTO 結構（包含層級標記）後回傳。
8. Controller 將結果序列化為 JSON Response 返回客戶端。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Router | `Resources/OddThreshold.py::list_settings` | 接收 GET 請求與 query params |
| 2 | Service | `OddThresholdService.list_all` / `OddThresholdService.query_by_filters` | 判斷查詢層級，組合查詢邏輯 |
| 3 | Provider | `OddThresholdProvider.list_sport_settings` | `SELECT * FROM oddthreshold_sport_setting WHERE …` |
| 4 | Provider | `OddThresholdProvider.list_league_settings` | `SELECT * FROM oddthreshold_league_setting WHERE …` |
| 5 | Provider | `OddThresholdProvider.list_game_settings` | `SELECT * FROM oddthreshold_game_setting WHERE …` |
| 6 | Service | `OddThresholdService` | 合併多表結果，標記 `level` 欄位 |
| 7 | Router | `Resources/OddThreshold.py` | JSONResponse |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_sport_setting` | Read | 取得運動層級閥值 |
| DB | `oddthreshold_league_setting` | Read | 取得聯盟層級閥值 |
| DB | `oddthreshold_game_setting` | Read | 取得遊戲層級閥值 |

> 此場景為純查詢，不寫入 Redis / Kafka / DB。

---

## 6. 重要規則
- **查詢無強制權限限制**，僅後台管理使用（*需人工確認未來是否需要加入 RBAC*）。
- 欄位限制：API 回傳時**不可暴露 `operator_account` 之外的個人身份資訊**。
- 三個層級的 table 欄位結構類似，但各有差異：
  - `oddthreshold_sport_setting`: 主鍵 `game_type`
  - `oddthreshold_league_setting`: 主鍵 `(sitelid, source, game_type)`
  - `oddthreshold_game_setting`: 主鍵 `(sitegid, source, gdate)`
- `playmode` 為 `JSONB` 型態，結構為玩法代碼與其閥值設定的映射，可能包含巢狀結構，前後端應有共用的 DTO 定義。
- 無 TTL、Transaction、Retry 規則。
- **不可修改欄位**：`created_at`, `updated_at` 僅供查詢，不應由客戶端傳入。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 查詢參數格式錯誤（如 `level` 非 `sport/league/game`） | 400 Bad Request，提示可用層級 |
| 無符合條件的設定 | 200 OK，回傳空 list |
| DB 連線失敗或 Timeout | 500 Internal Server Error |
| `game_type` 不存在於任何層級 | 200 OK，回傳空 list |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| OT-Q-01 | API Test | 不帶任何參數查詢全部設定 | 回傳含三個層級的所有設定 |
| OT-Q-02 | API Test | 帶 `level=sport` 參數 | 僅回傳運動層級設定 |
| OT-Q-03 | API Test | 帶 `level=game&game_type=soccer` | 僅回傳足球的遊戲層級設定 |
| OT-Q-04 | DB Test | 三表中任一缺少 `playmode` 資料 | 回傳該設定但 `playmode` 為 null 或空物件 |
| OT-Q-05 | Flow Test | Provider 查詢拋出例外 | Service 層捕捉並記錄錯誤，API 回傳 500 |

---

## 9. 高風險區域
- **無**：此為唯讀查詢，不涉及寫入、同步或快取一致性風險。
- 唯 DB 查詢效能需注意：若 `oddthreshold_game_setting` 資料量龐大且無 `WHERE` 條件可能造成慢查詢。建議確認 Provider 是否有強制分頁或限制筆數（*需人工確認*）。

---

## 10. 常見錯誤
- 新人可能誤以為此 API 需要傳入 body，實際為 GET 請求，參數皆在 query string。
- AI 可能誤解 `oddthreshold_sport_setting` 與 `oddthreshold_league_setting` / `oddthreshold_game_setting` 為同義 table，實際為三個獨立 DB table。
- 常見漏檢查：回傳的 `playmode` JSONB 結構未驗證完整性，前端可能因結構不符而解析失敗。
- 常見錯誤流程：未正確設定資料庫連線，導致健康檢查通過但查詢失敗。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | `Resources/OddThreshold.py`（推斷存在，需人工確認路由確切 path） |
| DB 表格 DDL | `migrations/001_create_core_tables.sql` |
| Provider 程式 | `Provider/oddthreshold_setting.py::list_all` |
| Service 程式 | `Service/OddThresholdService.py`（推斷存在，需人工確認） |
| DB Table Schema | `dbschema detail.md` - `oddthreshold_sport_setting`, `oddthreshold_league_setting`, `oddthreshold_game_setting` |