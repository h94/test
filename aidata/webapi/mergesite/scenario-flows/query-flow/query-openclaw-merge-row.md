# 取得單筆 OpenClaw 合併資料

## 1. 場景目的

提供管理後台查詢特定 OpenClaw 合併記錄的完整詳細資訊，包含合併狀態、主客隊、開盤數、站台賽事對照與投注項。用於人工比對、除錯或確認合併結果。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/merge/openclawmerge/row/{gameType}/{gdate}/{lid}/{id}` | 取得單筆 OpenClaw 合併資料 |

---

## 3. 流程總覽

1. 接收請求，驗證 JWT 權限。
2. 從路徑參數取得 `gameType`、`gdate`、`lid`、`id`。
3. 呼叫 PriceCenterService REST API 取得原始 OpenClaw 合併資料。
4. 將原始資料轉換為 DTO 結構，包含：
   - 合併主資訊（聯盟、主客隊、時間、狀態）
   - 站台賽事對照清單
   - 開盤數與各家賠率
   - 已合併的投注項對照
5. 回傳 `OpenClawMergeDTO`。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `MergeController.OpenClawMergeRow` | 接收請求，呼叫 Service |
| 2 | Service | `MergeService.OpenClawMergeRow` | 組合查詢參數，呼叫 PriceCenterService |
| 3 | Transfer | N/A | 將原始資料映射為 `OpenClawMergeDTO` |
| 4 | Provider | `PriceCenterService` (REST) | 透過 HTTP GET 取得合併資料 |
| 5 | Service | `MergeService.OpenClawMergeRow` | 執行補充轉換邏輯（名稱補全、狀態正規化） |
| 6 | Controller | `MergeController.OpenClawMergeRow` | 回傳 JSON |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| REST | PriceCenterService | Read | 查詢 OpenClaw 合併主檔與明細 |
| Kafka | N/A | 無 | 本查詢不涉及 Kafka 寫入 |
| Cache | N/A | 無 | 本查詢為即時資料，不經快取 |

---

## 6. 重要規則

- **gameType** 必須為球種代碼（如 `SCC`, `NBA`, `MLB`）。
- **gdate** 格式為 `yyyy-MM-dd`。
- **lid** 為主庫聯盟 ID，非站台聯盟 ID。
- **id** 為合併記錄的唯一識別碼，與聯盟、日期共同組成複合鍵。
- 查詢結果包含多語系名稱對照（`nameMaps`），前端應從中選擇合適語系。
- 查詢結果中的 `teamName` 應優先使用 `teamMaps` 中的譯名，而非原始資料的主隊名稱。
- `hTeamName` 與 `aTeamName` 需從 `teamMaps` 中透過對照取得實際名稱。
- 比對狀態（`Status`）為內部列舉值，前端不應依賴原始狀態碼。
- 回傳的 `bettingStop` 狀態需逐筆檢查，不可僅依賴合併主記錄的狀態。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供有效 JWT | 回傳 401 Unauthorized |
| `gameType` 不存在 | 回傳 400 Bad Request |
| `gdate` 格式錯誤 | 回傳 400 Bad Request |
| `lid` 不存在於主庫 | 回傳 204 No Content 或空的合併資料 |
| `id` 不存在 | 回傳 204 No Content |
| PriceCenterService 無回應 | 回傳 502 Bad Gateway，記錄錯誤 Log |
| PriceCenterService 回傳非 2xx | 根據狀態碼回傳對應錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| OC-ROW-01 | API Test | 傳入存在且已合併的資料 | 200，回傳完整合併結構，站台對照不為空 |
| OC-ROW-02 | API Test | 傳入存在但未完全合併的資料 | 200，回傳合併結構，未合併站台賽事應為 `null` 或空 |
| OC-ROW-03 | API Test | 傳入不存在的 `id` | 204 No Content |
| OC-ROW-04 | API Test | 未帶 JWT | 401 Unauthorized |
| OC-ROW-05 | Flow Test | PriceCenterService 回應延遲 | 正確處理 timeout，回傳 502，記錄錯誤 |
| OC-ROW-06 | Flow Test | 依序查詢列表 → 取得單筆 | 單筆資料應與列表中的摘要一致，且包含更多明細 |

---

## 9. 高風險區域

- **PriceCenterService 相依性**：此查詢為同步 HTTP 呼叫，PriceCenterService 異常將直接影響本 API 可用性。
- **無快取緩衝**：每次查詢皆直接呼叫下游，高頻率操作可能對 PriceCenterService 造成壓力。
- **無資料庫備份**：若 PriceCenterService 資料遺失，本 API 亦無法提供任何歷史資料查詢。
- **跨服務資料格式依賴**：若 PriceCenterService 回傳結構變更（如欄位增刪），可能導致轉換失敗或資料缺失。

---

## 10. 常見錯誤

- ❌ 將路徑參數 `lid` 誤認為站台聯盟 ID → ✅ `lid` 為主庫聯盟 ID，站台聯盟 ID 在回傳的 `SiteGames` 內部。
- ❌ 將 `teamName` 直接對應為主隊名稱 → ✅ 需透過 `teamMaps` 將 `homeId` 與 `awayId` 轉換為實際名稱。
- ❌ 預設所有投注項均已合併，未檢查 `bettingStop` → ✅ 應逐筆檢查每個投注項的停止狀態。
- ❌ 在查詢列表後，未透過此單筆 API 就進行強制合併操作 → ✅ 強制合併前應先取得單筆詳細資料確認比對結果。
- ❌ 直接修改回傳物件後用於 `PUT` 操作 → ✅ DTO 為展示用，不可直接作為請求 body 寫回。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `MergeController.OpenClawMergeRow` |
| Service | `MergeService.OpenClawMergeRow` |
| REST | PriceCenterService (192.168.55.60) |
| DTO | `OpenClawMergeDTO` / `OpenClawGame` / `OpenClawSiteGame` / `OpenClawMatch` / `OpenClawBet` |
| Auth | ECCore 3.0.2 JWT Middleware |
| Error | `ServiceMsgCode` (對外統一回傳格式) |

---

## 建議新增文件

- 需人工確認：PriceCenterService 的 OpenClaw 資料結構定義文件（含 REST API 規格與回傳範例）
- 需人工確認：`OpenClawMergeDTO` 完整欄位 mapping 表（原始欄位 → DTO 欄位）
- 需人工確認：比對狀態列舉值定義與說明（`Status` 欄位值域與語意）