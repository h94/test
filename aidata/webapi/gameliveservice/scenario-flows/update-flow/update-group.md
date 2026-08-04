# 編輯社群群組

## 1. 場景目的

允許群組擁有者或具管理權限的使用者修改社群群組的基本資訊，包括名稱（多語言）、圖示路徑、描述、排序以及置頂訊息設定。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/Community/Groups/{groupId}` | 編輯指定群組的資訊（需人工確認確切路由與 Methodist） |

---

## 3. 流程總覽

1. 接收前端請求，包含群組 ID、欲更新的欄位（名稱、圖示、描述、排序、置頂訊息 ID 等）及使用者 AuthKey。
2. 驗證 AuthKey，取得使用者身份（GameUserInfo）。
3. 查詢目標群組 (Community_Groups) 是否存在且已啟用（Enabled=1 或允許編輯停用群組？需人工確認）。
4. 驗證使用者是否為該群組的擁有者（Owner）或擁有管理權限（如 GType=official 的管理員？需人工確認）。
5. 檢查請求欄位合法性（名稱 JSON 格式、圖示路徑格式、排序整數範圍、置頂訊息所屬群組正確性）。
6. 更新 Community_Groups 的對應欄位，並設定 UpdateTime 為當前 Unix 毫秒時間。
7. 若修改了名稱或圖示，透過 SignalR 推播群組更新事件給群組成員（需人工確認）。
8. 回傳操作結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | CommunityController.EditGroup (推測) | 接收請求、調用 Service |
| 2 | Validator | 驗證方法 (推測) | 檢查必填參數、格式 |
| 3 | Service | CommunityService.EditGroup (推測) | 商業邏輯：權限檢查、存在性檢查、欄位合併 |
| 4 | Provider | CommunityDataProvider.UpdateGroup (推測) | 執行 UPDATE SQL |
| 5 | Service | (可能調用 SignalR Hub) | 發送通知訊息 |

> 所有推測方法名稱需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Community_Groups | Read | 載入現有群組資料，進行存在性與權限檢查 |
| DB | Community_Groups | Update | 寫入新的 Name、IconPath、Description、Seq、TopMessage (若有) 與 UpdateTime |
| Redis | 群組快取 (若有) | Delete / Invalidate | 更新後清除快取，避免資料不一致（需人工確認是否有快取） |
| SignalR | CommunityHub (推測) | Push | 將群組資訊變更通知群組內成員 |

> 本流程未使用 Kafka 或 Queue。

---

## 6. 重要規則

- **權限限制**：僅群組擁有者 (Owner 欄位對應使用者帳號) 或特定管理角色可編輯；不可編輯 Owner 與 GType。
- **欄位限制**：
  - Name 須為合法 JSON 字串（多語言字典）。
  - IconPath 須為有效路徑（或允許空值）。
  - Seq 須為整數。
  - 置頂訊息 (TopMessage) 若提供，必須檢查該訊息存在且屬於該群組（GID 一致）。
- **不可暴露資料**：不得在回應中洩漏其他使用者的 AuthKey 或敏感欄位。
- **Transaction 規則**：更新動作應在一個 DB transaction 中完成，確保原子性（需人工確認）。
- **狀態值限制**：Enabled 欄位不由此 API 修改（需人工確認）。
- **不可修改欄位**：ID、Owner、GType、UpdateTime（由系統自動更新）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 群組 ID 不存在 | 回傳 404，錯誤訊息「群組不存在」 |
| 使用者未提供有效 AuthKey | 回傳 401 |
| 使用者非擁有者且無管理權限 | 回傳 403，禁止操作 |
| 請求缺少必要欄位（如群組 ID） | 回傳 400，參數檢驗失敗 |
| Name 格式非合法 JSON | 回傳 400，「名稱格式錯誤」 |
| 置頂訊息 ID 不屬於該群組 | 回傳 400，「訊息不存在或非本群組」 |
| DB 連線失敗或更新失敗 | 回傳 500，系統錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 擁有者編輯群組名稱 | 200，DB 名稱更新，UpdateTime 更新 |
| T02 | Permission Test | 非擁有者嘗試編輯 | 403，權限不足 |
| T03 | Validation Test | 缺少群組 ID | 400，參數錯誤 |
| T04 | Validation Test | 置頂訊息 ID 無效 | 400，訊息查無或 GID 不符 |
| T05 | Flow Test | 編輯名稱後，SignalR 推播 | 群組成員收到更新通知 |
| T06 | Cache Test | 若有 Redis 快取，編輯後讀取 | 取得最新資料，非舊快取 |

---

## 9. 高風險區域

- **權限繞過**：務必嚴格比對 Owner 與當前使用者，防止透過竄改請求參數修改他人群組。
- **置頂訊息一致性**：若置頂訊息被刪除，群組 TopMessage 欄位應同步清空；本 API 若僅更新欄位，需考慮邊界情況（需人工確認）。
- **快取一致性**：若存在群組快取，更新後須立即失效或更新快取，避免前端讀到舊資料。
- **SignalR 通知失敗**：通知失敗不應阻止 DB 更新，但需記錄 log。

---

## 10. 常見錯誤

- 新人容易忘記檢查 Owner 權限，直接允許所有已登入使用者編輯。
- AI 可能誤解「編輯」為可修改 Enabled 或 GType，實際上這些欄位應由其他專用 API 管理。
- 忽略 Name 的多語言 JSON 格式，直接將前台輸入的純文字寫入導致後續解析失敗。
- 更新 DB 時未帶上 WHERE 條件或未限制 ID，可能影響其他群組（應使用 WHERE ID = @groupId）。
- 忘了設定 UpdateTime，導致前端排序或同步邏輯出錯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 需求描述 | README.md -> 社群群組：可設定名稱、圖示、排序，並管理置頂訊息 |
| DB Table | Community_Groups (欄位 ID, Name, IconPath, Description, Seq, Owner, GType, UpdateTime) - 來自 `CommunityDataProvider.cs` 分析 |
| 推測 API | 需人工確認 Controller 與路由 |
| 權限模型 | 需人工確認 Owner 欄位與管理員邏輯 |
| TopMessage 儲存方式 | 需人工確認欄位是否在 Community_Groups 或另有配置表 |