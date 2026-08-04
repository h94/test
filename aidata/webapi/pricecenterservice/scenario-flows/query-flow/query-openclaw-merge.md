# 查詢 OpenClaw 待合併賽事

## 1. 場景目的
提供後台管理人員查詢 OpenClaw 系統待合併賽事，用於審核與確認應由哪些來源站台賽事合併為單一平台賽事的清單。支援「列表查詢」與「單筆詳情查詢」兩種模式。

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/openclawmerge/{gtype}` | 查詢指定球種待合併賽事列表 |
| GET | `/api/v1/openclawmerge/row/{gtype}/{gdate}/{lid}/{id}` | 查詢單筆合併賽事詳情 |

## 3. 流程總覽
1. 接收查詢請求，路徑解析 `gtype` 遊戲類型與可選的複合主鍵 (`gdate`, `lid`, `id`)。
2. 經由 `ECFramework.ECService` 驗證請求的權限。
3. 轉發至對應的 `OpenClawMergeController` → `OpenClawMergeService` 處理。
4. `OpenClawMergeService` 從 **Redis DB6** 讀取站台賽事原始資料。
5. 資料經合併邏輯處理（去重、比對）後，產生待合併賽事清單或單筆詳情。
6. 回傳給調用端。

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `OpenClawMergeController.GetMergeList` | 接收 `GET /{gtype}`，驗證模型 |
| 2 | Controller | `OpenClawMergeController.GetMergeRow` | 接收 `GET /row/{gtype}/{gdate}/{lid}/{id}`，驗證模型 |
| 3 | Service | `OpenClawMergeService.GetMerges` | 查詢列表：調用 Redis DB6 取得站台原始賽事 |
| 4 | Service | `OpenClawMergeService.GetMergeRow` | 查詢單筆：依主鍵從 Redis DB6 取得特定賽事 |
| 5 | Redis Provider | `SiteGameProvider` | 封裝 Redis DB6 讀取操作 |

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | DB6: `siteGame:{site}:{gameType}` | Read | 讀取各站台原始賽事資料作為合併來源 |
| Redis | DB5: `{gameType}:{lid}:{gDate}` | 無直接操作 | （本場景未操作，僅說明）賽事即時資料由其他服務寫入 |

## 6. 重要規則

- **權限限制**：API 路徑前綴為 `pricecenter`，需通過 `ECFramework.ECService` 驗證。僅允許後台管理角色存取（需人工確認具體 Policy）。
- **欄位限制**：從 Redis DB6 讀取的原始站台賽事資料可能包含敏感賠率結構（如即時賠率），需確認回傳時是否需過濾特定站台欄位。**需人工確認**。
- **不可暴露資料**：不可回傳 `password`, `handler` 等與賽事合併無關的帳號欄位。
- **TTL 規則**：Redis DB6 的 `siteGame:*` 鍵的 TTL 由資料同步服務管理，本場景僅讀取。
- **Transaction 規則**：本場景為純讀取操作，不涉及跨儲存體交易。
- **狀態值限制**：合併賽事的狀態值定義（如已合併、待合併）**需人工確認**業務邏輯。
- **不可修改欄位**：本場景為 GET API，不執行任何寫入。

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過驗證（無效/過期 token） | 直接於 Middleware 返回 401，不進入 Controller |
| `gtype` 傳入不支援的球種 | 需人工確認：返回空列表或 400 參數錯誤 |
| Redis DB6 連線失敗或 Timeout | 返回 503 或特定錯誤碼，前端顯示服務暫時不可用 |
| 指定的 `gdate/lid/id` 不存在 | 返回 404 或空結果，需人工確認具體設計 |
| 請求參數格式非法 | 輸入驗證層返回 400 Bad Request |

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| OC-01 | API Test | 帶有效 token 查詢 `GET /openclawmerge/{gtype}` | 200，返回待合併賽事清單 |
| OC-02 | API Test | 帶有效 token 查詢 `GET /openclawmerge/row/{gtype}/{gdate}/{lid}/{id}` | 200，返回單筆賽事詳情 |
| OC-03 | Permission Test | 無 token 請求 | 401 |
| OC-04 | Permission Test | 一般使用者 token 請求 | 需人工確認：403 或 401 |
| OC-05 | API Test | 傳入不存在的 `gtype` | 需人工確認：空列表 [] 或 400 |
| OC-06 | Flow Test | Redis 模擬 Timeout | 503，且記錄錯誤日誌 |
| OC-07 | API Test | 驗證回傳欄位不包含 `password`, `handler`, `AuthKey` 等敏感欄位 | 回傳結構通過檢查 |

## 9. 高風險區域

- **高風險 table**：Redis DB6（站台原始賽事資料），資料量大（來自 70+ 來源），若無索引設計（Redis 鍵結構），可能影響查詢效能。
- **高風險 API**：`GET /api/v1/openclawmerge/{gtype}` 為全站台合併列表查詢，若資料結構設計不當，可能導致大量資料回傳造成 OOM。
- **跨服務資料同步**：Redis DB6 由外部爬蟲/同步服務寫入，資料延遲或不一致會直接影響本場景的查詢結果。
- **Cache consistency**：本場景直接讀取 Redis DB6，無應用層快取，每次請求即時拉取，無 cache stale 風險，但 Redis 壓力較大。

## 10. 常見錯誤

- **新人容易犯錯**：忽略 `gtype` 路徑參數的合法性驗證，直接傳入 Redis 查詢，可能導致 Redis 鍵不存在時報錯。
- **AI 容易誤解**：將 OpenClaw 合併賽事與 Redis DB5 的即時賽事資料混淆。OpenClaw 處理的是「站台賽事原始資料的合併過程」，而 DB5 儲存的是「已合併的即時賽事」。
- **常見漏檢查項目**：未確認回傳的 DTO 是否暴露了不必要的內部站台資料結構（如原始賠率結構）。
- **常見錯誤流程**：直接操作 Redis DB5 讀取即時賽事，而非從 DB6 取得待合併的原始站台賽事。

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md: OpenClaw 合併管理 |
| DB | README.md: Redis DB6 `siteGame:{site}:{gameType}` |
| Code | 需人工提供: `OpenClawMergeController`, `OpenClawMergeService` |
| Model | 需人工提供: OpenClaw 相關 DTO |

## 12. 建議新增

- **文件**：需補充 `OpenClaw` 合併賽事的詳細業務邏輯與資料結構說明（doc/openclaw-business-logic.md）。
- **規則**：補齊合併賽事狀態的列舉限制，以及各狀態的可異動權限（spec/rules/openclaw-merge-rules.md）。
- **測試**：補齊 Redis 無資料、資料格式不符、大量資料壓力測試的場景。