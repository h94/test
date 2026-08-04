# 使用者註冊

## 1. 場景目的

描述新用戶註冊流程，驗證用戶填寫的資料並生成新的會員記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/v1/game/user/register | 提供使用者註冊功能 |

---

## 3. 流程總覽

1. 收到註冊請求
2. 檢查 Email 格式及黑名單
3. 驗證密碼強度及一致性
4. 生成 `account` 與 `authkey`
5. 儲存使用者資訊至 `gameusers`
6. 設定初始 `status` 為未啟用
7. 回應註冊成功或錯誤訊息

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | UserController.Register | 接收註冊請求 |
| 2 | Service | UserService.ValidateEmail | 檢查 Email 格式及黑名單 |
| 3 | Service | UserService.HashPassword | 驗證與加密密碼 |
| 4 | Service | UserService.GenerateAccountAuthKey | 生成 `account` 和 `authkey` |
| 5 | Repository | UserRepository.Insert | 儲存至資料庫 |
| 6 | Response | — | 回應用戶 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | member.gameusers | Write | 儲存新的會員資料 |
| DB | member.forbidden_email_domains | Read | 檢查 Email 黑名單 |

---

## 6. 重要規則

- Email：檢查 `forbidden_email_domains` 黑名單 [evidence: DB schema member]
- 密碼：使用 `Hash.HashPasswordString` 雜湊後儲存 [evidence: service detail]
- account 設定：平台前綴 + Email hash
- status 預設：初始化為未啟用 (`0`) [evidence: DB detail member]
- authkey：生成後不可變更，僅內部使用 [evidence: service detail]

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Email 格式錯誤 | 回應無效 Email 格式訊息 |
| Email 黑名單 | 拒絕註冊並回應錯誤 |
| 密碼不符合規範 | 回應密碼格式錯誤訊息 |
| 資料庫寫入失敗 | 回應註冊失敗訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 註冊有效新用戶 | 成功回應 |
| T2 | Integration Test | 註冊 Email 黑名單用戶 | 錯誤提示 |
| T3 | Flow Test | 帳號重複註冊 | 回應重複帳號訊息 |
| T4 | Security Test | 密碼使用弱口令 | 回應拒絕 |

---

## 9. 高風險區域

- DB 寫入 `gameusers` 表
- Email 黑名單檢查
- 密碼加密與保存
- 狀態預設設置

---

## 10. 常見錯誤

- 驗證 Email 黑名單遺漏
- 明文保存密碼
- 忽略狀態初始設置
- 查詢時無法過濾未啟用帳號

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | UserController.Register |
| DB | member.gameusers |
| Code | UserService.ValidateEmail |
| Code | UserService.HashPassword |
| SQL | SELECT * FROM member.forbidden_email_domains |