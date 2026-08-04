# 使用者登入

## 1. 場景目的

會員透過登入 API 驗證身份並取得訪問權限，以訪問平台上的其他服務。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/v1/game/user/login | 用於會員登入 |

---

## 3. 流程總覽

1. 接收登入請求
2. 驗證提交的帳號與密碼
3. 查詢 `member.gameusers` 以取得使用者資訊
4. 驗證使用者狀態
5. 紀錄登入狀態到 `Redis`
6. 回傳登入成功 Token

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | AuthController.Login | 接收並驗證登入請求格式 |
| 2 | Service | AuthService.ValidateUser | 比對帳號與密碼 |
| 3 | Provider | UserProvider.GetUserByAuthKey | 查詢會員資料 |
| 4 | Service | AuthService.CheckStatus | 驗證狀態（`status=1`） |
| 5 | Cache | Redis.Set | 記錄登入狀態 |
| 6 | Controller | AuthController.LoginResponse | 回應成功 Token |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | member.gameusers | Read | 驗證帳號與狀態 |
| Redis | login_track:{loginTrackId} | Write | 記錄登入狀態與設備資訊 |

---

## 6. 重要規則

- 權限限制：僅 `status=1` 的帳號可登入。
- 欄位限制：不可直接返回 `password`。
- Transaction 規則：需確保狀態更新一至性（DB 與 Cache）。
- 對外不可暴露 `authkey`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號不存在 | 返回錯誤訊息 |
| 密碼錯誤 | 返回錯誤訊息 |
| 帳號狀態未啟用 | 返回錯誤訊息 |
| Redis 寫入失敗 | 重試或記錄例外 |
| DB timeout | 返回系統錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| 001 | Integration Test | 正確登入流程 | 成功取得 Token |
| 002 | API Test | 帳號或密碼錯誤 | 返回錯誤訊息 |
| 003 | Permission Test | 帳號未啟用 | 返回錯誤訊息 |
| 004 | Flow Test | Redis 寫入失敗 | 適當處理例外 |

---

## 9. 高風險區域

- 高風險 API：/api/v1/game/user/login
- Cache consistency：登入狀態不一致可能造成安全問題
- Idempotency：需確保重複請求的正確處理

---

## 10. 常見錯誤

- 未檢查狀態是否為啟用(`status=1`)
- 回傳過多使用者資訊，洩露 `authkey` 或敏感資料
- 未正確處理 Redis 寫入例外狀況

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | /api/v1/game/user/login |
| DB | member.gameusers |
| Redis | login_track:{loginTrackId} |
| Code | AuthService.ValidateUser |
| SQL | SELECT * FROM member.gameusers WHERE authkey=? |