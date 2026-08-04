# 更新主題

## 1. 場景目的

管理員透過後台介面，更新反饋服務（feedbackservice）中特定站點的主題設定，包括名稱、排序、啟用狀態。此流程會直接修改 ScyllaDB 內的 `topics_sport` 或 `topics_stock` 表，管理員權限為必要條件。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/admin/topics/{id}` | 需人工確認：實際 API 路徑可能依站點區分或由 request body 攜帶站點識別 |

---

## 3. 流程總覽

1. 管理後端發送 PUT 請求，攜帶主題 ID、站點代碼（sport / stock）及欲更新欄位
2. Controller 驗證請求來源的管理員身份（JWT / Session）
3. 根據站點代碼路由至對應的 Service（SportTopicService 或 StockTopicService）
4. Service 透過 Provider 查詢 ScyllaDB 中現有主題資料，確認 ID 存在
5. 執行欄位驗證（名稱格式、排序數值、Enabled 值）
6. 組裝更新指令（名稱若為多語言 MAP，需正確合併或覆蓋）
7. 執行 CQL UPDATE 寫入 `topics_sport` 或 `topics_stock` 表
8. 回傳更新結果與最新資料

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AdminTopicController.UpdateTopic` | 解析請求、驗證身份、轉送參數 |
| 2 | Service | `SportTopicService.UpdateTopic` 或 `StockTopicService.UpdateTopic` | 執行商業邏輯與驗證 |
| 3 | Provider | `SportTopicDataProvider.Update` 或 `StockTopicDataProvider.Update` | 組裝並執行 CQL UPDATE |
| 4 | Provider | 同上 | 執行 SELECT 確認更新後資料 |
| — | Validator | `TopicUpdateValidator` | 檢核名稱、排序、Enabled 格式 | *需人工確認：實際類別名稱可能不同* |
| — | Auth | `AuthMiddleware` | 確認管理員 JWT token 有效且具有 `admin` 角色 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | ScyllaDB `topics_sport` / `topics_stock` | Read | 查詢現有主題，確認存在 |
| DB | ScyllaDB `topics_sport` / `topics_stock` | Update | 寫入變更後的 `name`、`sort`、`enabled` 及 `updatetime` |
| Cache | 無明確使用 Redis | — | 需人工確認：是否需要在更新後清除前端列表快取 |
| Queue | 無使用 Kafka / Queue | — | 本場景為同步更新，無非同步操作 |

---

## 6. 重要規則

- **權限限制**：僅管理員（`admin` 角色）可調用此 API。JWT 中須包含有效 `role=admin`。
- **站點隔離**：體育主題與股票主題分別儲存於不同表（`topics_sport` / `topics_stock`），不可跨站點操作。
- **名稱欄位限制（體育站點）**：`name` 為 `MAP<text, text>`，新增或修改語言時需保留既有多語言內容（部分更新需合併而非全覆蓋）。需人工確認：前端傳遞格式與合併規則。
- **名稱欄位限制（股票站點）**：`name` 為 `text`（單一語言），直接覆寫。
- **排序規則**：`sort` 為整數，不可為負數，建議範圍 0 ~ 9999。
- **啟用狀態**：`enabled` 僅接受 `0`（停用）或 `1`（啟用）。停用主題後，前端應不再顯示該主題及其下問題。
- **不可修改欄位**：`id` 為主鍵，不可修改。
- **異動記錄**：更新時必須同步更新 `updatetime`（若表有該欄位），需人工確認：`topics_sport` / `topics_stock` 是否包含 `updatetime` 欄位。
- **Transaction 規則**：ScyllaDB 不支援 ACID 交易，更新為單一 CQL 指令，無鎖定機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 無管理員權限 | 回傳 HTTP 403，錯誤訊息：權限不足 |
| 主題 ID 不存在 | 回傳 HTTP 404，錯誤訊息：主題不存在 |
| 站點參數無效（非 sport/stock） | 回傳 HTTP 400，錯誤訊息：無效的站點 |
| `sort` 非數字或超出範圍 | 回傳 HTTP 400，錯誤訊息：排序數值不合法 |
| `enabled` 非 0 或 1 | 回傳 HTTP 400，錯誤訊息：啟用狀態值不合法 |
| 體育主題 `name` 格式錯誤（非 JSON / 非 MAP） | 回傳 HTTP 400，錯誤訊息：名稱格式錯誤 |
| ScyllaDB 寫入失敗（timeout） | 回傳 HTTP 500，需記錄錯誤日誌 |
| 併發更新（同一主題快速多筆請求） | 以最後寫入為準（無鎖），可能導致覆蓋；需人工確認是否需加入樂觀鎖機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-01 | Permission Test | 一般會員呼叫更新 API | 403 拒絕 |
| TC-02 | Integration Test | 管理員更新體育主題名稱（新增語言） | 資料庫 `name` MAP 正確更新，既有語言保留 |
| TC-03 | API Test | 傳送無效的 `enabled` 值 | 400 錯誤 |
| TC-04 | Flow Test | 更新已存在主題的全部欄位 | 回傳 200，查詢結果一致 |
| TC-05 | Flow Test | 更新不存在的 ID | 404 錯誤 |
| TC-06 | API Test | 股票主題更新名稱（純文字覆蓋） | 成功覆蓋 |
| TC-07 | Permission Test | 使用過期 Token 呼叫 | 401 未授權 |

