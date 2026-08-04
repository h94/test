# 場景：使用者驗證

## 1. 場景目的
依據使用者提供的 AuthKey 進行身份驗證，查詢 GameUserInfo 取得基本資料（帳號、等級、名稱、會籍），並檢查其訂閱記錄（GameUserSubLog）以確認會員權限是否有效。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| POST | /api/auth/verify | （需人工確認）猜想接收 AuthKey 進行驗證 |

---

## 3. 流程總覽
1. 接收請求中的 AuthKey
2. 查詢 `GameUserInfo` 表，依 `AuthKey` 取出使用者記錄
3. 若記錄不存在 → 回傳 401 或對應未授權錯誤
4. 檢查 `Rank` 或 `Memberships` 欄位，判斷基本權限
5. 查詢 `GameUserSubLog` 表，取該 AuthKey 最新一筆有效訂閱記錄，比較 `SubEndTime` 是否大於當前時間
6. 若無有效訂閱 → 依業務規則回傳 403 或提示過期
7. 組合回傳物件（不包含 AuthKey 本身），回傳成功

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | AuthController.Verify | 接收 AuthKey 參數，呼叫服務 |
| 2 | Service | AuthService.VerifyAsync | 呼叫 Provider 查詢 GameUserInfo |
| 3 | Provider | GameUserInfoProvider | 執行 `SELECT * FROM GameUserInfo WHERE AuthKey = @key` |
| 4 | Service | AuthService.VerifyAsync | 檢查回傳結果，若為 null 則拋例外 |
| 5 | Service | AuthService.VerifyAsync | 解析 `Rank`、`Memberships`，檢查權限 |
| 6 | Provider | GameUserSubLogProvider | 執行查詢最新訂閱記錄（依 `AuthKey` 排序 `AddTime DESC`） |
| 7 | Service | AuthService.VerifyAsync | 判斷 `SubEndTime` 是否仍有效，決定回傳成功或失敗 |

> 註：`Controller`、`Service`、`Provider` 實際名稱與呼叫方式**需人工確認**，此處為推估流程。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `GameUserInfo` 表 | Read | 讀取使用者基本資訊對應 AuthKey |
| DB | `GameUserSubLog` 表 | Read | 查詢最新有效訂閱記錄，檢查到期時間 |
| Cache | Redis | 可能存在 Read | 快取 AuthKey → GameUserInfo 映射（需人工確認） |
| Queue | 無 | – | 本場景未使用 Message Queue |

---

## 6. 重要規則
- **AuthKey 必須唯一**且存在於 `GameUserInfo` 表中，若不存在則拒絕驗證。
- 會員權限依 `Rank`（整數）或 `Memberships`（JSON 格式）欄位判斷；若使用 `Memberships`，需正確解析 JSON，內容格式尚未明確（**需人工確認**）。
- 訂閱有效條件：`GameUserSubLog` 中有 `SubEndTime` 大於當前時間的記錄；若使用字串格式比對，需注意時區與格式一致性（**需人工確認**）。
- AuthKey 本身不得輸出至回應或日誌，避免洩漏。
- 若使用快取，當使用者訂閱變更或 AuthKey 遭撤銷時，應立即清除對應快取（Cache Invalidation）。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| AuthKey 不存在於 `GameUserInfo` | 回傳 401 Unauthorized，訊息「無效的授權金鑰」 |
| AuthKey 存在但 `Rank` 不符合最低要求 | 回傳 403 Forbidden，訊息「權限不足」 |
| 無任何 `GameUserSubLog` 記錄或最新訂閱已過期 | 回傳 403 或特定錯誤碼，提示「訂閱已過期或不存在」 |
| 資料庫連線逾時 | 回傳 500 Internal Server Error，遮蔽細節 |
| AuthKey 參數為空或格式錯誤 | 回傳 400 Bad Request |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TEST-01 | API Test | 提供有效的 AuthKey，且擁有有效訂閱 | 回傳 200，包含 Account, UserName, Rank, Memberships, 訂閱狀態（有效） |
| TEST-02 | API Test | 提供無效的 AuthKey | 回傳 401 |
| TEST-03 | API Test | 提供有效 AuthKey 但無任何訂閱記錄 | 依業務規則回傳 403 或特定錯誤 |
| TEST-04 | Permission Test | AuthKey 對應的 Rank 低於所需門檻 | 回傳 403 |
| TEST-05 | Flow Test | 模擬 DB 查詢失敗 | 回傳 500，且不洩漏內部錯誤訊息 |
| TEST-06 | Flow Test | 驗證 Memberships JSON 解析，若格式錯誤 | 系統應有 fallback 處理或回傳明確錯誤 |

---

## 9. 高風險區域
- **敏感資料**：`GameUserInfo` 表的 `AuthKey` 查詢必須使用參數化查詢，避免 SQL Injection。
- **時間比較**：`GameUserSubLog` 的 `SubEndTime` 若為 `nvarchar`，需確認儲存格式並一致性處理（例如統一轉為 UTC 時間戳比較）。
- **快取一致性**：若採用 Redis 快取使用者驗證結果，需在訂閱變更或 AuthKey 失效時主動清除，避免使用者因快取而繼續擁有權限。
- **查詢效能**：`GameUserSubLog` 可能積累大量歷史資料，查詢最新訂閱時建議建立複合索引 `(AuthKey, AddTime DESC)`。

---

## 10. 常見錯誤
- 新手僅查詢 `GameUserInfo` 而遺漏訂閱狀態檢查，導致過期會員仍可通過驗證。
- 未處理 `Memberships` JSON 欄位為 null 或格式錯誤的情況，造成例外中斷整個流程。
- 回應中不慎回傳 `AuthKey` 欄位，造成資安風險。
- 誤將 `GameUserSubLog` 的 `SubEndTime` 直接當成字串比較，未考慮時區或格式差異，導致誤判。
- AI 可能誤解驗證流程僅需單表查詢，忽略與訂閱記錄的關聯。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| DB Table | `GameUserInfo` (欄位: Authkey, Account, Rank, UserName, Memberships) |
| DB Table | `GameUserSubLog` (欄位: AuthKey, SubEndTime, AddTime 等) |
| README | 「使用者與訂閱：維護使用者資訊（GameUserInfo）與訂閱記錄（GameUserSubLog），依據 AuthKey 驗證身份並檢查會員權限。」 |
| Code | 具體 Controller/Service/Provider 名稱與實作**尚缺實際代碼證據，需人工確認** |

---

### 建議新增文件/規則
- 明確 AuthKey 的產生與生命週期規範（如過期時間、撤銷機制）。
- 定義 `Memberships` JSON 的結構說明，供前後端一致使用。
- 若存在 Redis 快取，應補充 Cache Key 設計與更新策略文件。
- 針對訂閱狀態檢查，訂定標準錯誤碼與回應格式，避免不同情境回覆混亂。