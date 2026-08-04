# 建立社群群組

## 1. 場景目的
讓已驗證的使用者建立一個新的社群群組，支援官方、個人等多元類型，並設定名稱、圖示、描述及排序，供後續聊天、預測等社群功能使用。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| POST | /api/Community/CreateGroup | 需人工確認確切路由，推測為建立社群群組 |

---

## 3. 流程總覽
1. 從請求中取得 authKey，驗證使用者身份（查詢 GameUserInfo）。
2. 檢查會員權限：確認目前帳號是否可建立要求的群組類型（GType）。
3. 驗證輸入欄位：Name（JSON 格式多語言字典）、IconPath、GType、Owner、Description、Seq。
4. 若 GType 為 personal，強制檢查 Owner 是否等於目前登入帳號（並可選檢查是否超過一人一群限制，需人工確認）。
5. 產生唯一群組 ID（格式需人工確認，推測為 GUID）。
6. 設定 Enabled=1、UpdateTime=目前 Unix 毫秒時間。
7. 將群組資料寫入 `Community_Groups` 表。
8. 回傳建立的群組完整資訊。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | ActionFilter | AuthFilter | 驗證 authKey，查詢 GameUserInfo 取得 Account、Rank |
| 2 | Validator | CreateGroupValidator | 驗證輸入 Model（必填、格式、GType 合法範圍） |
| 3 | Controller | CommunityController.CreateGroup | 接收請求，呼叫 Service |
| 4 | Service | CommunityService.CreateGroup | 檢查業務規則（權限等級對應群組類型、個人群組限制） |
| 5 | Provider | CommunityDataProvider.InsertGroup | 執行 SQL INSERT 寫入 Community_Groups |
| 6 | Transfer | GroupTransfer.ToDto | 將資料庫回傳實體轉換為 API 回應 DTO |

*註：實際類別與方法名稱需人工確認程式碼。*

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | GameUserInfo | Read | 查詢 authKey 取得使用者資訊 |
| DB | Community_Groups | Insert | 新增群組 |
|  -  |  -  |  -  | 無 Cache 或 Queue 操作 |

---

## 6. 重要規則
- **權限限制**：建立 official 或 vip 群組可能需要較高會員 Rank（確切門檻需人工確認）；一般使用者僅可建立 normal 或 personal。
- **欄位限制**：
  - `GType` 值必須為官方定義的集合（official, normal, vip, personal, test）。
  - `Name` 必須為合法 JSON 字串，代表多語言名稱字典（如 `{"zh-TW":"名稱"}`）。
  - `Owner` 僅在 GType=personal 時為必填，且必須等於當前 authKey 所屬帳號。
  - `IconPath` 可為空字串或 null。
  - `Seq` 須為非負整數，預設可為 0。
- **不可暴露資料**：回應不能洩漏內部 ID 生成規則或未經處理的資料庫錯誤。
- **Transaction**：單表寫入，無跨表交易需求。
- **狀態值限制**：`Enabled` 建立時一律設為 1；`UpdateTime` 由系統賦值，不允許前端傳入。
- **不可修改欄位**：群組 ID 由系統產生，不允許前端指定。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 未提供 authKey 或 authKey 無效 | 回傳 401 或自訂未登入錯誤碼 |
| 使用者權限不足建立該類型群組 | 回傳 403 或自訂權限不足錯誤碼 |
| Name 非合法 JSON 格式 | 回傳 400，提示名稱格式錯誤 |
| GType 不在允許清單中 | 回傳 400，提示群組類型無效 |
| GType 為 personal，但 Owner 為空或不符登入帳號 | 回傳 400，提示擁有者錯誤 |
| 同帳號超過允許的個人群組數量（若有限制） | 回傳 400，提示已達上限（需人工確認） |
| DB 寫入失敗（逾時、鎖定、主鍵衝突） | 回傳 500，系統內部錯誤 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| CG-01 | Integration Test | 一般使用者建立 normal 群組，輸入合法 | 回傳 200，DB 出現完整記錄 |
| CG-02 | Integration Test | 建立 personal 群組，Owner 正確 | 回傳 200 |
| CG-03 | Permission Test | 一般使用者嘗試建立 official 群組 | 回傳 403 |
| CG-04 | API Test | Name 為非 JSON 字串 | 回傳 400，明確錯誤訊息 |
| CG-05 | API Test | personal 群組未提供 Owner | 回傳 400 |
| CG-06 | Flow Test | 模擬 DB 寫入失敗 | 回傳 500，不拋出過多內部細節 |

---

## 9. 高風險區域
- **高風險 table**：`Community_Groups` - 錯誤的 Owner 設定可能導致群組濫用或難以管理。
- **高風險 API**：此 API 若缺乏權限分級，可能被用來大量創建假群組或竊取名義。
- **Idempotency**：目前無冪等控制，重複提交可能建立多個相同群組（若前端未做防護），需評估是否應導入短時冪等鍵。

---

## 10. 常見錯誤
- **新人容易犯錯**：
  - 直接將使用者輸入文字存入 `Name`，忽略必須序列化為 JSON 多語言字典。
  - 未檢查 `GType` 大小寫或自訂值，導致存入不合法群組類型。
  - 忘記在 personal 群組驗證 Owner 與登入帳號之關聯。
- **AI 容易誤解**：
  - 假定所有欄位皆必填，但 IconPath 與 Description 可為空。
  - 猜測群組 ID 由前端傳入。
- **常見漏檢查項目**：
  - 未驗證使用者是否被封鎖或帳號凍結。
  - 未檢查 `Name` 長度是否超過資料庫欄位上限。
  - 未對 `Name` 內容做 HTML 編碼（若前端直接 innerHTML 可能引發 XSS）。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| DB Table: Community_Groups | 欄位定義來自 CommunityDataProvider.cs (Phase0/1 semantics) |
| GType 合法值 | 欄位註解：official/normal/vip/personal/test |
| 使用者驗證 | 由 authKey 查詢 GameUserInfo 表，細節需人工確認具體 AuthService 實作 |
| API 路由 | 無 OpenAPI 文件，路徑為慣例推測，需人工確認 Controller 路由 |
| 程式流程 | 無實際程式碼證據，類別與方法名為業界常見命名模式推斷 |