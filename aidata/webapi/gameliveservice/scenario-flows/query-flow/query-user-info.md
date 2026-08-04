# 查詢使用者資訊

## 1. 場景目的
根據使用者提供的帳號或 AuthKey，查詢該使用者的基本資料（含會員等級、顯示名稱）、擁有的會籍，以及歷史訂閱記錄。此流程為前端展示個人資料頁或進行會員權限判斷的基礎。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | /api/gameuser/info | 接受 account 或 authKey 參數，查詢使用者資訊（需人工確認實際路由） |

> 註：目前無明確 API 定義，推測路徑為 UsersController，參數可能透過 Header 攜帶 AuthKey 或 QueryString 傳遞 Account。

---

## 3. 流程總覽
1. 接收請求，解析參數（Account 或 AuthKey）。
2. 如有 AuthKey，先查詢 GameUserInfo 驗證有效性，並取得 Account。
3. 根據 Account 查詢 GameUserInfo 表，取得 Rank、UserName、Memberships。
4. 根據 AuthKey（或利用 Account 從 GameUserInfo 取得的 AuthKey）查詢 GameUserSubLog 表，取回該用戶的所有訂閱記錄（可能按時間倒序）。
5. 組裝回應資料：用戶資訊、會籍與訂閱歷史。
6. 回傳結果給客戶端。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | GameUserController.GetUserInfo | 接收參數，呼叫服務層（需人工確認） |
| 2 | Service | GameUserService.GetUserDetail | 調用資料存取層，組合回應（需人工確認） |
| 3 | Provider | GameUserInfoDataProvider.GetByAccount | 從 GameUserInfo 讀取 Rank、UserName、Memberships（需人工確認） |
| 4 | Provider | GameUserSubLogDataProvider.GetByAuthKey | 從 GameUserSubLog 讀取所有訂閱歷程（需人工確認） |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | GameUserInfo | Read | 取得 Rank、UserName、Memberships、AuthKey |
| DB | GameUserSubLog | Read | 取得該 AuthKey 的所有訂閱記錄（SubID, SubTime, SubEndTime, PayType, PayMethod, TradeNo） |
| DB | GameUser | Read（可能） | 交叉驗證使用者是否存在（需人工確認） |

> 目前無使用 Redis、Kafka 或 Queue 的證據。

---

## 6. 重要規則
- 權限限制：僅能查詢 **自己的資料**，AuthKey 必須與目標 Account 關聯一致，否則視為未授權。
- 欄位限制：回應中 **不應包含 AuthKey** 明文；Memberships 為 JSON 字串，前端需自行解析。
- 不可修改欄位：本場景僅提供讀取，無任何寫入操作。
- TTL 規則：無快取，即時查詢。
- Transaction：無跨表寫入，不需要 Transaction。
- Retry 規則：無外部呼叫，重試由客戶端決定。
- 狀態值限制：Rank 為整數，對應會員等級（如 0:一般會員, 1:VIP 等，需人工確認定義）。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 帳號不存在於 GameUserInfo | 回傳 HTTP 404 或自定義「用戶不存在」 |
| AuthKey 無效或已過期 | 回傳 HTTP 401 Unauthorized |
| 查詢參數缺失（無 account 且無 authKey） | 回傳 HTTP 400 Bad Request |
| 資料庫連線逾時 | 回傳 HTTP 500 Internal Server Error |
| 使用者 AuthKey 嘗試查詢他人 Account | 回傳 HTTP 403 Forbidden（權限不足） |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| GET-USER-01 | API Test | 以正確 AuthKey 查詢自身資訊 | 成功回傳 UserName、Rank、Memberships、SubLog |
| GET-USER-02 | API Test | 傳入不存在的 Account | 回傳 404，無資料 |
| GET-USER-03 | Permission Test | 使用 AuthKey A 查詢 Account B | 回傳 403 或拒絕存取 |
| GET-USER-04 | API Test | 無攜帶任何身分參數 | 回傳 400 |
| GET-USER-05 | Flow Test | 查詢包含多筆訂閱記錄的用戶 | 回傳的 SubLog 按照時間排序，內容正確 |
| GET-USER-06 | API Test | 資料庫無法連線 | 回傳 500，不暴露內部細節 |

---

## 9. 高風險區域
- 高風險 table：**GameUserInfo**（含憑證與會員等級）、**GameUserSubLog**（含支付方式）
- 高風險 API：若權限校驗不嚴謹，攻擊者可遍歷帳號取得所有用戶資料。
- 快取一致性：無快取層，風險低。
- 跨服務資料同步：無。
- Queue retry / Idempotency：本場景為唯讀，GET 具備天然冪等性。

---

## 10. 常見錯誤
- 新人常忽略 **AuthKey 與 Account 的關聯驗證**，導致任意用戶查詢漏洞。
- AI 可能將 Memberships 未經反序列化直接存入回應，造成前端解析失敗。
- 忽略訂閱記錄的分頁需求，當記錄數量過大時直接全表查詢，引發效能問題。
- 回應中誤將 AuthKey 欄位暴露，增加密碼學風險。
- 誤解 Rank 為字串，實為整數。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| 核心表定義 | Phase 1 analysis：GameUserInfo（Authkey, Account, Rank, UserName, Memberships） |
| 核心表定義 | Phase 1 analysis：GameUserSubLog（AuthKey, AddTime, SubEndTime, SubID, PayType, PayMethod, SubTime, TradeNo） |
| 功能驗證 | README.md：「使用者與訂閱 維護使用者資訊（GameUserInfo）與訂閱記錄（GameUserSubLog），依據 AuthKey 驗證身份並檢查會員權限。」 |
| 流程推導 | 基於 DB schema 及 README 描述，無 controller 層原始碼（需人工確認實際 Service / Provider 類別名） |