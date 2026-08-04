# 註冊遊戲編輯者

## 1. 場景目的

此流程為遊戲編輯者提供一個有效的註冊方式，使其能夠通過平台 API 註冊並將其資料緩存於 Redis，以後續使用者管理需要。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/v1/game/editors/{authKey} | 註冊遊戲編輯者 |

---

## 3. 流程總覽

1. 接收遊戲編輯者註冊請求。
2. 使用提供的 authKey 驗證請求合法性。
3. 檢查電子郵件是否合法且不在禁止域名列表中。
4. Hash 並儲存編輯者的密碼。
5. 新增資料至 Cassandra 中的 `member.gameusers` 表。
6. 將註冊資料寫入 Redis 快取。
7. 返回註冊成功的響應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | GameEditorController.Register | 接收註冊請求 |
| 2 | Service | GameEditorService.ValidateAuthKey | 驗證 authKey |
| 3 | Validator | EmailValidator.Validate | 驗證電子郵件格式與禁止域名 |
| 4 | Service | PasswordHasher.HashPassword | 雜湊密碼 |
| 5 | Repository | GameUserRepository.Insert | 寫入 `member.gameusers` |
| 6 | Cache | RedisManager.Set | 寫入 `editor_cache:{authkey}` |
| 7 | Controller | GameEditorController.ResponseSuccess | 返回成功響應 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | member.gameusers | Write | 存儲編輯者資料 |
| Redis | editor_cache:{authKey} | SET | 快取編輯者詳細資料 |

---

## 6. 重要規則

- email 須通過格式與禁止網域驗證。
- password 需使用安全雜湊儲存。
- authKey 必須合法且已經過驗證。
- 註冊用戶不得包含空白或不合法的角色資訊。
- 編輯者資訊變更需同步更新快取。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 禁止的 email 網域 | 返回錯誤訊息拒絕註冊 |
| 無效的 authKey | 返回錯誤訊息無法完成註冊 |
| Redis 寫入錯誤 | 回退資料庫寫入並返回錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | Integration Test | 正常註冊流程 | 註冊成功並返回成功訊息 |
| T02 | API Test | 使用禁止域名的 email | 返回錯誤消息 |
| T03 | Permission Test | 使用無效 authKey | 終止流程並返回授權錯誤 |

---

## 9. 高風險區域

- `member.gameusers` 表的寫操作。
- Redis 快取與數據庫一致性管理。
- 客戶端提供的 authKey 驗證機制。

---

## 10. 常見錯誤

- 常見使用未予以禁止的 email 網域進行註冊。
- 忘記在註冊後更新或刪除快取中的舊資料。

---

## 11. Evidence

所有重要結論必須附 evidence：

| 類型 | 來源 |
|---|---|
| API | /api/v1/game/editors/{authKey} |
| DB | member.gameusers |
| Redis | editor_cache:{authkey} |
| Code | GameEditorService.Register |