---

## 9. 高風險區域

- **高風險表**：`topics_sport` / `topics_stock` — 錯誤的更新可能導致前端顯示異常或服務降級
- **併發寫入**：ScyllaDB 不提供交易隔離，若有多人同時修改同主題，最後寫入者贏；建議前端限制同時編輯或後端加入版本號比對（需人工確認）
- **Cache consistency**：若前端有快取主題列表，更新後需確保快取失效（本場景未觀察到明確快取機制，需人工確認）
- **多語言部分更新**：體育主題的 MAP 合併邏輯若實作不當，可能遺失語言鍵值對
- **停用主題影響範圍**：將 `enabled` 設為 0 會使其下所有問題不顯示，操作前應提示管理員

---

## 10. 常見錯誤

- **新人容易犯錯**：混淆體育/股票站點的表，未依 `site` 參數正確路由 Provider
- **AI 容易誤解**：可能直接參考 MySQL `notification_topics` 結構，而誤認該表為儲存位置（實際應為 ScyllaDB `topics_sport` / `topics_stock`）
- **常見漏檢查項目**：
  - 未驗證 `name` 的 MAP 格式正確性就寫入
  - 更新後未重新讀取以確保成功
  - 忘記記錄 `updatetime`
- **常見錯誤流程**：在沒有找到主題時仍執行 UPDATE，導致無條件寫入（若 CQL 條件不足可能意外建立新行，需人工確認 ScyllaDB 行為）

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 服務描述 | README.md 主要功能：「管理員能檢視、回覆並追蹤處理狀態…多站點支援」 |
| 表結構（體育） | Source Code Semantics：`topics_sport` 含 `id,enabled,name(MAP),sort` |
| 表結構（股票） | Source Code Semantics：`topics_stock` 含 `id,enabled,name,enabled,sort` |
| 欄位語意 | Source Code Semantics：`SportTopic.Name` → `NameMap`；`SportTopic.Enabled`；`Sort` via `Seq` |
| 權限條件 | 需人工確認：無直接程式碼，但依系統通用規則管理員 API 須 JWT admin |
| DB 操作 | Phase1 分析：Provider 層負責 CQL 讀寫，無 Redis 或 Queue 涉入 |

---

> **需人工確認事項**  
> 1. 實際 API 路徑及 request/response schema  
> 2. 體育主題 MAP 名稱的部分更新合併規則  
> 3. `topics_sport` / `topics_stock` 是否包含 `updatetime` 欄位  
> 4. 更新後是否需要清除前端快取  
> 5. 併發更新的處理策略（樂觀鎖或無處理）  
> 6. 管理員身分驗證的具體實作（JWT 角色檢查位置）  
> 7. 停用主題時是否需要一併停用其下問題  
> 8. ScyllaDB 寫入失敗的重試機制