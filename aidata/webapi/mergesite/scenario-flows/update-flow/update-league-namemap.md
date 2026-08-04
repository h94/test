# 更新聯盟語系名稱

## 1. 場景目的
後台編輯人員上傳多語系名稱對照表，覆蓋指定聯盟的各語系顯示名稱（NameMap），供前端多語環境呈現。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/leagues/{gameType}/{id}/namemap` | 更新聯盟語系名稱 |

---

## 3. 流程總覽

1. 接收 PUT request，路徑包含 `gameType`、`id`，body 為 `UpdateLeagueNameMapData` 陣列。  
2. 驗證使用者後台權限（ECCore）。  
3. 透過 PriceCenterService Gateway 呼叫遠端 API，更新該聯盟的名稱對照。  
4. PriceCenterService 回傳結果，成功則回傳 200；失敗則回傳對應錯誤碼。  
5. 操作寫入 Kafka 應用程式 Log（非業務必要）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LeaguesController.UpdateNamemap` (需人工確認) | 接收 request，參數驗證，呼叫 Service |
| 2 | Service | `LeaguesService.UpdateNamemapAsync` (需人工確認) | 整理資料，調用 PriceCenterServiceClient |
| 3 | Provider | `PriceCenterServiceClient.UpdateLeagueNamemap` (需人工確認) | 發送 HTTP PUT 到 PriceCenterService，處理回應 |
| 4 | (背景) | Kafka Producer | 寫入操作 Log (非同步) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| - | 無直接 DB | - | 本服務無直接資料庫，資料讀寫均透過 PriceCenterService |
| Queue | Kafka | Publish | 記錄操作 Log（非核心流程） |

---

## 6. 重要規則

- **權限限制**：需後台管理員權限，ECCore 驗證。
- **欄位限制**：`gameType` 須為有效球種代碼；`id` 須對應存在的聯盟識別碼。
- **請求格式**：body 須為 `UpdateLeagueNameMapData` 陣列，內容應包含語系代碼與對應名稱。
- **不可修改欄位**：此 API 僅修改語系名稱對照，不影響聯盟基本屬性（如主鍵、狀態）。
- **Transaction / Retry**：實際操作在 PriceCenterService 端，本服務僅轉發（失敗時視 PriceCenterService 回傳決定重試策略，需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `gameType` 不存在 | 400 Bad Request or 404 |
| `id` 不存在 | 404 Not Found |
| body 格式錯誤（非陣列、缺必要欄位） | 400 Bad Request |
| PriceCenterService 無法連接 | 502 Bad Gateway 或 500 |
| PriceCenterService 內部更新失敗 | 5xx 並可能附帶錯誤訊息 |
| 權限不足 | 403 Forbidden |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-01 | API Test | 正常更新：提供有效 gameType、id 及多語系內容 | 200，回傳成功狀態 |
| UT-02 | Permission Test | 無權限使用者呼叫 | 403 |
| UT-03 | Error Test | 使用不存在的 gameType | 400/404 |
| UT-04 | Error Test | 使用不存在的 id | 404 |
| UT-05 | Flow Test | 更新後以 GET `/api/leagues/{gameType}` 查詢確認語系名稱已變更 | 名稱與提交一致 |

---

## 9. 高風險區域

- **跨服務資料同步**：依賴 PriceCenterService，其不可用將直接導致本 API 失敗。
- **一致性**：若 PriceCenterService 部分失敗（如多筆語系更新中斷），可能產生不一致的語系資料，需確認其是否支援全部成功或全部失敗。
- **權限控制**：後台 API 需確實攔截未授權請求，避免語系名稱被任意竄改。

---

## 10. 常見錯誤

- ❌ 對 `gameType` 與 `id` 未做有效性查驗，將無效請求轉發至 PriceCenterService，造成多餘錯誤。
- ❌ 未處理 PriceCenterService 回應的錯誤碼，直接回傳 200，導致前端誤判成功。
- ❌ 忽略請求內容格式（如語系代碼未定義），導致 PriceCenterService 回覆非預期結果。
- ❌ 在 Controller 層直接寄信或寫入 DB，違反分層；本服務應僅透過 Gateway 溝通。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | OpenAPI: `PUT /api/leagues/{gameType}/{id}/namemap` |
| 權限需求 | README: 該路由標示「需要驗證」 |
| 服務相依 | README: PriceCenterService (Gateway) |
| 請求格式 | OpenAPI: `RequestBody` 為 `UpdateLeagueNameMapData[]` |
| 程式實作 | 需人工確認 (Controller, Service, Provider 具體類別與方法) |
| 錯誤處理邏輯 | 需人工確認 (PriceCenterService 回傳格式與本服務的對應邏輯) |